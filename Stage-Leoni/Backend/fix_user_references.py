#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger les références cassées des utilisateurs
"""

from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

def connect_to_mongodb():
    try:
        print("🔍 Connexion à MongoDB Atlas...")
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        client.server_info()  # Test de connexion
        print("✅ Connexion MongoDB Atlas réussie")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def fix_user_references():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print("\n🔧 Correction des références utilisateurs...")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs avec des références cassées
    users = list(users_collection.find({}, {
        'firstName': 1, 
        'lastName': 1, 
        'email': 1, 
        'department': 1, 
        'location': 1,
        'locationRef': 1,
        'departmentRef': 1
    }))
    
    for user in users:
        print(f"\n👤 Utilisateur: {user.get('firstName')} {user.get('lastName')} ({user.get('email')})")
        updated = False
        update_data = {}
        
        # Si l'utilisateur a une location par nom mais pas de référence valide
        if user.get('location') and user.get('location') != 'Non spécifié':
            location_name = user['location']
            print(f"   🔍 Recherche location: {location_name}")
            
            # Chercher la location par nom
            location = locations_collection.find_one({'name': location_name})
            if location:
                print(f"   ✅ Location trouvée: {location['name']} (ID: {location['_id']})")
                update_data['locationRef'] = location['_id']
                updated = True
                
                # Si l'utilisateur a un département, le chercher
                if user.get('department') and user.get('department') != 'Non spécifié':
                    department_name = user['department']
                    print(f"   🔍 Recherche département: {department_name} dans {location_name}")
                    
                    # Chercher le département par nom ET location
                    department = departments_collection.find_one({
                        'name': department_name,
                        'locationRef': location['_id']
                    })
                    
                    if department:
                        print(f"   ✅ Département trouvé: {department['name']} (ID: {department['_id']})")
                        update_data['departmentRef'] = department['_id']
                    else:
                        print(f"   ❌ Département {department_name} non trouvé dans {location_name}")
                        # Lister les départements disponibles
                        available_depts = list(departments_collection.find(
                            {'locationRef': location['_id']}, 
                            {'name': 1}
                        ))
                        print(f"   📋 Départements disponibles dans {location_name}:")
                        for dept in available_depts:
                            print(f"      • {dept['name']}")
            else:
                print(f"   ❌ Location {location_name} non trouvée")
        
        # Si l'utilisateur n'a pas de location mais a un département, essayer de corriger le département
        elif user.get('department') and user.get('department') != 'Non spécifié':
            department_name = user['department']
            print(f"   🔍 Recherche département: {department_name} (sans location spécifique)")
            
            # Chercher le département par nom seulement
            department = departments_collection.find_one({'name': department_name})
            if department:
                print(f"   ✅ Département trouvé: {department['name']} (ID: {department['_id']})")
                update_data['departmentRef'] = department['_id']
                
                # Récupérer aussi la location de ce département
                location = locations_collection.find_one({'_id': department['locationRef']})
                if location:
                    print(f"   ✅ Location du département: {location['name']} (ID: {location['_id']})")
                    update_data['locationRef'] = location['_id']
                    update_data['location'] = location['name']
                    updated = True
            else:
                print(f"   ❌ Département {department_name} non trouvé")
        
        # Mettre à jour l'utilisateur si nécessaire
        if updated and update_data:
            result = users_collection.update_one(
                {'_id': user['_id']},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                print(f"   ✅ Utilisateur mis à jour avec succès")
            else:
                print(f"   ❌ Erreur lors de la mise à jour")
        else:
            print(f"   ⚠️ Aucune mise à jour nécessaire ou possible")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Correction des références utilisateurs cassées")
    print("=" * 60)
    
    fix_user_references()
