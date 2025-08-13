#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle DocumentRequest unifié pour la synchronisation avec l'interface admin
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DocumentRequest:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['document_requests']
    
    def create_request(self, user_id, document_type, description=None, urgency='normale'):
        """Créer une nouvelle demande de document"""
        try:
            # Récupérer les infos utilisateur pour le filtrage admin
            user = self.db['users'].find_one({'_id': ObjectId(user_id)})
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            request_data = {
                'userId': ObjectId(user_id),
                'userDepartment': user.get('department', ''),
                'userLocation': user.get('location', ''),
                'userName': f"{user.get('firstName', '')} {user.get('lastName', '')}",
                'userEmail': user.get('adresse1', user.get('email', '')),
                
                'documentType': document_type,
                'description': description or '',
                'urgency': urgency,
                
                'status': {
                    'current': 'en attente',
                    'progress': [
                        {'step': 'en attente', 'date': datetime.utcnow(), 'completed': True},
                        {'step': 'en cours', 'date': None, 'completed': False},
                        {'step': 'accepté', 'date': None, 'completed': False},
                        {'step': 'refusé', 'date': None, 'completed': False}
                    ]
                },
                
                'assignedAdminId': None,
                'assignedAdminName': None,
                'adminComments': [],
                
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = self.collection.insert_one(request_data)
            
            return {
                'success': True,
                'request_id': str(result.inserted_id),
                'message': 'Demande créée avec succès'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création de la demande'
            }
    
    def get_user_requests(self, user_id):
        """Récupérer les demandes d'un utilisateur"""
        try:
            requests = list(self.collection.find({
                'userId': ObjectId(user_id)
            }).sort('createdAt', -1))
            
            return {
                'success': True,
                'requests': requests,
                'count': len(requests)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des demandes'
            }
    
    def get_admin_requests(self, admin_department, admin_location, admin_role='ADMIN', status_filter=None):
        """Récupérer les demandes pour un admin avec filtrage"""
        try:
            # Construire le filtre selon le rôle
            if admin_role == 'SUPERADMIN':
                # SuperAdmin voit toutes les demandes
                filter_query = {}
            else:
                # Admin normal voit seulement les demandes de son département/location
                filter_query = {
                    'userDepartment': admin_department,
                    'userLocation': admin_location
                }
            
            # Ajouter le filtre de statut si fourni
            if status_filter:
                filter_query['status.current'] = status_filter
            
            requests = list(self.collection.find(filter_query).sort('createdAt', -1))
            
            return {
                'success': True,
                'requests': requests,
                'count': len(requests),
                'filter': filter_query
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des demandes admin'
            }
    
    def update_request_status(self, request_id, new_status, admin_id=None, admin_name=None, comment=None):
        """Mettre à jour le statut d'une demande"""
        try:
            # Récupérer la demande actuelle
            request = self.collection.find_one({'_id': ObjectId(request_id)})
            if not request:
                return {
                    'success': False,
                    'message': 'Demande non trouvée'
                }
            
            # Mettre à jour le statut
            update_data = {
                'status.current': new_status,
                'updatedAt': datetime.utcnow()
            }
            
            # Assigner l'admin si fourni
            if admin_id and admin_name:
                update_data['assignedAdminId'] = admin_id
                update_data['assignedAdminName'] = admin_name
            
            # Ajouter un commentaire admin si fourni
            if comment:
                admin_comment = {
                    'adminId': admin_id,
                    'adminName': admin_name,
                    'comment': comment,
                    'date': datetime.utcnow()
                }
                self.collection.update_one(
                    {'_id': ObjectId(request_id)},
                    {'$push': {'adminComments': admin_comment}}
                )
            
            # Mettre à jour les étapes de progression
            progress_update = f"status.progress.$.date"
            progress_completed = f"status.progress.$.completed"
            
            # Mettre à jour l'étape correspondante
            self.collection.update_one(
                {'_id': ObjectId(request_id), 'status.progress.step': new_status},
                {
                    '$set': {
                        progress_update: datetime.utcnow(),
                        progress_completed: True
                    }
                }
            )
            
            # Mettre à jour les données principales
            result = self.collection.update_one(
                {'_id': ObjectId(request_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Statut mis à jour avec succès'
                }
            else:
                return {
                    'success': False,
                    'message': 'Aucune modification effectuée'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour du statut'
            }
    
    def delete_request(self, request_id, user_id):
        """Supprimer une demande (seulement par l'utilisateur propriétaire)"""
        try:
            # Vérifier que la demande appartient à l'utilisateur
            request = self.collection.find_one({
                '_id': ObjectId(request_id),
                'userId': ObjectId(user_id)
            })
            
            if not request:
                return {
                    'success': False,
                    'message': 'Demande non trouvée ou non autorisée'
                }
            
            # Vérifier que la demande n'est pas déjà acceptée
            if request.get('status', {}).get('current') == 'accepté':
                return {
                    'success': False,
                    'message': 'Impossible de supprimer une demande acceptée'
                }
            
            # Supprimer la demande
            result = self.collection.delete_one({'_id': ObjectId(request_id)})
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': 'Demande supprimée avec succès'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erreur lors de la suppression'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la suppression de la demande'
            }
    
    def get_statistics(self, admin_department=None, admin_location=None, admin_role='ADMIN'):
        """Récupérer les statistiques des demandes"""
        try:
            # Construire le filtre selon le rôle
            if admin_role == 'SUPERADMIN':
                base_filter = {}
            else:
                base_filter = {
                    'userDepartment': admin_department,
                    'userLocation': admin_location
                }
            
            # Statistiques par statut
            stats = {}
            statuses = ['en attente', 'en cours', 'accepté', 'refusé']
            
            for status in statuses:
                count = self.collection.count_documents({
                    **base_filter,
                    'status.current': status
                })
                stats[status.replace(' ', '_')] = count
            
            # Total
            stats['total'] = self.collection.count_documents(base_filter)
            
            # Demandes récentes (dernières 24h)
            yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            stats['recent'] = self.collection.count_documents({
                **base_filter,
                'createdAt': {'$gte': yesterday}
            })
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du calcul des statistiques'
            }
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()