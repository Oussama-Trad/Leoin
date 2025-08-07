#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_users():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔍 UTILISATEURS DANS LA BASE DE DONNÉES")
        print("=" * 40)
        
        # Lister tous les utilisateurs
        users = list(db.users.find({}, {
            'email': 1, 
            'name': 1, 
            'departmentRef': 1, 
            'locationRef': 1,
            'department': 1,
            'location': 1,
            'workSite': 1,
            'position': 1
        }))
        
        if not users:
            print("❌ Aucun utilisateur trouvé")
        else:
            print(f"✅ {len(users)} utilisateur(s) trouvé(s):")
            print()
            
            for i, user in enumerate(users, 1):
                print(f"👤 Utilisateur {i}:")
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Nom: {user.get('name', 'N/A')}")
                print(f"   DepartmentRef: {user.get('departmentRef', 'N/A')}")
                print(f"   LocationRef: {user.get('locationRef', 'N/A')}")
                print(f"   Department: {user.get('department', 'N/A')}")
                print(f"   Location: {user.get('location', 'N/A')}")
                print(f"   WorkSite: {user.get('workSite', 'N/A')}")
                print(f"   Position: {user.get('position', 'N/A')}")
                
                # Afficher toutes les clés disponibles
                keys = [k for k in user.keys() if k != '_id']
                print(f"   Clés disponibles: {keys}")
                print()
        
        # Vérifier les collections disponibles
        print("\n📋 COLLECTIONS DISPONIBLES")
        print("=" * 25)
        collections = db.list_collection_names()
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"   {coll}: {count} documents")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_users()
