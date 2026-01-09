import re
from abc import ABC
from typing import Tuple

import numpy as np
from PIL import Image, ImageFilter

from processor.core import ImageProcessor, PipelineContext, start_process, get_processor
from processor.generators import MultiRichTextGenerator


class FilterProcessor(ImageProcessor, ABC):
    def category(self) -> str:
        return "filter"


class BlurFilter(FilterProcessor):
    def process(self, ctx: PipelineContext):
        radius = ctx.get("blur_radius", 5)

        buffer = []
        for img in ctx.get_buffer():
            if img.mode != "RGB":
                img = img.convert("RGB")
            ret_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
            buffer.append(ret_img)
        ctx.update_buffer(buffer).save_buffer(self.name()).success()

    def name(self) -> str:
        return "blur"


class ResizeFilter(FilterProcessor):
    def process(self, ctx: PipelineContext):
        width, height = ctx.get("width"), ctx.get("height")
        scale = ctx.get("scale")

        buffer = []
        for img in ctx.get_buffer():
            if width and height:
                target_size = (int(width), int(height))
            else:
                if width:
                    scale_f = float(width) / img.width
                elif height:
                    scale_f = float(height) / img.height
                elif scale:
                    scale_f = float(scale)
                else:
                    ctx.set("success", False)
                    return
                target_size = (int(img.width * scale_f), int(img.height * scale_f))

            ret_img = img.resize(target_size, resample=Image.Resampling.LANCZOS)
            buffer.append(ret_img)
        ctx.update_buffer(buffer).save_buffer(self.name()).success()

    def name(self) -> str:
        return "resize"


class TrimFilter(FilterProcessor):
    threshold: float = 10.0,
    padding: int = 0

    def process(self, ctx: PipelineContext):
        buffer = []
        for image in ctx.get_buffer():
            if image.height * image.width == 0:
                continue
            bbox = self.get_foreground_bbox(image, trim_left=ctx.get("trim_left"), trim_right=ctx.get("trim_right"),
                                            trim_top=ctx.get("trim_top"), trim_bottom=ctx.get("trim_bottom"))
            buffer.append(image.crop(bbox))
        ctx.update_buffer(buffer).save_buffer(self.name()).success()

    def name(self) -> str:
        return "trim"

    def _get_background_color(self, img_array: np.ndarray) -> np.ndarray:
        """取四角像素均值作为背景色"""
        corners = np.array([
            img_array[0, 0],  # 左上角
            img_array[0, -1],  # 右上角
            img_array[-1, 0],  # 左下角
            img_array[-1, -1]  # 右下角
        ])
        return np.mean(corners, axis=0)

    def _shrink_bbox(
            self,
            diff: np.ndarray,
            threshold: float,
            width: int,
            height: int
    ) -> Tuple[int, int, int, int]:
        """
        从四个方向向内收缩边界框

        Args:
            diff: 每个像素与背景的差异矩阵 shape: (height, width)
            threshold: 差异阈值
            width: 图像宽度
            height: 图像高度

        Returns:
            (left, right, top, bottom) 收缩后的边界
        """
        # 判断每个像素是否超过阈值（与背景有明显差异）
        exceeds = diff > threshold

        # 统计每列是否存在超过阈值的像素
        col_exceeds = np.any(exceeds, axis=0)  # shape: (width,)
        # 统计每行是否存在超过阈值的像素
        row_exceeds = np.any(exceeds, axis=1)  # shape: (height,)

        # 如果整张图都是背景（没有前景），返回原始边界
        if not np.any(col_exceeds):
            return 0, width, 0, height

        # 从左→右扫描：找到第一个超过阈值的列（argmax 返回第一个 True 的索引）
        # 从右→左扫描：反转后找第一个 True，再换算回原索引
        left = int(np.argmax(col_exceeds))
        right = int(width - np.argmax(col_exceeds[::-1]))
        top = int(np.argmax(row_exceeds))
        bottom = int(height - np.argmax(row_exceeds[::-1]))

        return left, right, top, bottom

    def get_foreground_bbox(
            self,
            image: Image.Image,
            threshold: float = 10.0,
            padding: int = 0,
            trim_left: bool = True,
            trim_right: bool = True,
            trim_top: bool = True,
            trim_bottom: bool = True,
    ) -> Tuple[int, int, int, int]:
        img_array = np.array(image, dtype=np.float32)

        # 处理灰度图（2D → 3D）
        if img_array.ndim == 2:
            img_array = img_array[:, :, np.newaxis]

        height, width, channels = img_array.shape

        # ===== 第一步：取四角像素均值作为背景色 =====
        background_color = self._get_background_color(img_array)

        # ===== 第二步：计算每个像素与背景的差异 =====
        diff = np.sqrt(np.sum((img_array - background_color) ** 2, axis=-1))

        # ===== 第三步：从四个方向向内扫描，收缩边界框 =====
        left, right, top, bottom = self._shrink_bbox(diff, threshold, width, height)

        if not trim_left:
            left = 0
        if not trim_right:
            right = width
        if not trim_top:
            top = 0
        if not trim_bottom:
            bottom = height
        # ===== 第四步：应用 padding 并确保边界合法 =====
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(width, right + padding)
        bottom = min(height, bottom + padding)

        return left, top, right, bottom


