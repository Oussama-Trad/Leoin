#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger la référence de département vers un département IT existant
"""

from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

def connect_to_mongodb():
    try:
        print("🔍 Connexion à MongoDB Atlas...")
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        client.server_info()  # Test de connexion
        print("✅ Connexion MongoDB Atlas réussie")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def fix_user_department():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    departments_collection = db['departments']
    
    print("\n🔧 Correction de la référence de département...")
    print("=" * 60)
    
    # Récupérer l'utilisateur
    user = users_collection.find_one({'email': 'aa@gmail.com'})
    
    if not user:
        print("❌ Utilisateur aa@gmail.com non trouvé")
        return False
        
    print(f"👤 Utilisateur: {user['firstName']} {user['lastName']}")
    print(f"📧 Email: {user['email']}")
    print(f"🏭 DepartmentRef actuel: {user.get('departmentRef')}")
    print(f"🏭 Department actuel: {user.get('department')}")
    
    # Trouver un département IT dans la nouvelle structure
    it_departments = list(departments_collection.find({'name': 'IT'}))
    
    print(f"\n🔍 Départements IT trouvés: {len(it_departments)}")
    
    if it_departments:
        # Prendre le premier département IT (ils sont tous équivalents maintenant)
        new_it_dept = it_departments[0]
        print(f"✅ Nouveau département IT sélectionné:")
        print(f"   • ID: {new_it_dept['_id']}")
        print(f"   • Nom: {new_it_dept['name']}")
        print(f"   • Champs: {list(new_it_dept.keys())}")
        
        # Mettre à jour l'utilisateur
        print(f"\n🔧 Mise à jour de l'utilisateur...")
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'departmentRef': new_it_dept['_id'],
                'department': new_it_dept['name']  # Mettre à jour aussi le nom
            }}
        )
        
        if result.modified_count > 0:
            print(f"✅ Utilisateur mis à jour avec succès")
            
            # Vérifier le résultat
            updated_user = users_collection.find_one({'_id': user['_id']})
            print(f"📊 Nouvelles données utilisateur:")
            print(f"   • DepartmentRef: {updated_user.get('departmentRef')}")
            print(f"   • Department: {updated_user.get('department')}")
        else:
            print(f"❌ Échec de la mise à jour")
    else:
        print(f"❌ Aucun département IT trouvé")
        
        # Lister tous les départements disponibles
        all_depts = list(departments_collection.find({}).limit(10))
        print(f"\n📋 Premiers départements disponibles:")
        for dept in all_depts:
            print(f"   • {dept['name']} (ID: {dept['_id']})")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Correction de la référence de département utilisateur")
    print("=" * 60)
    
    fix_user_department()
