# **CC98 热门话题追踪器 🚀**  

**CC98 Hot Topics Tracker**  

> **✨ 让 CC98 十大热帖尽在掌握！**  
> **✨ Stay updated with the hottest CC98 discussions!**  

---

## **🌍 项目简介 | Project Introduction**  

CC98 作为中国大学生最受欢迎的论坛之一，每天都有大量热门话题涌现。本项目自动追踪 **CC98 十大** 热门帖，提取并分析楼主发言、热评，并通过 **钉钉 & 企业微信** 发送通知，让你不错过任何热点！🔥  

CC98 is a popular student forum in China, where hot discussions emerge daily. This project **automatically tracks CC98’s top 10 trending posts**, extracts key information from the original post and hot comments, and sends notifications via **DingTalk & WeChat**. Never miss a trending topic again! 🚀  

---

## **🎯 核心功能 | Key Features**  

✅ **自动获取十大热帖**（自定义拉取间隔时间）  
✅ **分析楼主发言 & 热评**，转换 **UBB 代码** 为 Markdown  
✅ **计算风评指数** 📊，追踪帖子热度变化  
✅ **智能存储热门话题**，并记录标题变更历史  
✅ **支持阿里云 OSS**，自动上传 & 处理图片  
✅ **钉钉 & 企业微信通知**，让热点信息触手可得！🔔  

✅ **Auto-fetch top 10 trending posts** (updated freely)  
✅ **Analyze OP's content & hot comments**, converting **UBB code** to Markdown  
✅ **Calculate popularity index** 📊 & track topic heat changes  
✅ **Store trending topics smartly**, keep a history of title changes  
✅ **Aliyun OSS support** for automatic image upload & processing  
✅ **DingTalk & Wechat notifications** for instant updates! 🔔  

---

## **📌 技术栈 | Tech Stack**  

- **👨‍💻 后端 | Backend**: Python 3  
- **📟 平台 | Platform**: WSL2  
- **📡 接口 | API**: CC98 API, DeepSeek LLM  
- **🗄️ 数据库 | Database**: MySQL (存储话题 & 评论)  
- **☁️ 云存储 | Cloud Storage**: 阿里云 OSS  
- **📩 消息推送 | Notifications**: 钉钉 & 企业微信  

---

## **🚀 快速开始 | Quick Start**  

### **1️⃣ 安装依赖 | Install Dependencies**  

```bash
# python version = 3.10
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

### **2️⃣ 配置环境 | Configure Settings**  

将`config.template`重命名为`config.py`，并修改 `config.py`，填入CC98账号数据、数据库信息、钉钉/微信机器人 Webhook。
Rename `config.template` to `config.py`, then edit `config.py` and fill in CC98 user info, database info, and DingTalk/WeChat Webhooks.

### **3️⃣ 运行程序 | Run the program**  

```bash
python main.py
```
---

### **4️⃣ 设定定时任务（可选） | Schedule Automatic Execution (Optional)**  

如果希望程序每隔一段时间自动运行，可以使用 `crontab` 进行定时调度。例如，以下命令每 30 分钟运行一次 `main.py`：  
If you want the program to run automatically at regular intervals, you can use `crontab` for scheduled execution. For example, the following command runs `main.py` every 30 minutes:

```bash
crontab -e
```

在 `crontab` 编辑界面中，添加以下行（请替换 `/path/to/project` 为你的项目路径）：  
In the `crontab` editor, add the following line (replace `/path/to/project` with your actual project path):

```bash
*/30 * * * * /bin/bash -c 'cd /path/to/project && source .venv/bin/activate && python main.py >> cc98hotTopics.log 2>&1'
```

然后保存并退出，使用以下命令检查任务是否正确添加：  
Then, save and exit, and use the following command to verify that the task has been added correctly:

```bash
crontab -l
```

**⚠️ 注意 | Note:**  
请确保 `cron` 服务已启动，否则定时任务不会执行。WSL2 环境下，可以使用以下命令启动 `cron` 服务：  
Make sure the `cron` service is running; otherwise, the scheduled task will not execute. In a WSL2 environment, start the `cron` service using:

```bash
service cron start
```

🎉 **Enjoy! CC98 热门话题尽在掌握！** 🎉  
🎉 **Enjoy! Stay updated with CC98’s hottest topics!** 🎉  

---

## **🔮 未来计划 | Future Plans**  

🚀 **语义分析**：识别 **话题趋势 & 关键词**  
🚀 **订阅支持**：支持特定板块、内容推送给特定订阅用户
🚀 **Semantic analysis**: Detect **trending topics & key terms**  
🚀 **Subscription support**: Support publish specific topics to subscribers 

---

## **📢 贡献指南 | Contributing**  

欢迎 PR！请遵循以下流程：  
1. **Fork 本项目**  
2. **创建新分支** (`git checkout -b feature-xxx`)  
3. **提交代码** (`git commit -m "Add new feature xxx"`)  
4. **推送分支** (`git push origin feature-xxx`)  
5. **提交 Pull Request** 🚀  

We welcome all contributions! Follow these steps:  
1. **Fork this repo**  
2. **Create a new branch** (`git checkout -b feature-xxx`)  
3. **Commit your changes** (`git commit -m "Add new feature"`)  
4. **Push to your branch** (`git push origin feature-xxx`)  
5. **Submit a Pull Request** 🚀  

---

🚀 **加入我们，一起探索 CC98 的精彩世界！** 🚀  
🚀 **Join us and explore the vibrant world of CC98!** 🚀  


