#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.objectid import ObjectId

def fix_atlas_user_department():
    try:
        # Connexion à MongoDB Atlas
        MONGODB_ATLAS_URI = 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp'
        client = MongoClient(MONGODB_ATLAS_URI)
        db = client['LeoniApp']
        
        print("🔧 CORRECTION DÉPARTEMENT ATLAS")
        print("=" * 35)
        
        # Trouver l'ID du département IT
        it_dept = db.departments.find_one({"name": "IT"})
        if not it_dept:
            print("❌ Département IT non trouvé")
            return
        
        it_dept_id = it_dept["_id"]
        print(f"✅ Département IT trouvé: {it_dept_id}")
        
        # Mettre à jour l'utilisateur hh@gmail.com
        result = db.users.update_one(
            {"email": "hh@gmail.com"},
            {
                "$set": {
                    "departmentRef": it_dept_id,  # ObjectId correct
                    "name": "User HH"
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Utilisateur hh@gmail.com mis à jour")
            
            # Vérifier le résultat
            user = db.users.find_one({"email": "hh@gmail.com"})
            print(f"📋 Nouveau departmentRef: {user.get('departmentRef')} (type: {type(user.get('departmentRef'))})")
            
            # Tester la résolution
            dept = db.departments.find_one({"_id": user.get('departmentRef')})
            if dept:
                print(f"✅ Résolution réussie: {dept.get('name')}")
            else:
                print("❌ Résolution échouée")
        else:
            print("❌ Aucune modification")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_atlas_user_department()
