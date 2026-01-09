from abc import ABC
from typing import List

from PIL import Image

from processor.core import ImageProcessor, Direction, Alignment, PipelineContext


def _calc_offset(size: int, max_size: int, alignment: Alignment) -> int:
    """根据对齐方式计算偏移量"""
    align_value = alignment.value  # 获取实际值（处理别名）

    if align_value == "start":
        return 0
    elif align_value == "center":
        return (max_size - size) // 2
    elif align_value == "end":
        return max_size - size
    return 0

class Merger(ImageProcessor, ABC):
    def category(self) -> str:
        return "merger"


class ConcatMerger(Merger):
    def process(self, ctx: PipelineContext):
        buffer = ctx.get_buffer()
        alignment = ctx.get_enum_value("alignment", Alignment.BOTTOM, Alignment)
        direction = ctx.get_enum_value("direction", Direction.HORIZONTAL, Direction)
        spacing = ctx.get("spacing", 10)
        background: tuple = ctx.get("background", (255, 255, 255, 0))  # 默认透明

        # 确保所有图片都是 RGBA 模式
        images = [img.convert("RGBA") if img.mode == "RGB" else img for img in buffer]

        # 计算输出尺寸
        if direction == Direction.HORIZONTAL:
            total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
            max_height = max(img.height for img in images)
            canvas_size = (total_width, max_height)
        else:  # VERTICAL
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
            canvas_size = (max_width, total_height)

        # 创建画布
        canvas = Image.new("RGBA", canvas_size, background)

        # 拼接图片
        current_pos = 0
        for img in images:
            if direction == Direction.HORIZONTAL:
                # 计算 y 偏移（垂直对齐）
                y_offset = _calc_offset(img.height, max_height, alignment)
                canvas.paste(img, (current_pos, y_offset), img)
                current_pos += img.width + spacing
            else:  # VERTICAL
                # 计算 x 偏移（水平对齐）
                x_offset = _calc_offset(img.width, max_width, alignment)
                canvas.paste(img, (x_offset, current_pos), img)
                current_pos += img.height + spacing
        ctx.update_buffer([canvas]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "concat"
