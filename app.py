from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from models.kg_adapter import HybridKnowledgeGraph, HybridTransE
from models.database import close_database
import numpy as np
from config import config

app = Flask(__name__)
app.config.from_object(config['default'])

# 解决跨域问题
CORS(app, 
     origins=['http://localhost:5000', 'http://127.0.0.1:5000', '*'],
     methods=['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# 添加额外的响应头
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

# 全局变量存储知识图谱和模型
kg = None
model = None
use_database = True  # 可以设置为False使用纯内存模式

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/kg/init', methods=['POST'])
def init_kg():
    """初始化知识图谱"""
    global kg, model
    try:
        data = request.get_json()
        use_sample = data.get('use_sample', True)
        use_db = data.get('use_database', use_database)
        
        # 创建混合知识图谱
        kg = HybridKnowledgeGraph(use_database=use_db)
        
        # 只有在数据库为空或使用内存模式时才添加示例数据
        if use_sample:
            current_triple_count = kg.get_triple_count()
            if current_triple_count == 0:  # 数据库为空时才添加示例数据
                from models.kg_data import KGDataset
                sample_kg = KGDataset.create_sample_dataset()
                
                # 将示例数据添加到混合知识图谱
                for triple in sample_kg.triples:
                    kg.add_triple(triple[0], triple[1], triple[2])
                print(f"[INFO] 添加了 {len(sample_kg.triples)} 个示例三元组")
            else:
                print(f"[INFO] 数据库已有 {current_triple_count} 个三元组，跳过示例数据添加")
        
        # 初始化模型
        model = HybridTransE(kg, embedding_dim=50, epochs=50)
        
        # 获取数据库状态
        db_status = kg.get_database_statistics()
        
        return jsonify({
            'status': 'success',
            'message': '知识图谱初始化成功',
            'entity_count': kg.get_entity_count(),
            'relation_count': kg.get_relation_count(),
            'triple_count': kg.get_triple_count(),
            'database_status': db_status
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/train', methods=['POST'])
def train_model():
    """训练模型"""
    global model
    try:
        if model is None:
            return jsonify({'status': 'error', 'message': '请先初始化知识图谱'})
        
        data = request.get_json()
        epochs = data.get('epochs', 50)
        learning_rate = data.get('learning_rate', 0.01)
        
        model.epochs = epochs
        model.learning_rate = learning_rate
        model.train()
        
        return jsonify({'status': 'success', 'message': '模型训练完成'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/info', methods=['GET'])
def get_kg_info():
    """获取知识图谱信息"""
    global kg
    if kg is None:
        return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
    
    return jsonify({
        'status': 'success',
        'entities': list(kg.entities),
        'relations': list(kg.relations),
        'triples': kg.triples,
        'entity_count': kg.get_entity_count(),
        'relation_count': kg.get_relation_count(),
        'triple_count': kg.get_triple_count()
    })

@app.route('/api/kg/complete', methods=['POST'])
def complete_triple():
    """补全三元组"""
    global model
    try:
        if model is None:
            return jsonify({'status': 'error', 'message': '请先训练模型'})
        
        data = request.get_json()
        head = data.get('head')
        relation = data.get('relation')
        tail = data.get('tail')
        top_k = data.get('top_k', 5)
        
        results = model.complete_triple(head, relation, tail, top_k)
        
        return jsonify({
            'status': 'success',
            'results': [{'entity': entity, 'score': float(score)} for entity, score in results]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/add_triple', methods=['POST'])
def add_triple():
    """添加三元组"""
    global kg, model
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        data = request.get_json()
        head = data.get('head')
        relation = data.get('relation')
        tail = data.get('tail')
        
        if not all([head, relation, tail]):
            return jsonify({'status': 'error', 'message': '请提供完整的三元组'})
        
        kg.add_triple(head, relation, tail)
        kg.build_mappings()
        
        # 如果模型已存在，需要重新初始化以同步嵌入向量
        if model is not None:
            model._initialize_embeddings()
        
        return jsonify({'status': 'success', 'message': '三元组添加成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/predict', methods=['POST'])
def predict_links():
    """预测缺失链接"""
    global model
    try:
        if model is None:
            return jsonify({'status': 'error', 'message': '请先训练模型'})
        
        data = request.get_json()
        entity = data.get('entity')
        top_k = data.get('top_k', 10)
        
        if not entity:
            return jsonify({'status': 'error', 'message': '请提供实体名称'})
        
        results = model.predict_missing_links(entity, top_k)
        
        return jsonify({
            'status': 'success',
            'results': [{'head': head, 'relation': relation, 'tail': tail, 'score': float(score)} 
                       for head, relation, tail, score in results]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/database/status', methods=['GET'])
def database_status():
    """获取数据库状态"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        db_stats = kg.get_database_statistics()
        
        return jsonify({
            'status': 'success',
            'database': db_stats,
            'memory_stats': {
                'entity_count': kg.get_entity_count(),
                'relation_count': kg.get_relation_count(),
                'triple_count': kg.get_triple_count()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/database/sync', methods=['POST'])
def sync_to_database():
    """同步内存数据到数据库"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        if not kg.use_database:
            return jsonify({'status': 'error', 'message': '当前使用内存模式'})
        
        success = kg.save_to_database()
        
        if success:
            return jsonify({'status': 'success', 'message': '数据已同步到数据库'})
        else:
            return jsonify({'status': 'error', 'message': '同步到数据库失败'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/database/load', methods=['POST'])
def load_from_database():
    """从数据库重新加载知识图谱"""
    global kg, model
    try:
        data = request.get_json()
        use_db = data.get('use_database', use_database)
        
        # 重新创建知识图谱
        kg = HybridKnowledgeGraph(use_database=use_db)
        
        # 重新创建模型
        if kg:
            model = HybridTransE(kg, embedding_dim=50, epochs=50)
        
        return jsonify({
            'status': 'success',
            'message': '已从数据库重新加载',
            'entity_count': kg.get_entity_count(),
            'relation_count': kg.get_relation_count(),
            'triple_count': kg.get_triple_count(),
            'database_status': kg.get_database_statistics()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        print("\n[INFO] 正在关闭应用...")
    finally:
        # 清理数据库连接
        from models.database import close_database
        close_database()
        print("[INFO] 应用已安全关闭")
