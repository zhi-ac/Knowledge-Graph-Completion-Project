from flask import Flask, render_template, request, jsonify
import os
import json
from models.kg_data import KnowledgeGraph, KGDataset
from models.transe import TransE
import numpy as np

app = Flask(__name__)

# 全局变量存储知识图谱和模型
kg = None
model = None

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
        
        if use_sample:
            kg = KGDataset.create_sample_dataset()
        else:
            # 从文件加载或创建新的知识图谱
            kg = KnowledgeGraph()
        
        # 初始化模型
        model = TransE(kg, embedding_dim=50, epochs=50)
        
        return jsonify({
            'status': 'success',
            'message': '知识图谱初始化成功',
            'entity_count': kg.get_entity_count(),
            'relation_count': kg.get_relation_count(),
            'triple_count': kg.get_triple_count()
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

if __name__ == '__main__':
    app.run(debug=True)
