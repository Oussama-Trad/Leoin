#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle pour les utilisateurs
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['users']
    
    def create(self, email, password, first_name, last_name, department=None, location=None, 
               department_ref=None, location_ref=None, role='user'):
        """Créer un nouvel utilisateur"""
        try:
            # Vérifier si l'email existe déjà
            existing_user = self.collection.find_one({'email': email})
            if existing_user:
                return {
                    'success': False,
                    'message': 'Un utilisateur avec cet email existe déjà'
                }
            
            # Hacher le mot de passe
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user_data = {
                'email': email,
                'password': hashed_password,
                'firstName': first_name,
                'lastName': last_name,
                'department': department,
                'location': location,
                'departmentRef': ObjectId(department_ref) if department_ref else None,
                'locationRef': ObjectId(location_ref) if location_ref else None,
                'role': role,
                'active': True,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = self.collection.insert_one(user_data)
            return {
                'success': True,
                'user_id': str(result.inserted_id),
                'message': 'Utilisateur créé avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création de l\'utilisateur'
            }
    
    def find_by_email(self, email):
        """Récupérer un utilisateur par email"""
        try:
            user = self.collection.find_one({'email': email, 'active': True})
            
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            # Convertir ObjectId en string
            user['_id'] = str(user['_id'])
            if user.get('departmentRef'):
                user['departmentRef'] = str(user['departmentRef'])
            if user.get('locationRef'):
                user['locationRef'] = str(user['locationRef'])
            if user.get('createdAt'):
                user['createdAt'] = user['createdAt'].isoformat()
            if user.get('updatedAt'):
                user['updatedAt'] = user['updatedAt'].isoformat()
            
            return {
                'success': True,
                'user': user
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération de l\'utilisateur'
            }
    
    def find_by_id(self, user_id):
        """Récupérer un utilisateur par ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id), 'active': True})
            
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            # Convertir ObjectId en string
            user['_id'] = str(user['_id'])
            if user.get('departmentRef'):
                user['departmentRef'] = str(user['departmentRef'])
            if user.get('locationRef'):
                user['locationRef'] = str(user['locationRef'])
            if user.get('createdAt'):
                user['createdAt'] = user['createdAt'].isoformat()
            if user.get('updatedAt'):
                user['updatedAt'] = user['updatedAt'].isoformat()
            
            return {
                'success': True,
                'user': user
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération de l\'utilisateur'
            }
    
    def verify_password(self, email, password):
        """Vérifier le mot de passe d'un utilisateur"""
        try:
            user = self.collection.find_one({'email': email, 'active': True})
            
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            # Vérifier le mot de passe
            stored_password = user['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # Convertir ObjectId en string pour retourner l'utilisateur
                user['_id'] = str(user['_id'])
                if user.get('departmentRef'):
                    user['departmentRef'] = str(user['departmentRef'])
                if user.get('locationRef'):
                    user['locationRef'] = str(user['locationRef'])
                if user.get('createdAt'):
                    user['createdAt'] = user['createdAt'].isoformat()
                if user.get('updatedAt'):
                    user['updatedAt'] = user['updatedAt'].isoformat()
                
                return {
                    'success': True,
                    'user': user,
                    'message': 'Mot de passe correct'
                }
            else:
                return {
                    'success': False,
                    'message': 'Mot de passe incorrect'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la vérification du mot de passe'
            }
    
    def update(self, user_id, **kwargs):
        """Mettre à jour un utilisateur"""
        try:
            update_data = {'updatedAt': datetime.utcnow()}
            
            # Ajouter les champs à mettre à jour
            allowed_fields = ['firstName', 'lastName', 'email', 'department', 'location', 
                            'departmentRef', 'locationRef', 'role', 'active']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    if field in ['departmentRef', 'locationRef'] and value:
                        update_data[field] = ObjectId(value)
                    else:
                        update_data[field] = value
            
            # Si un nouveau mot de passe est fourni
            if 'password' in kwargs:
                hashed_password = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt())
                update_data['password'] = hashed_password
            
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            return {
                'success': True,
                'message': 'Utilisateur mis à jour avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour de l\'utilisateur'
            }
    
    def delete(self, user_id):
        """Supprimer un utilisateur (soft delete)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'active': False, 'updatedAt': datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            return {
                'success': True,
                'message': 'Utilisateur supprimé avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la suppression de l\'utilisateur'
            }
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()
