from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
import datetime
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

@app.route('/entity-management')
def entity_management():
    """实体管理页面"""
    return render_template('entity_management_simple.html')

@app.route('/analysis')
def analysis():
    """补全分析页面"""
    return render_template('analysis.html')

@app.route('/relation-management')
def relation_management():
    """关系管理页面"""
    return render_template('relation_management.html')

@app.route('/triple-management')
def triple_management():
    """三元组管理页面"""
    return render_template('triple_management.html')

@app.route('/model-management')
def model_management():
    """模型训练管理页面"""
    return render_template('model_management.html')

@app.route('/data-management')
def data_management():
    """数据管理页面"""
    return render_template('data_management.html')

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

@app.route('/api/kg/delete_triple', methods=['POST'])
def delete_triple():
    """删除三元组"""
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
        
        # 查找并删除三元组
        triple_to_delete = (head, relation, tail)
        if triple_to_delete in kg.triples:
            kg.triples.remove(triple_to_delete)
            kg.build_mappings()
            
            # 如果模型已存在，需要重新初始化
            if model is not None:
                model._initialize_embeddings()
            
            return jsonify({'status': 'success', 'message': '三元组删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '三元组不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/search_triples', methods=['POST'])
def search_triples():
    """搜索三元组"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        data = request.get_json()
        query = data.get('query', '').lower()
        search_type = data.get('type', 'all')  # 'head', 'relation', 'tail', 'all'
        
        if not query:
            return jsonify({'status': 'error', 'message': '请提供搜索关键词'})
        
        results = []
        for triple in kg.triples:
            head, relation, tail = triple
            match = False
            
            if search_type == 'head' or search_type == 'all':
                if query in head.lower():
                    match = True
            if search_type == 'relation' or search_type == 'all':
                if query in relation.lower():
                    match = True
            if search_type == 'tail' or search_type == 'all':
                if query in tail.lower():
                    match = True
            
            if match:
                results.append({
                    'head': head,
                    'relation': relation,
                    'tail': tail
                })
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results)
        })
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

# 实体和关系管理
@app.route('/api/kg/entities', methods=['GET'])
def get_entities():
    """获取所有实体"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        entities = list(kg.entities)
        entity_info = []
        
        # 如果使用数据库，获取详细信息
        if kg.use_database and kg.db_available:
            try:
                from models.database import KGDatabase
                db_entities = KGDatabase.get_all_entities_with_details()
                
                for db_entity in db_entities:
                    # 统计每个实体相关的三元组数量
                    entity_name = db_entity['name']
                    head_count = sum(1 for t in kg.triples if t[0] == entity_name)
                    tail_count = sum(1 for t in kg.triples if t[2] == entity_name)
                    
                    entity_info.append({
                        'name': entity_name,
                        'entity_type': db_entity.get('entity_type', 'unknown'),
                        'category': db_entity.get('category', ''),
                        'head_count': head_count,
                        'tail_count': tail_count,
                        'total_count': head_count + tail_count,
                        **db_entity
                    })
            except Exception as db_error:
                print(f"[ERROR] 从数据库获取实体详情失败: {db_error}")
                # 降级到基础信息
                for entity in entities:
                    head_count = sum(1 for t in kg.triples if t[0] == entity)
                    tail_count = sum(1 for t in kg.triples if t[2] == entity)
                    
                    entity_info.append({
                        'name': entity,
                        'entity_type': 'unknown',
                        'category': '',
                        'head_count': head_count,
                        'tail_count': tail_count,
                        'total_count': head_count + tail_count
                    })
        else:
            # 内存模式，只提供基础信息
            for entity in entities:
                head_count = sum(1 for t in kg.triples if t[0] == entity)
                tail_count = sum(1 for t in kg.triples if t[2] == entity)
                
                entity_info.append({
                    'name': entity,
                    'entity_type': 'unknown',
                    'category': '',
                    'head_count': head_count,
                    'tail_count': tail_count,
                    'total_count': head_count + tail_count
                })
        
        return jsonify({
            'status': 'success',
            'entities': entity_info,
            'count': len(entities)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/relations', methods=['GET'])
def get_relations():
    """获取所有关系"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        relations = list(kg.relations)
        relation_info = []
        
        for relation in relations:
            # 统计每个关系相关的三元组数量
            count = sum(1 for t in kg.triples if t[1] == relation)
            
            relation_info.append({
                'name': relation,
                'count': count
            })
        
        return jsonify({
            'status': 'success',
            'relations': relation_info,
            'count': len(relations)
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

@app.route('/api/kg/entity/<entity_name>', methods=['GET'])
def get_entity_detail(entity_name):
    """获取单个实体的详细信息"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        # 基础统计信息
        head_count = sum(1 for t in kg.triples if t[0] == entity_name)
        tail_count = sum(1 for t in kg.triples if t[2] == entity_name)
        
        entity_detail = {
            'name': entity_name,
            'entity_type': 'unknown',
            'category': '',
            'head_count': head_count,
            'tail_count': tail_count,
            'total_count': head_count + tail_count
        }
        
        # 如果使用数据库，获取详细信息
        if kg.use_database and kg.db_available:
            try:
                from models.database import KGDatabase
                db_details = KGDatabase.get_entity_details(entity_name)
                if db_details:
                    entity_detail.update(db_details)
            except Exception as db_error:
                print(f"[ERROR] 从数据库获取实体详情失败: {db_error}")
        
        return jsonify({
            'status': 'success',
            'entity': entity_detail
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/entity', methods=['POST'])
def add_entity():
    """添加实体"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        data = request.get_json()
        name = data.get('name')
        entity_type = data.get('entity_type')
        category = data.get('category')
        attributes = data.get('attributes', {})
        image_url = data.get('image_url')  # 获取图片URL
        
        if not name or not entity_type:
            return jsonify({'status': 'error', 'message': '请提供实体名称和类型'})
        
        if kg.use_database and kg.db_available:
            from models.database import KGDatabase
            entity_id = KGDatabase.add_entity(
                name=name,
                entity_type=entity_type,
                category=category,
                attributes=attributes,
                image_url=image_url
            )
            if entity_id:
                # 重新加载知识图谱
                kg._load_from_database()
                return jsonify({'status': 'success', 'message': '实体添加成功'})
            else:
                return jsonify({'status': 'error', 'message': '实体添加失败'})
        else:
            # 内存模式，直接添加到内存
            kg.entities.add(name)
            kg.build_mappings()
            return jsonify({'status': 'success', 'message': '实体添加成功（内存模式）'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/entity/<entity_name>', methods=['PUT'])
def update_entity(entity_name):
    """更新实体"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        data = request.get_json()
        new_name = data.get('name')
        entity_type = data.get('entity_type')
        category = data.get('category')
        attributes = data.get('attributes', {})
        image_url = data.get('image_url')  # 获取图片URL
        
        if not new_name or not entity_type:
            return jsonify({'status': 'error', 'message': '请提供实体名称和类型'})
        
        if kg.use_database and kg.db_available:
            from models.database import KGDatabase
            # 更新数据库中的实体
            entity_id = KGDatabase.add_entity(
                name=new_name,
                entity_type=entity_type,
                category=category,
                attributes=attributes,
                image_url=image_url
            )
            
            # 如果名称改变，需要更新所有相关的三元组
            if new_name != entity_name:
                # 删除旧实体相关的三元组
                kg.triples = [(new_name if h == entity_name else h, r, new_name if t == entity_name else t) 
                             for h, r, t in kg.triples]
                kg.build_mappings()
                
                # 重新初始化模型
                global model
                if model:
                    model._initialize_embeddings()
            
            kg._load_from_database()
            return jsonify({'status': 'success', 'message': '实体更新成功'})
        else:
            # 内存模式更新
            if entity_name in kg.entities:
                kg.entities.remove(entity_name)
            kg.entities.add(new_name)
            kg.build_mappings()
            return jsonify({'status': 'success', 'message': '实体更新成功（内存模式）'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/entity/<entity_name>', methods=['DELETE'])
def delete_entity(entity_name):
    """删除实体"""
    global kg, model
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        if kg.use_database and kg.db_available:
            from models.database import KGDatabase, Entity, Triple, session
            
            # 查找实体ID
            entity = session.query(Entity).filter_by(name=entity_name).first()
            if entity:
                # 删除相关的三元组
                session.query(Triple).filter(
                    (Triple.head_entity_id == entity.id) | 
                    (Triple.tail_entity_id == entity.id)
                ).delete()
                
                # 删除实体
                session.delete(entity)
                session.commit()
                
                # 重新加载知识图谱
                kg._load_from_database()
                
                # 重新初始化模型
                if model:
                    model._initialize_embeddings()
                
                return jsonify({'status': 'success', 'message': '实体删除成功'})
            else:
                return jsonify({'status': 'error', 'message': '实体不存在'})
        else:
            # 内存模式删除
            if entity_name in kg.entities:
                kg.entities.remove(entity_name)
                # 删除相关的三元组
                kg.triples = [(h, r, t) for h, r, t in kg.triples if h != entity_name and t != entity_name]
                kg.build_mappings()
                
                # 重新初始化模型
                if model:
                    model._initialize_embeddings()
                
                return jsonify({'status': 'success', 'message': '实体删除成功（内存模式）'})
            else:
                return jsonify({'status': 'error', 'message': '实体不存在'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/statistics', methods=['GET'])
def get_statistics():
    """获取知识图谱统计信息"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        # 基本统计
        entity_count = kg.get_entity_count()
        relation_count = kg.get_relation_count()
        triple_count = kg.get_triple_count()
        
        # 实体统计
        entity_stats = {}
        for triple in kg.triples:
            head, relation, tail = triple
            
            # 统计头实体
            if head not in entity_stats:
                entity_stats[head] = {'as_head': 0, 'as_tail': 0}
            entity_stats[head]['as_head'] += 1
            
            # 统计尾实体
            if tail not in entity_stats:
                entity_stats[tail] = {'as_head': 0, 'as_tail': 0}
            entity_stats[tail]['as_tail'] += 1
        
        # 关系统计
        relation_stats = {}
        for triple in kg.triples:
            relation = triple[1]
            if relation not in relation_stats:
                relation_stats[relation] = 0
            relation_stats[relation] += 1
        
        # 找出最活跃的实体和关系
        top_entities = sorted(
            [(entity, stats['as_head'] + stats['as_tail']) 
             for entity, stats in entity_stats.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        top_relations = sorted(
            [(relation, count) for relation, count in relation_stats.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return jsonify({
            'status': 'success',
            'basic_stats': {
                'entity_count': entity_count,
                'relation_count': relation_count,
                'triple_count': triple_count
            },
            'top_entities': top_entities,
            'top_relations': top_relations,
            'entity_stats': entity_stats,
            'relation_stats': relation_stats
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

# 数据管理功能
@app.route('/api/kg/export', methods=['GET'])
def export_kg():
    """导出知识图谱数据"""
    global kg
    try:
        if kg is None:
            return jsonify({'status': 'error', 'message': '知识图谱未初始化'})
        
        export_data = {
            'entities': list(kg.entities),
            'relations': list(kg.relations),
            'triples': kg.triples,
            'entity_count': kg.get_entity_count(),
            'relation_count': kg.get_relation_count(),
            'triple_count': kg.get_triple_count(),
            'export_time': str(datetime.datetime.now())
        }
        
        return jsonify({
            'status': 'success',
            'data': export_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/kg/import', methods=['POST'])
def import_kg():
    """导入知识图谱数据"""
    global kg, model
    try:
        data = request.get_json()
        import_data = data.get('data', {})
        
        if not import_data:
            return jsonify({'status': 'error', 'message': '导入数据为空'})
        
        # 创建新的知识图谱或清空现有图谱
        use_db = data.get('use_database', use_database)
        kg = HybridKnowledgeGraph(use_database=use_db)
        
        # 导入数据
        imported_entities = import_data.get('entities', [])
        imported_relations = import_data.get('relations', [])
        imported_triples = import_data.get('triples', [])
        
        # 添加三元组（会自动添加实体和关系）
        for triple in imported_triples:
            if len(triple) >= 3:
                kg.add_triple(triple[0], triple[1], triple[2])
        
        # 重建映射
        kg.build_mappings()
        
        # 重新初始化模型
        model = HybridTransE(kg, embedding_dim=50, epochs=50)
        
        return jsonify({
            'status': 'success',
            'message': f'成功导入 {len(imported_triples)} 个三元组',
            'entity_count': kg.get_entity_count(),
            'relation_count': kg.get_relation_count(),
            'triple_count': kg.get_triple_count()
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
