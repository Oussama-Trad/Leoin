#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour assigner les locationRef aux départements opérationnels
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

def assign_location_refs():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    departments_collection = db['departments']
    
    print("\n🔧 Attribution des locationRef aux départements opérationnels...")
    print("=" * 70)
    
    # Mapping site ID → location ID (using strings for comparison)
    site_to_location = {
        "688bd0501738d1adeeddaace": "688bab4fb35585626636ef7b",  # Messadine
        "688bd0501738d1adeeddaacf": "688bab4fb35585626636ef7c",  # Mateur
        "688bd0501738d1adeeddaad0": "688bab4fb35585626636ef7d",  # Manzel Hayet (Monastir)
    }
    
    # Récupérer tous les départements opérationnels (niveau DEPARTMENT)
    operational_depts = list(departments_collection.find({"level": "DEPARTMENT"}))
    
    print(f"📊 {len(operational_depts)} départements opérationnels trouvés")
    
    updates_count = 0
    
    for dept in operational_depts:
        parent_id = dept.get('parentId')
        dept_name = dept.get('name', 'N/A')
        
        # Convertir parentId en string pour la comparaison
        parent_id_str = str(parent_id) if parent_id else None
        
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
                updates_count += 1
                site_name = {
                    "688bd0501738d1adeeddaace": "Messadine",
                    "688bd0501738d1adeeddaacf": "Mateur", 
                    "688bd0501738d1adeeddaad0": "Manzel Hayet (Monastir)"
                }[parent_id_str]
                print(f"   ✅ {dept_name} → Assigné à {site_name}")
        else:
            print(f"   ❌ {dept_name} → Parent {parent_id_str} non mappé")
    
    print(f"\n🎉 Attribution terminée!")
    print(f"   • {updates_count} départements opérationnels mis à jour")
    
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
    print("🔧 Attribution des locationRef aux départements")
    print("=" * 70)
    
    assign_location_refs()