class MarginFilter(FilterProcessor):

    def process(self, ctx: PipelineContext):
        left_margin = ctx.getint("left_margin", 0)
        right_margin = ctx.getint("right_margin", 0)
        top_margin = ctx.getint("top_margin", 0)
        bottom_margin = ctx.getint("bottom_margin", 0)
        color = ctx.get("margin_color", "white")

        buffer = []
        for img in ctx.get_buffer():
            # 获取原图尺寸
            original_width, original_height = img.size

            # 计算新画布尺寸
            new_width = original_width + left_margin + right_margin
            new_height = original_height + top_margin + bottom_margin

            # 创建新画布，填充指定颜色
            new_img = Image.new(img.mode, (new_width, new_height), color)

            # 计算偏移量（原图粘贴位置）
            offset_x = left_margin
            offset_y = top_margin

            # 将原图粘贴到新画布上
            new_img.paste(img, (offset_x, offset_y))
            buffer.append(new_img)

        ctx.update_buffer(buffer).save_buffer(self.name()).success()

    def name(self) -> str:
        return "margin"



class MarginWithRatioFilter(FilterProcessor):
    ratio_pattern = re.compile('[0-9.]+:[0-9.]+')
    ratio_threshold = 0.01

    def process(self, ctx: PipelineContext):
        buffer = ctx.get_buffer()
        if not buffer:
            return
        real_ratio = 1. * int(ctx.get_exif().get('ImageWidth')) / int(ctx.get_exif().get('ImageHeight'))
        if 'ratio' in ctx and MarginWithRatioFilter.ratio_pattern.match(ctx.get("ratio")):
            ratio_w, ratio_h = ctx.get("ratio").split(':')
            real_ratio = 1. * float(ratio_w) / float(ratio_h)
        img = buffer[0]
        cur_ratio = 1. * img.width / img.height
        if cur_ratio - real_ratio > MarginWithRatioFilter.ratio_threshold:
            # 图片太宽, 增加高度
            new_h = int(img.width / real_ratio)
            pad_vertical = new_h - img.height
            ctx.set('top_margin', pad_vertical / 2)
            ctx.set('bottom_margin', pad_vertical - pad_vertical / 2)
        elif cur_ratio - real_ratio < MarginWithRatioFilter.ratio_threshold:
            # 图片太窄, 增加宽度
            new_w = int(img.height * real_ratio)
            pad_horizontal = new_w - img.width
            ctx.set('left_margin', pad_horizontal / 2)
            ctx.set('right_margin', pad_horizontal - pad_horizontal / 2)
        else:
            return
        MarginFilter().process(ctx)
        ctx.save_buffer(self.name()).success()

    def name(self) -> str:
        return "margin_with_ratio"


