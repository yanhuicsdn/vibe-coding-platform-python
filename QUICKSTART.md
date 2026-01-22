# Vibe Coding Platform (Python) - Quick Start

## 5分钟上手指南

### 前置要求

- Python 3.11+
- Poetry
- Docker & Docker Compose
- Git

### 1. 克隆并安装

```bash
cd vibe-coding-platform-python

# 安装依赖
poetry install

# 启动基础设施
docker-compose up -d
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,更改密钥和密码
```

### 3. 启动服务

```bash
# 开发模式
poetry run uvicorn vibe_coding.main:app --reload

# 生产模式
poetry run gunicorn vibe_coding.main:app
```

### 4. 访问 API

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/health
- **Hasura Console**: http://localhost:8080

### 5. 使用示例

#### 部署 Schema

```bash
curl -X POST http://localhost:8000/api/v1/schema/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "1.0.0",
    "tenant_mode": "row_isolation",
    "entities": {
      "Todo": {
        "name": "Todo",
        "fields": [
          {"name": "id", "type": "uuid", "required": true},
          {"name": "title", "type": "string", "required": true},
          {"name": "completed", "type": "boolean", "required": false}
        ],
        "ownership": {"mode": "user"}
      }
    },
    "permissions": {
      "Todo": {
        "read": "owner",
        "write": "owner",
        "delete": "owner"
      }
    }
  }'
```

#### 解析自然语言意图

```bash
curl -X POST http://localhost:8000/api/v1/intent/parse \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a new entity called Post with title and content fields",
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Python 客户端使用

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # 部署 Schema
        response = await client.post(
            "http://localhost:8000/api/v1/schema/deploy",
            json={...}  # 你的 schema
        )
        print(response.json())

asyncio.run(main())
```

### 下一步

- 📖 完整文档: [docs/](./docs/)
- 🎯 DSL 参考: [docs/DSL_REFERENCE.md](./docs/DSL_REFERENCE.md)
- 🔌 API 文档: [docs/API.md](./docs/API.md)
- 💡 示例代码: [examples/](./examples/)

### 常见问题

**Q: Poetry 安装失败?**
```bash
# 使用 pip 安装 poetry
pip install poetry

# 或使用 pipx
pipx install poetry
```

**Q: Docker 容器无法启动?**
```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

**Q: 端口被占用?**
修改 `.env` 文件中的端口配置:
```bash
API_PORT=8001  # 改为其他端口
```

### 开发工具

```bash
# 代码格式化
poetry run black src/
poetry run ruff check src/

# 类型检查
poetry run mypy src/

# 运行测试
poetry run pytest
```

---

**现在你可以开始构建了!** 🚀
