import json
import mimetypes
import socket
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse


IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


PAGE_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Semi-Utils 照片墙</title>
  <style>
    :root {
      color: #1f2428;
      background: #f7f7f4;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: #f7f7f4;
      color: #1f2428;
    }

    header {
      width: min(1440px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 20px;
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 18px;
      border-bottom: 1px solid #d8d9d2;
    }

    h1 {
      margin: 0;
      font-size: 30px;
      line-height: 1.15;
      font-weight: 760;
    }

    .meta {
      margin: 10px 0 0;
      color: #59615d;
      line-height: 1.7;
      font-size: 14px;
    }

    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    button {
      appearance: none;
      border: 1px solid #303633;
      background: #303633;
      color: #ffffff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
    }

    button.secondary {
      background: transparent;
      color: #303633;
    }

    main {
      width: min(1440px, calc(100% - 32px));
      margin: 0 auto;
      padding: 26px 0 42px;
    }

    .gallery {
      column-count: 4;
      column-gap: 18px;
    }

    figure {
      break-inside: avoid;
      margin: 0 0 18px;
      background: #ffffff;
      border: 1px solid #deded8;
      border-radius: 8px;
      overflow: hidden;
    }

    img {
      display: block;
      width: 100%;
      height: auto;
      background: #ecece7;
      cursor: zoom-in;
    }

    figcaption {
      padding: 10px 12px 12px;
      color: #59615d;
      font-size: 13px;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }

    .empty {
      border: 1px dashed #b8bbb3;
      border-radius: 8px;
      padding: 24px;
      color: #59615d;
      line-height: 1.7;
      background: #ffffff;
    }

    dialog {
      width: min(96vw, 1280px);
      max-height: 96vh;
      padding: 0;
      border: 0;
      border-radius: 8px;
      background: #111411;
    }

    dialog::backdrop {
      background: rgba(0, 0, 0, .78);
    }

    .viewer {
      display: grid;
      grid-template-rows: 1fr auto;
      max-height: 96vh;
    }

    .viewer img {
      width: 100%;
      max-height: calc(96vh - 54px);
      object-fit: contain;
      background: #111411;
      cursor: default;
    }

    .viewer-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      color: #ffffff;
      font-size: 14px;
    }

    @media (max-width: 1100px) {
      .gallery {
        column-count: 3;
      }
    }

    @media (max-width: 760px) {
      header {
        align-items: stretch;
        flex-direction: column;
        padding-top: 24px;
      }

      .toolbar {
        justify-content: flex-start;
      }

      .gallery {
        column-count: 2;
        column-gap: 12px;
      }

      figure {
        margin-bottom: 12px;
      }

      h1 {
        font-size: 24px;
      }
    }

    @media (max-width: 460px) {
      .gallery {
        column-count: 1;
      }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Semi-Utils 照片墙</h1>
      <p class="meta" id="summary">正在读取 output 文件夹...</p>
    </div>
    <div class="toolbar">
      <button id="refresh" type="button">刷新</button>
      <button class="secondary" id="top" type="button">回到顶部</button>
    </div>
  </header>
  <main>
    <section class="gallery" id="gallery"></section>
    <section class="empty" id="empty" hidden>
      output 文件夹里还没有可展示的图片。先运行一次照片处理，再刷新这个页面。
    </section>
  </main>
  <dialog id="dialog">
    <div class="viewer">
      <img id="viewer-img" alt="">
      <div class="viewer-bar">
        <span id="viewer-name"></span>
        <button class="secondary" id="close" type="button">关闭</button>
      </div>
    </div>
  </dialog>
  <script>
    const gallery = document.querySelector('#gallery');
    const empty = document.querySelector('#empty');
    const summary = document.querySelector('#summary');
    const dialog = document.querySelector('#dialog');
    const viewerImg = document.querySelector('#viewer-img');
    const viewerName = document.querySelector('#viewer-name');

    function formatSize(bytes) {
      if (bytes < 1024 * 1024) {
        return `${Math.round(bytes / 1024)} KB`;
      }
      return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
    }

    function render(photos) {
      gallery.replaceChildren();
      empty.hidden = photos.length !== 0;
      summary.textContent = photos.length ? `${photos.length} 张照片，按修改时间从新到旧排列` : '没有找到图片';

      for (const photo of photos) {
        const figure = document.createElement('figure');
        const img = document.createElement('img');
        const caption = document.createElement('figcaption');

        img.src = photo.url;
        img.alt = photo.name;
        img.loading = 'lazy';
        img.decoding = 'async';
        img.addEventListener('click', () => {
          viewerImg.src = photo.url;
          viewerImg.alt = photo.name;
          viewerName.textContent = photo.name;
          dialog.showModal();
        });

        caption.textContent = `${photo.name} · ${formatSize(photo.size)}`;
        figure.append(img, caption);
        gallery.append(figure);
      }
    }

    async function loadPhotos() {
      summary.textContent = '正在读取 output 文件夹...';
      const response = await fetch('/api/photos', {cache: 'no-store'});
      if (!response.ok) {
        throw new Error('读取失败');
      }
      const data = await response.json();
      render(data.photos);
    }

    document.querySelector('#refresh').addEventListener('click', () => {
      loadPhotos().catch(() => {
        summary.textContent = '读取失败，请回到终端查看提示';
      });
    });

    document.querySelector('#top').addEventListener('click', () => {
      window.scrollTo({top: 0, behavior: 'smooth'});
    });

    document.querySelector('#close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });

    loadPhotos().catch(() => {
      summary.textContent = '读取失败，请回到终端查看提示';
    });
  </script>
</body>
</html>
"""


def list_output_images(output_dir):
    output_path = Path(output_dir).resolve()
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    photos = []
    for file_path in output_path.rglob('*'):
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        stat = file_path.stat()
        name = file_path.relative_to(output_path).as_posix()
        photos.append({
            'name': name,
            'url': '/photos/' + quote(name),
            'size': stat.st_size,
            'mtime': stat.st_mtime,
        })

    photos.sort(key=lambda item: (item['mtime'], item['name']), reverse=True)
    return photos


def find_free_port(start_port=8765):
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('127.0.0.1', port))
            except OSError:
                continue
            return port
    raise OSError('没有找到可用端口')


class GalleryRequestHandler(BaseHTTPRequestHandler):
    output_dir = Path('./output').resolve()

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_html(PAGE_HTML)
            return
        if parsed.path == '/api/photos':
            self.send_json({'photos': list_output_images(self.output_dir)})
            return
        if parsed.path.startswith('/photos/'):
            self.send_photo(parsed.path.removeprefix('/photos/'))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def send_html(self, content):
        body = content.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_photo(self, url_name):
        name = unquote(url_name)
        if Path(name).name != name:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        photo_path = self.output_dir.joinpath(name).resolve()
        if not photo_path.is_relative_to(self.output_dir) or photo_path.suffix.lower() not in IMAGE_SUFFIXES:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not photo_path.exists() or not photo_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(photo_path.name)[0] or 'application/octet-stream'
        body = photo_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def open_gallery(output_dir, host='127.0.0.1', start_port=8765):
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    port = find_free_port(start_port)
    GalleryRequestHandler.output_dir = output_path
    server = ThreadingHTTPServer((host, port), GalleryRequestHandler)
    url = f'http://{host}:{port}/'

    print(f'照片墙已启动：{url}')
    print(f'正在展示文件夹：{output_path}')
    print('刷新网页即可看到新增图片，按 Ctrl+C 关闭照片墙并返回主菜单。')

    threading.Timer(.3, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n照片墙已关闭')
    finally:
        server.server_close()
