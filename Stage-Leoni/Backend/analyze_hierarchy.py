#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour analyser la structure hiérarchique des départements
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

def analyze_department_hierarchy():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    departments_collection = db['departments']
    
    print("\n🔍 Analyse de la hiérarchie des départements...")
    print("=" * 60)
    
    # Récupérer tous les départements
    departments = list(departments_collection.find({}))
    
    print(f"📊 Nombre total de départements: {len(departments)}")
    
    # Analyser les niveaux
    levels_stats = {}
    departments_by_level = {}
    
    for dept in departments:
        level = dept.get('level', 'N/A')
        name = dept.get('name', 'N/A')
        parent_id = dept.get('parentId', None)
        
        # Statistiques des niveaux
        if level not in levels_stats:
            levels_stats[level] = 0
            departments_by_level[level] = []
        
        levels_stats[level] += 1
        departments_by_level[level].append({
            'name': name,
            'id': dept['_id'],
            'parentId': parent_id
        })
    
    print(f"\n📈 Répartition par niveau:")
    for level, count in sorted(levels_stats.items()):
        print(f"   • Niveau {level}: {count} départements")
    
    print(f"\n🏗️ Structure hiérarchique détaillée:")
    for level in sorted(departments_by_level.keys()):
        print(f"\n📊 NIVEAU {level} ({levels_stats[level]} départements):")
        for dept in departments_by_level[level][:5]:  # Limiter à 5 pour la lisibilité
            parent_info = "Racine" if not dept['parentId'] else f"Parent: {dept['parentId']}"
            print(f"   • {dept['name']} ({parent_info})")
        
        if len(departments_by_level[level]) > 5:
            print(f"   ... et {len(departments_by_level[level]) - 5} autres")
    
    # Identifier les sites potentiels
    print(f"\n🏢 Identification des sites potentiels:")
    site_names = ["Messadine", "Mateur", "Manzel Hayet (Monastir)"]
    
    for site_name in site_names:
        matching_depts = [d for d in departments if d.get('name') == site_name]
        if matching_depts:
            dept = matching_depts[0]
            print(f"   ✅ {site_name} trouvé:")
            print(f"      - ID: {dept['_id']}")
            print(f"      - Niveau: {dept.get('level', 'N/A')}")
            print(f"      - Parent: {dept.get('parentId', 'Aucun')}")
        else:
            print(f"   ❌ {site_name} NON TROUVÉ")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔍 Analyse de la hiérarchie des départements")
    print("=" * 60)
    
    analyze_department_hierarchy()
