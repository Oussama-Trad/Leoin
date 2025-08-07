#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import connect_to_mongodb
from bson import ObjectId

def find_and_fix_users():
    try:
        # Utiliser la fonction de connexion de app.py
        client, connection_type = connect_to_mongodb()
        db = client['leoniApp']
        
        print(f'📡 Connexion {connection_type} établie')
        
        print('\n🔍 === TOUS LES UTILISATEURS ===')
        all_users = list(db.users.find({}, {
            'email': 1, 
            'firstName': 1, 
            'lastName': 1,
            'department': 1,
            'departmentRef': 1,
            'location': 1,
            'locationRef': 1
        }))
        
        if not all_users:
            print('❌ Aucun utilisateur trouvé dans la base de données')
            return
            
        for i, user in enumerate(all_users, 1):
            email = user.get("email", "Sans email")
            firstName = user.get("firstName", "?")
            lastName = user.get("lastName", "?")
            department = user.get("department", "VIDE")
            departmentRef = user.get("departmentRef", "VIDE")
            location = user.get("location", "VIDE")
            locationRef = user.get("locationRef", "VIDE")
            
            print(f'\n👤 Utilisateur #{i}:')
            print(f'   - Email: {email}')
            print(f'   - Nom: {firstName} {lastName}')
            print(f'   - Department: "{department}"')
            print(f'   - DepartmentRef: "{departmentRef}"')
            print(f'   - Location: "{location}"')
            print(f'   - LocationRef: "{locationRef}"')
            
            # Identifier les problèmes et proposer des solutions
            needs_fix = False
            
            if (not department or department == "VIDE") and departmentRef and departmentRef != "VIDE":
                print(f'   ⚠️ PROBLÈME: department vide mais departmentRef existe')
                needs_fix = True
                
            if (not location or location == "VIDE") and locationRef and locationRef != "VIDE":
                print(f'   ⚠️ PROBLÈME: location vide mais locationRef existe')
                needs_fix = True
                
            if needs_fix:
                print(f'   🔧 RÉPARATION AUTOMATIQUE...')
                
                update_fields = {}
                
                # Réparer le département
                if (not department or department == "VIDE") and departmentRef and departmentRef != "VIDE":
                    try:
                        dept_id = ObjectId(departmentRef) if isinstance(departmentRef, str) else departmentRef
                        department_doc = db.departments.find_one({'_id': dept_id})
                        if department_doc:
                            dept_name = department_doc.get("name", "Département inconnu")
                            update_fields['department'] = dept_name
                            print(f'   ✅ Département résolu: "{dept_name}"')
                        else:
                            print(f'   ❌ Département non trouvé pour ID: {dept_id}')
                    except Exception as e:
                        print(f'   ❌ Erreur département: {e}')
                
                # Réparer la location
                if (not location or location == "VIDE") and locationRef and locationRef != "VIDE":
                    try:
                        loc_id = ObjectId(locationRef) if isinstance(locationRef, str) else locationRef
                        location_doc = db.locations.find_one({'_id': loc_id})
                        if location_doc:
                            loc_name = location_doc.get("name", "Location inconnue")
                            update_fields['location'] = loc_name
                            print(f'   ✅ Location résolue: "{loc_name}"')
                        else:
                            print(f'   ❌ Location non trouvée pour ID: {loc_id}')
                    except Exception as e:
                        print(f'   ❌ Erreur location: {e}')
                
                # Appliquer les mises à jour
                if update_fields:
                    result = db.users.update_one(
                        {'_id': user['_id']},
                        {'$set': update_fields}
                    )
                    
                    if result.modified_count > 0:
                        print(f'   ✅ Utilisateur mis à jour avec succès!')
                        for field, value in update_fields.items():
                            print(f'      → {field}: "{value}"')
                    else:
                        print(f'   ❌ Échec de la mise à jour')
                        
            else:
                print(f'   ✅ Profil OK - aucune réparation nécessaire')

        client.close()
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False
    
    return True

if __name__ == "__main__":
    find_and_fix_users()
