#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour assigner les locationRef aux départements opérationnels (nouveaux IDs)
"""

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId

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

def assign_location_refs_v2():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    departments_collection = db['departments']
    
    print("\n🔧 Attribution des locationRef aux départements (v2 - nouveaux IDs)...")
    print("=" * 70)
    
    # Mapping site ID → location ID (nouveaux IDs)
    site_to_location = {
        "688bd5b3b722f3dc3a90ed8c": "688bab4fb35585626636ef7b",  # Messadine
        "688bd5b3b722f3dc3a90ed8d": "688bab4fb35585626636ef7c",  # Mateur
        "688bd5b3b722f3dc3a90ed8e": "688bab4fb35585626636ef7d",  # Manzel Hayet (Monastir)
    }
    
    # 1. Mettre à jour les SITES d'abord (niveau LOCATION)
    site_updates = 0
    for site_name in ["Messadine", "Mateur", "Manzel Hayet (Monastir)"]:
        site = departments_collection.find_one({"name": site_name, "level": "LOCATION"})
        if site:
            site_id_str = str(site['_id'])
            if site_id_str in site_to_location:
                location_ref = ObjectId(site_to_location[site_id_str])
                result = departments_collection.update_one(
                    {'_id': site['_id']},
                    {
                        '$set': {
                            'locationRef': location_ref,
                            'updatedAt': datetime.utcnow()
                        }
                    }
                )
                if result.modified_count > 0:
                    site_updates += 1
                    print(f"   ✅ Site '{site_name}' → Location mise à jour")
    
    # 2. Mettre à jour les DÉPARTEMENTS OPÉRATIONNELS (niveau DEPARTMENT)
    operational_depts = list(departments_collection.find({"level": "DEPARTMENT"}))
    dept_updates = 0
    
    print(f"\n📊 {len(operational_depts)} départements opérationnels à traiter...")
    
    for dept in operational_depts:
        parent_id_str = str(dept.get('parentId'))
        dept_name = dept.get('name', 'N/A')
        
        if parent_id_str in site_to_location:
            location_ref = ObjectId(site_to_location[parent_id_str])
            
            result = departments_collection.update_one(
                {'_id': dept['_id']},
                {
                    '$set': {
                        'locationRef': location_ref,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                dept_updates += 1
                site_name = {
                    "688bd5b3b722f3dc3a90ed8c": "Messadine",
                    "688bd5b3b722f3dc3a90ed8d": "Mateur", 
                    "688bd5b3b722f3dc3a90ed8e": "Manzel Hayet (Monastir)"
                }[parent_id_str]
                print(f"   ✅ {dept_name} → Assigné à {site_name}")
    
    print(f"\n🎉 Attribution terminée!")
    print(f"   • {site_updates} sites mis à jour")
    print(f"   • {dept_updates} départements opérationnels mis à jour")
    
    # Vérification finale
    print(f"\n🔍 Vérification finale par location:")
    location_names = {
        "688bab4fb35585626636ef7b": "Messadine",
        "688bab4fb35585626636ef7c": "Mateur", 
        "688bab4fb35585626636ef7d": "Manzel Hayet (Monastir)"
    }
    
    for location_id, location_name in location_names.items():
        dept_count = departments_collection.count_documents({'locationRef': ObjectId(location_id)})
        print(f"   📍 {location_name}: {dept_count} départements associés")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Attribution des locationRef aux départements (v2)")
    print("=" * 70)
    
    assign_location_refs_v2()
