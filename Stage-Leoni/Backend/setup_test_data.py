#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

def setup_test_data():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔧 CONFIGURATION DES DONNÉES DE TEST")
        print("=" * 40)
        
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
        
        # Supprimer et recréer la collection départements
        db.departements.drop()
        result = db.departements.insert_many(departments)
        print(f"✅ {len(result.inserted_ids)} départements créés")
        
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
        
        # Supprimer et recréer la collection locations
        db.locations.drop()
        result = db.locations.insert_many(locations)
        print(f"✅ {len(result.inserted_ids)} lieux de travail créés")
        
        # 3. Créer un utilisateur de test avec les bonnes références
        test_user = {
            "_id": ObjectId("688bda31852e29fc18c4c42d"),
            "email": "test@leoni.com",
            "name": "Utilisateur Test",
            "phone": "123456789",
            "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb6"),  # IT
            "locationRef": ObjectId("688e3fcd8233d57cac4f9cc1"),    # Tunis Centre
            "position": "Développeur",
            "createdAt": datetime.now(),
            "isActive": True
        }
        
        # Supprimer l'ancien utilisateur et créer le nouveau
        db.users.delete_one({"email": "test@leoni.com"})
        result = db.users.insert_one(test_user)
        print(f"✅ Utilisateur test créé avec ID: {result.inserted_id}")
        
        # 4. Mettre à jour un utilisateur existant
        existing_user = db.users.find_one({"email": "oussamatrzd19@gmail.com"})
        if existing_user:
            db.users.update_one(
                {"email": "oussamatrzd19@gmail.com"},
                {
                    "$set": {
                        "name": "Oussama",
                        "phone": "98765432",
                        "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb6"),  # IT
                        "locationRef": ObjectId("688e3fcd8233d57cac4f9cc1"),    # Tunis Centre
                        "position": "Chef de projet"
                    },
                    "$unset": {
                        "department": "",
                        "position": ""  # Supprimer les anciennes clés hardcodées
                    }
                }
            )
            print("✅ Utilisateur oussamatrzd19@gmail.com mis à jour")
        
        print("\n🎯 RÉSUMÉ DE LA CONFIGURATION")
        print("=" * 30)
        print("✅ 3 départements créés (IT, RH, Production)")
        print("✅ 2 lieux de travail créés (Tunis Centre, Sousse Usine)")
        print("✅ Utilisateur test@leoni.com créé avec références correctes")
        print("✅ Utilisateur oussamatrzd19@gmail.com mis à jour")
        print("\n📝 Vous pouvez maintenant vous connecter avec:")
        print("   - test@leoni.com (nouvel utilisateur)")
        print("   - oussamatrzd19@gmail.com (utilisateur existant mis à jour)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    setup_test_data()
