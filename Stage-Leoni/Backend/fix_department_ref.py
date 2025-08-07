#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vérifier et corriger les références de département
"""

from pymongo import MongoClient
from bson.objectid import ObjectId
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

def check_department_reference():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    departments_collection = db['departments']
    locations_collection = db['locations']
    
    print("\n🔍 Vérification des références de département...")
    print("=" * 60)
    
    # Récupérer l'utilisateur problématique
    user = users_collection.find_one({'email': 'aa@gmail.com'})
    
    if not user:
        print("❌ Utilisateur aa@gmail.com non trouvé")
        return False
        
    print(f"👤 Utilisateur: {user['firstName']} {user['lastName']}")
    print(f"📧 Email: {user['email']}")
    print(f"🏢 LocationRef: {user.get('locationRef')}")
    print(f"🏭 DepartmentRef: {user.get('departmentRef')}")
    
    # Vérifier la location
    if user.get('locationRef'):
        location = locations_collection.find_one({'_id': user['locationRef']})
        if location:
            print(f"✅ Location trouvée: {location['name']}")
        else:
            print(f"❌ Location non trouvée pour ID: {user['locationRef']}")
    
    # Vérifier le département
    if user.get('departmentRef'):
        department = departments_collection.find_one({'_id': user['departmentRef']})
        if department:
            print(f"✅ Département trouvé: {department['name']}")
        else:
            print(f"❌ Département non trouvé pour ID: {user['departmentRef']}")
            
            # Chercher un département IT à Messadine
            print(f"\n🔍 Recherche d'un département IT à Messadine...")
            it_dept = departments_collection.find_one({
                'name': 'IT', 
                'locationRef': user['locationRef']
            })
            
            if it_dept:
                print(f"✅ Département IT trouvé: {it_dept['_id']}")
                print(f"   Nom: {it_dept['name']}")
                print(f"   Location: {it_dept['locationRef']}")
                
                # Corriger la référence
                print(f"\n🔧 Correction de la référence département...")
                result = users_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'departmentRef': it_dept['_id']}}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Référence département corrigée")
                else:
                    print(f"❌ Échec de la correction")
            else:
                print(f"❌ Aucun département IT trouvé à Messadine")
                
                # Lister tous les départements de cette location
                print(f"\n📋 Départements disponibles à Messadine:")
                depts = list(departments_collection.find({'locationRef': user['locationRef']}))
                for dept in depts:
                    print(f"   • {dept['name']} (ID: {dept['_id']})")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Vérification et correction des références de département")
    print("=" * 60)
    
    check_department_reference()
