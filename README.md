# semi-utils

> [![hugo-papermod](https://img.shields.io/badge/Semi--Utils-@LeslieVan-red)](https://github.com/leslievan/semi-utils)
> [![download](https://img.shields.io/github/downloads/leslievan/semi-utils/total.svg)](https://github.com/leslievan/semit-utils/releases)
> [![release](https://img.shields.io/github/v/release/leslievan/semi-utils)](https://github.com/leslievan/semi-utils/releases)
> [![license](https://img.shields.io/github/license/leslievan/semi-utils)](https://github.com/leslievan/semi-utils/blob/master/LICENSE)
> ![language](https://img.shields.io/github/languages/top/leslievan/semi-utils?color=orange)
>
> **这是一个用于给照片批量添加水印、处理照片像素比、图像色彩和质量的工具。**

如果您觉得程序对您有所帮助的话，可以点击 [Sponsor](https:/su/cdn.lsvm.xyz/wechat.jpg) 按钮请作者喝杯咖啡，谢谢！


## 快速开始

### 1. 环境要求

- **Python ≥ 3.13**
- **exiftool**：读取照片 EXIF 信息（相机型号、镜头、光圈、快门、ISO、拍摄时间等）必需。它是独立的命令行程序，**不是 Python 包，无法通过 pip/uv 安装**，需单独安装：
  - macOS：`brew install exiftool`
  - Linux：`sudo apt install libimage-exiftool-perl`
  - Windows：从 [exiftool.org](https://exiftool.org/) 下载，解压到项目的 `./exiftool/` 目录
  > ⚠️ 缺少 exiftool 时程序仍能启动，但生成的图片不会有任何水印文字和品牌 Logo。

### 2. 运行

#### 方式一：uv（推荐）

[uv](https://docs.astral.sh/uv/) 会自动安装匹配的 Python 版本，并按 `uv.lock` 锁定依赖：

```bash
uv run app.py
```

#### 方式二：init.sh（没有 uv 时）

脚本会校验 Python 版本、创建虚拟环境、安装依赖，并检测 exiftool（macOS 上用 Homebrew 自动安装；其他系统若缺少则提示手动安装并退出），最后启动：

```bash
./init.sh
```

### 3. 使用

启动后会自动打开浏览器访问 **http://localhost:15050**（若未自动打开，手动访问该地址即可）。在网页里选择照片所在文件夹、挑选水印模板，点击处理即可。处理后的图片会输出到 `output/` 目录。

> 端口、输入/输出目录、输出质量、默认模板等均可在 `config/config.ini` 中修改。


## 效果展示

| 模板                                     | 描述                                      | 效果                                      |
|----------------------------------------|-----------------------------------------|-----------------------------------------|
| [standard1](./static/standard1.json)   | 经典 EXIF 水印，包含相机型号、镜头、焦距、光圈、快门、ISO、拍摄时间和相机品牌 Logo | ![standard1](./static/standard1.jpeg)   |
| [standard2](./static/standard2.json)   | 在 standard1 基础上添加圆角、阴影效果和留白，适合社交媒体分享 | ![standard2](./static/standard2.jpeg)   |
| [nikon_blur](./static/nikon_blur.json) | 尼康风格水印，相机型号中的红色「Z」字高亮，配合模糊背景效果 | ![nikon_blur](./static/nikon_blur.jpeg) |
| [blur](./static/blur.json)             | 简洁风格，相机型号+参数垂直居中展示，配合模糊背景效果 | ![blur](./static/blur.jpeg)             |
| [normal1](./static/normal1.json)       | 极简风格，右下角显示拍摄参数，低调不抢眼 | ![normal1](./static/normal1.jpeg)       |
| [normal2](./static/normal2.json)       | 文件夹名称+拍摄时间，橙色文字，简洁实用 | ![normal2](./static/normal2.jpeg)       |
| [center_logo](./static/center_logo.json) | 中心 Logo 水印，可自定义四周文字内容 | ![center_logo](./static/center_logo.jpeg)       |


## 开发文档

**[Wiki](../../wiki)**


## 许可证

Semi-Utils 的发布基于 [Apache License 2.0](LICENSE).

### exiftool

Semi-Utils 引用了 [exiftool](https://exiftool.org/)，其发布基于 [GPL v1 + Artistic License 2.0](https://exiftool.org/#license)。


## 关于

[![Stargazers over time](https://starchart.cc/leslievan/semi-utils.svg)](https://starchart.cc/leslievan/semi-utils)
