#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes Chat unifiées pour la synchronisation avec l'interface admin
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from models.Chat import Chat
from models.ChatMessage import ChatMessage
from datetime import datetime

chat_routes = Blueprint('chat_routes', __name__)

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

@chat_routes.route('/api/chats/create', methods=['POST', 'OPTIONS'])
@token_required
def create_conversation(current_user_id, current_user_email):
    """Créer une nouvelle conversation avec filtrage strict"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['targetDepartment', 'targetLocation', 'subject']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Le champ {field} est requis'
                }), 400
        
        # Récupérer les informations utilisateur
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        user = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
        
        # Créer la conversation
        chat = Chat()
        result = chat.create_conversation(
            user_id=current_user_id,
            user_name=user_name,
            user_email=current_user_email,
            user_department=user.get('department', ''),
            user_location=user.get('location', ''),
            target_department=data['targetDepartment'],
            target_location=data['targetLocation'],
            subject=data['subject'],
            initial_message=data.get('initialMessage')
        )
        
        chat.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'conversationId': result['conversation_id'],
                'message': 'Conversation créée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }), 500

@chat_routes.route('/api/chats', methods=['GET', 'OPTIONS'])
@token_required
def get_user_conversations(current_user_id, current_user_email):
    """Récupérer les conversations d'un utilisateur"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        chat = Chat()
        result = chat.get_user_conversations(current_user_id)
        chat.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['conversations'],
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
            'message': f'Erreur lors de la récupération: {str(e)}'
        }), 500

@chat_routes.route('/api/chat/conversation/<conversation_id>/messages', methods=['GET'])
@token_required
def get_conversation_messages(current_user_id, current_user_email, conversation_id):
    """Récupérer les messages d'une conversation"""
    try:
        # Vérifier que la conversation appartient à l'utilisateur
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        conversation = db.chats.find_one({
            '_id': ObjectId(conversation_id),
            'userId': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Récupérer les messages
        chat_message = ChatMessage()
        messages = chat_message.get_conversation_messages(conversation_id)
        
        # Marquer les messages comme lus
        chat_message.mark_messages_as_read(conversation_id, current_user_id, 'user')
        
        chat_message.close_connection()
        client.close()
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des messages: {str(e)}'
        }), 500

@chat_routes.route('/api/chat/conversation/<conversation_id>/message', methods=['POST'])
@token_required
def send_message(current_user_id, current_user_email, conversation_id):
    """Envoyer un message dans une conversation"""
    try:
        data = request.get_json()
        
        if not data.get('content', '').strip():
            return jsonify({'success': False, 'message': 'Le message ne peut pas être vide'}), 400
        
        # Vérifier que la conversation appartient à l'utilisateur
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        conversation = db.chats.find_one({
            '_id': ObjectId(conversation_id),
            'userId': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Récupérer l'utilisateur
        user = db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
        
        # Créer le message
        chat_message = ChatMessage()
        result = chat_message.create_message(
            chat_ref=conversation_id,
            sender_id=current_user_id,
            sender_name=user_name,
            sender_email=current_user_email,
            sender_type='user',
            message=data['content'].strip()
        )
        
        chat_message.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'messageId': result['message_id'],
                'message': 'Message envoyé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi du message: {str(e)}'
        }), 500

# Routes pour l'interface admin
@chat_routes.route('/api/admin/chat/conversations', methods=['GET', 'OPTIONS'])
def get_admin_conversations():
    """Récupérer les conversations pour un admin avec filtrage strict"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Récupérer les paramètres admin
        admin_username = request.args.get('admin_username')
        admin_role = request.args.get('admin_role', 'ADMIN')
        status_filter = request.args.get('status')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin depuis la base
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        admin = db.admins.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Récupérer les conversations avec filtrage
        chat = Chat()
        result = chat.get_admin_conversations(
            admin_department=admin.get('department'),
            admin_location=admin.get('location'),
            admin_role=admin_role,
            status_filter=status_filter
        )
        
        chat.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'conversations': result['conversations'],
                'count': result['count'],
                'adminRole': admin_role,
                'filter': result['filter']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération: {str(e)}'
        }), 500

@chat_routes.route('/api/admin/chat/conversation/<conversation_id>/reply', methods=['POST'])
def admin_reply_to_conversation(conversation_id):
    """Admin répond à une conversation"""
    try:
        data = request.get_json()
        
        if not data.get('content', '').strip():
            return jsonify({'success': False, 'message': 'Le message ne peut pas être vide'}), 400
        
        admin_username = data.get('admin_username')
        admin_role = data.get('admin_role', 'ADMIN')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        admin = db.admins.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Vérifier que la conversation existe et que l'admin a les droits
        conversation = db.chats.find_one({'_id': ObjectId(conversation_id)})
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Vérifier les permissions
        if admin_role != 'SUPERADMIN':
            if (conversation.get('targetDepartment') != admin.get('department') or 
                conversation.get('targetLocation') != admin.get('location')):
                return jsonify({'success': False, 'message': 'Droits insuffisants'}), 403
        
        # Créer le message de réponse
        chat_message = ChatMessage()
        result = chat_message.create_message(
            chat_ref=conversation_id,
            sender_id=str(admin['_id']),
            sender_name=admin.get('username', 'Admin'),
            sender_email=admin.get('email', ''),
            sender_type='admin',
            message=data['content'].strip()
        )
        
        # Mettre à jour le statut de la conversation
        if result['success']:
            chat = Chat()
            chat.update_conversation_status(
                conversation_id=conversation_id,
                new_status='in_progress',
                admin_id=str(admin['_id']),
                admin_name=admin.get('username', 'Admin')
            )
            chat.close_connection()
        
        chat_message.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'messageId': result['message_id'],
                'message': 'Réponse envoyée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi de la réponse: {str(e)}'
        }), 500

@chat_routes.route('/api/admin/chat/statistics', methods=['GET'])
def get_admin_chat_statistics():
    """Récupérer les statistiques des conversations pour un admin"""
    try:
        admin_username = request.args.get('admin_username')
        admin_role = request.args.get('admin_role', 'ADMIN')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        admin = db.admins.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Récupérer les statistiques
        chat = Chat()
        result = chat.get_statistics(
            admin_department=admin.get('department'),
            admin_location=admin.get('location'),
            admin_role=admin_role
        )
        
        chat.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'statistics': result['statistics'],
                'adminRole': admin_role,
                'adminUsername': admin_username
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la récupération des statistiques: {str(e)}'
        }), 500