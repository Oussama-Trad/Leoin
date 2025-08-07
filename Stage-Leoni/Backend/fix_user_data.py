#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import bcrypt

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB Atlas
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['leoni_app']

# Collections
users_collection = db['users']
departments_collection = db['departments']
locations_collection = db['locations']

def fix_user_department_location():
    """Corriger les données utilisateur pour afficher le département et site de travail"""
    try:
        print("🔍 Recherche de l'utilisateur hh@gmail.com...")
        
        # Trouver l'utilisateur avec l'email hh@gmail.com
        user = users_collection.find_one({'email': 'hh@gmail.com'})
        if not user:
            print("❌ Utilisateur hh@gmail.com non trouvé")
            print("✅ Création d'un nouvel utilisateur...")
            
            # Créer un nouvel utilisateur
            new_password = "123456"
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            new_user = {
                'firstName': 'Oussama',
                'lastName': 'Trad',
                'email': 'hh@gmail.com',
                'password': hashed_password,
                'department': 'IT',
                'location': 'Sousse',
                'phoneNumber': '12345678',
                'parentalEmail': 'parent@gmail.com',
                'parentalPhoneNumber': '87654321',
                'employeeId': 'EMP001',
                'position': 'Développeur',
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            result = users_collection.insert_one(new_user)
            if result.inserted_id:
                print("✅ Utilisateur créé avec succès!")
                print(f"📧 Email: hh@gmail.com")
                print(f"🔑 Mot de passe: {new_password}")
                print(f"🏢 Département: IT")
                print(f"📍 Site de travail: Sousse")
            return
            
        print(f"✅ Utilisateur trouvé: {user['firstName']} {user['lastName']}")
        print(f"📧 Email: {user['email']}")
        
        # Nouveau mot de passe simple pour les tests
        new_password = "123456"
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Ajouter directement les champs department et location comme strings + reset password
        update_data = {
            'department': 'IT',
            'location': 'Sousse',
            'password': hashed_password
        }
        
        # Mettre à jour l'utilisateur
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print("✅ Utilisateur mis à jour avec succès!")
            print(f"✅ Département: IT")
            print(f"✅ Site de travail: Sousse")
            print(f"✅ Nouveau mot de passe: {new_password}")
            
            # Vérifier la mise à jour
            updated_user = users_collection.find_one({'_id': user['_id']})
            print("\n🔍 Vérification des données mises à jour:")
            print(f"- Département: {updated_user.get('department', 'NON DÉFINI')}")
            print(f"- Site de travail: {updated_user.get('location', 'NON DÉFINI')}")
            print(f"- Email: {updated_user['email']}")
            print(f"- Mot de passe réinitialisé: OUI")
        else:
            print("❌ Aucune modification effectuée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_user_department_location()
