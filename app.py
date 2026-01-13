import json
import os
import threading
import webbrowser
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import render_template, jsonify, request, send_file, Flask, Response, stream_with_context

from core import CONFIG_PATH
from core.configs import load_config, load_project_info
from core.logger import logger, init_from_config
from core.util import (list_files, log_rt, get_exif, convert_heic_to_jpeg, get_template, get_template_content,
                       save_template, list_templates)
from processor.core import start_process

# 加载配置
config = load_config()
project_info = load_project_info()

# 初始化日志系统（必须在创建 Flask app 之前）
init_from_config(config)

# 创建 Flask app
api = Flask(__name__)


@api.route('/')
def index():
    return render_template('index.html', title='Semi-Utils Pro', version=project_info['project']['version'])


@api.route('/api/v1/config', methods=['GET'])
def get_config():
    template_name = config.get('render', 'template_name')
    template = get_template_content(template_name)

    return jsonify({
        'input_folder': config.get('DEFAULT', 'input_folder'),
        'output_folder': config.get('DEFAULT', 'output_folder'),
        'override_existed': config.getboolean('DEFAULT', 'override_existed'),
        'template_name': template_name,
        'template': template,
        'quality': config.get('DEFAULT', 'quality'),
        'templates': list_templates(),
    })


@api.route('/api/v1/config', methods=['POST'])
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
        if 'override_existed' in data:
            config.set('DEFAULT', 'override_existed', str(data['override_existed']))
        if 'quality' in data:
            config.set('DEFAULT', 'quality', data['quality'])
        if 'template_name' in data:
            config.set('render', 'template_name', data['template_name'])

        # 保存配置到配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)

        # 保存模板文件
        if 'template' in data and 'template_name' in data:
            save_template(data['template_name'], data['template'])

        return jsonify({'message': 'Config saved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/v1/file/tree', methods=['GET'])
@log_rt
def list_input_files():
    import time
    start = time.time()
    suffixes = set([ft for ft in config.get('DEFAULT', 'supported_file_suffixes').split(',')])

    input_folder = config.get('DEFAULT', 'input_folder')
    output_folder = config.get('DEFAULT', 'output_folder')

    logger.debug(f"开始扫描文件系统, input={input_folder}, output={output_folder}")

    # 扫描输入文件夹
    t1 = time.time()
    input_children = list_files(input_folder, suffixes)
    logger.debug(f"输入文件夹扫描完成, 耗时: {time.time() - t1:.2f}s, 文件数: {len(input_children)}")

    # 扫描输出文件夹
    t2 = time.time()
    output_children = list_files(output_folder, suffixes)
    logger.debug(f"输出文件夹扫描完成, 耗时: {time.time() - t2:.2f}s, 文件数: {len(output_children)}")

    logger.debug(f"文件扫描总耗时: {time.time() - start:.2f}s")

    return jsonify({
        'input_files': [{'children': input_children, 'label': 'Root'}],
        'output_files': [{'children': output_children, 'label': 'Root'}],
    })


@api.route('/api/v1/file', methods=['GET'])
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
        # HEIC 文件转换处理
        if Path(abs_path).suffix.lower() in {'.heic', '.heif'}:
            response = send_file(
                convert_heic_to_jpeg(abs_path),
                mimetype='image/jpeg',
                download_name=f"{Path(abs_path).stem}.jpg"
            )
            response.headers['Accept-Ranges'] = 'none'
        else:
            # 其他文件直接返回
            response = send_file(abs_path, as_attachment=False)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Accept-Ranges'] = 'none'
        return response

    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/v1/start_process', methods=['POST'])
@log_rt
def handle_process():
    # 获取模板
    template = get_template(config.get('render', 'template_name'))

    data = request.get_json()
    input_files = data['selectedItems']
    input_folder = config.get('DEFAULT', 'input_folder')
    output_folder = config.get('DEFAULT', 'output_folder')

    total_count = len(input_files)

    @log_rt
    def process_single_file(input_path):
        """处理单个文件，返回 (success, skipped, error_message)"""
        if not os.path.exists(input_path):
            return False, False, f"文件不存在: {input_path}"

        try:
            # 获取 input_path 相对 input_folder 的位置
            relative_path = os.path.relpath(input_path, input_folder)
            # 基于 output_folder 组装出输出路径 output_path
            output_path = os.path.join(output_folder, relative_path)

            # 如果路径不存在, 那么递归创建文件夹
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 如果 output_path 对应的文件存在, 直接跳过
            if os.path.exists(output_path) and not config.getboolean('DEFAULT', 'override_existed'):
                return False, True, None

            _input_path = Path(input_path)
            # 开始处理
            context = {
                'exif': get_exif(input_path),
                'filename': _input_path.stem,
                'file_dir': str(_input_path.parent.absolute()).replace('\\', '/'),
                'file_path': str(_input_path).replace('\\', '/'),
                'files': input_files
            }
            final_template = template.render(context)
            logger.debug(f"{'-'*8}template start{'-'*8}\n{final_template}\n{'-'*8}template end{'-'*8}")
            start_process(json.loads(final_template), input_path, output_path=output_path)
            return True, False, None

        except Exception as e:
            logger.error(f"处理文件失败 {input_path}: {e}")
            return False, False, str(e)

    def generate():
        """生成 SSE 事件流 - 使用多线程处理"""
        # 使用线程安全的计数器和锁
        counters = {
            'processed': 0,
            'success': 0,
            'failure': 0,
            'skipped': 0
        }
        counters_lock = threading.Lock()

        # 结果队列，用于接收线程完成事件
        result_queue = queue.Queue()

        def worker(file_path):
            """工作线程函数，处理单个文件并将结果放入队列"""
            file_name = os.path.basename(file_path)
            # 发送开始处理的事件
            result_queue.put(('start', file_name, None))

            try:
                success, skipped, error = process_single_file(file_path)

                with counters_lock:
                    if skipped:
                        counters['skipped'] += 1
                        status = 'skipped'
                    elif success:
                        counters['success'] += 1
                        status = 'success'
                    else:
                        counters['failure'] += 1
                        status = 'failure'
                    counters['processed'] += 1

                result_queue.put(('complete', file_name, (status, error)))
            except Exception as e:
                with counters_lock:
                    counters['failure'] += 1
                    counters['processed'] += 1
                result_queue.put(('complete', file_name, ('failure', str(e))))

        def sse(event: str, data: dict):
            """生成 SSE 格式数据"""
            return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

        # 发送开始事件
        yield sse('start', {
            'total': total_count,
            'message': f'开始处理 {total_count} 个文件...'
        })

        # 使用线程池并发处理
        max_workers = min(4, total_count)  # 最多 4 个线程
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {executor.submit(worker, f): f for f in input_files}

            # 等待任务完成并发送进度
            for future in as_completed(futures):
                # 从队列获取结果
                while True:
                    try:
                        event_type, file_name, result = result_queue.get_nowait()
                        if event_type == 'start':
                            yield sse('progress', {
                                'total': total_count,
                                'processed': counters['processed'],
                                'success': counters['success'],
                                'failure': counters['failure'],
                                'skipped': counters['skipped'],
                                'current': file_name,
                                'percent': round((counters['processed'] / total_count) * 100) if total_count > 0 else 0,
                                'message': f'正在处理: {file_name}'
                            })
                        elif event_type == 'complete':
                            status, error = result
                            status_text = {'success': '完成', 'failure': '失败', 'skipped': '跳过'}[status]
                            yield sse('progress', {
                                'total': total_count,
                                'processed': counters['processed'],
                                'success': counters['success'],
                                'failure': counters['failure'],
                                'skipped': counters['skipped'],
                                'current': file_name,
                                'percent': round((counters['processed'] / total_count) * 100) if total_count > 0 else 0,
                                'message': f'{status_text}: {file_name}'
                            })
                        break
                    except queue.Empty:
                        break

        # 确保所有结果都被处理
        while not result_queue.empty():
            event_type, file_name, result = result_queue.get()
            if event_type == 'complete':
                status, error = result
                status_text = {'success': '完成', 'failure': '失败', 'skipped': '跳过'}[status]
                yield sse('progress', {
                    'total': total_count,
                    'processed': counters['processed'],
                    'success': counters['success'],
                    'failure': counters['failure'],
                    'skipped': counters['skipped'],
                    'current': file_name,
                    'percent': round((counters['processed'] / total_count) * 100) if total_count > 0 else 0,
                    'message': f'{status_text}: {file_name}'
                })

        # 发送完成事件
        yield sse('complete', {
            'total': total_count,
            'processed': counters['processed'],
            'success': counters['success'],
            'failure': counters['failure'],
            'skipped': counters['skipped'],
            'percent': 100,
            'message': f'处理完成! 成功: {counters["success"]}, 跳过: {counters["skipped"]}, 失败: {counters["failure"]}'
        })

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


@api.route('/api/v1/template/<template_name>', methods=['GET'])
def get_template_api(template_name):
    """获取指定模板的内容"""
    try:
        content = get_template_content(template_name)
        return jsonify({'template_name': template_name, 'content': content})
    except FileNotFoundError:
        return jsonify({'error': f'Template "{template_name}" not found'}), 404


@api.route('/api/v1/template', methods=['POST'])
def create_template_api():
    """创建新模板"""
    try:
        data = request.get_json()
        if not data or 'template_name' not in data:
            return jsonify({'error': 'Missing template_name'}), 400

        template_name = data['template_name'].strip()
        if not template_name:
            return jsonify({'error': 'template_name cannot be empty'}), 400

        content = data.get('content', '[]')

        # 检查模板是否已存在
        existing_templates = list_templates()
        if template_name in existing_templates:
            return jsonify({'error': f'Template "{template_name}" already exists'}), 409

        # 保存新模板
        save_template(template_name, content)

        return jsonify({'message': f'Template "{template_name}" created successfully'}), 201

    except FileExistsError:
        return jsonify({'error': f'Template already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/api/v1/templates', methods=['GET'])
def list_templates_api():
    """获取所有可用模板列表"""
    templates = list_templates()
    return jsonify({'templates': templates})


def start_server():
    logger.info('✅ Semi-Utils Pro 启动成功')
    logger.info(f'服务地址: http://{config.get("DEFAULT", "host")}:{config.getint("DEFAULT", "port")}')
    api.run(
        port=config.getint('DEFAULT', 'port'),
        host=config.get('DEFAULT', 'host'),
        debug=config.getboolean('DEFAULT', 'debug'),
    )


def open_browser(delay: int = 0):
    # 等待服务器启动
    import time
    time.sleep(delay)
    # 打开浏览器并访问指定的URL
    webbrowser.open(f"http://{config.get('DEFAULT', 'host')}:{config.get('DEFAULT', 'port')}")


if __name__ == '__main__':
    # 在单独的线程中打开浏览器
    debug = config.getboolean('DEFAULT', 'debug')
    open_browser_later = lambda: open_browser(1)

    if not debug:
        threading.Thread(target=open_browser_later).start()

    start_server()
