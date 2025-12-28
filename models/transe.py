import numpy as np
import random
from typing import List, Tuple
from .kg_data import KnowledgeGraph

class TransE:
    """TransE算法实现"""
    
    def __init__(self, kg: KnowledgeGraph, embedding_dim: int = 100, margin: float = 1.0, 
                 learning_rate: float = 0.01, epochs: int = 100):
        self.kg = kg
        self.embedding_dim = embedding_dim
        self.margin = margin
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        # 确保知识图谱有映射
        if not hasattr(kg, 'entity2id') or len(kg.entity2id) == 0:
            kg.build_mappings()
        
        # 初始化实体和关系的嵌入向量
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """初始化或更新嵌入向量"""
        current_entity_count = len(self.kg.entities)
        current_relation_count = len(self.kg.relations)
        
        # 初始化实体嵌入向量
        if not hasattr(self, 'entity_embeddings'):
            self.entity_embeddings = np.random.normal(0, 1, (current_entity_count, self.embedding_dim))
        else:
            # 如果实体数量增加，扩展嵌入向量
            old_entity_count = self.entity_embeddings.shape[0]
            if current_entity_count > old_entity_count:
                new_embeddings = np.random.normal(0, 1, (current_entity_count - old_entity_count, self.embedding_dim))
                self.entity_embeddings = np.vstack([self.entity_embeddings, new_embeddings])
        
        # 初始化关系嵌入向量
        if not hasattr(self, 'relation_embeddings'):
            self.relation_embeddings = np.random.normal(0, 1, (current_relation_count, self.embedding_dim))
        else:
            # 如果关系数量增加，扩展嵌入向量
            old_relation_count = self.relation_embeddings.shape[0]
            if current_relation_count > old_relation_count:
                new_embeddings = np.random.normal(0, 1, (current_relation_count - old_relation_count, self.embedding_dim))
                self.relation_embeddings = np.vstack([self.relation_embeddings, new_embeddings])
        
        # 归一化关系嵌入向量
        for i in range(min(current_relation_count, self.relation_embeddings.shape[0])):
            norm = np.linalg.norm(self.relation_embeddings[i])
            if norm > 0:
                self.relation_embeddings[i] /= norm
    
    def check_embeddings_sync(self):
        """检查并同步嵌入向量与知识图谱"""
        if not hasattr(self, 'entity_embeddings') or not hasattr(self, 'relation_embeddings'):
            self._initialize_embeddings()
            return False
        
        entity_sync = self.entity_embeddings.shape[0] == len(self.kg.entities)
        relation_sync = self.relation_embeddings.shape[0] == len(self.kg.relations)
        
        if not entity_sync or not relation_sync:
            self._initialize_embeddings()
            return False
        
        return True
    
    def _normalize_embeddings(self):
        """归一化实体嵌入向量"""
        for i in range(len(self.kg.entities)):
            norm = np.linalg.norm(self.entity_embeddings[i])
            if norm > 0:
                self.entity_embeddings[i] /= norm
    
    def _get_negative_sample(self, head_id: int, relation_id: int, tail_id: int) -> Tuple[int, int, int]:
        """生成负样本"""
        neg_head, neg_tail = head_id, tail_id
        
        # 随机替换头实体或尾实体
        if random.random() < 0.5:
            # 替换头实体
            neg_head = random.randint(0, len(self.kg.entities) - 1)
            while (neg_head, relation_id, tail_id) in [(h, r, t) for h, r, t in 
                                                      [(self.kg.entity2id[h], self.kg.relation2id[r], self.kg.entity2id[t]) 
                                                       for h, r, t in self.kg.triples]]:
                neg_head = random.randint(0, len(self.kg.entities) - 1)
        else:
            # 替换尾实体
            neg_tail = random.randint(0, len(self.kg.entities) - 1)
            while (head_id, relation_id, neg_tail) in [(h, r, t) for h, r, t in 
                                                      [(self.kg.entity2id[h], self.kg.relation2id[r], self.kg.entity2id[t]) 
                                                       for h, r, t in self.kg.triples]]:
                neg_tail = random.randint(0, len(self.kg.entities) - 1)
        
        return neg_head, relation_id, neg_tail
    
    def _calculate_loss(self, pos_triple: Tuple[int, int, int], 
                       neg_triple: Tuple[int, int, int]) -> float:
        """计算损失函数"""
        h_pos, r_pos, t_pos = pos_triple
        h_neg, r_neg, t_neg = neg_triple
        
        # 正样本距离
        pos_dist = np.linalg.norm(
            self.entity_embeddings[h_pos] + self.relation_embeddings[r_pos] - self.entity_embeddings[t_pos]
        )
        
        # 负样本距离
        neg_dist = np.linalg.norm(
            self.entity_embeddings[h_neg] + self.relation_embeddings[r_neg] - self.entity_embeddings[t_neg]
        )
        
        # Hinge loss
        loss = max(0, pos_dist - neg_dist + self.margin)
        return loss
    
    def train(self):
        """训练模型"""
        # 确保嵌入向量与知识图谱同步
        self.check_embeddings_sync()
        
        print(f"开始训练TransE模型，实体数: {len(self.kg.entities)}, 关系数: {len(self.kg.relations)}")
        print(f"训练轮数: {self.epochs}, 学习率: {self.learning_rate}")
        
        for epoch in range(self.epochs):
            total_loss = 0
            # 随机打乱训练数据
            triples_ids = [(self.kg.entity2id[h], self.kg.relation2id[r], self.kg.entity2id[t]) 
                          for h, r, t in self.kg.triples]
            random.shuffle(triples_ids)
            
            for head_id, relation_id, tail_id in triples_ids:
                # 获取负样本
                neg_head, neg_relation, neg_tail = self._get_negative_sample(head_id, relation_id, tail_id)
                
                # 计算损失
                loss = self._calculate_loss((head_id, relation_id, tail_id), 
                                          (neg_head, neg_relation, neg_tail))
                total_loss += loss
                
                if loss > 0:
                    # 计算梯度并更新参数
                    pos_head_emb = self.entity_embeddings[head_id]
                    pos_rel_emb = self.relation_embeddings[relation_id]
                    pos_tail_emb = self.entity_embeddings[tail_id]
                    
                    neg_head_emb = self.entity_embeddings[neg_head]
                    neg_tail_emb = self.entity_embeddings[neg_tail]
                    
                    # 计算梯度
                    pos_diff = pos_head_emb + pos_rel_emb - pos_tail_emb
                    neg_diff = neg_head_emb + pos_rel_emb - neg_tail_emb
                    
                    # 更新嵌入向量
                    if np.linalg.norm(pos_diff) > 0:
                        pos_diff_norm = pos_diff / np.linalg.norm(pos_diff)
                        self.entity_embeddings[head_id] -= self.learning_rate * pos_diff_norm
                        self.relation_embeddings[relation_id] -= self.learning_rate * pos_diff_norm
                        self.entity_embeddings[tail_id] += self.learning_rate * pos_diff_norm
                    
                    if np.linalg.norm(neg_diff) > 0:
                        neg_diff_norm = neg_diff / np.linalg.norm(neg_diff)
                        self.entity_embeddings[neg_head] += self.learning_rate * neg_diff_norm
                        self.entity_embeddings[neg_tail] -= self.learning_rate * neg_diff_norm
            
            # 每10轮归一化一次
            if epoch % 10 == 0:
                self._normalize_embeddings()
                print(f"Epoch {epoch}/{self.epochs}, Loss: {total_loss:.4f}")
        
        print("训练完成！")
    
    def predict_missing_links(self, entity: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """预测缺失链接"""
        # 确保嵌入向量与知识图谱同步
        if not self.check_embeddings_sync():
            print("警告: 嵌入向量与知识图谱不同步，已重新初始化")
        
        if entity not in self.kg.entity2id:
            return []
        
        entity_id = self.kg.entity2id[entity]
        
        # 安全检查：确保索引不越界
        if entity_id >= self.entity_embeddings.shape[0]:
            print(f"错误: 实体索引 {entity_id} 超出嵌入向量范围")
            return []
        entity_emb = self.entity_embeddings[entity_id]
        scores = []
        
        # 计算与其他实体的相似度
        for other_entity, other_id in self.kg.entity2id.items():
            if other_entity != entity:
                other_emb = self.entity_embeddings[other_id]
                
                # 计算所有可能的关系得分
                for relation, rel_id in self.kg.relation2id.items():
                    rel_emb = self.relation_embeddings[rel_id]
                    
                    # 计算预测得分 (distance越小，可能性越大)
                    score = np.linalg.norm(entity_emb + rel_emb - other_emb)
                    scores.append((other_entity, relation, score))
        
        # 按得分排序并返回top_k
        scores.sort(key=lambda x: x[2])
        return [(head if head == entity else tail, rel, score) 
                for head, rel, score in scores[:top_k]]
    
    def complete_triple(self, head: str = None, relation: str = None, tail: str = None, 
                       top_k: int = 5) -> List[Tuple[str, float]]:
        """补全三元组（预测缺失的实体）"""
        # 确保嵌入向量与知识图谱同步
        if not self.check_embeddings_sync():
            print("警告: 嵌入向量与知识图谱不同步，已重新初始化")
        
        results = []
        
        if head and relation and not tail:  # 预测尾实体
            if head in self.kg.entity2id and relation in self.kg.relation2id:
                head_id = self.kg.entity2id[head]
                rel_id = self.kg.relation2id[relation]
                
                # 安全检查
                if (head_id >= self.entity_embeddings.shape[0] or 
                    rel_id >= self.relation_embeddings.shape[0]):
                    print(f"错误: 索引超出范围 - head_id: {head_id}, rel_id: {rel_id}")
                    return results
                
                head_emb = self.entity_embeddings[head_id]
                rel_emb = self.relation_embeddings[rel_id]
                
                for entity, entity_id in self.kg.entity2id.items():
                    if entity != head and entity_id < self.entity_embeddings.shape[0]:
                        entity_emb = self.entity_embeddings[entity_id]
                        score = np.linalg.norm(head_emb + rel_emb - entity_emb)
                        results.append((entity, score))
        
        elif not head and relation and tail:  # 预测头实体
            if tail in self.kg.entity2id and relation in self.kg.relation2id:
                tail_id = self.kg.entity2id[tail]
                rel_id = self.kg.relation2id[relation]
                
                # 安全检查
                if (tail_id >= self.entity_embeddings.shape[0] or 
                    rel_id >= self.relation_embeddings.shape[0]):
                    print(f"错误: 索引超出范围 - tail_id: {tail_id}, rel_id: {rel_id}")
                    return results
                
                tail_emb = self.entity_embeddings[tail_id]
                rel_emb = self.relation_embeddings[rel_id]
                
                for entity, entity_id in self.kg.entity2id.items():
                    if entity != tail and entity_id < self.entity_embeddings.shape[0]:
                        entity_emb = self.entity_embeddings[entity_id]
                        score = np.linalg.norm(entity_emb + rel_emb - tail_emb)
                        results.append((entity, score))
        
        # 按得分排序并返回top_k
        results.sort(key=lambda x: x[1])
        return results[:top_k]
    
    def save_embeddings(self, filepath: str):
        """保存嵌入向量"""
        np.savez(filepath, 
                entity_embeddings=self.entity_embeddings,
                relation_embeddings=self.relation_embeddings)
    
    def load_embeddings(self, filepath: str):
        """加载嵌入向量"""
        data = np.load(filepath)
        self.entity_embeddings = data['entity_embeddings']
        self.relation_embeddings = data['relation_embeddings']