import glob
import logging
import os
import shutil
import subprocess


def gen_video(images_path, video_path, duration, background_color, background_music, size, ffmpeg_path='ffmpeg'):
    try:
        # 读取 config 中的参数
        if size == 'middle':
            scale = '2688:1344'
        elif size == 'small':
            scale = '1920:1080'
        else:
            scale = '3840:1920'

        # 列出所有的jpg文件
        image_files = glob.glob(f'{images_path}/*.jpg')

        # 创建一个文本文件，其中包含所有.jpg文件的路径
        with open(f'output_images.txt', 'w') as f:
            for image_file in sorted(image_files):
                f.write(f"file '{os.path.abspath(image_file)}'\n")
                f.write(f"duration {duration}\n")

        # 如果 ffmpeg_path 存在，则执行 command_gen_video，否则提示用户 ffmpeg_path 不存在，返回
        command_gen_video = f'''
            {ffmpeg_path} -f concat -safe 0 -i output_images.txt -vf "scale={scale}:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color={background_color}" -c:v libx264 -r 24 -pix_fmt yuv420p -y {video_path}
            '''

        # 如果 ffmpeg_path 是默认值'ffmpeg'或者是一个存在的文件路径，则执行 command_gen_video，否则提示用户 ffmpeg_path 不存在，返回
        if ffmpeg_path == 'ffmpeg' or os.path.exists(ffmpeg_path):
            if shutil.which(ffmpeg_path) is not None:
                with open('./logs/all.log', 'w') as f:
                    logging.info(command_gen_video)
                    subprocess.call(command_gen_video, shell=True, stdout=f, stderr=subprocess.STDOUT)
            else:
                print(f"{ffmpeg_path} is not installed or not found.")
                return
        else:
            print("ffmpeg_path doesn't exist.")
            return

        # 添加 bgm 的 ffmpeg 命令
        command_attach_music = f'''
        {ffmpeg_path} -i {video_path} -i {background_music} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -y temp.mp4
        '''

        # 如果 background_music 存在，则添加 bgm，然后将临时文件 temp.mp4 重命名为 video_path，否则提示用户 background_music 不存在，返回
        if os.path.exists(background_music):
            with open('./logs/all.log', 'w') as f:
                logging.info(command_attach_music)
                subprocess.call(command_attach_music, shell=True, stdout=f, stderr=subprocess.STDOUT)
                if os.path.exists('temp.mp4'):
                    shutil.move('temp.mp4', video_path)
        else:
            print(f"BGM 文件不存在，请检查路径是否正确：{background_music}，已生成无 BGM 的视频文件")
            return
    except Exception as e:
        print(
            '''
            在视频生成过程中发生了错误。请联系作者邮箱 leslie.van@outlook.com，描述问题，并将 './logs/all.log' 文件作为附件发送。
            ''')
        with open('./logs/all.log', 'a') as f:
            f.write(str(e))


if __name__ == '__main__':
    gen_video(images_path='output', video_path='output.mp4', ffmpeg_path='ffmpeg', duration='2',
              background_color='white', background_music='./output/bgm.mp3', size='middle')
