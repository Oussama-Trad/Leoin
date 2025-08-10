#!/usr/bin/env python3
"""
Script simple d'analyse de la base de données
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return super().default(o)

def simple_analyze():
    load_dotenv()
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

    try:
        client = MongoClient(MONGODB_URI)
        db = client.LeoniApp
        
        print('=== ANALYSE SIMPLE ===')
        
        # CHATS
        chats_count = db.chats.count_documents({})
        print(f'Total chats: {chats_count}')
        
        if chats_count > 0:
            sample_chat = db.chats.find_one()
            print('\nStructure du premier chat:')
            print(json.dumps(sample_chat, indent=2, cls=JSONEncoder))
            
            # Compter par status
            statuses = {}
            for chat in db.chats.find({}, {'status': 1}):
                status = chat.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
            print(f'\nChats par statut: {statuses}')
            
            # Vérifier structure
            old_structure = db.chats.count_documents({'participants': {'$exists': True}})
            new_structure = db.chats.count_documents({'targetDepartment': {'$exists': True}})
            print(f'Chats avec ancienne structure (participants): {old_structure}')
            print(f'Chats avec nouvelle structure (targetDepartment): {new_structure}')
        
        # MESSAGES
        messages_count = db.chat_messages.count_documents({})
        print(f'\nTotal messages: {messages_count}')
        
        if messages_count > 0:
            sample_message = db.chat_messages.find_one()
            print('\nStructure du premier message:')
            print(json.dumps(sample_message, indent=2, cls=JSONEncoder))
            
            # Vérifier les références
            chatRef_count = db.chat_messages.count_documents({'chatRef': {'$exists': True}})
            chatId_count = db.chat_messages.count_documents({'chatId': {'$exists': True}})
            print(f'\nMessages avec chatRef: {chatRef_count}')
            print(f'Messages avec chatId: {chatId_count}')
        
        # ADMINS
        admins_count = db.admins.count_documents({})
        print(f'\nTotal admins: {admins_count}')
        
        if admins_count > 0:
            admin_sample = db.admins.find_one()
            # Masquer le mot de passe
            if 'password' in admin_sample:
                admin_sample['password'] = '***'
            print('\nStructure du premier admin:')
            print(json.dumps(admin_sample, indent=2, cls=JSONEncoder))
            
            # Lister tous les admins
            print('\nTous les admins:')
            for admin in db.admins.find({}, {'username': 1, 'department': 1, 'location': 1, 'role': 1}):
                username = admin.get('username', 'unknown')
                dept = admin.get('department', 'unknown')
                loc = admin.get('location', 'unknown')
                role = admin.get('role', 'unknown')
                print(f'  {username} - {dept} ({loc}) - {role}')
        
        # DÉPARTEMENTS
        departments_count = db.departments.count_documents({})
        print(f'\nTotal departments: {departments_count}')
        
        if departments_count > 0:
            print('\nDépartements disponibles:')
            for dept in db.departments.find({}):
                name = dept.get('name', 'unknown')
                location = dept.get('location', 'unknown')
                active = dept.get('active', True)
                print(f'  {name} - {location} (active: {active})')
        
        print('\n=== DIAGNOSTIC ===')
        
        # Problème 1: App mobile vs Admin - incohérence schéma
        if old_structure > 0 and new_structure == 0:
            print('❌ PROBLÈME MAJEUR: L\'app mobile crée des chats avec la nouvelle structure (targetDepartment)')
            print('   mais tous les chats existants utilisent l\'ancienne structure (participants/service)')
            print('   L\'interface admin ne peut pas lire les nouveaux chats!')
            
        # Problème 2: Messages avec mauvaise référence
        if chatId_count > 0 and chatRef_count == 0:
            print('❌ PROBLÈME: Les messages utilisent chatId au lieu de chatRef')
            print('   L\'interface admin Spring Boot cherche chatRef!')
            
        print('\n=== SOLUTIONS ===')
        
        if old_structure > 0 and new_structure == 0:
            print('1. MIGRATION URGENTE DU SCHÉMA:')
            print('   - Convertir tous les anciens chats vers la nouvelle structure')
            print('   - OU adapter l\'interface admin pour lire l\'ancienne structure')
            
        if chatId_count > 0:
            print('2. MIGRATION DES RÉFÉRENCES:')
            print('   - Renommer chatId en chatRef dans tous les messages')
            
        if admins_count > 0 and new_structure == 0:
            print('3. TESTER LA CRÉATION DE NOUVEAUX CHATS:')
            print('   - Créer un chat depuis l\'app mobile')
            print('   - Vérifier qu\'il apparaît dans l\'interface admin')
        
    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    simple_analyze()
