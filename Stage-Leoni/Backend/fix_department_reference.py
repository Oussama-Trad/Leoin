#!/usr/bin/env python3
"""
Script pour corriger la référence du département de l'utilisateur hh@gmail.com
"""

import pymongo
from pymongo import MongoClient
from bson import ObjectId

def main():
    try:
        # Connexion à MongoDB avec la bonne URI
        client = MongoClient('mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp?retryWrites=true&w=majority')
        db = client['LeoniApp']
        
        print("🔍 CORRECTION DE LA RÉFÉRENCE DÉPARTEMENT")
        print("=" * 50)
        
        # 1. Chercher l'utilisateur
        user = db.users.find_one({'email': 'hh@gmail.com'})
        
        if not user:
            print("❌ Utilisateur avec email hh@gmail.com non trouvé")
            return
            
        print("✅ Utilisateur trouvé:")
        print(f"   - ID: {user['_id']}")
        print(f"   - Email: {user['email']}")
        print(f"   - DepartmentRef actuel: {user.get('departmentRef', 'VIDE')}")
        print()
        
        # 2. Chercher le département IT
        it_department = db.departements.find_one({'name': 'IT', 'active': True})
        
        if not it_department:
            print("❌ Département IT non trouvé!")
            return
            
        print("✅ Département IT trouvé:")
        print(f"   - ID: {it_department['_id']}")
        print(f"   - Nom: {it_department['name']}")
        print(f"   - Parent ID: {it_department.get('parentId', 'N/A')}")
        print()
        
        # 3. Mettre à jour l'utilisateur
        result = db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'departmentRef': it_department['_id']
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Référence du département mise à jour!")
            print(f"   Ancien departmentRef: {user.get('departmentRef')}")
            print(f"   Nouveau departmentRef: {it_department['_id']}")
        else:
            print("⚠️ Aucune modification nécessaire")
        
        # 4. Vérification - recharger l'utilisateur
        updated_user = db.users.find_one({'_id': user['_id']})
        print("\n🔍 VÉRIFICATION:")
        print(f"   - DepartmentRef final: {updated_user.get('departmentRef')}")
        
        # 5. Tester si le département est maintenant résolu
        dept_id = updated_user.get('departmentRef')
        if dept_id:
            department = db.departements.find_one({'_id': dept_id})
            if department:
                print(f"   - Département résolu: {department['name']}")
                print("✅ SUCCÈS: Le département devrait maintenant s'afficher correctement!")
            else:
                print("❌ ÉCHEC: Le département n'est toujours pas résolu")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
