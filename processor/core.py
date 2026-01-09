import functools
import os
import time
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain
from typing import Dict, Any, Type, List, MutableMapping, Iterator

from PIL import Image, ImageColor

from processor.mergers import Merger
from util import get_exif


class PipelineContext(MutableMapping):
    """管道上下文"""

    def __init__(self, config: Dict[str, Any]):
        self._config = config

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key) if key in self._config and self._config.get(key) is not None else default

    def get_exif(self) -> Dict[str, Any]:
        return self.get('exif')

    def getcolor(self, key: str, default: Any = None) -> Any:
        return _parse_color(self._config.get(key, default))

    def getint(self, key: str, default: int = 0) -> int:
        return int(self.get(key, default))

    def getenum(self, key: str, default: Any = None, enum: Type[Enum] = None) -> Any:
        value = self.get(key, default)

        # 未指定枚举类型，直接返回原值
        if enum is None:
            return value

        # 已经是目标枚举类型，直接返回
        if isinstance(value, enum):
            return value

        # 尝试通过 name 查找 (如 "RED" -> Color.RED)
        if isinstance(value, str):
            try:
                return enum[value]
            except KeyError:
                pass

        # 尝试通过 value 查找 (如 1 -> Color.RED)
        try:
            return enum(value)
        except ValueError:
            pass

        # 都找不到，返回默认值
        return default

    def get_processor_name(self):
        return self.get("processor_name")

    def get_buffer(self) -> List[Image]:
        if not self.get("buffer_loaded", False) and self.get("buffer_path"):
            self.set("buffer", [Image.open(path) for path in self.get("buffer_path")])
            self.set("buffer_loaded", True)
        return self.get("buffer", [])

    def set(self, key: str, value: Any):
        self._config[key] = value

    def save_buffer(self, processor_name: str, force_save: bool = False):
        if not (force_save or self.get("save_buffer", False)):
            return self
        directory = self.get("output", "./tmp")
        if not os.path.isdir(directory):
            os.makedirs(directory)
        buffer_path = []
        for img in self.get_buffer():
            if img.mode == "RGB":
                file_ext = "jpg"
            elif img.mode == "RGBA":
                file_ext = "png"
            else:
                raise RuntimeError(f"Unsupported image mode {img.mode}")

            new_filename = f"{processor_name}_{uuid.uuid4().hex}.{file_ext}"
            path = os.path.join(directory, new_filename)
            img.save(path)
            buffer_path.append(path)
        self.set("buffer_path", buffer_path)
        return self

    def update_buffer(self, buffer: List[Image]):
        self.set("buffer", buffer)
        return self

    def success(self, success: bool = True):
        if self.get("buffer_path"):
            print(f"generate new image {self.get('buffer_path')}")
        self.set("success", success)
        return self

    # MutableMapping 要求实现的抽象方法
    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._config[key] = value

    def __delitem__(self, key: str) -> None:
        del self._config[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._config)

    def __len__(self) -> int:
        return len(self._config)


class ImageProcessor(ABC):
    @abstractmethod
    def process(self, ctx: PipelineContext):
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def category(self) -> str:
        pass

    def __init_subclass__(cls, **kwargs):
        """
        这个钩子方法会在子类定义时自动调用。
        在这里我们可以对子类的方法进行拦截（Hook）。
        """
        super().__init_subclass__(**kwargs)

        # 获取子类原本定义的 process 方法
        original_process = cls.process

        # 定义一个包装函数（切面逻辑）
        @functools.wraps(original_process)
        def wrapper(self, ctx: PipelineContext):
            start_time = time.perf_counter()  # 使用高精度计时
            try:
                # 执行原本的业务逻辑
                return original_process(self, ctx)
            finally:
                end_time = time.perf_counter()
                cost_ms = (end_time - start_time) * 1000
                # 打印日志
                print(f"{self.name()} cost {cost_ms:.2f} ms")

        # 将子类的 process 方法替换为包装后的方法
        cls.process = wrapper

        # 自动注册到注册表
        # 注意：这里我们注册的是类本身，而不是实例
        # 需要创建一个临时实例来获取 name()，或者要求子类实现类方法/属性
        try:
            # 尝试创建实例来获取 name
            # 注意：如果 __init__ 需要参数，这里可能会失败
            instance = cls()
            key = instance.name()
            register_processor(key, cls)
        except Exception as e:
            # 如果无法创建实例，可以要求子类实现类级别的 name 属性
            print(f"Warning: Could not auto-register {cls.__name__}: {e}")
            # 或者可以抛出自定义异常要求子类实现特定接口
            raise TypeError(
                f"{cls.__name__} must be instantiable without arguments "
                f"for auto-registration, or implement a class-level 'name' property."
            ) from e


