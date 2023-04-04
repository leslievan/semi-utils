# semi-utils

> [![hugo-papermod](https://img.shields.io/badge/Semi--Utils-@LeslieVan-red)](https://github.com/leslievan/semi-utils)
> [![GitHub](https://img.shields.io/github/license/leslievan/semi-utils)](https://github.com/leslievan/semi-utils/blob/master/LICENSE)
> [![download](https://img.shields.io/github/v/release/leslievan/semi-utils)](https://github.com/leslievan/semi-utils/releases)
> ![language](https://img.shields.io/github/languages/top/leslievan/semi-utils?color=orange)
>
> **这是一个用于给照片批量添加水印的工具。**

## 功能列表

| 功能          | 描述                                                              | 可显示/隐藏             | 可定义位置              |
|-------------|-----------------------------------------------------------------|--------------------|--------------------|
| **厂商 Logo** | 支持自动识别厂商 Logo。                                                  | :white_check_mark: | :x:                |
| **相机厂商**    | 支持自动识别相机厂商。                                                     | :white_check_mark: | :white_check_mark: |
| **相机型号**    | 支持自动识别相机型号。                                                     | :white_check_mark: | :white_check_mark: |
| **拍摄参数**    | 支持自动识别感光度、快门、光圈大小和焦距/等效焦距，如 `70mm f/8.0 1/250 IS0400`，优先读取等效焦距。 | :white_check_mark: | :white_check_mark: |
| **拍摄日期**    | 支持自动识别拍摄日期，如 `2023-03-25 17:08`。                                | :white_check_mark: | :white_check_mark: |
| **自定义文字**   | 支持自定义文字。                                                        | :white_check_mark: | :white_check_mark: |

## 效果展示

> **布局：normal_with_right**
> 
> logo 居右，下方文字内容可自定义

![]()

---

> **布局：normal_with_right**
> 
> logo 居右，添加外包围白框，下方文字内容可自定义

![]()

---

> **布局：normal**
> 
> logo 居左，下方文字内容可自定义

![]()

---

> **布局：square**
> 
> 布局：square" attr="正方形白色边框

![]()

## 使用方法

> **简要步骤**
> 
> ![]()

### Windows

1. 从[Release](https://github.com/leslievan/semi-utils/releases)下载软件后解压，比如解压到 `D:\semi-utils`
1. 将需要添加水印的图片复制到 `D:\semi-utils\input` 文件夹中
1. 双击 `D:\semi-utils\main.exe` 运行程序
1. 按照提示输入 `y或回车` 开始执行
1. 处理好的图片存放在 `D:\semi-utils\output` 中

### macOS/Linux

1. 下载源码后解压，比如解压到 `~/semi-utils`

2. **安装需要的依赖（正式运行前执行一次即可）**

   打开命令行/终端，输入：

   ```shell
   cd ~/semi-utils
   pip install -r requirements.txt
   ```

3. 将需要添加水印的图片复制到 `~/semi-utils/input` 文件夹中

4. 打开命令行/终端，输入

   ```shell
   cd ~/semi-utils
   python ~/semi-utils/main.py
   ```

5. 按照提示输入 `y或回车` 开始执行

6. 处理好的图片存放在 `~/semi-utils/output` 中

## 高级配置

通过 `config.yaml` 配置。

| 参数                     | 描述                                 |
|------------------------|------------------------------------|
| `base.font`            | 水印字体路径，常规字重                        |
| `base.bold_font`       | 水印字体路径，加粗字重                        |
| `base.input_dir`       | 输入的原始照片，建议将原始照片复制一份到该文件夹           |
| `base.output_dir`      | 输出的带水印的照片                          |
| `base.quality`         | 输出质量，默认为 100，可以输入 60-100 之间的数字     |
| `logo.enable`          | true 或者 false，是否显示厂商 logo          |
| `logo.makes`           | 厂商 logo 列表，默认支持尼康、佳能、索尼、宾得，可自行添加配置 |
| `logo.makes.item`      | 厂商配置，一个带有 `id` 和 `path` 两个键的字典     |
| `logo.makes.item.id`   | 厂商标识，由 Exif 信息提供                   |
| `logo.makes.item.path` | 厂商 logo 路径，可自定义                    |

## 关于

鸣谢：[JetBrains](https://jb.gg/OpenSourceSupport) 为本项目提供的开源许可

## 许可证

本项目的发布基于 [Apache License 2.0](https://github.com/leslievan/semi-utils/blob/main/LICENSE).