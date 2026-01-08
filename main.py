import configparser
import json
import os
import threading
import webbrowser

from flask import Flask, render_template, jsonify, request, send_file
from jinja2 import Template

from processor.core import start_process
from util import list_files, log_rt, get_exif, vh, vw

CONFIG_PATH = 'config.ini'

# 解析配置
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 创建 flask 服务器
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Semi-Utils')


@app.route('/api/v1/config', methods=['GET'])
def get_config():
    template_path = config.get('render', 'template_path')

    with open(template_path) as f:
        template = f.read()

    return jsonify({
        'input_folder': config.get('DEFAULT', 'input_folder'),
        'output_folder': config.get('DEFAULT', 'output_folder'),
        'skip_existed': config.get('DEFAULT', 'skip_existed'),
        'template': template,
    })


@app.route('/api/v1/config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # 更新配置项
        if 'input_folder' in data:
            config.set('DEFAULT', 'input_folder', data['input_folder'])
        if 'output_folder' in data:
            config.set('DEFAULT', 'output_folder', data['output_folder'])
        if 'skip_existed' in data:
            config.set('DEFAULT', 'skip_existed', str(data['skip_existed']))

        # 保存配置到配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)

        # 保存模板文件
        if 'template' in data:
            template_path = config.get('render', 'template_path')
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(data['template'])

        return jsonify({'message': 'Config saved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/file/tree', methods=['GET'])
def list_input_files():
    suffixes = set([ft for ft in config.get('DEFAULT', 'supported_file_suffixes').split(',')])
    return jsonify({
        'input_files': [{'children': list_files(config.get('DEFAULT', 'input_folder'), suffixes), 'label': 'Root'}],
        'output_files': [{'children': list_files(config.get('DEFAULT', 'output_folder'), suffixes), 'label': 'Root'}],
    })


@app.route('/api/v1/file', methods=['GET'])
def get_file():
    """
    获取文件内容
    GET /api/v1/file?path=xxx
    """
    file_path = request.args.get('path')

    # 参数验证
    if not file_path:
        return jsonify({'error': 'Missing path parameter'}), 400

    # 转为绝对路径
    abs_path = os.path.abspath(file_path)

    # 安全检查：确保路径存在
    if not os.path.exists(abs_path):
        return jsonify({'error': 'File not found'}), 404

    # 确保是文件而不是目录
    if os.path.isdir(abs_path):
        return jsonify({'error': 'Path is a directory, not a file'}), 400

    try:
        # 直接发送文件（适用于下载或二进制文件）
        return send_file(abs_path, as_attachment=False)

    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/start_process', methods=['POST'])
@log_rt
def handle_process():
    # 获取模板
    with open(config.get('render', 'template_path')) as f:
        template_str = f.read()
    template = Template(template_str)
    template.globals['vh'] = vh
    template.globals['vw'] = vw

    data = request.get_json()
    input_files = [item['value'] for item in data['selectedItems']]
    input_folder = config.get('DEFAULT', 'input_folder')
    output_folder = config.get('DEFAULT', 'output_folder')
    def process_file(input_path):
        if not os.path.exists(input_path):
            return
        # 获取 input_path 相对 input_folder 的位置
        relative_path = os.path.relpath(input_path, input_folder)

        # 基于 output_folder 组装出输出路径 output_path
        output_path = os.path.join(output_folder, relative_path)

        # 如果路径不存在, 那么递归创建文件夹
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 如果 output_path 对应的文件存在, 直接跳过
        if os.path.exists(output_path) and not config.getboolean('DEFAULT', 'skip_existed'):
            return

        # 开始处理
        print(f'input_path: {input_path}, output_path: {output_path}')
        start_process(json.loads(template.render({'exif': get_exif(input_path)})), input_path, output_path=output_path)
    threads = []
    for input_path in input_files:
        thread = threading.Thread(target=process_file, args=(input_path,))
        threads.append(thread)
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    return jsonify({'message': 'Process started successfully'}), 200


def open_browser():
    # 等待服务器启动
    import time
    time.sleep(1)
    # 打开浏览器并访问指定的URL
    webbrowser.open('http://localhost:15050')

if __name__ == '__main__':
    # 在单独的线程中打开浏览器
    debug = config.getboolean('DEFAULT', 'debug')
    if not debug:
        threading.Thread(target=open_browser).start()
    app.run(port=15050, host="localhost", debug=debug)