class Direction(Enum):
    """拼接方向"""
    HORIZONTAL = "horizontal"  # 水平拼接（左到右）
    VERTICAL = "vertical"  # 垂直拼接（上到下）
    DIAGONAL = "diagonal"  # 对角
    RADIAL = "radial"  # 径向


class Alignment(Enum):
    """对齐方式"""
    # 通用
    START = "start"
    CENTER = "center"
    END = "end"

    # 语义化别名（水平拼接时的垂直对齐）
    TOP = "start"
    MIDDLE = "center"
    BOTTOM = "end"

    # 语义化别名（垂直拼接时的水平对齐）
    LEFT = "start"
    RIGHT = "end"


def _parse_color(color) -> tuple:
    """
    解析颜色为 RGBA 元组

    支持格式:
    - 元组: (255, 255, 255) 或 (255, 255, 255, 128)
    - 字符串元组: '(255,255,255,0)' 或 '255,255,255,0'
    - 十六进制: '#FFFFFF' 或 '#FFFFFFFF'
    - 颜色名称: 'red', 'blue' 等
    """
    # 已经是元组或列表
    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            return *color, 255
        return tuple(color)

    # 字符串处理
    if isinstance(color, str):
        color = color.strip()

        # 处理元组格式字符串: '(255,255,255,0)' 或 '255,255,255,0'
        color_clean = color.strip('()')
        if ',' in color_clean:
            try:
                parts = [int(x.strip()) for x in color_clean.split(',')]
                if len(parts) == 3:
                    return *parts, 255
                elif len(parts) == 4:
                    return tuple(parts)
            except ValueError:
                pass

        # 处理十六进制或颜色名称
        try:
            rgba = ImageColor.getrgb(color)
            if len(rgba) == 3:
                return *rgba, 255
            return rgba
        except ValueError:
            pass

    raise ValueError(f"无法解析颜色: {color}")


_processor_registry: Dict[str, Type['ImageProcessor']] = {}


def get_all_processors() -> Dict[str, Type['ImageProcessor']]:
    """获取所有已注册的处理器"""
    return _processor_registry.copy()


def get_processor(key: str) -> Type['ImageProcessor']:
    """从注册表获取处理器类"""
    return _processor_registry.get(key)


def register_processor(key: str, processor_cls: Type['ImageProcessor']):
    """注册处理器到全局注册表"""
    if key in _processor_registry:
        return
    _processor_registry[key] = processor_cls
    print(f"Registered processor: {key} -> {processor_cls.__name__}")


def start_process(data: List[dict], input_path: str = None, output_path: str = None):
    nodes = [PipelineContext(datum) for datum in data]
    if input_path is not None:
        nodes[0].set("buffer_path", [input_path])

    # 填充 exif 信息
    exif = get_exif(input_path)
    for node in nodes:
        if 'exif' not in node:
            node['exif'] = exif

    # 所有处理器的输出, 0 被看作是头元素的输出
    output = nodes[0].get_buffer()

    all_buffer = [output]
    last_merger_idx = -1

    for idx, node in enumerate(nodes):  # 修正1: 添加 enumerate
        processor = get_processor(node.get_processor_name())
        if processor is None:
            raise RuntimeError(f"Processor '{node.get_processor_name()}' not found")

        if not isinstance(processor, Merger):
            node.update_buffer(output)
        else:
            # 收集下标从上一个 merger 之后, 到当前 idx 为止的 buffer
            buffers_to_merge = all_buffer[last_merger_idx + 1:idx + 1]

            # 将数组的数组展平为数组
            flattened = list(chain.from_iterable(buffers_to_merge))
            node.update_buffer(flattened)
            last_merger_idx = idx

        processor().process(node)
        output = node.get_buffer()
        all_buffer.append(output)

    nodes[-1].save_buffer("final").success()
    if output_path is not None:
        nodes[-1].get_buffer()[0].convert("RGB").save(output_path)
        print(f"generate new image {output_path}")
    return nodes[-1].get_buffer()[0]
