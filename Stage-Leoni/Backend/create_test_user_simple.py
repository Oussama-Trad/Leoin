#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour créer un utilisateur de test simple
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

def create_test_user():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print("\n👤 Création d'un utilisateur de test...")
    print("=" * 60)
    
    # Données de l'utilisateur de test
    test_email = "test@leoni.com"
    test_password = "123456"
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = users_collection.find_one({'email': test_email})
    if existing_user:
        print(f"✅ Utilisateur de test existe déjà: {test_email}")
        print(f"🔑 Mot de passe: {test_password}")
        return True
    
    # Récupérer une location (Messadine)
    location = locations_collection.find_one({'name': 'Messadine'})
    if not location:
        print("❌ Location 'Messadine' non trouvée")
        return False
    
    # Récupérer un département IT
    it_department = departments_collection.find_one({'name': 'IT'})
    if not it_department:
        print("❌ Département 'IT' non trouvé")
        return False
    
    print(f"🏢 Location: {location['name']} (ID: {location['_id']})")
    print(f"🏭 Département: {it_department['name']} (ID: {it_department['_id']})")
    
    # Hacher le mot de passe
    hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
    
    # Créer l'utilisateur de test
    test_user = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': test_email,
        'parentalEmail': 'parent@leoni.com',
        'phoneNumber': '12345678',
        'parentalPhoneNumber': '87654321',
        'password': hashed_password,
        'employeeId': 'TEST001',
        'department': it_department['name'],
        'position': 'Testeur',
        'locationRef': location['_id'],
        'departmentRef': it_department['_id'],
        'location': location['name'],
        'profilePicture': None,
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow()
    }
    
    # Insérer l'utilisateur
    result = users_collection.insert_one(test_user)
    
    if result.inserted_id:
        print(f"✅ Utilisateur de test créé avec succès!")
        print(f"📧 Email: {test_email}")
        print(f"🔑 Mot de passe: {test_password}")
        print(f"👤 ID: {result.inserted_id}")
        print(f"🏢 Location: {location['name']}")
        print(f"🏭 Département: {it_department['name']}")
    else:
        print(f"❌ Échec de la création de l'utilisateur de test")
    
    client.close()
    return True

if __name__ == "__main__":
    print("👤 Création d'un utilisateur de test")
    print("=" * 60)
    
    create_test_user()
