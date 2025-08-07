#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

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

def create_base_data():
    """Créer les données de base : locations, départements et utilisateur"""
    try:
        print("🏗️ Création des données de base...")
        
        # 1. Créer les locations
        print("\n📍 Création des sites de travail...")
        locations_data = [
            {
                "_id": ObjectId(),
                "name": "Sousse",
                "address": "Zone Industrielle, Sousse, Tunisie",
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "name": "Tunis",
                "address": "Zone Industrielle, Tunis, Tunisie", 
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "name": "Sfax",
                "address": "Zone Industrielle, Sfax, Tunisie",
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        # Supprimer anciennes locations
        locations_collection.delete_many({})
        # Insérer nouvelles locations
        locations_collection.insert_many(locations_data)
        print(f"✅ {len(locations_data)} sites créés")
        
        # 2. Créer les départements pour chaque location
        print("\n🏢 Création des départements...")
        departments_data = []
        
        for location in locations_data:
            # Départements communs pour chaque site
            dept_names = ["IT", "RH", "Production", "Finance", "Qualité", "Maintenance"]
            
            for dept_name in dept_names:
                dept = {
                    "_id": ObjectId(),
                    "name": dept_name,
                    "description": f"Département {dept_name} - {location['name']}",
                    "locationRef": location["_id"],
                    "isActive": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                departments_data.append(dept)
        
        # Supprimer anciens départements
        departments_collection.delete_many({})
        # Insérer nouveaux départements
        departments_collection.insert_many(departments_data)
        print(f"✅ {len(departments_data)} départements créés")
        
        # 3. Créer l'utilisateur de test
        print("\n👤 Création de l'utilisateur de test...")
        
        # Trouver la location Sousse et le département IT
        sousse_location = locations_collection.find_one({"name": "Sousse"})
        it_dept = departments_collection.find_one({"name": "IT", "locationRef": sousse_location["_id"]})
        
        # Supprimer utilisateur existant s'il existe
        users_collection.delete_many({"adresse1": "hh@gmail.com"})
        
        # Créer utilisateur
        password = "123456"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "firstName": "Oussama",
            "lastName": "Trad", 
            "adresse1": "hh@gmail.com",
            "phoneNumber": "20123456",
            "adresse2": "parent@gmail.com",
            "parentalPhoneNumber": "20654321",
            "password": hashed_password,
            "employeeId": "10000001",
            # Utiliser les références ET les champs directs
            "locationRef": sousse_location["_id"],
            "departmentRef": it_dept["_id"],
            "location": "Sousse",
            "department": "IT",
            "position": "Développeur",
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        users_collection.insert_one(user_data)
        print("✅ Utilisateur créé:")
        print(f"   📧 Adresse1: hh@gmail.com")
        print(f"   📧 Adresse2: parent@gmail.com")
        print(f"   🔑 Mot de passe: {password}")
        print(f"   🏢 Département: IT")
        print(f"   📍 Site: Sousse")
        
        # 4. Vérification
        print("\n🔍 Vérification des données créées:")
        locations_count = locations_collection.count_documents({})
        departments_count = departments_collection.count_documents({})
        users_count = users_collection.count_documents({})
        
        print(f"   📍 Sites: {locations_count}")
        print(f"   🏢 Départements: {departments_count}")  
        print(f"   👤 Utilisateurs: {users_count}")
        
        # Test des départements pour Sousse
        sousse_depts = list(departments_collection.find({"locationRef": sousse_location["_id"]}))
        print(f"   🏢 Départements à Sousse: {len(sousse_depts)}")
        for dept in sousse_depts:
            print(f"      - {dept['name']}")
            
        print("\n✅ Toutes les données de base ont été créées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_base_data()
