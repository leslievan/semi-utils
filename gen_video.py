import glob
import os
import platform
import subprocess
import sys
import time
from datetime import datetime

import requests as requests
from tqdm import tqdm


def get_ffmpeg_path():
    if platform.system() == "Windows":
        ffmpeg_local_path = "./bin/ffmpeg.exe"
        if os.path.exists(ffmpeg_local_path):
            if os.path.exists(ffmpeg_local_path):
                return os.path.abspath(ffmpeg_local_path)  # 返回ffmpeg的绝对路径
        # 尝试使用 where 获取 ffmpeg 路径
        ffmpeg_path = subprocess.getoutput("where ffmpeg")
        if "ffmpeg" in ffmpeg_path:
            return ffmpeg_path.split('\n')[0]  # 取第一个结果
        return None
    else:
        ffmpeg_path = subprocess.getoutput("which ffmpeg")
        if "ffmpeg" in ffmpeg_path:
            return ffmpeg_path
        elif os.path.exists("./bin/ffmpeg"):
            return "./bin/ffmpeg"
        return None


def download_ffmpeg(target_path):
    url = "https://file.lsvm.xyz/bin/ffmpeg.exe"
    response = requests.get(url, stream=True)

    # 获取文件总大小（单位：字节）
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192  # 设置块大小为8KB
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

    with open(target_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=block_size):
            f.write(chunk)
            progress_bar.update(len(chunk))

    # 关闭进度条
    progress_bar.close()

    # 提示下载完成，同时输出 ffmpeg 路径
    print("- 下载完成，ffmpeg 路径为：", target_path)
    print("- 更新新版时请保留此文件，放到对应的位置下，否则无法生成视频。")


def generate_video(path, gap_time=2):
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("- 找不到ffmpeg。正在下载...")
        bin_dir = 'bin'
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)
        download_ffmpeg(os.path.join(bin_dir, 'ffmpeg.exe'))

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(path, f"{current_time}.mp4")

    file_patterns = ['jpg', 'jpeg', 'JPG', 'JPEG']

    # 获取所有匹配的文件路径
    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(f"{path}/*.{pattern}"))

    # 如果没有找到图片，提示用户并返回
    if not files:
        print("- 不存在图片!")
        return

    # 否则，生成文件列表
    with open('temp.txt', 'w', encoding='utf-8') as f:
        for filename in sorted(files):
            f.write(f"file '{filename}'\n")

    command = f'"{ffmpeg_path}" -f concat -safe 0 -r 1/{gap_time} -i temp.txt -vf "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=white" -c:v libx264 -r 24 -pix_fmt yuv420p -color_range 1 "{output_file}"'

    # 开启新的线程来执行命令
    process = subprocess.Popen(command, shell=True, encoding='utf-8')

    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("\ro 视频拼接成功，输出至：" + output_file)
    else:
        print("\r- 视频拼接失败，错误信息：", stderr)
        return

    # 检查是否存在 bgm.mp3 文件
    bgm_path = os.path.join(path, "bgm.mp3")
    if os.path.exists(bgm_path):
        temp_output_file = os.path.join(path, f"temp_{current_time}.mp4")
        command_bgm = f'"{ffmpeg_path}" -i "{output_file}" -i "{bgm_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{temp_output_file}"'

        # 开启新的线程来执行命令
        process = subprocess.Popen(command_bgm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding='utf-8')

        # 转动字符显示
        spinning_chars = ['-', '\\', '|', '/']
        idx = 0
        while process.poll() is None:  # 当命令正在执行时
            sys.stdout.write('\r' + spinning_chars[idx % len(spinning_chars)])
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("\ro 视频附加 bgm 成功，输出至：" + temp_output_file)
        else:
            print("\r- 视频附加 bgm 失败，错误信息：", stderr)
    else:
        print("\r- 未找到 bgm.mp3 文件，跳过附加 bgm 步骤。")

    # 提示视频生成成功，告诉用户视频的路径
    print(f"o 视频生成成功，路径为：{output_file}")


if __name__ == '__main__':
    generate_video("./output")
