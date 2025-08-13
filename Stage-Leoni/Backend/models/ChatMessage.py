#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle ChatMessage unifié pour la synchronisation avec l'interface admin
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class ChatMessage:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['LeoniApp']
        self.collection = self.db['chat_messages']
    
    def create_message(self, chat_ref, sender_id, sender_name, sender_email, sender_type, message, message_type='text'):
        """Créer un nouveau message dans une conversation"""
        try:
            message_data = {
                'chatRef': ObjectId(chat_ref),  # IMPORTANT: utilise chatRef pour compatibilité admin
                'senderId': ObjectId(sender_id),
                'senderName': sender_name,
                'senderEmail': sender_email,
                'senderType': sender_type,  # 'user', 'admin', 'superadmin'
                'senderRole': 'employee' if sender_type == 'user' else sender_type,  # Compatibilité
                
                'message': message,  # Champ principal
                'content': message,  # Compatibilité
                'messageType': message_type,
                
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                
                'isRead': False,
                'readAt': None,
                'readBy': None,
                
                'isEdited': False,
                'editedAt': None,
                'originalMessage': None
            }
            
            result = self.collection.insert_one(message_data)
            
            # Mettre à jour la conversation
            self._update_conversation_activity(chat_ref)
            
            return {
                'success': True,
                'message_id': str(result.inserted_id),
                'message': 'Message créé avec succès'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors de la création du message'
            }
    
    def get_conversation_messages(self, chat_ref, limit=50):
        """Récupérer les messages d'une conversation"""
        try:
            messages = list(self.collection.find({
                'chatRef': ObjectId(chat_ref)
            }).sort('createdAt', 1).limit(limit))
            
            return messages
            
        except Exception as e:
            print(f"Erreur récupération messages: {e}")
            return []
    
    def get_last_message(self, chat_ref):
        """Récupérer le dernier message d'une conversation"""
        try:
            last_message = self.collection.find_one(
                {'chatRef': ObjectId(chat_ref)},
                sort=[('createdAt', -1)]
            )
            return last_message
            
        except Exception as e:
            print(f"Erreur récupération dernier message: {e}")
            return None
    
    def mark_messages_as_read(self, chat_ref, reader_id, reader_type='user'):
        """Marquer les messages comme lus"""
        try:
            # Marquer tous les messages non lus de la conversation comme lus
            # sauf ceux envoyés par le lecteur lui-même
            result = self.collection.update_many(
                {
                    'chatRef': ObjectId(chat_ref),
                    'isRead': False,
                    'senderId': {'$ne': ObjectId(reader_id)}
                },
                {
                    '$set': {
                        'isRead': True,
                        'readAt': datetime.utcnow(),
                        'readBy': reader_id,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            
            # Mettre à jour le statut de la conversation
            if result.modified_count > 0:
                self._update_conversation_read_status(chat_ref)
            
            return {
                'success': True,
                'marked_count': result.modified_count,
                'message': f'{result.modified_count} messages marqués comme lus'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur lors du marquage des messages'
            }
    
    def count_unread_for_user(self, chat_ref, user_id):
        """Compter les messages non lus pour un utilisateur"""
        try:
            # Messages non lus qui ne sont pas de l'utilisateur
            count = self.collection.count_documents({
                'chatRef': ObjectId(chat_ref),
                'isRead': False,
                'senderId': {'$ne': ObjectId(user_id)}
            })
            return count
            
        except Exception as e:
            print(f"Erreur comptage messages non lus: {e}")
            return 0
    
    def count_unread_admin_messages(self, chat_ref):
        """Compter les messages non lus pour les admins"""
        try:
            # Messages d'utilisateurs non lus par les admins
            count = self.collection.count_documents({
                'chatRef': ObjectId(chat_ref),
                'isRead': False,
                'senderType': 'user'
            })
            return count
            
        except Exception as e:
            print(f"Erreur comptage messages admin non lus: {e}")
            return 0
    
    def _update_conversation_activity(self, chat_ref):
        """Mettre à jour l'activité de la conversation"""
        try:
            # Mettre à jour les timestamps et compteurs
            self.db['chats'].update_one(
                {'_id': ObjectId(chat_ref)},
                {
                    '$set': {
                        'lastActivityAt': datetime.utcnow(),
                        'updatedAt': datetime.utcnow(),
                        'hasUnreadMessages': True
                    },
                    '$inc': {'messageCount': 1}
                }
            )
        except Exception as e:
            print(f"Erreur mise à jour activité conversation: {e}")
    
    def _update_conversation_read_status(self, chat_ref):
        """Mettre à jour le statut de lecture de la conversation"""
        try:
            # Vérifier s'il reste des messages non lus
            unread_count = self.collection.count_documents({
                'chatRef': ObjectId(chat_ref),
                'isRead': False
            })
            
            # Mettre à jour le statut
            self.db['chats'].update_one(
                {'_id': ObjectId(chat_ref)},
                {
                    '$set': {
                        'hasUnreadMessages': unread_count > 0,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            print(f"Erreur mise à jour statut lecture: {e}")
    
    def close_connection(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self, 'client'):
            self.client.close()