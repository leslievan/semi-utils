import sys
from abc import ABC
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, List

import numpy as np
from PIL import ImageFont, Image, ImageDraw

from processor.core import PipelineContext, ImageProcessor, Direction, _parse_color

BASE_FONT_SIZE = 512


def load_font(font_path: str):
    try:
        if font_path:
            font_file = Path(font_path)

            # 如果是相对路径，转换为基于执行文件所在目录的绝对路径
            if not font_file.is_absolute():
                # 获取执行文件（主程序入口）的目录
                if getattr(sys, 'frozen', False):
                    # 如果是打包后的可执行文件（如 PyInstaller）
                    base_dir = Path(sys.executable).parent
                else:
                    # 如果是普通 Python 脚本
                    base_dir = Path(sys.argv[0]).resolve().parent

                font_file = base_dir / font_path

            return ImageFont.truetype(str(font_file), BASE_FONT_SIZE)
        else:
            # 尝试常见系统字体
            for fallback in ["fonts/AlibabaPuHuiTi-2-45-Light.otf", "arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]:
                try:
                    return ImageFont.truetype(fallback, BASE_FONT_SIZE)
                except OSError:
                    continue
            else:
                return ImageFont.load_default()
    except OSError:
        return ImageFont.load_default()


@dataclass
class TextSegment:
    text: str
    font_path: Optional[str] = None
    height: int = 100
    is_bold: bool = False
    color: str = "black"
    trim: bool = False

    def get(self, key: str, default=None):
        return getattr(self, key, default)

    @staticmethod
    def from_dict(data: dict):
        return TextSegment(
            text=data.get("text"),
            font_path=data.get("font_path", None),
            height=data.get("height", 100),
            color=data.get("color", "black"),
            is_bold=data.get("is_bold", False),
            trim=data.get("trim", False),
        )

    @staticmethod
    def from_dicts(data: List[dict]):
        return [TextSegment(
            text=datum.get("text"),
            font_path=datum.get("font_path", None),
            height=datum.get("height", 100),
            color=datum.get("color", "black"),
            is_bold=data.get("is_bold", False),
            trim=data.get("trim", False),
        ) for datum in data]


class Generator(ImageProcessor, ABC):

    def category(self) -> str:
        return "generator"


class SolidColorGenerator(Generator):

    def process(self, ctx: PipelineContext):
        width, height = ctx.get("width"), ctx.get("height")
        color = ctx.get("color")
        image = Image.new("RGBA", (width, height), color)
        ctx.update_buffer([image]).save_buffer().success()

    def name(self) -> str:
        return "solid_color"


class InterpolateMethod(Enum):
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


# ============ 缓动函数（处理 t 值）============
def _easing_linear(t: np.ndarray) -> np.ndarray:
    """线性"""
    return t


def _easing_ease_in(t: np.ndarray) -> np.ndarray:
    """缓入"""
    return t * t


def _easing_ease_out(t: np.ndarray) -> np.ndarray:
    """缓出"""
    return 1 - (1 - t) ** 2


def _easing_ease_in_out(t: np.ndarray) -> np.ndarray:
    """缓入缓出"""
    return np.where(t < 0.5, 2 * t * t, 1 - (-2 * t + 2) ** 2 / 2)


EASING_FUNCTIONS = {
    InterpolateMethod.LINEAR: _easing_linear,
    InterpolateMethod.EASE_IN: _easing_ease_in,
    InterpolateMethod.EASE_OUT: _easing_ease_out,
    InterpolateMethod.EASE_IN_OUT: _easing_ease_in_out,
}


# ============ NumPy 加速绘制 ============
def _draw_gradient_numpy(
        width: int,
        height: int,
        start_rgba: tuple,
        end_rgba: tuple,
        direction: Direction,
        method: InterpolateMethod = InterpolateMethod.LINEAR
) -> Image.Image:
    """NumPy 加速的渐变绘制"""

    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)

    # 计算进度 t
    if direction == Direction.HORIZONTAL:
        t = xx / (width - 1) if width > 1 else np.zeros_like(xx, dtype=float)
    elif direction == Direction.VERTICAL:
        t = yy / (height - 1) if height > 1 else np.zeros_like(yy, dtype=float)
    elif direction == Direction.DIAGONAL:
        t = (xx + yy) / (width + height - 2) if (width + height) > 2 else np.zeros_like(xx, dtype=float)
    elif direction == Direction.RADIAL:
        cx, cy = width / 2, height / 2
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        max_dist = np.sqrt(cx ** 2 + cy ** 2)
        t = np.clip(dist / max_dist, 0, 1)
    else:
        t = np.zeros((height, width), dtype=float)

    # 应用缓动函数
    easing_func = EASING_FUNCTIONS.get(method, _easing_linear)
    t = easing_func(t.astype(float))

    # 向量化颜色插值
    start = np.array(start_rgba, dtype=float)
    end = np.array(end_rgba, dtype=float)

    # 扩展维度 (height, width) -> (height, width, 1)
    t = t[:, :, np.newaxis]

    # 插值计算
    pixels = start + (end - start) * t
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)

    return Image.fromarray(pixels, mode='RGBA')


