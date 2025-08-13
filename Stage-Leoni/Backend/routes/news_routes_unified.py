#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes News unifiées pour la synchronisation avec l'interface admin
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from models.News import News
from datetime import datetime

news_routes = Blueprint('news_routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(None, None, *args, **kwargs)
            
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, '123', algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_email = data.get('email', '')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        return f(current_user_id, current_user_email, *args, **kwargs)
    
    return decorated

@news_routes.route('/api/news/user', methods=['GET', 'OPTIONS'])
@token_required
def get_user_news(current_user_id, current_user_email):
    """Récupérer les actualités filtrées pour un utilisateur"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Récupérer les informations utilisateur
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        user = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        user_department = user.get('department', '')
        user_location = user.get('location', '')
        
        # Récupérer les actualités filtrées
        news = News()
        result = news.get_filtered_news_for_user(user_department, user_location)
        news.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'news': result['news'],
                'count': result['count'],
                'userInfo': result['userInfo']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des actualités: {str(e)}'
        }), 500

# Routes pour l'interface admin
@news_routes.route('/api/admin/news/create', methods=['POST', 'OPTIONS'])
def create_admin_news():
    """Créer une actualité depuis l'interface admin"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Récupérer le token admin
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token admin requis'}), 401
        
        data = request.get_json()
        
        # Validation des données
        required_fields = ['title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Le champ {field} est requis'
                }), 400
        
        # Récupérer les informations admin depuis le token ou les paramètres
        admin_id = data.get('authorId', 'admin-default')
        admin_name = data.get('authorName', 'Admin')
        
        # Créer l'actualité
        news = News()
        result = news.create_news(
            title=data['title'],
            content=data['content'],
            author_id=admin_id,
            author_name=admin_name,
            target_department=data.get('targetDepartment'),
            target_location=data.get('targetLocation'),
            category=data.get('category', 'general'),
            priority=data.get('priority', 'normal'),
            summary=data.get('summary')
        )
        
        news.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'newsId': result['news_id'],
                'message': 'Actualité créée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création de l\'actualité: {str(e)}'
        }), 500

@news_routes.route('/api/admin/news', methods=['GET'])
def get_admin_news():
    """Récupérer les actualités pour un admin"""
    try:
        admin_role = request.args.get('role', 'ADMIN')
        admin_department = request.args.get('department')
        admin_location = request.args.get('location')
        
        # Récupérer les actualités
        news = News()
        result = news.get_admin_news(
            admin_department=admin_department,
            admin_location=admin_location,
            admin_role=admin_role
        )
        
        news.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'news': result['news'],
                'count': result['count']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des actualités: {str(e)}'
        }), 500