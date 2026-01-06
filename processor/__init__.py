from processor.filters import BlurFilter, MarginFilter, ResizeFilter, TrimFilter, WatermarkFilter, \
    WatermarkWithTimestampFilter
from processor.generators import SolidColorGenerator, GradientColorGenerator, RichTextGenerator, MultiRichTextGenerator
from processor.mergers import ConcatMerger

if __name__ == '__main__':
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
