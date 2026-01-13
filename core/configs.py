import configparser
from pathlib import Path

from core import CONFIG_PATH, PROJECT_INFO

# 优先使用内置 tomllib (Python 3.11+)，否则使用 tomli
try:
    import tomllib as _toml
except ImportError:
    import tomli as _toml

fonts_dir = Path('./config/fonts')
logos_dir = Path('./config/logos')
templates_dir = Path('./config/templates')

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    return config


def load_project_info():
    with open(PROJECT_INFO, "rb", encoding='utf-8') as f:
        data = _toml.load(f)
    return data
