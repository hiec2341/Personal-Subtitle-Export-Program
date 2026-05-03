# 本地字幕生成工具

基于 PyQt5 + Whisper 的离线字幕生成工具，支持音频/视频输入，自动识别语音并生成带时间轴的 SRT 字幕文件。

## 核心特性

- 🔒 **完全本地** - 无需联网，音视频数据不上传
- 🎯 **精准时间轴** - 自动生成与音视频同步的字幕
- 🎬 **多格式支持** - 支持 MP3/WAV/M4A/MP4/MKV/AVI 等格式
- 📝 **SRT输出** - 通用字幕格式，兼容所有播放器
- 🎨 **可视化界面** - 直观的图形界面操作
- ⚡ **中文路径支持** - 自动处理中文文件名和路径

## 安装步骤

### 1. 安装 Python

需要 Python 3.8 或更高版本。
官网: https://www.python.org/downloads/

### 2. 安装 FFmpeg

Whisper 需要 FFmpeg 来处理音频：

**Windows 用户：**
1. 下载 FFmpeg: https://github.com/BtbN/FFmpeg-Builds/releases
2. 选择 `ffmpeg-master-latest-win64-gpl.zip`
3. 解压到 `C:\ffmpeg`
4. 添加 `C:\ffmpeg\bin` 到系统环境变量 PATH

**验证安装：**
```bash
ffmpeg -version
```

### 3. 安装依赖

打开命令提示符 (CMD)，运行:

```bash
cd "c:\Users\Mechrevo\Desktop\VC2010相关\text"
pip install -r requirements.txt
```

### 4. 启动工具

双击运行 `启动工具.bat`

或者在命令行中运行:

```bash
python main.py
```

## 使用说明

### 基本使用

1. 点击"浏览..."按钮选择音视频文件
2. 选择合适的模型 (推荐 small)
3. 选择识别语言
4. 点击"🎯 开始生成字幕"按钮
5. 等待转录完成
6. 在表格预览字幕
7. 点击"导出字幕文件"保存

### 模型选择

- **tiny** - 最快，体积小 (~75MB)，准确率一般
- **base** - 较快，体积适中 (~140MB)，适合一般使用
- **small** - 平衡之选 (~450MB)，**推荐**
- **medium** - 较慢，体积大 (~1.5GB)，准确率高
- **large** - 最慢，体积最大 (~3GB)，最高准确率

### 支持的语言

- 中文 (推荐)
- 英文
- 日文
- 韩文
- 法文
- 德文
- 西班牙文
- 意大利文
- 葡萄牙文
- 俄文

## 硬件要求

### 最低配置
- CPU (可用)
- 4GB 内存
- 2GB 硬盘空间

### 推荐配置
- NVIDIA GPU (CUDA 加速)
- 8GB+ 内存
- 5GB 硬盘空间

### GPU 加速

如果有 NVIDIA 显卡，建议安装 CUDA 以提升速度:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## 项目结构

```
c:\Users\Mechrevo\Desktop\VC2010相关\text\
├── main.py                    # 🎯 主程序入口
├── requirements.txt           # 📦 Python依赖
├── README.md                 # 📖 文档说明
├── 启动工具.bat             # 🚀 一键启动脚本
└── src/                      # 📂 源代码目录
    ├── __init__.py
    ├── subtitle_generator.py  # 字幕生成模块
    └── whisper_recognizer.py # Whisper语音识别模块
```

## 常见问题

### Q: 首次运行很慢？
A: 首次使用需要下载模型文件，请耐心等待。

### Q: 提示找不到模块？
A: 请运行: `pip install -r requirements.txt`

### Q: 提示找不到 ffmpeg？
A: 请确保已安装 FFmpeg 并添加到系统 PATH 环境变量。

### Q: 中文路径报错？
A: 程序已内置中文路径处理，如仍有问题请使用英文路径。

### Q: 如何提高识别速度？
A:
1. 使用较小的模型 (small/medium)
2. 使用 GPU 加速
3. 减少线程数

## 技术栈

- **GUI**: PyQt5
- **语音识别**: OpenAI Whisper
- **深度学习**: PyTorch
- **音视频处理**: FFmpeg
- **语言**: Python 3.8+

## 开源许可

- 本项目: MIT License
- Whisper: Apache 2.0
- FFmpeg: LGPL 2.1+
- PyQt5: GPL/LGPL

## 更新日志

### v1.0.0 (2026-05-03)
- 初始版本
- 支持 Whisper 语音识别
- 支持 SRT 格式导出
- 可视化界面操作
- 中文路径自动处理
