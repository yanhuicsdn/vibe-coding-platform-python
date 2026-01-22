# Vibe Coding Platform - Python Implementation

多租户 Hasura Engine 作为 Vibe Coding 平台后端支撑系统 (Python 版本)

## 系统概述

这是一个 AI 可编程的、多租户、声明式后端操作系统,支持:

- ✅ 多租户隔离(Row-level Security)
- ✅ AI 安全修改后端能力
- ✅ Schema 可演进、可回滚
- ✅ 前端完全解耦(无需 GraphQL 知识)
- ✅ 声明式 DSL 驱动

## 技术栈

- **Python 3.11+** - 编程语言
- **FastAPI** - 高性能 Web 框架
- **Pydantic** - 数据验证和序列化
- **PyJWT** - JWT 认证
- **AsyncPG** - 异步 PostgreSQL 驱动
- **Redis** - 缓存和会话管理
- **Alembic** - 数据库迁移
- **Poetry** - 依赖管理

## 快速开始

### 前置要求

- Python 3.11+
- Poetry
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd vibe-coding-platform-python

# 安装依赖
poetry install

# 启动基础设施
docker-compose up -d

# 运行数据库迁移
poetry run alembic upgrade head

# 启动服务
poetry run uvicorn vibe_coding.main:app --reload
```

### 环境变量

复制 `.env.example` 到 `.env` 并配置:

```bash
cp .env.example .env
```

## 项目结构

```
vibe-coding-platform-python/
├── src/vibe_coding/           # 源代码
│   ├── core/                  # 核心模块
│   │   ├── config.py         # 配置管理
│   │   ├── security.py       # 安全相关
│   │   └── exceptions.py     # 自定义异常
│   ├── models/               # Pydantic 模型
│   │   ├── dsl.py           # DSL 类型定义
│   │   ├── auth.py          # 认证类型
│   │   └── schema.py        # Schema 类型
│   ├── services/             # 业务逻辑
│   │   ├── dsl/             # DSL 服务
│   │   │   ├── parser.py    # 解析器
│   │   │   ├── validator.py # 验证器
│   │   │   ├── diff.py      # Diff 引擎
│   │   │   └── sql_gen.py   # SQL 生成器
│   │   ├── hasura.py        # Hasura 客户端
│   │   ├── auth.py          # 认证服务
│   │   ├── schema_manager.py # Schema 管理
│   │   └── version_service.py # 版本管理
│   ├── api/                  # API 层
│   │   ├── routes/          # 路由
│   │   ├── dependencies.py  # 依赖注入
│   │   └── middleware.py    # 中间件
│   ├── db/                   # 数据库
│   │   ├── session.py       # 数据库会话
│   │   └── repositories/    # 数据访问层
│   └── main.py              # 应用入口
├── tests/                     # 测试
├── alembic/                   # 数据库迁移
├── docs/                      # 文档
├── examples/                  # 示例
├── docker-compose.yml        # Docker 编排
├── pyproject.toml            # Poetry 配置
└── README.md                 # 项目说明
```

## 核心功能

### 1. DSL 系统

声明式 Schema 定义语言示例:

```yaml
project_id: "550e8400-e29b-41d4-a716-446655440000"
version: "1.0.0"
tenant_mode: "row_isolation"

entities:
  Todo:
    name: "Todo"
    fields:
      - name: "id"
        type: "uuid"
        required: true
      - name: "title"
        type: "string"
        required: true
      - name: "completed"
        type: "boolean"
        required: false
    ownership:
      mode: "user"

permissions:
  Todo:
    read: "owner"
    write: "owner"
    delete: "owner"
```

### 2. 多租户模型

每条业务数据强制包含:

- `tenant_id`: 租户 ID
- `project_id`: 项目 ID
- `owner_user_id`: 所有者用户 ID

权限通过 Hasura Row-level Security + JWT Claims 实现。

### 3. 前端 SDK (Python)

简化 API 调用,隐藏 GraphQL 复杂性:

```python
from vibe_coding import VibeClient

backend = VibeClient(
    api_url="http://localhost:8000",
    jwt_token="your-jwt-token"
)

# 创建 Todo
await backend.todo.create(title="Buy milk")

# 列表
todos = await backend.todo.list()

# 更新
await backend.todo.update(id, completed=True)
```

## 开发指南

### 运行测试

```bash
poetry run pytest
```

### 代码格式化

```bash
poetry run black src/
poetry run ruff check src/
```

### 类型检查

```bash
poetry run mypy src/
```

## API 文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 部署

生产环境配置请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 许可证

MIT

## 贡献

欢迎贡献! 请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

Generated with [Claude Code](https://claude.ai/code)
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>
