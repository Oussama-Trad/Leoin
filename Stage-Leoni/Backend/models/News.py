#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle News unifié pour la synchronisation avec l'interface admin
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class News:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['news']
    
    def get_filtered_news_for_user(self, user_department, user_location):
        """Récupérer les actualités filtrées pour un utilisateur"""
        try:
            # Filtre pour les actualités ciblées vers l'utilisateur
            filter_query = {
                'isActive': True,  # Seulement les actualités actives
                '$or': [
                    # Actualités pour tous
                    {'targetDepartment': None, 'targetLocation': None},
                    {'targetDepartment': 'All', 'targetLocation': 'All'},
                    
                    # Actualités pour le département de l'utilisateur
                    {'targetDepartment': user_department, 'targetLocation': None},
                    {'targetDepartment': user_department, 'targetLocation': 'All'},
                    
                    # Actualités pour la location de l'utilisateur
                    {'targetDepartment': None, 'targetLocation': user_location},
                    {'targetDepartment': 'All', 'targetLocation': user_location},
                    
                    # Actualités pour le département ET la location de l'utilisateur
                    {'targetDepartment': user_department, 'targetLocation': user_location}
                ]
            }
            
            news = list(self.collection.find(filter_query).sort('createdAt', -1))
            
            return {
                'success': True,
                'news': news,
                'count': len(news),
                'userInfo': {
                    'department': user_department,
                    'location': user_location
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des actualités'
            }
    
    def create_news(self, title, content, author_id, author_name, target_department=None, target_location=None, 
                   category='general', priority='normal', summary=None):
        """Créer une nouvelle actualité"""
        try:
            news_data = {
                'title': title,
                'content': content,
                'summary': summary or content[:200] + '...' if len(content) > 200 else content,
                'category': category,
                'priority': priority,
                
                # Informations auteur
                'authorRef': ObjectId(author_id),
                'authorName': author_name,
                
                # Ciblage
                'targetDepartment': target_department,
                'targetLocation': target_location,
                
                # Statut
                'isActive': True,
                'visibility': {
                    'status': 'published'
                },
                
                # Timestamps
                'createdAt': datetime.utcnow(),
                'publishedAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                
                # Statistiques
                'stats': {
                    'views': 0,
                    'likes': 0,
                    'comments': 0
                }
            }
            
            result = self.collection.insert_one(news_data)
            
            return {
                'success': True,
                'news_id': str(result.inserted_id),
                'message': 'Actualité créée avec succès'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création de l\'actualité'
            }
    
    def update_news(self, news_id, update_data):
        """Mettre à jour une actualité"""
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(news_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Actualité mise à jour avec succès'
                }
            else:
                return {
                    'success': False,
                    'message': 'Actualité non trouvée'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour de l\'actualité'
            }
    
    def get_admin_news(self, admin_department=None, admin_location=None, admin_role='ADMIN'):
        """Récupérer les actualités pour un admin"""
        try:
            # Construire le filtre selon le rôle
            if admin_role == 'SUPERADMIN':
                # SuperAdmin voit toutes les actualités
                filter_query = {}
            else:
                # Admin normal voit seulement les actualités de son département/location
                filter_query = {
                    '$or': [
                        {'targetDepartment': admin_department, 'targetLocation': admin_location},
                        {'targetDepartment': admin_department, 'targetLocation': None},
                        {'targetDepartment': None, 'targetLocation': admin_location},
                        {'targetDepartment': None, 'targetLocation': None}
                    ]
                }
            
            news = list(self.collection.find(filter_query).sort('createdAt', -1))
            
            return {
                'success': True,
                'news': news,
                'count': len(news)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des actualités admin'
            }
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()