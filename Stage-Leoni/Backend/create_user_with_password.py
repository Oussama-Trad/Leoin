#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId
import bcrypt

def create_user_with_password():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔧 CRÉATION D'UTILISATEUR AVEC MOT DE PASSE")
        print("=" * 45)
        
        # Générer un hash pour le mot de passe "123456"
        password = "123456"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"🔐 Hash généré pour le mot de passe: {password}")
        
        # Mettre à jour oussamatrzd19@gmail.com
        result1 = db.users.update_one(
            {"email": "oussamatrzd19@gmail.com"},
            {
                "$set": {
                    "password": password_hash,
                    "name": "Oussama Trad",
                    "phone": "98765432",
                    "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb6"),  # IT
                    "locationRef": ObjectId("688e3fcd8233d57cac4f9cc1"),    # Tunis Centre
                    "position": "Chef de projet",
                    "isActive": True
                },
                "$unset": {
                    "department": ""  # Supprimer l'ancien champ
                }
            }
        )
        
        if result1.modified_count > 0:
            print("✅ oussamatrzd19@gmail.com mis à jour avec mot de passe")
        
        # Mettre à jour test@example.com
        result2 = db.users.update_one(
            {"email": "test@example.com"},
            {
                "$set": {
                    "password": password_hash,
                    "name": "Utilisateur Test",
                    "phone": "123456789",
                    "departmentRef": ObjectId("688e3fcd8233d57cac4f9bb7"),  # RH
                    "locationRef": ObjectId("688e3fcd8233d57cac4f9cc2"),    # Sousse Usine
                    "position": "Assistant RH",
                    "isActive": True
                },
                "$unset": {
                    "department": ""
                }
            }
        )
        
        if result2.modified_count > 0:
            print("✅ test@example.com mis à jour avec mot de passe")
        
        # Vérifier les utilisateurs
        print("\n👥 UTILISATEURS AVEC MOTS DE PASSE:")
        users = list(db.users.find(
            {"password": {"$exists": True}}, 
            {"email": 1, "name": 1, "departmentRef": 1, "locationRef": 1, "position": 1}
        ))
        
        for user in users:
            print(f"   📧 {user.get('email')}")
            print(f"      Nom: {user.get('name')}")
            print(f"      DepartmentRef: {user.get('departmentRef')}")
            print(f"      LocationRef: {user.get('locationRef')}")
            print(f"      Position: {user.get('position')}")
            print("   ---")
        
        print(f"\n✅ {len(users)} utilisateur(s) avec mot de passe configuré")
        print("🔑 Mot de passe pour tous: 123456")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_user_with_password()
