#!/usr/bin/env python3
"""
Script de diagnostic pour le système de filtrage des chats admin
"""

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Configuration MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

try:
    client = MongoClient(MONGODB_URI)
    db = client.LeoniApp
    users_collection = db.users
    chats_collection = db.chats
    chat_messages_collection = db.chat_messages
    departments_collection = db.departments
    admins_collection = db.admins
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    exit(1)

def debug_chat_system():
    print("\n🔍 DIAGNOSTIC DU SYSTÈME DE CHAT ADMIN")
    print("=" * 50)
    
    # 1. Lister tous les admins
    print("\n1️⃣ ADMINS EN BASE:")
    admins = list(admins_collection.find({}))
    for admin in admins:
        print(f"  👤 {admin.get('username', 'N/A')} - Dept: {admin.get('department', 'N/A')} - Location: {admin.get('location', 'N/A')} - Active: {admin.get('active', 'N/A')}")
    
    if not admins:
        print("  ❌ Aucun admin trouvé en base!")
        return
    
    # 2. Lister toutes les conversations
    print("\n2️⃣ CONVERSATIONS EN BASE:")
    conversations = list(chats_collection.find({}))
    print(f"  📊 Total conversations: {len(conversations)}")
    
    for conv in conversations:
        print(f"  💬 {conv.get('_id')} - Target: {conv.get('targetDepartment', 'N/A')}/{conv.get('targetLocation', 'N/A')} - User: {conv.get('userName', 'N/A')}")
    
    if not conversations:
        print("  ❌ Aucune conversation trouvée en base!")
        return
    
    # 3. Lister tous les départements
    print("\n3️⃣ DÉPARTEMENTS EN BASE:")
    departments = list(departments_collection.find({}))
    for dept in departments:
        print(f"  🏢 {dept.get('name', 'N/A')} - {dept.get('location', 'N/A')}")
    
    # 4. Tester le filtrage pour chaque admin
    print("\n4️⃣ TEST FILTRAGE POUR CHAQUE ADMIN:")
    for admin in admins:
        admin_username = admin.get('username', '')
        admin_department = admin.get('department', '')
        admin_location = admin.get('location', '')
        admin_role = admin.get('role', 'ADMIN')
        
        print(f"\n  👤 Admin: {admin_username} (Role: {admin_role})")
        print(f"     Département: '{admin_department}'")
        print(f"     Location: '{admin_location}'")
        
        # Construire le filtre
        if admin_role == 'SUPERADMIN':
            filter_query = {}
            print("     Filtre: SUPERADMIN - Voit tout")
        else:
            if admin_location and admin_department:
                filter_query = {
                    'targetLocation': admin_location,
                    'targetDepartment': admin_department
                }
                print(f"     Filtre: targetDepartment='{admin_department}' AND targetLocation='{admin_location}'")
            elif admin_department:
                filter_query = {'targetDepartment': admin_department}
                print(f"     Filtre: targetDepartment='{admin_department}'")
            else:
                filter_query = {'_id': None}
                print("     Filtre: Aucune conversation visible (pas de département défini)")
        
        # Appliquer le filtre
        filtered_conversations = list(chats_collection.find(filter_query))
        print(f"     Résultat: {len(filtered_conversations)} conversation(s) trouvée(s)")
        
        for conv in filtered_conversations:
            print(f"       ➡️ {conv.get('subject', 'N/A')} - {conv.get('targetDepartment', 'N/A')}/{conv.get('targetLocation', 'N/A')}")
    
    # 5. Recommandations
    print("\n5️⃣ RECOMMANDATIONS:")
    
    # Vérifier les valeurs exactes
    unique_target_depts = set()
    unique_target_locations = set()
    
    for conv in conversations:
        if conv.get('targetDepartment'):
            unique_target_depts.add(conv.get('targetDepartment'))
        if conv.get('targetLocation'):
            unique_target_locations.add(conv.get('targetLocation'))
    
    print(f"  📊 Départements cibles uniques dans les conversations: {sorted(unique_target_depts)}")
    print(f"  📊 Locations cibles uniques dans les conversations: {sorted(unique_target_locations)}")
    
    admin_depts = set()
    admin_locations = set()
    
    for admin in admins:
        if admin.get('department'):
            admin_depts.add(admin.get('department'))
        if admin.get('location'):
            admin_locations.add(admin.get('location'))
    
    print(f"  👥 Départements des admins: {sorted(admin_depts)}")
    print(f"  👥 Locations des admins: {sorted(admin_locations)}")
    
    # Détecter les incohérences
    print("\n6️⃣ INCOHÉRENCES DÉTECTÉES:")
    
    # Départements qui ne matchent pas
    missing_depts = unique_target_depts - admin_depts
    if missing_depts:
        print(f"  ⚠️ Départements dans conversations mais pas d'admin correspondant: {missing_depts}")
    
    # Locations qui ne matchent pas
    missing_locations = unique_target_locations - admin_locations
    if missing_locations:
        print(f"  ⚠️ Locations dans conversations mais pas d'admin correspondant: {missing_locations}")
    
    # Admins sans département/location
    for admin in admins:
        if not admin.get('department') and admin.get('role') != 'SUPERADMIN':
            print(f"  ⚠️ Admin '{admin.get('username')}' n'a pas de département défini")
        if not admin.get('location') and admin.get('role') != 'SUPERADMIN':
            print(f"  ⚠️ Admin '{admin.get('username')}' n'a pas de location définie")

def create_test_admin():
    """Créer un admin de test pour le département Production à Mateur"""
    print("\n🔧 CRÉATION D'UN ADMIN DE TEST")
    print("=" * 30)
    
    # Vérifier s'il existe déjà
    existing_admin = admins_collection.find_one({'username': 'admin_production_mateur'})
    if existing_admin:
        print("  ✅ Admin de test existe déjà")
        return
    
    # Créer l'admin
    test_admin = {
        'username': 'admin_production_mateur',
        'email': 'admin.production.mateur@leoni.com',
        'password': '$2b$12$test_hash_password',  # Mot de passe hashé fictif
        'role': 'ADMIN',
        'department': 'Production',
        'location': 'Mateur',
        'active': True,
        'createdAt': datetime.utcnow()
    }
    
    try:
        result = admins_collection.insert_one(test_admin)
        print(f"  ✅ Admin de test créé avec ID: {result.inserted_id}")
        print(f"     Username: admin_production_mateur")
        print(f"     Département: Production")
        print(f"     Location: Mateur")
        print(f"     Role: ADMIN")
    except Exception as e:
        print(f"  ❌ Erreur lors de la création: {e}")

if __name__ == "__main__":
    debug_chat_system()
    create_test_admin()
    
    print("\n" + "="*50)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("="*50)