class GradientColorGenerator(Generator):
    def process(self, ctx: PipelineContext):
        width, height = ctx.get("width"), ctx.get("height")
        start_color = ctx.get("start_color")
        end_color = ctx.get("end_color")
        direction = ctx.getenum("direction", Direction.HORIZONTAL, Direction)  # horizontal, vertical, diagonal
        method = ctx.getenum("interpolate_method", InterpolateMethod.LINEAR, InterpolateMethod)

        start_rgba = _parse_color(start_color)
        end_rgba = _parse_color(end_color)

        image = _draw_gradient_numpy(
            width, height,
            start_rgba, end_rgba,
            direction, method
        )

        ctx.update_buffer([image]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "gradient_color"


class RichTextGenerator(Generator):
    @staticmethod
    def generate(segment: TextSegment) -> Image.Image:
        from processor.filters import ResizeFilter, TrimFilter
        font = load_font(segment.font_path)

        # 获取文本尺寸
        metrics = font.getmetrics()
        text = ' ' if not segment.text or segment.text == '' else segment.text
        bbox = font.getbbox(text)
        # 创建透明画布
        image = Image.new('RGBA', (int(bbox[2] - bbox[0]), metrics[0] + abs(metrics[1])), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # 直接绘制文本
        draw.text((0, 0), text, font=font, fill=_parse_color(segment.color))

        resize_ctx = PipelineContext({
            "buffer": [image],
            "height": segment.height * 1.13 if segment.is_bold else segment.height,
            "save_buffer": False,
            "trim_top": segment.trim,
            "trim_bottom": segment.trim,
        })
        TrimFilter().process(resize_ctx)
        ResizeFilter().process(resize_ctx)
        return resize_ctx.get_buffer()[0]

    def process(self, ctx: PipelineContext):
        img = RichTextGenerator.generate(TextSegment.from_dict(ctx))
        ctx.update_buffer([img]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "rich_text"


class MultiRichTextGenerator(Generator):
    def process(self, ctx: PipelineContext):
        from processor.mergers import ConcatMerger
        text_segments: List[TextSegment] = TextSegment.from_dicts(ctx.get("text_segments"))
        text_alignment = ctx.get("text_alignment")
        text_spacing = ctx.get("text_spacing")
        height = ctx.get("height", 100)

        text_images = []
        for segment in text_segments:
            segment.height = height
            context = PipelineContext(asdict(segment))
            context.set("save_buffer", False)
            RichTextGenerator().process(context)
            text_images.extend(context.get_buffer())

        concat_ctx = PipelineContext({
            "buffer": text_images,
            "alignment": text_alignment,
            "spacing": text_spacing,
            "output": ctx.get("output"),
            "save_buffer": False,
        })
        ConcatMerger().process(concat_ctx)

        ctx.update_buffer(concat_ctx.get_buffer()).save_buffer(self.name()).success()

    def name(self) -> str:
        return "multi_rich_text"


class ImageLoader(Generator):
    def process(self, ctx: PipelineContext):
        if isinstance(ctx.get('path'), str):
            ctx.update_buffer([Image.open(ctx.get('path'))]).success()
        elif isinstance(ctx.get('path'), list):
            ctx.update_buffer([Image.open(path) for path in ctx.get('path')])

    def name(self) -> str:
        return "image"
