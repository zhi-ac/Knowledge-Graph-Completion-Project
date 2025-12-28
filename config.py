#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置文件
"""

import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = '123456'
    DB_NAME = 'kgc_project'
    DB_CHARSET = 'utf8mb4'
    
    # 数据库连接URL
    DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"
    
    # 应用配置
    DEBUG = True
    JSON_AS_ASCII = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}