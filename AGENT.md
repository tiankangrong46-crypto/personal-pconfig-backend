# 电脑自动搭配网站

## 项目说明

本项目用于构建电脑硬件自动搭配网站。Django 提供数据管理、业务接口和管理后台；Vue 负责面向用户的前台页面。

## 技术栈

- 后端：Python 3.14、Django 6.1
- 管理后台：Django Admin、django-simpleui
- 数据库：SQLite（开发环境）
- 前端：Vue 3、Vite、JavaScript、npm

## 目录约定

- `config/`：Django 项目配置、路由及 WSGI/ASGI 入口。
- `pc_builder/`：电脑配置领域的 Django 应用，存放模型、接口和管理后台配置。
- `frontend/`：Vue 前端项目，独立运行和构建。
- `.venv/`：本项目 Python 虚拟环境，不提交版本控制。

## 常用命令

在项目根目录执行以下命令。

```powershell
# 激活 Python 虚拟环境
.\.venv\Scripts\Activate.ps1

# 启动 Django 后端
python manage.py runserver

# 执行数据库迁移
python manage.py migrate

# 启动 Vue 前端
cd frontend
npm run dev
```

当 PowerShell 阻止脚本执行时，可在当前终端临时允许：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 开发约定

- 后台界面默认使用简体中文，后台入口为 `/admin/`。
- 新增业务模型应放在 `pc_builder/models.py`，并完成迁移后在 `pc_builder/admin.py` 注册。
- 前台页面和组件只放在 `frontend/src/`，通过 HTTP API 与 Django 后端通信。
- 不提交 `.venv/`、`node_modules/`、`db.sqlite3` 及本地环境配置。
