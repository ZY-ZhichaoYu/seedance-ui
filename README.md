# Seedance UI

本地 Seedance 视频生成工具，支持 Text-to-Video 和 Image-to-Video。

## 前置条件

1. [注册火山引擎账号](https://console.volcengine.com/)
2. 在 [方舟控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement) 开通以下任一模型：
   - `doubao-seedance-2-0-260128`（推荐）
   - `doubao-seedance-2-0-fast-260128`
   - `doubao-seedance-1-5-pro-251215`
3. 在 [API Key 页面](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) 创建 API Key

## 快速开始

```bash
git clone https://github.com/ZY-ZhichaoYu/seedance-ui.git
cd seedance-ui
pip install -r requirements.txt
python app.py
```

浏览器访问 http://localhost:8080 ，在页面顶部填入 API Key 即可使用。

## 可选：通过 .env 预配置 API Key

适合自用或在服务器上部署时，避免每次手动填写 Key：

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

`.env` 文件内容：

```
API_KEY=你的_API_Key
```

启动后页面会自动隐藏 API Key 输入框，直接可用。

## 使用说明

- **模式**：Text-to-Video（文字生图）/ Image-to-Video（图片转视频）
- **时长**：5 / 10 / 15 秒
- **分辨率**：1280×720 / 1920×1080 / 960×960
- 生成完成后可在页面内嵌播放器预览，并通过**下载 MP4** 按钮保存到本地
- 任务每 5 秒自动轮询状态；视频文件保存在 `output/` 目录

## 目录结构

```
seedance-ui/
├── app.py            # Flask 后端
├── requirements.txt
├── .env.example      # 环境变量示例
├── static/
│   └── index.html    # 前端（单文件，无需构建）
└── output/           # 生成的视频（已加入 .gitignore）
```
