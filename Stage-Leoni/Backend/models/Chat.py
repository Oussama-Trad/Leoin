#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle Chat unifié pour la synchronisation avec l'interface admin
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Chat:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['chats']
    
    def create_conversation(self, user_id, user_name, user_email, user_department, user_location, 
                          target_department, target_location, subject, initial_message=None):
        """Créer une nouvelle conversation avec filtrage strict"""
        try:
            conversation_data = {
                # Informations utilisateur
                'userId': ObjectId(user_id),
                'userName': user_name,
                'userEmail': user_email,
                'userDepartment': user_department,
                'userLocation': user_location,
                
                # Ciblage strict pour filtrage admin
                'targetDepartment': target_department,
                'targetLocation': target_location,
                
                # Métadonnées conversation
                'subject': subject,
                'title': subject,  # Compatibilité
                'description': initial_message or subject,
                'status': 'open',  # open, in_progress, closed
                'priority': 'normal',  # low, normal, high, urgent
                
                # Gestion admin
                'assignedAdminId': None,
                'assignedAdminName': None,
                
                # Timestamps
                'createdAt': datetime.utcnow(),
                'lastActivityAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                
                # Compteurs
                'messageCount': 0,
                'hasUnreadMessages': False,
                
                # Participants (pour compatibilité)
                'participants': [str(user_id)]
            }
            
            result = self.collection.insert_one(conversation_data)
            conversation_id = result.inserted_id
            
            # Créer le message initial si fourni
            if initial_message:
                from models.ChatMessage import ChatMessage
                chat_message = ChatMessage()
                chat_message.create_message(
                    chat_ref=conversation_id,
                    sender_id=user_id,
                    sender_name=user_name,
                    sender_email=user_email,
                    sender_type='user',
                    message=initial_message
                )
                
                # Mettre à jour le compteur
                self.collection.update_one(
                    {'_id': conversation_id},
                    {
                        '$inc': {'messageCount': 1},
                        '$set': {'lastActivityAt': datetime.utcnow()}
                    }
                )
            
            return {
                'success': True,
                'conversation_id': str(conversation_id),
                'message': 'Conversation créée avec succès'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création de la conversation'
            }
    
    def get_user_conversations(self, user_id):
        """Récupérer les conversations d'un utilisateur"""
        try:
            conversations = list(self.collection.find({
                'userId': ObjectId(user_id)
            }).sort('lastActivityAt', -1))
            
            # Enrichir avec le dernier message
            for conv in conversations:
                from models.ChatMessage import ChatMessage
                chat_message = ChatMessage()
                last_message = chat_message.get_last_message(str(conv['_id']))
                if last_message:
                    conv['lastMessage'] = last_message
                
                # Compter les messages non lus
                unread_count = chat_message.count_unread_for_user(str(conv['_id']), str(user_id))
                conv['unreadCount'] = unread_count
                conv['hasUnreadMessages'] = unread_count > 0
            
            return {
                'success': True,
                'conversations': conversations,
                'count': len(conversations)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des conversations'
            }
    
    def get_admin_conversations(self, admin_department, admin_location, admin_role='ADMIN', status_filter=None):
        """Récupérer les conversations pour un admin avec filtrage strict"""
        try:
            # Construire le filtre selon le rôle
            if admin_role == 'SUPERADMIN':
                # SuperAdmin voit toutes les conversations
                filter_query = {}
            else:
                # Admin normal voit seulement son département et location
                filter_query = {
                    'targetDepartment': admin_department,
                    'targetLocation': admin_location
                }
            
            # Ajouter le filtre de statut si fourni
            if status_filter:
                filter_query['status'] = status_filter
            
            conversations = list(self.collection.find(filter_query).sort('lastActivityAt', -1))
            
            # Enrichir avec les derniers messages
            for conv in conversations:
                from models.ChatMessage import ChatMessage
                chat_message = ChatMessage()
                last_message = chat_message.get_last_message(str(conv['_id']))
                if last_message:
                    conv['lastMessage'] = last_message
                
                # Compter les messages non lus pour l'admin
                unread_count = chat_message.count_unread_admin_messages(str(conv['_id']))
                conv['unreadCount'] = unread_count
            
            return {
                'success': True,
                'conversations': conversations,
                'count': len(conversations),
                'filter': filter_query
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération des conversations admin'
            }
    
    def update_conversation_status(self, conversation_id, new_status, admin_id=None, admin_name=None):
        """Mettre à jour le statut d'une conversation"""
        try:
            update_data = {
                'status': new_status,
                'updatedAt': datetime.utcnow(),
                'lastActivityAt': datetime.utcnow()
            }
            
            # Assigner l'admin si fourni
            if admin_id and admin_name:
                update_data['assignedAdminId'] = admin_id
                update_data['assignedAdminName'] = admin_name
            
            result = self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
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
                    'message': 'Conversation non trouvée'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la mise à jour du statut'
            }
    
    def get_conversation_by_id(self, conversation_id):
        """Récupérer une conversation par ID"""
        try:
            conversation = self.collection.find_one({'_id': ObjectId(conversation_id)})
            
            if conversation:
                # Enrichir avec les messages
                from models.ChatMessage import ChatMessage
                chat_message = ChatMessage()
                messages = chat_message.get_conversation_messages(conversation_id)
                conversation['messages'] = messages
                
                return {
                    'success': True,
                    'conversation': conversation
                }
            else:
                return {
                    'success': False,
                    'message': 'Conversation non trouvée'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la récupération de la conversation'
            }
    
    def get_statistics(self, admin_department=None, admin_location=None, admin_role='ADMIN'):
        """Récupérer les statistiques des conversations"""
        try:
            # Construire le filtre selon le rôle
            if admin_role == 'SUPERADMIN':
                base_filter = {}
            else:
                base_filter = {
                    'targetDepartment': admin_department,
                    'targetLocation': admin_location
                }
            
            # Statistiques générales
            total_conversations = self.collection.count_documents(base_filter)
            
            # Par statut
            open_conversations = self.collection.count_documents({**base_filter, 'status': 'open'})
            in_progress_conversations = self.collection.count_documents({**base_filter, 'status': 'in_progress'})
            closed_conversations = self.collection.count_documents({**base_filter, 'status': 'closed'})
            
            # Conversations avec messages non lus
            unread_conversations = self.collection.count_documents({**base_filter, 'hasUnreadMessages': True})
            
            # Conversations récentes (dernières 24h)
            yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            recent_conversations = self.collection.count_documents({
                **base_filter,
                'createdAt': {'$gte': yesterday}
            })
            
            return {
                'success': True,
                'statistics': {
                    'totalConversations': total_conversations,
                    'openConversations': open_conversations,
                    'inProgressConversations': in_progress_conversations,
                    'closedConversations': closed_conversations,
                    'unreadConversations': unread_conversations,
                    'recentConversations': recent_conversations
                }
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