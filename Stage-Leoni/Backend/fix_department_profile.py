#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import connect_to_mongodb
from bson import ObjectId

def debug_user_department():
    try:
        # Utiliser la fonction de connexion de app.py
        client, connection_type = connect_to_mongodb()
        db = client['leoniApp']
        
        print(f'📡 Connexion {connection_type} établie')
        
        # Chercher l'utilisateur avec l'email
        user = db.users.find_one({'email': 'hh@gmail.com'})
        
        if user:
            print('\n🔍 === DIAGNOSTIC DÉPARTEMENT UTILISATEUR ===')
            print(f'   - ID utilisateur: {user["_id"]}')
            print(f'   - Email: {user["email"]}')
            print(f'   - Prénom: {user.get("firstName", "Non défini")}')
            print(f'   - Nom: {user.get("lastName", "Non défini")}')
            print()
            
            print('🏢 === INFORMATIONS DÉPARTEMENT ===')
            department_field = user.get("department", "VIDE")
            departmentRef_field = user.get("departmentRef", "VIDE")
            
            print(f'   - Champ "department": "{department_field}"')
            print(f'   - Champ "departmentRef": "{departmentRef_field}"')
            print(f'   - Type departmentRef: {type(departmentRef_field)}')
            
            # Problème identifié : le champ "department" pourrait être vide
            if not department_field or department_field == "VIDE":
                print('❌ PROBLÈME: Le champ "department" est vide!')
                print('   → C\'est pourquoi "Non renseigné" apparaît dans le profil')
            else:
                print(f'✅ Le champ "department" contient: "{department_field}"')
            print()
            
            print('🏭 === INFORMATIONS LOCATION ===')
            location_field = user.get("location", "VIDE")
            locationRef_field = user.get("locationRef", "VIDE")
            
            print(f'   - Champ "location": "{location_field}"')
            print(f'   - Champ "locationRef": "{locationRef_field}"')
            print(f'   - Type locationRef: {type(locationRef_field)}')
            
            if not location_field or location_field == "VIDE":
                print('❌ PROBLÈME: Le champ "location" est vide!')
            else:
                print(f'✅ Le champ "location" contient: "{location_field}"')
            print()
            
            # Vérifier si departmentRef pointe vers un département valide
            if departmentRef_field and departmentRef_field != "VIDE":
                try:
                    print('🔍 === RECHERCHE DU DÉPARTEMENT RÉFÉRENCÉ ===')
                    dept_id = ObjectId(departmentRef_field) if isinstance(departmentRef_field, str) else departmentRef_field
                    department = db.departments.find_one({'_id': dept_id})
                    
                    if department:
                        dept_name = department.get("name", "Non défini")
                        print(f'✅ Département trouvé:')
                        print(f'   - ID: {department["_id"]}')
                        print(f'   - Nom: {dept_name}')
                        print(f'   - Code: {department.get("code", "Non défini")}')
                        print(f'   - LocationRef: {department.get("locationRef", "Non défini")}')
                        print(f'   - Actif: {department.get("isActive", "Non défini")}')
                        
                        # SOLUTION: Mettre à jour le champ "department" avec le nom
                        if not department_field or department_field == "VIDE":
                            print(f'\n🔧 === SOLUTION PROPOSÉE ===')
                            print(f'   Mettre à jour user.department = "{dept_name}"')
                            
                            # Mettre à jour l'utilisateur
                            result = db.users.update_one(
                                {'_id': user['_id']},
                                {'$set': {'department': dept_name}}
                            )
                            
                            if result.modified_count > 0:
                                print(f'✅ Champ "department" mis à jour avec succès!')
                                print(f'   → Le profil devrait maintenant afficher: "{dept_name}"')
                            else:
                                print(f'❌ Échec de la mise à jour')
                        
                    else:
                        print(f'❌ Département avec ID {dept_id} non trouvé!')
                        
                        # Chercher tous les départements pour voir ce qui existe
                        print('\n🔍 === DÉPARTEMENTS DISPONIBLES ===')
                        all_depts = list(db.departments.find({'isActive': True}).limit(5))
                        for dept in all_depts:
                            print(f'   - {dept["_id"]}: {dept.get("name", "Sans nom")} ({dept.get("code", "Sans code")})')
                            
                except Exception as e:
                    print(f'❌ Erreur lors de la recherche du département: {e}')
            else:
                print('⚠️ Aucune référence de département trouvée')
                
            # Vérifier locationRef aussi
            if locationRef_field and locationRef_field != "VIDE":
                try:
                    print('\n🔍 === RECHERCHE DE LA LOCATION RÉFÉRENCÉE ===')
                    loc_id = ObjectId(locationRef_field) if isinstance(locationRef_field, str) else locationRef_field
                    location = db.locations.find_one({'_id': loc_id})
                    
                    if location:
                        loc_name = location.get("name", "Non défini")
                        print(f'✅ Location trouvée:')
                        print(f'   - ID: {location["_id"]}')
                        print(f'   - Nom: {loc_name}')
                        print(f'   - Code: {location.get("code", "Non défini")}')
                        print(f'   - Active: {location.get("isActive", "Non défini")}')
                        
                        # SOLUTION: Mettre à jour le champ "location" avec le nom
                        if not location_field or location_field == "VIDE":
                            print(f'\n🔧 === SOLUTION LOCATION ===')
                            print(f'   Mettre à jour user.location = "{loc_name}"')
                            
                            # Mettre à jour l'utilisateur
                            result = db.users.update_one(
                                {'_id': user['_id']},
                                {'$set': {'location': loc_name}}
                            )
                            
                            if result.modified_count > 0:
                                print(f'✅ Champ "location" mis à jour avec succès!')
                                print(f'   → Le profil devrait maintenant afficher: "{loc_name}"')
                            else:
                                print(f'❌ Échec de la mise à jour location')
                        
                    else:
                        print(f'❌ Location avec ID {loc_id} non trouvée!')
                        
                except Exception as e:
                    print(f'❌ Erreur lors de la recherche de la location: {e}')
            else:
                print('⚠️ Aucune référence de location trouvée')
                
        else:
            print('❌ Utilisateur avec email hh@gmail.com non trouvé')
            
            # Chercher tous les utilisateurs pour voir ce qui existe
            print('\n🔍 === UTILISATEURS DISPONIBLES ===')
            all_users = list(db.users.find({}, {'email': 1, 'firstName': 1, 'lastName': 1}).limit(5))
            for user in all_users:
                print(f'   - {user.get("email", "Sans email")}: {user.get("firstName", "?")} {user.get("lastName", "?")}')

        client.close()
        
    except Exception as e:
        print(f'❌ Erreur de connexion à la base de données: {e}')
        return False
    
    return True

if __name__ == "__main__":
    debug_user_department()
