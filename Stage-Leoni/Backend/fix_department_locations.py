#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger la structure des départements en ajoutant des locationRef appropriés
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

def fix_department_location_refs():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    departments_collection = db['departments']
    locations_collection = db['locations']
    
    print("\n🔧 Correction des références de location pour les départements...")
    print("=" * 70)
    
    # Récupérer toutes les locations
    locations = list(locations_collection.find({}))
    location_mapping = {}
    
    print("🌍 Locations disponibles:")
    for loc in locations:
        print(f"   • {loc['name']} (ID: {loc['_id']})")
        location_mapping[loc['name']] = loc['_id']
    
    # Mapper les noms de départements LOCATION vers les locations MongoDB
    site_to_location = {
        "Messadine": "688bab4fb35585626636ef7b",
        "Mateur": "688bab4fb35585626636ef7c", 
        "Manzel Hayet (Monastir)": "688bab4fb35585626636ef7d"
    }
    
    # Récupérer tous les départements
    departments = list(departments_collection.find({}))
    
    print(f"\n📊 Traitement de {len(departments)} départements...")
    
    # Identifier la hiérarchie
    sites = {}  # départements niveau LOCATION (sites)
    operational_depts = {}  # départements niveau DEPARTMENT (départements opérationnels)
    
    for dept in departments:
        level = dept.get('level', '')
        name = dept.get('name', '')
        dept_id = dept['_id']
        
        if level == 'LOCATION':  # Sites (Messadine, Mateur, Monastir)
            sites[dept_id] = {
                'name': name,
                'locationRef': site_to_location.get(name, None)
            }
            print(f"🏢 Site trouvé: {name} → Location: {site_to_location.get(name, 'NON MAPPÉ')}")
            
        elif level == 'DEPARTMENT':  # Départements opérationnels
            parent_id = dept.get('parentId')
            operational_depts[dept_id] = {
                'name': name,
                'parentId': parent_id,
                'level': level
            }
    
    print(f"\n📈 Résumé de la hiérarchie:")
    print(f"   • Sites (niveau LOCATION): {len(sites)}")
    print(f"   • Départements opérationnels (niveau DEPARTMENT): {len(operational_depts)}")
    
    # Maintenant, attribuer les locationRef
    updates_count = 0
    
    print(f"\n🔄 Mise à jour des références de location...")
    
    # 1. Mettre à jour les sites (niveau LOCATION)
    for site_id, site_info in sites.items():
        location_ref = site_info['locationRef']
        if location_ref:
            result = departments_collection.update_one(
                {'_id': site_id},
                {
                    '$set': {
                        'locationRef': ObjectId(location_ref),
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            if result.modified_count > 0:
                updates_count += 1
                print(f"   ✅ Site '{site_info['name']}' → Location mise à jour")
    
    # 2. Mettre à jour les départements opérationnels (niveau DEPARTMENT)
    for dept_id, dept_info in operational_depts.items():
        parent_id = dept_info['parentId']
        
        # Trouver la location du parent (site)
        if parent_id in sites:
            location_ref = sites[parent_id]['locationRef']
            if location_ref:
                result = departments_collection.update_one(
                    {'_id': dept_id},
                    {
                        '$set': {
                            'locationRef': ObjectId(location_ref),
                            'updatedAt': datetime.utcnow()
                        }
                    }
                )
                if result.modified_count > 0:
                    updates_count += 1
                    print(f"   ✅ Département '{dept_info['name']}' → Location héritée du site '{sites[parent_id]['name']}'")
                else:
                    print(f"   ⚠️  Département '{dept_info['name']}' → Pas de mise à jour nécessaire")
            else:
                print(f"   ❌ Département '{dept_info['name']}' → Parent site '{sites[parent_id]['name']}' sans location")
        else:
            print(f"   ❌ Département '{dept_info['name']}' → Parent {parent_id} non trouvé dans les sites")
    
    print(f"\n🎉 Mise à jour terminée!")
    print(f"   • {updates_count} départements mis à jour avec des locationRef")
    
    # Vérification finale
    print(f"\n🔍 Vérification finale...")
    for location_id, location_name in [(loc['_id'], loc['name']) for loc in locations]:
        dept_count = departments_collection.count_documents({'locationRef': location_id})
        print(f"   📍 {location_name}: {dept_count} départements associés")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔧 Correction des références de location pour les départements")
    print("=" * 70)
    
    fix_department_location_refs()
