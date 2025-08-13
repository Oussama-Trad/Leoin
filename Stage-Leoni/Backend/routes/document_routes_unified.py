#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes Document unifiées pour la synchronisation avec l'interface admin
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from models.DocumentRequest import DocumentRequest
from datetime import datetime

document_routes = Blueprint('document_routes', __name__)

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

@document_routes.route('/api/documents/request', methods=['POST', 'OPTIONS'])
@token_required
def create_document_request(current_user_id, current_user_email):
    """Créer une nouvelle demande de document"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        
        # Validation des données
        if not data.get('documentType'):
            return jsonify({
                'success': False,
                'message': 'Le type de document est requis'
            }), 400
        
        # Créer la demande
        doc_request = DocumentRequest()
        result = doc_request.create_request(
            user_id=current_user_id,
            document_type=data['documentType'],
            description=data.get('description'),
            urgency=data.get('urgency', 'normale')
        )
        
        doc_request.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'requestId': result['request_id'],
                'message': 'Demande créée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création de la demande: {str(e)}'
        }), 500

@document_routes.route('/api/documents/user', methods=['GET', 'OPTIONS'])
@token_required
def get_user_documents(current_user_id, current_user_email):
    """Récupérer les demandes de documents d'un utilisateur"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        doc_request = DocumentRequest()
        result = doc_request.get_user_requests(current_user_id)
        doc_request.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'documents': result['requests'],
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
            'message': f'Erreur lors de la récupération des demandes: {str(e)}'
        }), 500

@document_routes.route('/api/documents/delete/<request_id>', methods=['DELETE'])
@token_required
def delete_document_request(current_user_id, current_user_email, request_id):
    """Supprimer une demande de document"""
    try:
        doc_request = DocumentRequest()
        result = doc_request.delete_request(request_id, current_user_id)
        doc_request.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        }), 500

# Routes pour l'interface admin
@document_routes.route('/api/admin/documents/requests', methods=['GET'])
def get_admin_document_requests():
    """Récupérer les demandes de documents pour un admin"""
    try:
        admin_username = request.args.get('admin_username')
        admin_role = request.args.get('admin_role', 'ADMIN')
        status_filter = request.args.get('status')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        admin = db.admins.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Récupérer les demandes avec filtrage
        doc_request = DocumentRequest()
        result = doc_request.get_admin_requests(
            admin_department=admin.get('department'),
            admin_location=admin.get('location'),
            admin_role=admin_role,
            status_filter=status_filter
        )
        
        doc_request.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'requests': result['requests'],
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
            'message': f'Erreur lors de la récupération des demandes: {str(e)}'
        }), 500

@document_routes.route('/api/admin/documents/request/<request_id>/process', methods=['PUT'])
def process_document_request(request_id):
    """Traiter une demande de document (admin)"""
    try:
        data = request.get_json()
        
        new_status = data.get('newStatus')
        admin_username = data.get('admin_username')
        admin_role = data.get('admin_role', 'ADMIN')
        comment = data.get('comment')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Nouveau statut requis'}), 400
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client.LeoniApp
        
        admin = db.admins.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Mettre à jour la demande
        doc_request = DocumentRequest()
        result = doc_request.update_request_status(
            request_id=request_id,
            new_status=new_status,
            admin_id=str(admin['_id']),
            admin_name=admin.get('username', 'Admin'),
            comment=comment
        )
        
        doc_request.close_connection()
        client.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du traitement de la demande: {str(e)}'
        }), 500

@document_routes.route('/api/admin/documents/statistics', methods=['GET'])
def get_admin_document_statistics():
    """Récupérer les statistiques des demandes pour un admin"""
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
        doc_request = DocumentRequest()
        result = doc_request.get_statistics(
            admin_department=admin.get('department'),
            admin_location=admin.get('location'),
            admin_role=admin_role
        )
        
        doc_request.close_connection()
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