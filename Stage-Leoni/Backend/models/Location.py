#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle pour les locations
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Location:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['locations']
    
    def create(self, name, address=None, city=None, country=None, active=True):
        """Créer une nouvelle location"""
        try:
            location_data = {
                'name': name,
                'address': address,
                'city': city,
                'country': country,
                'active': active,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = self.collection.insert_one(location_data)
            return {
                'success': True,
                'location_id': str(result.inserted_id),
                'message': 'Location créée avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création de la location'
            }
    
    def find_all(self, active_only=True):
        """Récupérer toutes les locations"""
        try:
            filter_query = {'active': True} if active_only else {}
            locations = list(self.collection.find(filter_query))
            
            # Convertir ObjectId en string
            for location in locations:
                location['_id'] = str(location['_id'])
                if location.get('createdAt'):
                    location['createdAt'] = location['createdAt'].isoformat()
                if location.get('updatedAt'):
                    location['updatedAt'] = location['updatedAt'].isoformat()
            
            return {
                'success': True,
                'locations': locations,
                'count': len(locations)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des locations'
            }
    
    def find_by_id(self, location_id):
        """Récupérer une location par ID"""
        try:
            location = self.collection.find_one({'_id': ObjectId(location_id)})
            
            if not location:
                return {
                    'success': False,
                    'message': 'Location non trouvée'
                }
            
            # Convertir ObjectId en string
            location['_id'] = str(location['_id'])
            if location.get('createdAt'):
                location['createdAt'] = location['createdAt'].isoformat()
            if location.get('updatedAt'):
                location['updatedAt'] = location['updatedAt'].isoformat()
            
            return {
                'success': True,
                'location': location
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération de la location'
            }
    
    def update(self, location_id, name=None, address=None, city=None, country=None, active=None):
        """Mettre à jour une location"""
        try:
            update_data = {'updatedAt': datetime.utcnow()}
            
            if name is not None:
                update_data['name'] = name
            if address is not None:
                update_data['address'] = address
            if city is not None:
                update_data['city'] = city
            if country is not None:
                update_data['country'] = country
            if active is not None:
                update_data['active'] = active
            
            result = self.collection.update_one(
                {'_id': ObjectId(location_id)},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Location non trouvée'
                }
            
            return {
                'success': True,
                'message': 'Location mise à jour avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour de la location'
            }
    
    def delete(self, location_id):
        """Supprimer une location (soft delete)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(location_id)},
                {'$set': {'active': False, 'updatedAt': datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Location non trouvée'
                }
            
            return {
                'success': True,
                'message': 'Location supprimée avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la suppression de la location'
            }
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()
