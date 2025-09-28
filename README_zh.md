!\[Python](https://img.shields.io/badge/python-v3.7+-blue.svg)

!\[Flask](https://img.shields.io/badge/flask-v2.3.2-green.svg)

!\[License](https://img.shields.io/badge/license-MIT-blue.svg)

!\[PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)



\#### `README\_zh.md` (中文说明文档)

```markdown

\# ARK 豆包翻译器 🔤



基于 ARK 豆包翻译 API 的轻量级暗黑主题网页翻译器，支持 Markdown 渲染。



!\[演示截图](screenshots/demo.png)



\## 功能特点 ✨



\- 🌙 \*\*暗黑模式\*\*：护眼深色主题设计

\- 🔄 \*\*自动翻译\*\*：输入即翻译，智能防抖优化

\- 📝 \*\*Markdown 支持\*\*：支持格式化文本渲染

\- 🌍 \*\*中英互译\*\*：支持中英双向翻译

\- 📋 \*\*一键复制\*\*：便捷复制翻译结果

\- ⚡ \*\*轻量极简\*\*：最少依赖，快速启动

\- 🎯 \*\*全屏布局\*\*：充分利用屏幕空间



\## 技术栈 🛠



\- \*\*后端框架\*\*：Flask (Python)

\- \*\*前端技术\*\*：原生 HTML/CSS/JavaScript

\- \*\*翻译 API\*\*：ARK 豆包翻译模型

\- \*\*Markdown 渲染\*\*：Python-Markdown



\## 快速开始 🚀



\### 环境要求



\- Python 3.7+

\- ARK API 密钥（\[获取地址](https://www.volcengine.com/)）



\### 安装步骤



1\. \*\*克隆仓库\*\*

&nbsp;  ```bash

&nbsp;  git clone https://github.com/yourusername/ark-translator.git

&nbsp;  cd ark-translator



2\.安装依赖

pip install -r requirements.txt



3\.配置 API 密钥

cp .env.example translator.env

\# 编辑 translator.env 文件，填入您的 ARK API 密钥



4\.运行应用

python app.py



5\.访问应用

http://localhost:5000



配置说明 ⚙️

应用使用环境变量进行配置。创建 translator.env 文件：

ARK\_API\_KEY=您的API密钥



使用方法 📖

在左侧输入框输入或粘贴文本

翻译结果自动显示在右侧

使用交换按钮（⇄）切换源语言和目标语言

点击复制按钮（📋）复制翻译结果

底部开关可控制自动翻译功能

豆包翻译模型介绍 🤖

豆包翻译模型特点：



支持 28 种语言互译

中英翻译效果接近 DeepSeek-R1

摆脱"翻译腔"，提供地道流畅的译文

适配办公、娱乐等多场景需求

贡献指南 🤝

欢迎贡献代码！请按以下步骤：



Fork 本项目

创建特性分支 (git checkout -b feature/AmazingFeature)

提交更改 (git commit -m '添加某个很棒的特性')

推送到分支 (git push origin feature/AmazingFeature)

提交 Pull Request

安全提醒 🔒

切勿提交 API 密钥到代码库

使用环境变量存储敏感信息

.gitignore 已配置忽略环境文件

开源协议 📄

本项目采用 MIT 协议开源 - 查看 LICENSE 文件了解详情



致谢 🙏

火山引擎 提供 ARK API

Flask Web 框架

Python-Markdown Markdown 渲染



作者 👤



GitHub: @LouisLau-art

Email: louis.shawn@qq.com



支持项目 ⭐

如果这个项目对您有帮助，请给个 Star！



用 ❤️ 和 ☕ 制作





