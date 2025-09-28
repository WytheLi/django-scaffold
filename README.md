[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Django Scaffold（Developing）
基于Django用户组权限管理的Django脚手架，集成JWT认证，celery实现异步任务、以及定时任务的处理，Django Channels处理WebSocket会话。为企业级应用开发提供强大而灵活的基础架构。

### 快速开始
1. 克隆项目并安装依赖
```bash
git clone <repository>

pip install poetry
poetry install
```

2. 环境配置

```bash
cp .env.example .env
# 编辑.env文件配置数据库和密钥
```

3. 数据库迁移

```bash
python manage.py migrate
```

4. 收集静态文件
```bash
python manage.py collectstatic
cp resource/* static/
```

6. 启动celery
```bash
# 启动 Celery Worker
celery -A core.celery.celery_app worker -P threads -l info -P solo

# 启动 Celery Beat
celery -A core.celery.celery_app beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 在开发环境中（Windows环境不可用），同时启动 worker 和 beat 进行调试
celery -A core.celery.celery_app worker --beat --loglevel=info
```

5. 启动开发服务器

```bash
daphne scaffold.asgi:application -b 0.0.0.0 -p 8000
or
uvicorn scaffold.asgi:application --reload --host 0.0.0.0 --port 8000
```

### drf-spectacular自动生成API文档
http://localhost:8000/docs/

### IM工作流
1. 前端请求创建新会话：`POST /api/conversation/`（后端返回 conversation_id）。
2. 前端拿到 conversation_id 后，用 WebSocket 连接 `wss://host/ws/chat/{conversation_id}/`，同时通过 sec-websocket-protocol 或 query string 传 token。
3. 服务端 connect() 从 `scope['url_route']['kwargs']['conversation_id']` 取 id，校验用户是否为参与者（或该会话是否公开），再决定 accept() 或 close()。
4. 所有消息写入 DB 时，使用 conversation_id 进行关联，group name 使用安全前缀。


### 文档资源
- [Django文档](https://docs.djangoproject.com/zh-hans/5.2/)
- [Django REST framework文档](https://www.django-rest-framework.org/)
- [Django Channels to handle WebSockets, chat protocols, IoT protocols](https://channels.readthedocs.io/en/latest/)
- [pre-commit预提交钩子 - 代码质量检查](https://pre-commit.com/)]


### 项目初衷
最近在研究和学习开源项目 [MaxKB](https://github.com/1Panel-dev/MaxKB)（基于大语言模型的知识库问答系统）时，我发现其 Django 后端项目的代码结构、Django基于用户组的权限管理，以及DRF应用等工程实践存在不少可优化的空间，未能完全遵循 Django 特性，这给项目的长期维护和扩展性带来了一定挑战。

正是基于这样的观察和思考，我萌生了构建一个高质量 Django 脚手架项目的想法。这个脚手架旨在提供一个企业级的基础框架，整合现代 Django 开发中的各种最佳实践和常用功能模块，让开发者能够快速启动项目，同时确保代码质量和可维护性。

本项目是利用业余时间开发的，虽然已经集成了部分基础功能，但仍可能存在诸多不足之处。我非常希望能够与社区开发者一起探讨、完善这个项目，共同打造一个真正开箱即用、符合生产环境要求的 Django 脚手架解决方案。

### 贡献指南
欢迎提交Issue和Pull Request来帮助完善该项目。
