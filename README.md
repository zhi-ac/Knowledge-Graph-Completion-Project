# 知识图谱补全系统 (Knowledge Graph Completion)

基于TransE算法的智能知识图谱补全平台，提供Web界面和API接口。

## 🌟 功能特性

- **知识图谱管理**: 支持添加、查询和可视化知识图谱
- **TransE算法**: 实现了经典的TransE知识图谱嵌入算法
- **智能补全**: 预测缺失的实体和关系
- **链接预测**: 发现实体间的潜在关联
- **可视化界面**: 美观的Web界面，支持交互式图谱可视化
- **RESTful API**: 完整的API接口，支持第三方集成
- **动态扩展**: 支持运行时动态添加三元组，自动同步嵌入向量
- **错误修复**: 解决了动态添加数据时的索引越界问题

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示脚本

```bash
python demo.py
```

这将展示TransE算法的基本功能，包括知识图谱创建、模型训练和补全演示。

### 3. 启动Web服务

```bash
python app.py
```

然后在浏览器中访问 `http://localhost:5000`

## 📁 项目结构

```
KGCProject/
├── app.py                 # Flask Web应用主程序
├── demo.py               # 演示脚本
├── requirements.txt       # 依赖包列表
├── models/               # 模型模块
│   ├── __init__.py
│   ├── kg_data.py       # 知识图谱数据结构
│   └── transe.py        # TransE算法实现
├── templates/           # HTML模板
│   └── index.html       # 主界面
└── static/              # 静态资源
```

## 🧠 核心算法

### TransE (Translating Embeddings)

TransE是一种简单而有效的知识图谱嵌入方法，核心思想是：

- 将实体和关系都映射到低维向量空间
- 对于三元组 (h, r, t)，希望满足: **h + r ≈ t**
- 通过最小化正负样本的距离差异来训练嵌入向量

### 损失函数

使用Hinge Loss：
```
L = max(0, ||h + r - t|| - ||h' + r - t'|| + margin)
```

其中 (h, r, t) 是正样本，(h', r, t') 是负样本。

## 🔧 API 接口

### 初始化知识图谱
```http
POST /api/kg/init
Content-Type: application/json

{
    "use_sample": true
}
```

### 训练模型
```http
POST /api/kg/train
Content-Type: application/json

{
    "epochs": 100,
    "learning_rate": 0.01
}
```

### 获取图谱信息
```http
GET /api/kg/info
```

### 添加三元组
```http
POST /api/kg/add_triple
Content-Type: application/json

{
    "head": "实体1",
    "relation": "关系",
    "tail": "实体2"
}
```

### 知识图谱补全
```http
POST /api/kg/complete
Content-Type: application/json

{
    "head": "头实体",
    "relation": "关系", 
    "tail": "尾实体",
    "top_k": 5
}
```

### 链接预测
```http
POST /api/kg/predict
Content-Type: application/json

{
    "entity": "实体名称",
    "top_k": 10
}
```

## 💡 使用示例

### Web界面操作

1. **初始化**: 点击"初始化知识图谱"加载示例数据
2. **训练**: 点击"训练模型"开始学习嵌入向量
3. **添加数据**: 使用"添加三元组"功能扩展知识图谱
4. **补全测试**: 使用"知识图谱补全"功能预测缺失实体
5. **链接发现**: 使用"链接预测"发现实体间潜在关系

### 代码示例

```python
from models.kg_data import KGDataset
from models.transe import TransE

# 创建知识图谱
kg = KGDataset.create_sample_dataset()

# 训练TransE模型
model = TransE(kg, embedding_dim=100, epochs=100)
model.train()

# 补全三元组
results = model.complete_triple(head="爱因斯坦", relation="提出了", top_k=5)
for entity, score in results:
    print(f"爱因斯坦 提出了 {entity} (置信度: {1-score:.3f})")

# 预测链接
predictions = model.predict_missing_links("爱因斯坦", top_k=10)
for entity, relation, score in predictions:
    print(f"爱因斯坦 --{relation}--> {entity}")
```

## 🎯 应用场景

- **知识图谱构建**: 自动补全不完整的知识图谱
- **推荐系统**: 基于知识图谱的个性化推荐
- **问答系统**: 回答需要推理的问题
- **数据挖掘**: 发现隐藏的实体关系
- **语义搜索**: 提升搜索结果的相关性

## 🛠️ 技术栈

- **后端**: Python Flask
- **算法**: NumPy, TransE
- **可视化**: vis.js
- **前端**: HTML5, Bootstrap 5
- **交互**: JavaScript

## 📊 示例数据

系统内置了科学领域的示例知识图谱，包含：

- **人物**: 爱因斯坦、牛顿等科学家
- **地点**: 德国、英国等国家城市
- **概念**: 相对论、万有引力定律等科学理论
- **奖项**: 诺贝尔物理学奖等

## 🔮 扩展功能

- 支持更多嵌入算法 (TransR, ComplEx, RotatE)
- 添加知识图谱评估指标
- 支持大规模知识图谱处理
- 集成更多数据源
- 添加模型解释性功能

## 📈 性能优化

- 使用负采样提高训练效率
- 支持GPU加速训练
- 内存优化处理大规模图谱
- 缓存机制提升响应速度

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

---

**🌟 如果这个项目对您有帮助，请给个Star支持一下！**