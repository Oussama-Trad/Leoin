#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour déboguer les départements dans la base de données
"""

from pymongo import MongoClient
from datetime import datetime
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

def debug_departments():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    departments_collection = db['departments']
    locations_collection = db['locations']
    
    print("\n🔍 Analyse des départements...")
    print("=" * 60)
    
    # Récupérer tous les départements
    departments = list(departments_collection.find({}))
    
    print(f"📊 Nombre total de départements: {len(departments)}")
    
    if len(departments) == 0:
        print("❌ AUCUN DÉPARTEMENT TROUVÉ dans la collection!")
        print("🔧 Cela explique pourquoi les dropdowns sont vides.")
    else:
        print("\n📋 Liste des départements:")
        for i, dept in enumerate(departments, 1):
            print(f"\n🏢 Département {i}:")
            print(f"   • ID: {dept.get('_id', 'N/A')}")
            print(f"   • Nom: {dept.get('name', 'N/A')}")
            print(f"   • Code: {dept.get('code', 'N/A')}")
            print(f"   • LocationRef: {dept.get('locationRef', 'N/A')}")
            print(f"   • Active: {dept.get('active', 'N/A')}")
            print(f"   • Tous les champs: {list(dept.keys())}")
            
            # Vérifier la location associée
            if dept.get('locationRef'):
                location = locations_collection.find_one({'_id': dept['locationRef']})
                if location:
                    print(f"   ✅ Location associée: {location['name']}")
                else:
                    print(f"   ❌ Location NOT FOUND pour ID: {dept['locationRef']}")
    
    # Vérifier les locations aussi
    print(f"\n🌍 Analyse des locations...")
    locations = list(locations_collection.find({}))
    print(f"📊 Nombre total de locations: {len(locations)}")
    
    for location in locations:
        print(f"📍 Location: {location.get('name', 'N/A')} (ID: {location.get('_id', 'N/A')})")
        
        # Compter les départements pour cette location
        dept_count = departments_collection.count_documents({'locationRef': location['_id']})
        print(f"   → {dept_count} départements associés")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔍 Debug des départements")
    print("=" * 60)
    
    debug_departments()