class WatermarkFilter(FilterProcessor):
    def process(self, ctx: PipelineContext):
        img = ctx.get_buffer()[0]
        color = ctx.get("color", "white")
        delimiter_color = ctx.get("delimiter_color", "black")
        left_margin = ctx.getint("left_margin", 0)
        right_margin = ctx.getint("right_margin", 0)
        top_margin = ctx.getint("top_margin", 0)
        bottom_margin = ctx.getint("bottom_margin", int(img.height * .12))
        middle_spacing = ctx.getint("middle_spacing", int(bottom_margin * .05))

        for t_s in [ctx.get("left_top"), ctx.get("left_bottom"), ctx.get("right_top"), ctx.get("right_bottom")]:
            if "height" not in t_s:
                t_s["height"] = int(bottom_margin * .3)

        left_top = start_process([ctx.get("left_top")])
        left_bottom = start_process([ctx.get("left_bottom")])
        right_top = start_process([ctx.get("right_top")])
        right_bottom = start_process([ctx.get("right_bottom")])

        left_logo = Image.open(ctx.get("left_logo")).convert('RGBA') if ctx.get("left_logo") else None
        right_logo = Image.open(ctx.get("right_logo")).convert('RGBA') if ctx.get("right_logo") else None

        canvas_width = img.width + left_margin + right_margin
        canvas_height = img.height + top_margin + bottom_margin
        common_spacing = int(.02 * canvas_width)

        # 新建画布
        canvas = Image.new("RGBA", (canvas_width, canvas_height), color)
        # 主图
        canvas.paste(img, (left_margin, top_margin))
        # 底部区域
        footer_start_y = top_margin + img.height
        # 左图标处理
        left_logo_width = 0
        if left_logo:
            # 缩放图标以适应底部高度 (正方形)
            logo_size = canvas_height - footer_start_y
            left_logo = left_logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            canvas.paste(left_logo, (left_margin, footer_start_y), mask=left_logo if left_logo.mode == 'RGBA' else None)
            left_logo_width = logo_size
        # 文本处理
        elem_height = max(left_top.height + left_bottom.height, right_top.height + right_bottom.height) + middle_spacing
        # 计算文本块距离底部边缘的留白，使其在 bottom_margin 区域内垂直居中
        elem_margin = int((bottom_margin - elem_height) / 2)
        # PIL 坐标原点在左上角。
        l_x = left_margin + left_logo_width + common_spacing

        # 右侧文本 X 坐标基准 (右对齐)
        # 右侧内容的右边界 = canvas_width - right_margin - right_logo_width
        right_content_end_x = canvas_width - right_margin
        # --- 左上 (Left Top) ---
        # 距离下边缘: elem_margin + left_bottom.height + middle_spacing + left_top.height
        bottom_dist_lt = elem_margin + left_bottom.height + middle_spacing + left_top.height
        lt_y = canvas_height - bottom_dist_lt

        # --- 左下 (Left Bottom) ---
        # 距离下边缘: elem_margin + left_bottom.height
        bottom_dist_lb = elem_margin + left_bottom.height
        lb_y = canvas_height - bottom_dist_lb

        # --- 右上 (Right Top) ---
        # 规则：右上和左上是“底部对齐”。
        # 左上图片的底部 Y 坐标 = lt_y + left_top.height
        # 右上 Y = 左上底部 Y - 右上高度
        rt_y = (lt_y + left_top.height) - right_top.height
        rt_x = right_content_end_x - right_top.width - common_spacing  # 右对齐计算
        # --- 右下 (Right Bottom) ---
        # 规则：右下和左下是“底部对齐”。
        # 左下图片的底部 Y 坐标 = lb_y + left_bottom.height
        # 右下 Y = 左下底部 Y - 右下高度
        rb_y = (lb_y + left_bottom.height) - right_bottom.height
        rb_x = right_content_end_x - right_bottom.width - common_spacing  # 右对齐计算

        # 6. 绘制文本元素
        # 使用 mask 确保透明背景的文字能正确叠加
        canvas.paste(left_top, (l_x, lt_y), mask=left_top if left_top.mode == 'RGBA' else None)
        canvas.paste(left_bottom, (l_x, lb_y), mask=left_bottom if left_bottom.mode == 'RGBA' else None)
        canvas.paste(right_top, (rt_x, rt_y), mask=right_top if right_top.mode == 'RGBA' else None)
        canvas.paste(right_bottom, (rb_x, rb_y), mask=right_bottom if right_bottom.mode == 'RGBA' else None)

        # 右图标处理 (逻辑类推：放置在右边距内侧)
        if right_logo:
            # 先画一条分割线
            logo_size = elem_height
            delimiter = Image.new("RGB", (int(canvas_width * .005), int(logo_size * 1.1)), delimiter_color)
            delimiter_x = canvas_width - right_margin - max(right_top.width,
                                                            right_bottom.width) - 2 * common_spacing - delimiter.width
            delimiter_y = int(footer_start_y + elem_margin - logo_size * .05)
            canvas.paste(delimiter, (delimiter_x, delimiter_y))

            right_logo = right_logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            right_logo_x = delimiter_x - common_spacing - logo_size
            right_logo_y = footer_start_y + elem_margin
            canvas.paste(right_logo, (right_logo_x, right_logo_y),
                         mask=right_logo if right_logo.mode == 'RGBA' else None)

        # 7. 返回结果
        ctx.update_buffer([canvas]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "watermark"


class WatermarkWithTimestampFilter(FilterProcessor):
    def process(self, ctx: PipelineContext):
        img = ctx.get_buffer()[0]

        if "height" not in ctx:
            ctx.set("height", int(img.height * .02))
        MultiRichTextGenerator().process(ctx)
        text = ctx.get_buffer()[0]

        text_x = int(img.width * .93) - text.width
        text_y = int(img.height * .95)

        img.paste(text, (text_x, text_y), mask=text)
        ctx.update_buffer([img]).save_buffer(self.name()).success()

    def name(self) -> str:
        return "watermark_with_timestamp"
