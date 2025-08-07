#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle pour les départements
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Department:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['departments']
    
    def create(self, name, description=None, location_ref=None, active=True):
        """Créer un nouveau département"""
        try:
            department_data = {
                'name': name,
                'description': description,
                'locationRef': ObjectId(location_ref) if location_ref else None,
                'active': active,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = self.collection.insert_one(department_data)
            return {
                'success': True,
                'department_id': str(result.inserted_id),
                'message': 'Département créé avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création du département'
            }
    
    def find_all(self, active_only=True):
        """Récupérer tous les départements"""
        try:
            filter_query = {'active': True} if active_only else {}
            departments = list(self.collection.find(filter_query))
            
            # Convertir ObjectId en string
            for dept in departments:
                dept['_id'] = str(dept['_id'])
                if dept.get('locationRef'):
                    dept['locationRef'] = str(dept['locationRef'])
                if dept.get('createdAt'):
                    dept['createdAt'] = dept['createdAt'].isoformat()
                if dept.get('updatedAt'):
                    dept['updatedAt'] = dept['updatedAt'].isoformat()
            
            return {
                'success': True,
                'departments': departments,
                'count': len(departments)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des départements'
            }
    
    def find_by_location(self, location_id):
        """Récupérer les départements par location"""
        try:
            # Pour l'instant, retourner tous les départements actifs
            # car la structure actuelle n'a pas de locationRef
            filter_query = {'active': True}
            departments = list(self.collection.find(filter_query))
            
            # Convertir ObjectId en string
            for dept in departments:
                dept['_id'] = str(dept['_id'])
                if dept.get('locationRef'):
                    dept['locationRef'] = str(dept['locationRef'])
                if dept.get('createdAt'):
                    dept['createdAt'] = dept['createdAt'].isoformat()
                if dept.get('updatedAt'):
                    dept['updatedAt'] = dept['updatedAt'].isoformat()
            
            return {
                'success': True,
                'departments': departments,
                'count': len(departments),
                'location_id': location_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des départements'
            }
    
    def find_by_id(self, department_id):
        """Récupérer un département par ID"""
        try:
            department = self.collection.find_one({'_id': ObjectId(department_id)})
            
            if not department:
                return {
                    'success': False,
                    'message': 'Département non trouvé'
                }
            
            # Convertir ObjectId en string
            department['_id'] = str(department['_id'])
            if department.get('locationRef'):
                department['locationRef'] = str(department['locationRef'])
            if department.get('createdAt'):
                department['createdAt'] = department['createdAt'].isoformat()
            if department.get('updatedAt'):
                department['updatedAt'] = department['updatedAt'].isoformat()
            
            return {
                'success': True,
                'department': department
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération du département'
            }
    
    def update(self, department_id, name=None, description=None, location_ref=None, active=None):
        """Mettre à jour un département"""
        try:
            update_data = {'updatedAt': datetime.utcnow()}
            
            if name is not None:
                update_data['name'] = name
            if description is not None:
                update_data['description'] = description
            if location_ref is not None:
                update_data['locationRef'] = ObjectId(location_ref) if location_ref else None
            if active is not None:
                update_data['active'] = active
            
            result = self.collection.update_one(
                {'_id': ObjectId(department_id)},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Département non trouvé'
                }
            
            return {
                'success': True,
                'message': 'Département mis à jour avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour du département'
            }
    
    def delete(self, department_id):
        """Supprimer un département (soft delete)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(department_id)},
                {'$set': {'active': False, 'updatedAt': datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Département non trouvé'
                }
            
            return {
                'success': True,
                'message': 'Département supprimé avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la suppression du département'
            }
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()
