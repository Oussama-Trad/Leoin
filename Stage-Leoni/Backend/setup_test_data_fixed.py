#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

def setup_test_data_fixed():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔧 CONFIGURATION DES DONNÉES DE TEST (CORRIGÉE)")
        print("=" * 50)
        
        # 1. Créer des départements
        departments = [
            {
                "_id": ObjectId("688e3fcd8233d57cac4f9bb6"),
                "name": "IT",
                "description": "Département Informatique",
                "isActive": True,
                "createdAt": datetime.now()
            },
            {
                "_id": ObjectId("688e3fcd8233d57cac4f9bb7"),
                "name": "RH",
                "description": "Ressources Humaines", 
                "isActive": True,
                "createdAt": datetime.now()
            },
            {
                "_id": ObjectId("688e3fcd8233d57cac4f9bb8"),
                "name": "Production",
                "description": "Département Production",
                "isActive": True,
                "createdAt": datetime.now()
            }
        ]
        
        # Vérifier si les départements existent déjà
        if db.departements.count_documents({}) == 0:
            result = db.departements.insert_many(departments)
            print(f"✅ {len(result.inserted_ids)} départements créés")
        else:
            print("✅ Départements déjà existants")
        
        # 2. Créer des lieux de travail
        locations = [
            {
                "_id": ObjectId("688e3fcd8233d57cac4f9cc1"),
                "name": "Tunis Centre",
                "address": "Avenue Habib Bourguiba, Tunis",
                "isActive": True,
                "createdAt": datetime.now()
            },
            {
                "_id": ObjectId("688e3fcd8233d57cac4f9cc2"), 
                "name": "Sousse Usine",
                "address": "Zone Industrielle, Sousse",
                "isActive": True,
                "createdAt": datetime.now()
            }
        ]
        
        # Vérifier si les lieux existent déjà
        if db.locations.count_documents({}) == 0:
            result = db.locations.insert_many(locations)
            print(f"✅ {len(result.inserted_ids)} lieux de travail créés")
        else:
            print("✅ Lieux de travail déjà existants")
        
        # 3. Mettre à jour les utilisateurs existants au lieu d'en créer de nouveaux
        print("\n📝 MISE À JOUR DES UTILISATEURS EXISTANTS")
        print("=" * 40)
        
        # Mettre à jour oussamatrzd19@gmail.com
        result1 = db.users.update_one(
            {"email": "oussamatrzd19@gmail.com"},
            {
                "$set": {
                    "name": "Oussama Trad",
                    "phone": "98765432",
                    "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb6"),  # IT
                    "locationRef": ObjectId("688e3fcd8233d57cac4f9cc1"),    # Tunis Centre
                    "position": "Chef de projet"
                },
                "$unset": {
                    "department": "",  # Supprimer les anciennes clés hardcodées
                }
            }
        )
        
        if result1.modified_count > 0:
            print("✅ oussamatrzd19@gmail.com mis à jour avec les références")
        
        # Mettre à jour test@example.com
        result2 = db.users.update_one(
            {"email": "test@example.com"},
            {
                "$set": {
                    "name": "Utilisateur Test",
                    "phone": "123456789",
                    "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb7"),  # RH
                    "locationRef": ObjectId("688e3fcd8233d57cac4f9cc2"),    # Sousse Usine
                    "position": "Assistant RH"
                },
                "$unset": {
                    "department": "",
                }
            }
        )
        
        if result2.modified_count > 0:
            print("✅ test@example.com mis à jour avec les références")
        
        print("\n🎯 VÉRIFICATION DES DONNÉES")
        print("=" * 30)
        
        # Vérifier un utilisateur mis à jour
        user = db.users.find_one({"email": "oussamatrzd19@gmail.com"})
        if user:
            print(f"👤 Utilisateur: {user.get('name', 'N/A')}")
            print(f"   Email: {user.get('email')}")
            print(f"   DepartmentRef: {user.get('departmentRef')}")
            print(f"   LocationRef: {user.get('locationRef')}")
            print(f"   Position: {user.get('position')}")
        
        print("\n📋 COLLECTIONS FINALES")
        print("=" * 20)
        collections = db.list_collection_names()
        for coll in collections:
            count = db.count_documents({}) if coll in db.list_collection_names() else 0
            print(f"   {coll}: documents")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    setup_test_data_fixed()
