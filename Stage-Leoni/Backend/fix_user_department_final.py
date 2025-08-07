#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson import ObjectId

def fix_user_department():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔧 CORRECTION DE LA RÉFÉRENCE DÉPARTEMENT")
        print("=" * 45)
        
        # Trouver l'utilisateur avec l'ancien departmentRef
        old_dept_ref = "688bd7b34a733682695ff214"
        user = db.users.find_one({"departmentRef": ObjectId(old_dept_ref)})
        
        if user:
            print(f"👤 Utilisateur trouvé: {user.get('email')}")
            print(f"   Ancien departmentRef: {user.get('departmentRef')}")
            
            # Nouveau departmentRef (IT department)
            new_dept_ref = ObjectId("688e3fcd8233d57cac4f9bb6")
            
            # Mettre à jour l'utilisateur
            result = db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "departmentRef": new_dept_ref,
                        "locationRef": ObjectId("688e3fcd8233d57cac4f9cc1"),  # Tunis Centre
                        "name": user.get("name", "Utilisateur"),
                        "phone": user.get("phone", "123456789"),
                        "position": user.get("position", "Employé")
                    },
                    "$unset": {
                        "department": ""  # Supprimer l'ancien champ hardcodé
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Utilisateur mis à jour avec le nouveau departmentRef: {new_dept_ref}")
                
                # Vérifier le résultat
                updated_user = db.users.find_one({"_id": user["_id"]})
                print(f"\n📋 UTILISATEUR APRÈS MISE À JOUR:")
                print(f"   Email: {updated_user.get('email')}")
                print(f"   Nom: {updated_user.get('name')}")
                print(f"   DepartmentRef: {updated_user.get('departmentRef')}")
                print(f"   LocationRef: {updated_user.get('locationRef')}")
                print(f"   Position: {updated_user.get('position')}")
                
                # Vérifier que le département existe
                dept = db.departements.find_one({"_id": new_dept_ref})
                if dept:
                    print(f"\n✅ Département trouvé: {dept.get('name')}")
                else:
                    print(f"\n❌ Département non trouvé pour l'ID: {new_dept_ref}")
                
            else:
                print("❌ Aucune modification effectuée")
        else:
            print(f"❌ Aucun utilisateur trouvé avec departmentRef: {old_dept_ref}")
            
            # Chercher tous les utilisateurs
            print("\n🔍 TOUS LES UTILISATEURS:")
            all_users = list(db.users.find({}, {"email": 1, "departmentRef": 1}))
            for u in all_users:
                print(f"   {u.get('email')}: {u.get('departmentRef', 'N/A')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_user_department()
