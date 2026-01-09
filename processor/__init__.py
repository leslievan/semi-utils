import pillow_heif

from processor.filters import BlurFilter, MarginFilter, ResizeFilter, TrimFilter, WatermarkFilter, \
    WatermarkWithTimestampFilter
from processor.generators import SolidColorGenerator, GradientColorGenerator, RichTextGenerator, MultiRichTextGenerator
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

# 注册 pillow heic 支持
pillow_heif.register_heif_opener()
print("Registered plugin: pillow_heif")
