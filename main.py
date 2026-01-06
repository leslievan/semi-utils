import os
from processor.core import start_process
from util import get_exif

date_key_set = ["DateCreated", "CreateDate", "DateTimeOriginal", "DateTimeCreated", "DigitalCreationDateTime"]

if __name__ == "__main__":
    # 读取 input 文件夹下的所有子文件夹
    input_base_path = "./input"

    # 确保输入路径存在
    if not os.path.exists(input_base_path):
        print(f"错误: 输入路径 {input_base_path} 不存在")
        exit(1)

    # 遍历所有子文件夹
    for folder_name in os.listdir(input_base_path):
        folder_path = os.path.join(input_base_path, folder_name)

        # 跳过非文件夹项
        if not os.path.isdir(folder_path):
            continue

        print(f"处理文件夹: {folder_name}")

        # 遍历子文件夹下的所有 png/jpg 文件
        for filename in os.listdir(folder_path):
            # 检查文件扩展名
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            file_path = os.path.join(folder_path, filename)
            print(f"  处理文件: {filename}")

            # 获取EXIF信息
            exif_dict = get_exif(file_path)

            # 获取时间
            time_str = None
            for key in date_key_set:
                if key in exif_dict:
                    time_str = exif_dict[key][:16]
                    break

            # 如果没有找到时间信息，跳过该文件
            if not time_str:
                print(f"    警告: 文件 {filename} 没有找到时间信息，跳过")
                continue

            # 拼接text
            text = f"{folder_name} {time_str}"

            # 运行处理
            data = [
                {

                    "text_segments": [
                        {
                            "text": f"{folder_name} {time_str}",
                            "font_path": "fonts/AlibabaPuHuiTi-2-85-Bold.otf",
                            "color": "(232,141,52,188)",
                        }
                    ],

                    "processor_name": "watermark_with_timestamp",
                    "save_buffer": False
                }
            ]

            # 调用处理函数
            start_process(
                data,
                input_path=file_path,
                output_path=f"./output/{folder_name}_{filename}"
            )

            print(f"    完成: {folder_name}_{filename}")


