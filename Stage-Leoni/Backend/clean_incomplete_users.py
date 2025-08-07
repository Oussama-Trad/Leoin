#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour nettoyer les utilisateurs incomplets
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

def clean_incomplete_users():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🔍 Recherche des utilisateurs incomplets...")
    print("=" * 60)
    
    # Trouver les utilisateurs sans email (incomplets)
    incomplete_users = list(users_collection.find({'email': {'$exists': False}}))
    
    print(f"📊 Utilisateurs incomplets trouvés: {len(incomplete_users)}")
    
    if len(incomplete_users) > 0:
        print("\n👤 Utilisateurs à supprimer:")
        for user in incomplete_users:
            print(f"   • {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')} (ID: {user.get('employeeId', user['_id'])})")
        
        # Supprimer automatiquement
        print(f"\n🗑️  Suppression automatique de {len(incomplete_users)} utilisateurs incomplets...")
        result = users_collection.delete_many({'email': {'$exists': False}})
        print(f"✅ {result.deleted_count} utilisateurs supprimés")
    else:
        print("✅ Aucun utilisateur incomplet trouvé")
    
    # Afficher les utilisateurs restants
    remaining_users = list(users_collection.find({}))
    print(f"\n📊 Utilisateurs restants: {len(remaining_users)}")
    
    for user in remaining_users:
        print(f"   • {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')} - {user.get('email', 'N/A')}")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🧹 Nettoyage des utilisateurs incomplets")
    print("=" * 60)
    
    clean_incomplete_users()
