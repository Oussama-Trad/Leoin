#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from bson import ObjectId
import sys

def debug_user_department():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb+srv://oussamatrad40:KAKdUhxKcJfANHQ7@cluster0.0q6fb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        db = client['leoniApp']
        
        # Chercher l'utilisateur avec l'email
        user = db.users.find_one({'email': 'hh@gmail.com'})
        
        if user:
            print('🔍 === DIAGNOSTIC DÉPARTEMENT UTILISATEUR ===')
            print(f'   - ID utilisateur: {user["_id"]}')
            print(f'   - Email: {user["email"]}')
            print(f'   - Prénom: {user.get("firstName", "Non défini")}')
            print(f'   - Nom: {user.get("lastName", "Non défini")}')
            print()
            
            print('🏢 === INFORMATIONS DÉPARTEMENT ===')
            print(f'   - Champ "department": "{user.get("department", "VIDE")}"')
            print(f'   - Champ "departmentRef": "{user.get("departmentRef", "VIDE")}"')
            print(f'   - Type departmentRef: {type(user.get("departmentRef", "VIDE"))}')
            print()
            
            print('🏭 === INFORMATIONS LOCATION ===')
            print(f'   - Champ "location": "{user.get("location", "VIDE")}"')
            print(f'   - Champ "locationRef": "{user.get("locationRef", "VIDE")}"')
            print(f'   - Type locationRef: {type(user.get("locationRef", "VIDE"))}')
            print()
            
            # Vérifier si departmentRef pointe vers un département valide
            if user.get('departmentRef'):
                try:
                    print('🔍 === RECHERCHE DU DÉPARTEMENT RÉFÉRENCÉ ===')
                    dept_id = ObjectId(user['departmentRef']) if isinstance(user['departmentRef'], str) else user['departmentRef']
                    department = db.departments.find_one({'_id': dept_id})
                    
                    if department:
                        print(f'✅ Département trouvé:')
                        print(f'   - ID: {department["_id"]}')
                        print(f'   - Nom: {department.get("name", "Non défini")}')
                        print(f'   - Code: {department.get("code", "Non défini")}')
                        print(f'   - LocationRef: {department.get("locationRef", "Non défini")}')
                        print(f'   - Actif: {department.get("isActive", "Non défini")}')
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
                
            # Vérifier si locationRef pointe vers une location valide
            if user.get('locationRef'):
                try:
                    print('\n🔍 === RECHERCHE DE LA LOCATION RÉFÉRENCÉE ===')
                    loc_id = ObjectId(user['locationRef']) if isinstance(user['locationRef'], str) else user['locationRef']
                    location = db.locations.find_one({'_id': loc_id})
                    
                    if location:
                        print(f'✅ Location trouvée:')
                        print(f'   - ID: {location["_id"]}')
                        print(f'   - Nom: {location.get("name", "Non défini")}')
                        print(f'   - Code: {location.get("code", "Non défini")}')
                        print(f'   - Active: {location.get("isActive", "Non défini")}')
                    else:
                        print(f'❌ Location avec ID {loc_id} non trouvée!')
                        
                except Exception as e:
                    print(f'❌ Erreur lors de la recherche de la location: {e}')
            else:
                print('⚠️ Aucune référence de location trouvée')
                
            print('\n🔍 === STRUCTURE COMPLÈTE UTILISATEUR ===')
            for key, value in user.items():
                if key != '_id':
                    print(f'   - {key}: {value} ({type(value).__name__})')
                    
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
