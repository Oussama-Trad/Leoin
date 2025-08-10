#!/usr/bin/env python3
"""
Script d'analyse de la base de données MongoDB pour diagnostiquer les problèmes de chat
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
from datetime import datetime

def analyze_database():
    # Charger les variables d'environnement
    load_dotenv()
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

    try:
        client = MongoClient(MONGODB_URI)
        db = client.LeoniApp
        
        print('🔍 ANALYSE DE LA BASE DE DONNÉES MONGODB 🔍')
        print('=' * 60)
        
        # Collections existantes
        collections = db.list_collection_names()
        print(f'📁 Collections disponibles: {collections}')
        
        # ========================================
        # ANALYSE DES CHATS
        # ========================================
        chats_count = db.chats.count_documents({})
        print(f'\n💬 CHATS ({chats_count} total)')
        print('-' * 40)
        
        if chats_count > 0:
            # Premier chat pour voir la structure
            sample_chat = db.chats.find_one()
            print('📋 Structure d\'un chat:')
            for key, value in sample_chat.items():
                if key != '_id':
                    print(f'  {key}: {type(value).__name__} = {value}')
            
            # Statistiques par département et location (ancienne structure)
            print('\n📊 Chats par service/catégorie:')
            pipeline = [
                {'$group': {
                    '_id': {
                        'category': '$category',
                        'service': '$participants.service.serviceName'
                    },
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            dept_stats = list(db.chats.aggregate(pipeline))
            for stat in dept_stats:
                category = stat['_id']['category'] or 'Unknown'
                service = stat['_id']['service'] or 'Unknown'
                count = stat['count']
                print(f'  {category} ({service}): {count} chats')
            
            # Vérifier s'il y a des chats avec la nouvelle structure
            new_structure_count = db.chats.count_documents({'targetDepartment': {'$exists': True}})
            print(f'\n📊 Chats avec nouvelle structure (targetDepartment): {new_structure_count}')
            
            # Statistiques par statut
            print('\n📈 Chats par statut:')
            status_pipeline = [
                {'$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            status_stats = list(db.chats.aggregate(status_pipeline))
            for stat in status_stats:
                status = stat['_id'] or 'None'
                count = stat['count']
                print(f'  {status}: {count} chats')
        else:
            print('⚠️ Aucun chat trouvé dans la base de données!')
        
        # ========================================
        # ANALYSE DES MESSAGES
        # ========================================
        messages_count = db.chat_messages.count_documents({})
        print(f'\n💌 CHAT_MESSAGES ({messages_count} total)')
        print('-' * 40)
        
        if messages_count > 0:
            # Premier message pour voir la structure
            sample_message = db.chat_messages.find_one()
            print('📋 Structure d\'un message:')
            for key, value in sample_message.items():
                if key != '_id':
                    print(f'  {key}: {type(value).__name__} = {value}')
            
            # Vérifier les champs de référence au chat
            messages_with_chatRef = db.chat_messages.count_documents({'chatRef': {'$exists': True}})
            messages_with_chatId = db.chat_messages.count_documents({'chatId': {'$exists': True}})
            print(f'\n🔗 Références aux chats:')
            print(f'  Messages avec chatRef: {messages_with_chatRef}')
            print(f'  Messages avec chatId: {messages_with_chatId}')
            
            # Compter les messages par rôle d'expéditeur
            print(f'\n👥 Messages par rôle:')
            role_pipeline = [
                {'$group': {
                    '_id': '$senderRole',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            role_stats = list(db.chat_messages.aggregate(role_pipeline))
            for stat in role_stats:
                role = stat['_id'] or 'None'
                count = stat['count']
                print(f'  {role}: {count} messages')
                
            # Vérifier la cohérence des références
            print(f'\n🔍 Vérification cohérence:')
            # Messages orphelins (qui référencent des chats inexistants)
            all_chat_ids = set(str(chat['_id']) for chat in db.chats.find({}, {'_id': 1}))
            
            orphan_messages = 0
            for message in db.chat_messages.find({'chatRef': {'$exists': True}}, {'chatRef': 1}):
                chat_ref = str(message.get('chatRef', ''))
                if chat_ref not in all_chat_ids:
                    orphan_messages += 1
            
            print(f'  Messages orphelins (chatRef invalide): {orphan_messages}')
            
        else:
            print('⚠️ Aucun message trouvé dans la base de données!')
        
        # ========================================
        # ANALYSE DES ADMINS
        # ========================================
        admins_count = db.admins.count_documents({})
        print(f'\n👤 ADMINS ({admins_count} total)')
        print('-' * 40)
        
        if admins_count > 0:
            # Premier admin pour voir la structure
            sample_admin = db.admins.find_one()
            print('📋 Structure d\'un admin:')
            for key, value in sample_admin.items():
                if key not in ['_id', 'password']:  # Ne pas afficher le mot de passe
                    print(f'  {key}: {type(value).__name__} = {value}')
            
            # Admins par département et location
            print(f'\n📊 Admins par département:')
            admin_pipeline = [
                {'$group': {
                    '_id': {
                        'department': '$department',
                        'location': '$location'
                    },
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            admin_stats = list(db.admins.aggregate(admin_pipeline))
            for stat in admin_stats:
                dept = stat['_id']['department'] or 'Unknown'
                loc = stat['_id']['location'] or 'Unknown'
                count = stat['count']
                print(f'  {dept} ({loc}): {count} admins')
        else:
            print('⚠️ Aucun admin trouvé dans la base de données!')
        
        # ========================================
        # ANALYSE DES DÉPARTEMENTS
        # ========================================
        departments_count = db.departments.count_documents({})
        print(f'\n🏢 DEPARTMENTS ({departments_count} total)')
        print('-' * 40)
        
        if departments_count > 0:
            departments = list(db.departments.find({}))
            for dept in departments[:10]:  # Montrer les 10 premiers
                name = dept.get('name', 'Unknown')
                location = dept.get('location', 'Unknown')
                active = dept.get('active', True)
                print(f'  {name} ({location}) - Active: {active}')
        else:
            print('⚠️ Aucun département trouvé dans la base de données!')
        
        # ========================================
        # DIAGNOSTIC DES PROBLÈMES
        # ========================================
        print(f'\n🔍 DIAGNOSTIC DES PROBLÈMES')
        print('=' * 60)
        
        problems = []
        
        # Problème 1: Incohérence dans les champs chatId vs chatRef
        if messages_count > 0:
            if messages_with_chatRef == 0 and messages_with_chatId > 0:
                problems.append("❌ Tous les messages utilisent 'chatId' au lieu de 'chatRef'")
            elif messages_with_chatRef > 0 and messages_with_chatId > 0:
                problems.append("⚠️ Certains messages utilisent 'chatId', d'autres 'chatRef'")
            elif messages_with_chatRef == 0 and messages_with_chatId == 0:
                problems.append("❌ Aucun message n'a de référence vers un chat")
        
        # Problème 2: Messages orphelins
        if orphan_messages > 0:
            problems.append(f"❌ {orphan_messages} messages orphelins (références invalides)")
        
        # Problème 3: Schéma de données incohérent
        if chats_count > 0:
            # Vérifier les différentes structures de chats
            old_structure_count = db.chats.count_documents({'participants.service': {'$exists': True}})
            new_structure_count = db.chats.count_documents({'targetDepartment': {'$exists': True}})
            
            if old_structure_count > 0 and new_structure_count == 0:
                problems.append(f"❌ Tous les chats ({old_structure_count}) utilisent l'ancienne structure (service/participants)")
            elif old_structure_count > 0 and new_structure_count > 0:
                problems.append(f"⚠️ Structure mixte: {old_structure_count} anciens chats, {new_structure_count} nouveaux")
        
        # Problème 4: Pas d'admin dans la bonne location/département (pour nouvelle structure seulement)
        if new_structure_count > 0 and admins_count > 0:
            # Vérifier s'il y a des admins pour chaque département/location ayant des chats
            chat_departments = set()
            for chat in db.chats.find({'targetDepartment': {'$exists': True}}, {'targetDepartment': 1, 'targetLocation': 1}):
                dept = chat.get('targetDepartment')
                loc = chat.get('targetLocation')
                if dept and loc:
                    chat_departments.add((dept, loc))
            
            admin_departments = set()
            for admin in db.admins.find({}, {'department': 1, 'location': 1}):
                dept = admin.get('department')
                loc = admin.get('location')
                if dept and loc:
                    admin_departments.add((dept, loc))
            
            uncovered_departments = chat_departments - admin_departments
            if uncovered_departments:
                problems.append(f"⚠️ Départements sans admin: {list(uncovered_departments)}")
        
        # Problème 5: Pas de départements définis
        if departments_count == 0:
            problems.append("❌ Aucun département défini dans la collection 'departments'")
        
        if problems:
            print("PROBLÈMES DÉTECTÉS:")
            for problem in problems:
                print(f"  {problem}")
        else:
            print("✅ Aucun problème détecté!")
        
        # ========================================
        # SOLUTIONS PROPOSÉES
        # ========================================
        if problems:
            print(f'\n🔧 SOLUTIONS PROPOSÉES')
            print('=' * 60)
            
            if "chatId" in str(problems):
                print("1. Migration des champs chatId vers chatRef:")
                print("   db.chat_messages.updateMany({chatId: {$exists: true}}, [{$set: {chatRef: '$chatId'}}, {$unset: 'chatId'}])")
            
            if "ancienne structure" in str(problems):
                print("2. Migration du schéma de chats:")
                print("   Convertir les chats de l'ancienne structure (service/participants) vers la nouvelle (targetDepartment/targetLocation)")
            
            if orphan_messages > 0:
                print("3. Nettoyer les messages orphelins:")
                print("   Identifier et supprimer les messages sans chat valide")
            
            if 'uncovered_departments' in locals() and uncovered_departments:
                print("4. Créer des admins pour les départements manquants")
            
            if departments_count == 0:
                print("5. Initialiser la collection departments avec les départements standard")
        
        print(f'\n✅ Analyse terminée!')
        
    except Exception as e:
        print(f'❌ Erreur lors de l\'analyse: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_database()
