#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour réinitialiser le mot de passe de l'utilisateur existant
"""

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import bcrypt

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

def reset_user_password():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🔐 Réinitialisation du mot de passe...")
    print("=" * 60)
    
    # Trouver l'utilisateur aa@gmail.com
    user = users_collection.find_one({'email': 'aa@gmail.com'})
    
    if not user:
        print("❌ Utilisateur aa@gmail.com introuvable")
        return False
        
    print(f"👤 Utilisateur trouvé: {user['firstName']} {user['lastName']}")
    print(f"📧 Email: {user['email']}")
    
    # Nouveau mot de passe simple
    new_password = "123456"
    
    # Hacher le nouveau mot de passe
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Mettre à jour le mot de passe dans la base de données
    result = users_collection.update_one(
        {'_id': user['_id']},
        {
            '$set': {
                'password': hashed_password,
                'updatedAt': datetime.utcnow()
            }
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ Mot de passe mis à jour avec succès")
        print(f"🔑 Nouveau mot de passe: {new_password}")
        print(f"📧 Email pour se connecter: {user['email']}")
    else:
        print("❌ Échec de la mise à jour du mot de passe")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔐 Réinitialisation du mot de passe utilisateur")
    print("=" * 60)
    
    reset_user_password()
