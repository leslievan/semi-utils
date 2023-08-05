import os
import platform
import subprocess
from datetime import datetime

import requests as requests


def get_ffmpeg_path():
    if platform.system() == "Windows":
        if os.path.exists("./bin/ffmpeg.exe"):
            return "./bin/ffmpeg.exe"
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
    url = "https://github.com/leslievan/semi-utils/raw/exiftool/bin/ffmpeg.exe"
    response = requests.get(url, stream=True)
    with open(target_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    # 提示下载完成，同时输出 ffmpeg 路径
    print("下载完成，ffmpeg 路径为：", target_path)


def generate_video(path, gap_time=2):
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("找不到ffmpeg。正在下载...")
        bin_dir = 'bin'
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)
        download_ffmpeg(os.path.join(bin_dir, 'ffmpeg.exe'))

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(path, f"{current_time}.mp4")
    command = f'{ffmpeg_path} -framerate 1/{gap_time} -pattern_type glob -i "{path}/*.jpg" -vf "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=white" -c:v libx264 -r 24 -pix_fmt yuv420p -color_range 1 {output_file}'

    subprocess.call(command, shell=True)

    # 检查是否存在 bgm.mp3 文件
    bgm_path = os.path.join(path, "bgm.mp3")
    if os.path.exists(bgm_path):
        temp_output_file = os.path.join(path, f"temp_{current_time}.mp4")
        command_bgm = f'{ffmpeg_path} -i {output_file} -i {bgm_path} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest {temp_output_file}'
        subprocess.call(command_bgm, shell=True)
        # 重命名临时文件回原文件名
        os.rename(temp_output_file, output_file)

    # 提示视频生成成功，告诉用户视频的路径
    print(f"视频生成成功，路径为：{output_file}")


if __name__ == '__main__':
    generate_video("./output")
