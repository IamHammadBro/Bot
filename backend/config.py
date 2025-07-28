#!/usr/bin/env python3
"""
Production Configuration for Flask Backend
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FRONTEND_URL = "http://localhost:3000"
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FRONTEND_URL = os.environ.get('FRONTEND_URL', '*')

class RenderConfig(ProductionConfig):
    """Render.com specific configuration"""
    PORT = int(os.environ.get('PORT', 10000))

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'render': RenderConfig,
    'default': DevelopmentConfig
}
