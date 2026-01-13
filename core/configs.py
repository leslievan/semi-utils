import configparser
from pathlib import Path

import tomli

from core import CONFIG_PATH, PROJECT_INFO

fonts_dir = Path('config/fonts')
logos_dir = Path('./config/logos')
templates_dir = Path('./config/templates')

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def load_project_info():
    with open(PROJECT_INFO, "rb") as f:  # 注意：tomllib 需要以二进制模式（"rb"）打开文件
        data = tomli.load(f)
    return data
