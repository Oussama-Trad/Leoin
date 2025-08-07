#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger la base de données des utilisateurs
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

def fix_users_database():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🧹 Nettoyage de la base de données utilisateurs...")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs
    users = list(users_collection.find({}))
    print(f"📊 Utilisateurs trouvés: {len(users)}")
    
    # Identifier les utilisateurs incomplets (sans email)
    incomplete_users = []
    for user in users:
        print(f"\n👤 Vérification utilisateur: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
        print(f"   Champs disponibles: {list(user.keys())}")
        
        # Vérifier si l'utilisateur a les champs essentiels
        has_email = 'email' in user and user['email']
        has_parental_email = 'parentalEmail' in user and user['parentalEmail'] 
        has_location = 'location' in user and user['location']
        has_department = 'department' in user and user['department']
        
        print(f"   ✅ Email: {has_email}")
        print(f"   ✅ Adresse2: {has_parental_email}")
        print(f"   ✅ Location: {has_location}")
        print(f"   ✅ Department: {has_department}")
        
        if not (has_email and has_parental_email and has_location and has_department):
            print(f"   ❌ Utilisateur incomplet détecté")
            incomplete_users.append(user)
        else:
            print(f"   ✅ Utilisateur complet")
    
    print(f"\n📊 Résumé:")
    print(f"   • Utilisateurs complets: {len(users) - len(incomplete_users)}")
    print(f"   • Utilisateurs incomplets: {len(incomplete_users)}")
    
    if incomplete_users:
        print(f"\n🗑️ Suppression des utilisateurs incomplets...")
        for user in incomplete_users:
            result = users_collection.delete_one({'_id': user['_id']})
            if result.deleted_count > 0:
                print(f"   ✅ Supprimé: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
            else:
                print(f"   ❌ Échec suppression: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
    
    # Vérifier le résultat final
    remaining_users = list(users_collection.find({}))
    print(f"\n✅ Nettoyage terminé. Utilisateurs restants: {len(remaining_users)}")
    
    for user in remaining_users:
        print(f"   👤 {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')} - {user.get('email', 'N/A')}")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🧹 Correction de la base de données utilisateurs")
    print("=" * 60)
    
    fix_users_database()
