#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour déboguer les données d'un utilisateur spécifique
"""

from pymongo import MongoClient
from datetime import datetime
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

def debug_user_profile():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print("\n🔍 Analyse des utilisateurs...")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs avec TOUS les champs
    users = list(users_collection.find({}))
    
    print(f"📊 Nombre d'utilisateurs: {len(users)}")
    
    for i, user in enumerate(users, 1):
        print(f"\n👤 Utilisateur {i}:")
        print(f"   • Nom: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
        print(f"   • Email: {user.get('email', 'N/A')}")
        print(f"   • Department: {user.get('department', 'NON DÉFINI')}")
        print(f"   • Location: {user.get('location', 'NON DÉFINI')}")
        print(f"   • LocationRef: {user.get('locationRef', 'NON DÉFINI')}")
        print(f"   • DepartmentRef: {user.get('departmentRef', 'NON DÉFINI')}")
        print(f"   • Créé le: {user.get('createdAt', 'N/A')}")
        
        # Afficher tous les champs disponibles pour debug
        print(f"   • TOUS LES CHAMPS: {list(user.keys())}")
        
        # Vérifier si les références existent
        if user.get('locationRef'):
            location = locations_collection.find_one({'_id': user['locationRef']})
            if location:
                print(f"   ✅ Location trouvée: {location['name']}")
            else:
                print(f"   ❌ Location NOT FOUND pour ID: {user['locationRef']}")
                
        if user.get('departmentRef'):
            department = departments_collection.find_one({'_id': user['departmentRef']})
            if department:
                print(f"   ✅ Department trouvé: {department['name']}")
            else:
                print(f"   ❌ Department NOT FOUND pour ID: {user['departmentRef']}")
    
    # Statistiques
    print(f"\n📈 Statistiques:")
    users_with_location = len([u for u in users if u.get('location') and u.get('location') != 'Non spécifié'])
    users_with_department = len([u for u in users if u.get('department') and u.get('department') != 'Non spécifié'])
    
    print(f"   • Utilisateurs avec location définie: {users_with_location}/{len(users)}")
    print(f"   • Utilisateurs avec département défini: {users_with_department}/{len(users)}")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔍 Debug des profils utilisateurs")
    print("=" * 60)
    
    debug_user_profile()
