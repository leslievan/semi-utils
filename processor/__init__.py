import pillow_heif

from processor.filters import BlurFilter, MarginFilter, ResizeFilter, TrimFilter, WatermarkFilter, \
    WatermarkWithTimestampFilter, ShadowFilter, RoundedCornerFilter
from processor.generators import SolidColorGenerator, GradientColorGenerator, RichTextGenerator, MultiRichTextGenerator, \
    ImageLoader
from processor.mergers import ConcatMerger

# 注册处理器
BlurFilter()
MarginFilter()
ResizeFilter()
TrimFilter()
WatermarkFilter()
SolidColorGenerator()
GradientColorGenerator()
RichTextGenerator()
MultiRichTextGenerator()
ConcatMerger()
WatermarkWithTimestampFilter()
ShadowFilter()
ImageLoader()
RoundedCornerFilter()

# 注册 pillow heic 支持
pillow_heif.register_heif_opener()
print("✓ Registered plugin: pillow_heif")
