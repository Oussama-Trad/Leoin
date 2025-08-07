#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vérifier les collections et les données existantes
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

def check_all_collections():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    
    print("\n🔍 Liste des collections...")
    print("=" * 60)
    
    collections = db.list_collection_names()
    print(f"📊 Collections trouvées: {collections}")
    
    for collection_name in collections:
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"\n📁 Collection '{collection_name}': {count} documents")
        
        if count > 0:
            # Afficher quelques documents exemple
            documents = list(collection.find({}).limit(2))
            for i, doc in enumerate(documents, 1):
                print(f"   Document {i} - Champs: {list(doc.keys())}")
                
    # Vérifier spécifiquement les locations et départements
    print(f"\n🏢 Locations:")
    locations = list(db['locations'].find({}))
    for loc in locations:
        print(f"   • {loc.get('name', 'N/A')} (ID: {loc.get('_id', 'N/A')})")
        
    print(f"\n🏭 Départements:")
    departments = list(db['departments'].find({}))
    for dept in departments:
        print(f"   • {dept.get('name', 'N/A')} (ID: {dept.get('_id', 'N/A')}) - Location: {dept.get('locationRef', 'N/A')}")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔍 Vérification des collections")
    print("=" * 60)
    
    check_all_collections()
