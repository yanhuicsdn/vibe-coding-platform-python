FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件和 README
COPY pyproject.toml README.md ./

# 配置 Poetry 不创建虚拟环境（因为已经在容器中）
RUN poetry config virtualenvs.create false

# 复制源代码
COPY src/ ./src/

# 安装项目及其依赖
RUN poetry install --only main --no-interaction --no-ansi

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "vibe_coding.main:app", "--host", "0.0.0.0", "--port", "8000"]
