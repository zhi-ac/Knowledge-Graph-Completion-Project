# MySQL数据库集成指南

## 🎯 概述

知识图谱补全系统现已支持MySQL数据库存储，采用混合模式：
- ✅ **内存模式**：高性能实时操作
- ✅ **数据库模式**：数据持久化存储
- ✅ **混合模式**：内存+数据库，性能与持久化兼顾

## 📋 前置要求

### 1. MySQL服务
确保MySQL服务正在运行：
```bash
# Windows
net start mysql

# Linux/Mac
sudo systemctl start mysql
# 或
brew services start mysql
```

### 2. 数据库用户
- 用户名：`root`
- 密码：`123456`
- 端口：`3306`
- 主机：`localhost`

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

## 🚀 快速启动

### 方法一：一键启动（推荐）
```bash
python start.py
```
这个命令会：
1. 自动创建数据库 `kgc_project`
2. 创建所有必需的表
3. 加载示例数据
4. 启动Web应用

### 方法二：手动启动
```bash
# 1. 创建数据库
python init_database.py create

# 2. 加载示例数据
python init_database.py sample

# 3. 启动应用
python app.py
```

## 🗄️ 数据库结构

### 实体表 (entities)
```sql
CREATE TABLE entities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME,
    INDEX idx_entity_name (name)
);
```

### 关系表 (relations)
```sql
CREATE TABLE relations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME,
    INDEX idx_relation_name (name)
);
```

### 三元组表 (triples)
```sql
CREATE TABLE triples (
    id INT PRIMARY KEY AUTO_INCREMENT,
    head_entity_id INT NOT NULL,
    relation_id INT NOT NULL,
    tail_entity_id INT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at DATETIME,
    INDEX idx_triple_head_relation (head_entity_id, relation_id),
    INDEX idx_triple_relation_tail (relation_id, tail_entity_id),
    INDEX idx_triple_complete (head_entity_id, relation_id, tail_entity_id)
);
```

### 嵌入向量表 (embeddings)
```sql
CREATE TABLE embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    entity_id INT UNIQUE,
    relation_id INT UNIQUE,
    embedding_type VARCHAR(20) NOT NULL,
    vector_data TEXT NOT NULL,
    embedding_dim INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    INDEX idx_embedding_entity_type (entity_id, embedding_type)
);
```

## 🌐 Web界面功能

### 新增的数据库管理按钮：

1. **🗄️ 数据库状态** - 查看数据库连接和统计信息
2. **💾 同步到数据库** - 将内存数据保存到数据库
3. **🔄 从数据库加载** - 从数据库重新加载知识图谱

### API接口：

```bash
# 获取数据库状态
GET /api/database/status

# 同步到数据库
POST /api/database/sync

# 从数据库加载
POST /api/database/load
```

## 💡 使用技巧

### 1. 自动同步
- 添加三元组时自动保存到数据库
- 训练模型时自动保存嵌入向量

### 2. 混合模式优势
- **高性能**：内存操作，响应快速
- **持久化**：数据不会丢失
- **可恢复**：重启后自动加载

### 3. 切换模式
在初始化时可以选择：
```javascript
{
    "use_sample": true,
    "use_database": true  // true=数据库模式, false=纯内存模式
}
```

## 🔧 故障排除

### 数据库连接失败
```bash
# 检查MySQL服务
mysql -u root -p123456 -e "SHOW DATABASES;"

# 检查端口
netstat -an | grep 3306
```

### 权限问题
```sql
-- 确保用户有足够权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 字符编码问题
确保使用UTF-8编码：
```sql
ALTER DATABASE kgc_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📈 性能优化

### 1. 索引优化
数据库已创建复合索引，支持高效查询：
- 实体名称索引
- 关系名称索引
- 三元组组合索引

### 2. 连接池
使用SQLAlchemy连接池：
```python
pool_pre_ping=True
pool_recycle=3600
```

### 3. 批量操作
添加三元组支持批量插入，提高性能。

## 🔄 数据迁移

### 从内存模式迁移到数据库
1. 启动应用（内存模式）
2. 点击"💾 同步到数据库"
3. 重启应用自动加载数据

### 导出数据
```python
from models.database import KGDatabase
triples = KGDatabase.get_all_triples()
# 保存到文件
```

## 🎉 完成！

现在您的知识图谱补全系统具备了完整的数据库支持：

- ✅ **数据持久化**：重启不丢失
- ✅ **高性能**：内存+数据库混合
- ✅ **易管理**：Web界面管理
- ✅ **可扩展**：支持大数据量

访问 `http://localhost:5000` 开始使用！