#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger spécifiquement le profil d'Oussama (compte principal)
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

def fix_oussama_main_profile():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print(f"\n🔧 Correction du profil principal d'Oussama...")
    print("=" * 60)
    
    # Trouver l'utilisateur Oussama (compte principal)
    user = users_collection.find_one({'email': 'oussamatrzd19@gmail.com'})
    if not user:
        print("❌ Utilisateur Oussama non trouvé")
        client.close()
        return False
    
    print(f"👤 Utilisateur trouvé: {user['firstName']} {user['lastName']}")
    print(f"📧 Email: {user['email']}")
    print(f"📍 Location actuelle: {user.get('location', 'NON DÉFINI')}")
    print(f"🏢 Département actuel: {user.get('department', 'NON DÉFINI')}")
    print(f"🔗 LocationRef: {user.get('locationRef', 'NON DÉFINI')}")
    print(f"🔗 DepartmentRef: {user.get('departmentRef', 'NON DÉFINI')}")
    
    # Trouver la location Messadine (déjà correcte)
    location = locations_collection.find_one({'name': 'Messadine'})
    if not location:
        print("❌ Location Messadine non trouvée")
        client.close()
        return False
    
    print(f"✅ Location Messadine trouvée (ID: {location['_id']})")
    
    # Quel département voulez-vous ? Utilisons IT comme les autres comptes
    department_name = "IT"  # Changez ici si vous voulez un autre département
    
    # Trouver le département IT à Messadine
    department = departments_collection.find_one({
        'name': department_name,
        'locationRef': location['_id']
    })
    
    if not department:
        print(f"❌ Département '{department_name}' non trouvé à Messadine")
        client.close()
        return False
    
    print(f"✅ Département '{department_name}' trouvé (ID: {department['_id']})")
    
    # Mettre à jour le profil d'Oussama
    update_data = {
        'location': 'Messadine',
        'locationRef': location['_id'],
        'department': department_name,
        'departmentRef': department['_id']
    }
    
    result = users_collection.update_one(
        {'email': 'oussamatrzd19@gmail.com'},
        {'$set': update_data}
    )
    
    if result.modified_count > 0:
        print("✅ Profil principal d'Oussama mis à jour avec succès!")
        print(f"   📍 Location: Messadine")
        print(f"   🏢 Département: {department_name}")
        
        # Vérifier la mise à jour
        updated_user = users_collection.find_one({'email': 'oussamatrzd19@gmail.com'})
        print(f"\n🔍 Vérification post-mise à jour:")
        print(f"   • Location: {updated_user.get('location')}")
        print(f"   • LocationRef: {updated_user.get('locationRef')}")
        print(f"   • Department: {updated_user.get('department')}")
        print(f"   • DepartmentRef: {updated_user.get('departmentRef')}")
        
    else:
        print("❌ Erreur lors de la mise à jour du profil")
        client.close()
        return False
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Correction du profil principal d'Oussama")
    print("=" * 60)
    
    fix_oussama_main_profile()
