import gradio as gr
from entity.image_container import ImageContainer
from entity.image_processor import ProcessorChain
from entity.image_processor import BackgroundBlurProcessor
from entity.image_processor import BackgroundBlurWithWhiteBorderProcessor
from entity.image_processor import CustomWatermarkProcessor
from entity.image_processor import DarkWatermarkLeftLogoProcessor
from entity.image_processor import DarkWatermarkRightLogoProcessor
from entity.image_processor import EmptyProcessor
from entity.image_processor import MarginProcessor
from entity.image_processor import PaddingToOriginalRatioProcessor
from entity.image_processor import PureWhiteMarginProcessor
from entity.image_processor import ShadowProcessor
from entity.image_processor import SimpleProcessor
from entity.image_processor import SquareProcessor
from entity.image_processor import WatermarkLeftLogoProcessor
from entity.image_processor import WatermarkProcessor
from entity.image_processor import WatermarkRightLogoProcessor
from init import LayoutItem
from pathlib import Path
from entity.config import Config


def processing(file_path, config):
    config = Config(None, config)
    EMPTY_PROCESSOR = EmptyProcessor(config)
    WATERMARK_PROCESSOR = WatermarkProcessor(config)
    WATERMARK_LEFT_LOGO_PROCESSOR = WatermarkLeftLogoProcessor(config)
    WATERMARK_RIGHT_LOGO_PROCESSOR = WatermarkRightLogoProcessor(config)
    MARGIN_PROCESSOR = MarginProcessor(config)
    SHADOW_PROCESSOR = ShadowProcessor(config)
    SQUARE_PROCESSOR = SquareProcessor(config)
    SIMPLE_PROCESSOR = SimpleProcessor(config)
    PADDING_TO_ORIGINAL_RATIO_PROCESSOR = PaddingToOriginalRatioProcessor(config)
    BACKGROUND_BLUR_PROCESSOR = BackgroundBlurProcessor(config)
    BACKGROUND_BLUR_WITH_WHITE_BORDER_PROCESSOR = BackgroundBlurWithWhiteBorderProcessor(config)
    PURE_WHITE_MARGIN_PROCESSOR = PureWhiteMarginProcessor(config)

    LAYOUT_ITEMS = [
        LayoutItem.from_processor(WATERMARK_LEFT_LOGO_PROCESSOR),
        LayoutItem.from_processor(WATERMARK_RIGHT_LOGO_PROCESSOR),
        LayoutItem.from_processor(DarkWatermarkLeftLogoProcessor(config)),
        LayoutItem.from_processor(DarkWatermarkRightLogoProcessor(config)),
        LayoutItem.from_processor(CustomWatermarkProcessor(config)),
        LayoutItem.from_processor(SQUARE_PROCESSOR),
        LayoutItem.from_processor(SIMPLE_PROCESSOR),
        LayoutItem.from_processor(BACKGROUND_BLUR_PROCESSOR),
        LayoutItem.from_processor(BACKGROUND_BLUR_WITH_WHITE_BORDER_PROCESSOR),
        LayoutItem.from_processor(PURE_WHITE_MARGIN_PROCESSOR),
    ]
    layout_items_dict = {item.value: item for item in LAYOUT_ITEMS}

    processor_chain = ProcessorChain()
    # 如果需要添加阴影，则添加阴影处理器，阴影处理器优先级最高，但是正方形布局不需要阴影
    if config.has_shadow_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(SHADOW_PROCESSOR)

    # 根据布局添加不同的水印处理器
    if config.get_layout_type() in layout_items_dict:
        processor_chain.add(layout_items_dict.get(config.get_layout_type()).processor)
    else:
        processor_chain.add(SIMPLE_PROCESSOR)

    # 如果需要添加白边，且是水印布局，则添加白边处理器，白边处理器优先级最低
    if config.has_white_margin_enabled() and 'watermark' in config.get_layout_type():
        processor_chain.add(MARGIN_PROCESSOR)

    # 如果需要按原有比例填充，且不是正方形布局，则添加填充处理器
    if config.has_padding_with_original_ratio_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(PADDING_TO_ORIGINAL_RATIO_PROCESSOR)

    # 打开图片
    container = ImageContainer(Path(file_path))

    # 使用等效焦距
    container.is_use_equivalent_focal_length(config.use_equivalent_focal_length())

    # 处理图片
    try:
        processor_chain.process(container)
    except Exception as e:
        raise e

    # 导出图片
    img = container.export()
    container.close()
    return img


if __name__ == "__main__":
    with open('config.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    with gr.Blocks() as demo:
        with gr.Row():
            image_input = gr.Image(type="filepath")
            image_output = gr.Image()
        image_btn = gr.Button("处理图片")
        with gr.Accordion("修改配置文件", open=False):
            config = gr.Code(value=content, language='yaml')
        try:
            image_btn.click(processing, inputs=[image_input, config], outputs=image_output)
        except Exception as e:
            gr.Warning(str(e))
    demo.launch()
