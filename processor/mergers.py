import json
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


class AlignmentMerger(Merger):
    def process(self, ctx: PipelineContext):
        buffer: List[Image] = ctx.get_buffer()
        horizontal_alignment = ctx.getenum("horizontal_alignment", Alignment.CENTER, Alignment)
        vertical_alignment = ctx.getenum("vertical_alignment", Alignment.CENTER, Alignment)
        background: tuple = ctx.getcolor("background", (255, 255, 255, 0))  # 默认透明
        offsets = json.loads(ctx.get("offsets", "[]"))

        if not buffer:
            return
        # 计算画布大小（所有图片的最大宽高）
        max_width = max(img.width for img in buffer)
        max_height = max(img.height for img in buffer)
        # 创建画布
        canvas = Image.new("RGBA", (max_width, max_height), background)
        # 遍历所有图片进行合并
        for i, img in enumerate(buffer):
            # 获取偏移量，索引超出时默认为 (0, 0)
            offset_x, offset_y = offsets[i] if i < len(offsets) else (0, 0)
            offset_x, offset_y = -offset_x, -offset_y
            # 处理水平对齐
            img_x = _calc_offset(img.width, max_width, horizontal_alignment)
            # 处理垂直对齐
            img_y = _calc_offset(img.height, max_height, vertical_alignment)
            # 处理偏移量
            img_x += offset_x
            img_y += offset_y
            # 确保图片是 RGBA 模式以正确处理透明度
            paste_img = img if img.mode == 'RGBA' else img.convert('RGBA')
            # 粘贴图片到画布（使用 alpha 通道作为蒙版）
            canvas.paste(paste_img, (img_x, img_y), paste_img)
        ctx.update_buffer([canvas]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "alignment"


class ConcatMerger(Merger):
    def process(self, ctx: PipelineContext):
        buffer = ctx.get_buffer()
        alignment = ctx.getenum("alignment", Alignment.BOTTOM, Alignment)
        direction = ctx.getenum("direction", Direction.HORIZONTAL, Direction)
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
