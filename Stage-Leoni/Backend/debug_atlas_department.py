#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.objectid import ObjectId
import os

def debug_atlas_department():
    try:
        # Connexion à MongoDB Atlas
        MONGODB_ATLAS_URI = 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp'
        client = MongoClient(MONGODB_ATLAS_URI)
        db = client['LeoniApp']
        
        print("🔍 DEBUG MONGODB ATLAS - DÉPARTEMENTS")
        print("=" * 50)
        
        # 1. Vérifier les collections disponibles
        collections = db.list_collection_names()
        print(f"📋 Collections disponibles: {collections}")
        
        # 2. Vérifier les utilisateurs
        print(f"\n👥 UTILISATEURS:")
        users = list(db.users.find({}, {
            'email': 1, 
            'name': 1, 
            'departmentRef': 1, 
            'locationRef': 1,
            'department': 1,
            'position': 1
        }))
        
        for user in users:
            print(f"   📧 {user.get('email')}")
            print(f"      Name: {user.get('name')}")
            print(f"      DepartmentRef: {user.get('departmentRef')} (type: {type(user.get('departmentRef'))})")
            print(f"      LocationRef: {user.get('locationRef')} (type: {type(user.get('locationRef'))})")
            print(f"      Department field: {user.get('department')}")
            print(f"      Position: {user.get('position')}")
            print("   ---")
        
        # 3. Vérifier les départements (différents noms possibles)
        dept_collections = ['departements', 'departments', 'department']
        
        for coll_name in dept_collections:
            if coll_name in collections:
                print(f"\n🏢 COLLECTION '{coll_name.upper()}':")
                depts = list(db[coll_name].find({}))
                for dept in depts:
                    print(f"   ID: {dept.get('_id')} (type: {type(dept.get('_id'))})")
                    print(f"   Name: {dept.get('name')}")
                    print(f"   Active: {dept.get('isActive', dept.get('active'))}")
                    print("   ---")
        
        # 4. Vérifier les locations
        loc_collections = ['locations', 'location', 'sites']
        
        for coll_name in loc_collections:
            if coll_name in collections:
                print(f"\n🏗️ COLLECTION '{coll_name.upper()}':")
                locs = list(db[coll_name].find({}))
                for loc in locs:
                    print(f"   ID: {loc.get('_id')} (type: {type(loc.get('_id'))})")
                    print(f"   Name: {loc.get('name')}")
                    print(f"   Active: {loc.get('isActive', loc.get('active'))}")
                    print("   ---")
        
        # 5. Simuler la logique de l'endpoint /me
        print(f"\n🔍 SIMULATION ENDPOINT /ME:")
        
        # Prendre le premier utilisateur avec departmentRef
        user_with_dept = None
        for user in users:
            if user.get('departmentRef'):
                user_with_dept = user
                break
        
        if user_with_dept:
            print(f"   👤 Test avec utilisateur: {user_with_dept.get('email')}")
            dept_ref = user_with_dept.get('departmentRef')
            print(f"   🔍 Recherche département avec ID: {dept_ref} (type: {type(dept_ref)})")
            
            # Essayer de trouver le département
            dept_found = None
            for coll_name in dept_collections:
                if coll_name in collections:
                    try:
                        dept_found = db[coll_name].find_one({'_id': dept_ref})
                        if dept_found:
                            print(f"   ✅ Département trouvé dans '{coll_name}': {dept_found.get('name')}")
                            break
                        else:
                            print(f"   ❌ Département non trouvé dans '{coll_name}'")
                    except Exception as e:
                        print(f"   ❌ Erreur recherche dans '{coll_name}': {e}")
            
            if not dept_found:
                print(f"   ❌ AUCUN département trouvé pour l'ID: {dept_ref}")
                print(f"   🔧 Ceci explique pourquoi 'Non spécifié' est retourné")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    debug_atlas_department()
