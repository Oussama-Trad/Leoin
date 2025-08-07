"""
Routes d'administration avancées pour l'intégration Spring Boot
Ajoute les fonctionnalités manquantes pour le système de filtrage complet
"""

from flask import Flask, request, jsonify
from functools import wraps
import jwt
from bson import ObjectId
from datetime import datetime
import logging

def create_admin_routes_extended(app, db, JWT_SECRET):
    """
    Routes d'administration étendues pour l'intégration Spring Boot
    """
    
    def token_required_admin(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({'success': False, 'message': 'Token manquant'}), 401
            
            try:
                data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                current_admin = {
                    'username': data.get('username'),
                    'role': data.get('role'),
                    'department': data.get('department'),
                    'location': data.get('location'),
                    'email': data.get('email')
                }
            except jwt.ExpiredSignatureError:
                return jsonify({'success': False, 'message': 'Token expiré'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'success': False, 'message': 'Token invalide'}), 401
            
            return f(current_admin, *args, **kwargs)
        return decorated

    @app.route('/api/admin/departments-locations', methods=['GET'])
    def get_departments_locations():
        """
        Récupérer tous les départements et locations disponibles
        """
        try:
            # Récupérer les départements uniques
            departments = db.users.distinct('department', {'department': {'$ne': None}})
            departments = [dept for dept in departments if dept and dept.strip()]
            
            # Récupérer les locations uniques
            locations = db.users.distinct('location', {'location': {'$ne': None}})
            locations = [loc for loc in locations if loc and loc.strip()]
            
            return jsonify({
                'success': True,
                'departments': sorted(departments),
                'locations': sorted(locations),
                'totalDepartments': len(departments),
                'totalLocations': len(locations)
            })
            
        except Exception as e:
            app.logger.error(f"Erreur récupération départements/locations: {e}")
            return jsonify({
                'success': False, 
                'message': f'Erreur: {str(e)}'
            }), 500

    @app.route('/api/admin/employees/filtered-extended', methods=['GET'])
    @token_required_admin
    def get_filtered_employees_extended(current_admin):
        """
        Récupérer les employés filtrés selon les permissions admin
        """
        try:
            # Paramètres de filtrage
            department_filter = request.args.get('department')
            location_filter = request.args.get('location')
            role = request.args.get('role', current_admin['role'])
            
            # Construire la requête de base
            query = {}
            
            # Appliquer le filtrage selon le rôle
            if role == 'ADMIN':
                # ADMIN : seulement son département et sa location
                if current_admin['department']:
                    query['department'] = current_admin['department']
                if current_admin['location']:
                    query['location'] = current_admin['location']
            elif role == 'SUPERADMIN':
                # SUPERADMIN : peut filtrer par département/location optionnels
                if department_filter:
                    query['department'] = department_filter
                if location_filter:
                    query['location'] = location_filter
            
            # Récupérer les employés
            employees = list(db.users.find(
                query,
                {
                    '_id': 1,
                    'firstName': 1,
                    'lastName': 1,
                    'email': 1,
                    'department': 1,
                    'location': 1,
                    'employeeId': 1,
                    'phoneNumber': 1,
                    'createdAt': 1,
                    'isActive': 1
                }
            ))
            
            # Convertir ObjectId en string
            for employee in employees:
                employee['_id'] = str(employee['_id'])
                if employee.get('createdAt'):
                    employee['createdAt'] = employee['createdAt'].isoformat()
            
            return jsonify({
                'success': True,
                'employees': employees,
                'count': len(employees),
                'appliedFilters': {
                    'department': query.get('department', 'ALL'),
                    'location': query.get('location', 'ALL'),
                    'adminRole': role
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erreur récupération employés filtrés: {e}")
            return jsonify({
                'success': False, 
                'message': f'Erreur: {str(e)}'
            }), 500

    @app.route('/api/admin/documents/filtered-extended', methods=['GET'])
    @token_required_admin
    def get_filtered_document_requests_extended(current_admin):
        """
        Récupérer les demandes de documents filtrées selon les permissions admin
        """
        try:
            department_filter = request.args.get('department')
            location_filter = request.args.get('location')
            role = request.args.get('role', current_admin['role'])
            
            # Construire la requête pour les utilisateurs autorisés
            user_query = {}
            if role == 'ADMIN':
                if current_admin['department']:
                    user_query['department'] = current_admin['department']
                if current_admin['location']:
                    user_query['location'] = current_admin['location']
            elif role == 'SUPERADMIN':
                if department_filter:
                    user_query['department'] = department_filter
                if location_filter:
                    user_query['location'] = location_filter
            
            # Récupérer les IDs des utilisateurs autorisés
            if user_query:
                authorized_users = list(db.users.find(user_query, {'_id': 1}))
                authorized_user_ids = [str(user['_id']) for user in authorized_users]
            else:
                # SUPERADMIN sans filtre = tous les utilisateurs
                authorized_user_ids = None
            
            # Construire la requête pour les documents
            document_query = {}
            if authorized_user_ids is not None:
                document_query['userId'] = {'$in': authorized_user_ids}
            
            # Récupérer les demandes de documents
            documents = list(db.documents.find(
                document_query,
                {
                    '_id': 1,
                    'userId': 1,
                    'documentType': 1,
                    'status': 1,
                    'requestDate': 1,
                    'reason': 1,
                    'urgency': 1
                }
            ))
            
            # Enrichir avec les informations utilisateur
            for doc in documents:
                doc['_id'] = str(doc['_id'])
                if doc.get('requestDate'):
                    doc['requestDate'] = doc['requestDate'].isoformat()
                
                # Récupérer les infos utilisateur
                user = db.users.find_one({'_id': ObjectId(doc['userId'])}, {
                    'firstName': 1, 'lastName': 1, 'email': 1, 'department': 1, 'location': 1
                })
                if user:
                    doc['userInfo'] = {
                        'name': f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
                        'email': user.get('email'),
                        'department': user.get('department'),
                        'location': user.get('location')
                    }
            
            return jsonify({
                'success': True,
                'documents': documents,
                'count': len(documents),
                'appliedFilters': {
                    'department': user_query.get('department', 'ALL'),
                    'location': user_query.get('location', 'ALL'),
                    'adminRole': role
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erreur récupération documents filtrés: {e}")
            return jsonify({
                'success': False, 
                'message': f'Erreur: {str(e)}'
            }), 500

    @app.route('/api/admin/documents/<document_id>/status-extended', methods=['PUT'])
    @token_required_admin
    def update_document_status_extended(current_admin, document_id):
        """
        Mettre à jour le statut d'une demande de document
        """
        try:
            data = request.get_json()
            new_status = data.get('newStatus')
            
            if not new_status:
                return jsonify({'success': False, 'message': 'Nouveau statut requis'}), 400
            
            # Valider le statut
            valid_statuses = ['pending', 'approved', 'rejected', 'processing']
            if new_status.lower() not in valid_statuses:
                return jsonify({
                    'success': False, 
                    'message': f'Statut invalide. Statuts autorisés: {", ".join(valid_statuses)}'
                }), 400
            
            # Vérifier que le document existe et que l'admin a les permissions
            document = db.documents.find_one({'_id': ObjectId(document_id)})
            if not document:
                return jsonify({'success': False, 'message': 'Document non trouvé'}), 404
            
            # Vérifier les permissions admin
            if current_admin['role'] == 'ADMIN':
                user = db.users.find_one({'_id': ObjectId(document['userId'])})
                if not user:
                    return jsonify({'success': False, 'message': 'Utilisateur du document non trouvé'}), 404
                
                # Vérifier département/location
                if (current_admin['department'] and user.get('department') != current_admin['department']) or \
                   (current_admin['location'] and user.get('location') != current_admin['location']):
                    return jsonify({'success': False, 'message': 'Permissions insuffisantes'}), 403
            
            # Mettre à jour le statut
            result = db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'status': new_status.lower(),
                        'updatedAt': datetime.utcnow(),
                        'updatedBy': current_admin['username']
                    }
                }
            )
            
            if result.modified_count > 0:
                return jsonify({
                    'success': True,
                    'message': 'Statut mis à jour avec succès',
                    'documentId': document_id,
                    'newStatus': new_status.lower()
                })
            else:
                return jsonify({'success': False, 'message': 'Aucune modification effectuée'}), 400
            
        except Exception as e:
            app.logger.error(f"Erreur mise à jour statut document: {e}")
            return jsonify({
                'success': False, 
                'message': f'Erreur: {str(e)}'
            }), 500

    @app.route('/api/admin/news/create-extended', methods=['POST'])
    @token_required_admin
    def create_news_extended(current_admin):
        """
        Créer une nouvelle actualité avec ciblage par département/location
        """
        try:
            data = request.get_json()
            
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            target_departments = data.get('targetDepartments', [])
            target_locations = data.get('targetLocations', [])
            priority = data.get('priority', 'normal')
            
            if not title:
                return jsonify({'success': False, 'message': 'Titre requis'}), 400
            
            if not content:
                return jsonify({'success': False, 'message': 'Contenu requis'}), 400
            
            # Pour les ADMIN, limiter le ciblage
            if current_admin['role'] == 'ADMIN':
                if current_admin['department']:
                    target_departments = [current_admin['department']]
                if current_admin['location']:
                    target_locations = [current_admin['location']]
            
            # Créer l'actualité
            news_data = {
                'title': title,
                'content': content,
                'targetDepartments': target_departments,
                'targetLocations': target_locations,
                'priority': priority,
                'authorUsername': current_admin['username'],
                'authorRole': current_admin['role'],
                'createdAt': datetime.utcnow(),
                'isActive': True
            }
            
            result = db.news.insert_one(news_data)
            
            return jsonify({
                'success': True,
                'message': 'Actualité créée avec succès',
                'newsId': str(result.inserted_id),
                'targetInfo': {
                    'departments': target_departments,
                    'locations': target_locations
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erreur création actualité: {e}")
            return jsonify({
                'success': False, 
                'message': f'Erreur: {str(e)}'
            }), 500

    app.logger.info("Routes d'administration étendues créées avec succès")
