# 上线部署说明

本项目由 Django 同时提供 Vue 前台、`/api/` 接口和 `/admin/` 管理后台。生产环境不运行 Vite 开发服务器。

## 1. 准备环境变量

复制 `.env.example` 的变量到部署平台的环境变量设置中。必须替换 `DJANGO_SECRET_KEY`，并填写实际域名。`DJANGO_DEBUG` 必须为 `False`。

可用以下命令生成密钥：

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 2. 安装与构建

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

## 3. 启动服务

Windows 可使用 Waitress：

```powershell
.\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8002 config.wsgi:application
```

将 Nginx、Caddy 或部署平台的反向代理配置为把正式域名的请求转发到该端口，并由代理终止 HTTPS。健康检查地址为 `/api/health/`。

## 4. 上线前检查

```powershell
.\.venv\Scripts\python.exe manage.py check --deploy
.\.venv\Scripts\python.exe manage.py test pc_builder
```

生产环境首次部署后，确认首页、`/admin/`、`/api/components/` 与 `/api/health/` 都可访问；定期备份 `db.sqlite3`。当并发或数据量增长时，迁移到 PostgreSQL。
