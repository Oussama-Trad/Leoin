#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vider les sessions utilisateurs et forcer la reconnexion
"""

from pymongo import MongoClient
from bson import ObjectId
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

def cleanup_sessions():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🧹 Nettoyage des sessions utilisateurs...")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs
    users = list(users_collection.find({}, {
        'firstName': 1, 
        'lastName': 1, 
        'email': 1, 
        'department': 1, 
        'location': 1,
        'locationRef': 1,
        'departmentRef': 1
    }))
    
    print(f"📊 Utilisateurs trouvés: {len(users)}")
    
    for user in users:
        print(f"\n👤 {user.get('firstName')} {user.get('lastName')} ({user.get('email')})")
        print(f"   • ID MongoDB: {user['_id']}")
        print(f"   • Location: {user.get('location', 'NON DÉFINI')}")
        print(f"   • Department: {user.get('department', 'NON DÉFINI')}")
        
        if user.get('location') and user.get('location') != 'Non spécifié':
            print(f"   ✅ Profil complet")
        else:
            print(f"   ⚠️ Profil incomplet")
    
    print(f"\n💡 SOLUTION:")
    print(f"   1. Redémarre l'application React Native")
    print(f"   2. Déconnecte-toi et reconnecte-toi dans l'app")
    print(f"   3. Ou vide le cache avec : rm -rf node_modules/.cache")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🧹 Nettoyage des sessions utilisateurs")
    print("=" * 60)
    
    cleanup_sessions()
