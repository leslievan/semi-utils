# 创建 flask 服务器
import threading
import webbrowser

import pystray
from PIL import Image
from pystray import MenuItem

from server import start_server
from util import load_config

config = load_config()


def open_browser(delay: int = 0):
    # 等待服务器启动
    import time
    time.sleep(delay)
    # 打开浏览器并访问指定的URL
    webbrowser.open(f"http://{config.get('DEFAULT', 'host')}:{config.get('DEFAULT', 'port')}")


class TrayApp:
    def __init__(self, server, open_app):
        self.tray = None
        self.running = True
        self.server = server
        self.open_app = open_app

    def create_image(self):
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        return image

    def setup_menu(self):
        return pystray.Menu(
            MenuItem('打开应用', self.open_app),
            pystray.Menu.SEPARATOR,
            MenuItem('退出', self.quit_app),
        )

    def quit_app(self):
        self.running = False
        self.tray.stop()

    def run(self):
        bg_thread = threading.Thread(target=self.server, daemon=True)
        bg_thread.start()

        self.tray = pystray.Icon(
            name='Semi-Utils Pro',
            icon=self.create_image(),
            title='Semi-Utils Pro',
            menu=self.setup_menu()
        )

        print('✅ Semi-Utils Pro 启动成功')
        self.tray.run()


if __name__ == '__main__':
    # 在单独的线程中打开浏览器
    debug = config.getboolean('DEFAULT', 'debug')
    open_browser_later = lambda: open_browser(1)

    if not debug:
        threading.Thread(target=open_browser_later).start()
        tray = TrayApp(start_server, open_browser_later)
        tray.run()
    else:
        start_server()
