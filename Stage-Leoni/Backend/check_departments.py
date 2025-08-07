#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def check_departments():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔍 VÉRIFICATION DE LA COLLECTION DÉPARTEMENTS")
        print("=" * 50)
        
        # Lister tous les départements
        departments = list(db.departements.find({}))
        
        if not departments:
            print("❌ Aucun département trouvé dans la collection 'departements'")
            
            # Vérifier d'autres noms possibles de collection
            collections = db.list_collection_names()
            print(f"📋 Collections disponibles: {collections}")
            
            # Chercher des collections similaires
            dept_collections = [c for c in collections if 'dept' in c.lower() or 'department' in c.lower()]
            if dept_collections:
                print(f"🔍 Collections liées aux départements trouvées: {dept_collections}")
                
                for coll_name in dept_collections:
                    items = list(db[coll_name].find({}))
                    print(f"\n--- Collection '{coll_name}' ({len(items)} documents) ---")
                    for item in items[:3]:  # Afficher les 3 premiers
                        print(f"  ID: {item.get('_id')}")
                        print(f"  Nom: {item.get('name', item.get('nom', 'N/A'))}")
                        print(f"  Actif: {item.get('isActive', item.get('active', 'N/A'))}")
                        print("  ---")
        else:
            print(f"✅ {len(departments)} département(s) trouvé(s):")
            print()
            
            for i, dept in enumerate(departments, 1):
                print(f"📁 Département {i}:")
                print(f"   ID: {dept.get('_id')}")
                print(f"   Nom: {dept.get('name', dept.get('nom', 'N/A'))}")
                print(f"   Actif: {dept.get('isActive', dept.get('active', 'N/A'))}")
                
                # Afficher toutes les clés disponibles
                keys = list(dept.keys())
                print(f"   Clés disponibles: {keys}")
                print()
        
        # Vérifier aussi l'utilisateur
        print("\n🧍‍♂️ VÉRIFICATION DE L'UTILISATEUR")
        print("=" * 35)
        
        user = db.users.find_one({"email": "hh@gmail.com"})
        if user:
            print(f"✅ Utilisateur trouvé:")
            print(f"   Email: {user.get('email')}")
            print(f"   DepartmentRef: {user.get('departmentRef')}")
            print(f"   LocationRef: {user.get('locationRef')}")
        else:
            print("❌ Utilisateur hh@gmail.com non trouvé")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_departments()
