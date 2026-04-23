# Seedance UI

本地 Seedance 视频生成工具，支持 Text-to-Video 和 Image-to-Video。

---

## 第一步：准备 API Key

1. [注册火山引擎账号](https://console.volcengine.com/)
2. 进入 [方舟控制台 → 模型广场](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement)，搜索并开通 **doubao-seedance-2-0-260128**（或其他 Seedance 模型）
3. 进入 [API Key 管理页](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)，点击「创建 API Key」，复制保存

---

## 第二步：下载项目

点击页面右上角绿色 **Code** 按钮 → **Download ZIP**，解压到任意目录。

---

## 第三步：安装 Python（如已安装可跳过）

需要 Python 3.8 及以上，**无需安装任何其他依赖**。

- 打开终端（Windows 搜索「cmd」），输入 `python --version`，有版本号即可跳过
- 如未安装，前往 [python.org](https://www.python.org/downloads/) 下载，安装时勾选 **Add Python to PATH**

---

## 第四步：启动

进入解压后的文件夹，**双击 `start.bat`**（Windows）。

浏览器会自动打开 http://localhost:8080。

> 也可以在终端中运行 `python app.py`，效果相同。  
> 每次使用前需要先启动，关闭窗口后服务停止。

---

## 第五步：使用

在顶部「API Key」框粘贴第一步获取的 Key（自动保存，下次无需重填），选择模型和参数，填写 Prompt，点击「生成视频」。

生成完成后可直接预览，点击**下载 MP4** 保存到本地。

---

## 可选：预置 API Key（避免每次填写）

在项目根目录新建名为 `.env` 的文件，内容：

```
API_KEY=你的_API_Key
```

启动后页面自动隐藏输入框，直接可用。

---

## 参数说明

| 选项 | 可选值 |
|---|---|
| 模式 | Text-to-Video（文字→视频）/ Image-to-Video（图片→视频） |
| 时长 | 5 / 10 / 15 秒 |
| 分辨率 | 1280×720 / 1920×1080 / 960×960 |

生成的视频保存在项目目录下的 `output/` 文件夹。
