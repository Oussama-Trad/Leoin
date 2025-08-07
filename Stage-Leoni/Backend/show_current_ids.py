#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour afficher les IDs actuels des locations et départements
"""

from pymongo import MongoClient
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

def show_current_ids():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print("\n📍 IDs ACTUELS DES LOCATIONS:")
    print("=" * 60)
    
    locations = list(locations_collection.find({}, {'name': 1, 'code': 1}))
    
    for location in locations:
        print(f"🏢 {location['name']} ({location['code']})")
        print(f"   ID: {location['_id']}")
        
        # Afficher les départements de cette location
        departments = list(departments_collection.find(
            {'locationRef': location['_id']}, 
            {'name': 1, 'code': 1}
        ))
        
        print(f"   📋 Départements ({len(departments)}):")
        for dept in departments:
            print(f"      • {dept['name']} - ID: {dept['_id']}")
        print()
    
    client.close()
    return True

if __name__ == "__main__":
    print("📍 IDs actuels des locations et départements")
    print("=" * 60)
    
    show_current_ids()
