# Docker 部署说明

本项目已配置完整的Docker环境，包括应用程序、MongoDB数据库和Redis缓存。

## 文件说明

- `Dockerfile`: 主应用程序的Docker镜像配置
- `.dockerignore`: Docker构建时忽略的文件列表
- `docker-compose.yml`: 完整的服务编排配置
- `mongo-init/init-mongo.js`: MongoDB数据库初始化脚本

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- Docker
- Docker Compose

### 2. 配置环境变量

复制环境变量模板并填写配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置项：
- `TUSHARE_TOKEN`: Tushare API令牌
- `MONGODB_URI`: 使用 `mongodb://user:password@mongodb:27017/?authSource=long-quant`
- 其他API令牌和配置

### 3. 启动服务

使用Docker Compose启动所有服务：
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f long-quant
```

### 4. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止服务并删除数据卷（谨慎使用）
docker-compose down -v
```

## 服务说明

### 主应用 (long-quant)
- 容器名: `long-quant-app`
- 功能: 运行量化交易主程序
- 依赖: MongoDB

### MongoDB数据库
- 容器名: `long-quant-mongodb`
- 端口: `27017`
- 用户名: `user`
- 密码: `password`
- 数据库: `long-quant`

### Redis缓存
- 容器名: `long-quant-redis`
- 端口: `6379`
- 用途: 可选的缓存服务

## 常用命令

### 查看日志
```bash
# 查看主应用日志
docker-compose logs -f long-quant

# 查看MongoDB日志
docker-compose logs -f mongodb

# 查看所有服务日志
docker-compose logs -f
```

### 进入容器
```bash
# 进入主应用容器
docker-compose exec long-quant bash

# 进入MongoDB容器
docker-compose exec mongodb mongosh
```

### 重启服务
```bash
# 重启主应用
docker-compose restart long-quant

# 重启所有服务
docker-compose restart
```

### 更新应用
```bash
# 重新构建并启动
docker-compose up -d --build
```

## 数据持久化

- MongoDB数据存储在Docker卷 `mongodb_data` 中
- Redis数据存储在Docker卷 `redis_data` 中
- 应用日志映射到本地 `./logs` 目录
- 应用数据映射到本地 `./data` 目录

## 网络配置

所有服务运行在自定义网络 `long-quant-network` 中，服务间可以通过服务名进行通信。

## 故障排除

### 1. 端口冲突
如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "27018:27017"  # 将MongoDB映射到27018端口
```

### 2. 权限问题
确保日志和数据目录有正确的权限：
```bash
mkdir -p logs data
chmod 755 logs data
```

### 3. 内存不足
如果遇到内存问题，可以限制容器内存使用：
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

### 4. 查看详细错误
```bash
# 查看容器状态
docker-compose ps

# 查看详细日志
docker-compose logs --tail=100 long-quant
```

## 生产环境建议

1. **安全性**:
   - 修改默认密码
   - 使用环境变量管理敏感信息
   - 配置防火墙规则

2. **监控**:
   - 添加健康检查
   - 配置日志轮转
   - 监控资源使用

3. **备份**:
   - 定期备份MongoDB数据
   - 备份配置文件

4. **更新**:
   - 定期更新基础镜像
   - 测试后再部署到生产环境
