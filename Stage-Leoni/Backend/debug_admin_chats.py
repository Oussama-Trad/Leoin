#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier pourquoi les admins ne voient pas les conversations
"""
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

try:
    client = MongoClient(MONGODB_URI)
    db = client.LeoniApp
    
    chats_collection = db.chats
    admins_collection = db.admins
    users_collection = db.users
    departments_collection = db.departments
    
    print("🔍 DIAGNOSTIC ADMIN CHATS")
    print("=" * 50)
    
    # 1. Vérifier les conversations existantes
    print("\n1. CONVERSATIONS EXISTANTES:")
    conversations = list(chats_collection.find({}))
    print(f"   Total conversations: {len(conversations)}")
    
    if conversations:
        for i, conv in enumerate(conversations[:3], 1):  # Afficher les 3 premières
            print(f"\n   Conversation {i}:")
            print(f"   - ID: {conv['_id']}")
            print(f"   - Subject: {conv.get('subject', 'N/A')}")
            print(f"   - Target Department: {conv.get('targetDepartment', 'N/A')}")
            print(f"   - Target Location: {conv.get('targetLocation', 'N/A')}")
            print(f"   - Status: {conv.get('status', 'N/A')}")
            print(f"   - User Name: {conv.get('userName', 'N/A')}")
            print(f"   - Created At: {conv.get('createdAt', 'N/A')}")
    
    # 2. Vérifier les admins existants
    print("\n\n2. ADMINS EXISTANTS:")
    admins = list(admins_collection.find({}))
    print(f"   Total admins: {len(admins)}")
    
    if admins:
        for i, admin in enumerate(admins, 1):
            print(f"\n   Admin {i}:")
            print(f"   - Username: {admin.get('username', 'N/A')}")
            print(f"   - Department: {admin.get('department', 'N/A')}")
            print(f"   - Location: {admin.get('location', 'N/A')}")
            print(f"   - Role: {admin.get('role', 'N/A')}")
            print(f"   - Active: {admin.get('active', 'N/A')}")
    else:
        print("   ⚠️  AUCUN ADMIN TROUVÉ!")
        print("   Créons un admin de test...")
        
        # Créer un admin de test
        test_admin = {
            'username': 'trad',
            'password': 'admin123',  # En production, utilisez un hash
            'department': 'Production',
            'location': 'Mateur',
            'role': 'ADMIN',
            'active': True,
            'createdAt': datetime.utcnow()
        }
        
        result = admins_collection.insert_one(test_admin)
        print(f"   ✅ Admin de test créé avec ID: {result.inserted_id}")
    
    # 3. Vérifier les départements
    print("\n\n3. DÉPARTEMENTS EXISTANTS:")
    departments = list(departments_collection.find({}))
    print(f"   Total départements: {len(departments)}")
    
    dept_names = []
    dept_locations = []
    for dept in departments:
        name = dept.get('name', 'N/A')
        location = dept.get('location', 'N/A')
        dept_names.append(name)
        dept_locations.append(location)
        print(f"   - {name} @ {location}")
    
    # 4. Test de filtrage admin
    print("\n\n4. TEST DE FILTRAGE ADMIN:")
    if admins and conversations:
        admin = admins[0]  # Premier admin
        admin_dept = admin.get('department')
        admin_location = admin.get('location')
        
        print(f"   Admin: {admin.get('username')} ({admin_dept} @ {admin_location})")
        
        # Filtre exact comme dans le code
        filter_query = {
            'targetLocation': admin_location,
            'targetDepartment': admin_dept
        }
        
        print(f"   Filtre: {filter_query}")
        
        matching_convs = list(chats_collection.find(filter_query))
        print(f"   Conversations correspondantes: {len(matching_convs)}")
        
        if len(matching_convs) == 0:
            print("\n   🔍 ANALYSE DES INCOMPATIBILITÉS:")
            
            # Vérifier les valeurs uniques dans les conversations
            unique_target_depts = list(chats_collection.distinct('targetDepartment'))
            unique_target_locs = list(chats_collection.distinct('targetLocation'))
            
            print(f"   Target Departments dans les conversations: {unique_target_depts}")
            print(f"   Target Locations dans les conversations: {unique_target_locs}")
            print(f"   Admin Department: '{admin_dept}'")
            print(f"   Admin Location: '{admin_location}'")
            
            # Vérifications de compatibilité
            if admin_dept not in unique_target_depts:
                print(f"   ❌ Le département admin '{admin_dept}' ne correspond à aucune conversation")
                if unique_target_depts:
                    print(f"   💡 Suggestion: Changer le département admin vers: {unique_target_depts[0]}")
            
            if admin_location not in unique_target_locs:
                print(f"   ❌ La location admin '{admin_location}' ne correspond à aucune conversation")
                if unique_target_locs:
                    print(f"   💡 Suggestion: Changer la location admin vers: {unique_target_locs[0]}")
    
    # 5. Proposer une solution
    print("\n\n5. SOLUTION RECOMMANDÉE:")
    if conversations and admins:
        conv = conversations[0]
        admin = admins[0]
        
        target_dept = conv.get('targetDepartment')
        target_loc = conv.get('targetLocation')
        
        print(f"   Pour que l'admin voit les conversations:")
        print(f"   - Mettre le département admin à: '{target_dept}'")
        print(f"   - Mettre la location admin à: '{target_loc}'")
        
        # Mise à jour automatique
        update_result = admins_collection.update_one(
            {'_id': admin['_id']},
            {'$set': {
                'department': target_dept,
                'location': target_loc
            }}
        )
        
        if update_result.modified_count > 0:
            print(f"   ✅ Admin '{admin.get('username')}' mis à jour automatiquement!")
        
        # Re-test du filtrage
        updated_filter = {
            'targetLocation': target_loc,
            'targetDepartment': target_dept
        }
        
        matching_convs_after = list(chats_collection.find(updated_filter))
        print(f"   ✅ Conversations visibles après mise à jour: {len(matching_convs_after)}")
    
    print("\n" + "=" * 50)
    print("✅ DIAGNOSTIC TERMINÉ")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    if 'client' in locals():
        client.close()
