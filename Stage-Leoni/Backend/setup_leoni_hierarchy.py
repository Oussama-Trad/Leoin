#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour créer la hiérarchie Leoni Tunisia dans MongoDB
- Locations (sites)
- Departments (départements)
"""

from pymongo import MongoClient
from datetime import datetime
import os
import uuid
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

def setup_leoni_hierarchy():
    """Créer la hiérarchie Leoni Tunisia dans la base de données"""
    
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    print("\n🏢 Configuration de la hiérarchie Leoni Tunisia")
    print("=" * 60)
    
    # 1. Créer les locations (sites)
    print("\n1. Création des sites (Locations)...")
    
    locations_data = [
        {
            "name": "Messadine",
            "code": "MESSADINE",
            "address": {
                "street": "Zone Industrielle Messadine",
                "city": "Messadine",
                "postalCode": "4054",
                "country": "Tunisia"
            },
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "adminUsers": [],
            "employeeCount": 0,
            "departmentCount": 0
        },
        {
            "name": "Mateur",
            "code": "MATEUR", 
            "address": {
                "street": "Zone Industrielle Mateur",
                "city": "Mateur",
                "postalCode": "7030",
                "country": "Tunisia"
            },
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "adminUsers": [],
            "employeeCount": 0,
            "departmentCount": 0
        },
        {
            "name": "Manzel Hayet (Monastir)",
            "code": "MONASTIR",
            "address": {
                "street": "Zone Industrielle Manzel Hayet",
                "city": "Monastir", 
                "postalCode": "5000",
                "country": "Tunisia"
            },
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "adminUsers": [],
            "employeeCount": 0,
            "departmentCount": 0
        }
    ]
    
    # Supprimer les anciennes locations si elles existent
    locations_collection.delete_many({})
    
    # Insérer les nouvelles locations
    location_results = locations_collection.insert_many(locations_data)
    location_ids = location_results.inserted_ids
    
    print(f"   ✅ {len(location_ids)} sites créés")
    for i, location in enumerate(locations_data):
        print(f"      • {location['name']} ({location['code']})")
    
    # 2. Créer les départements pour chaque site
    print("\n2. Création des départements...")
    
    # Départements pour tous les sites (sauf Bureau d'études qui n'est que pour Monastir)
    standard_departments = [
        "Production",
        "Logistique", 
        "Qualité",
        "Maintenance",
        "RH",
        "Finance et Comptabilité",
        "Informatique",
        "Sécurité, Santé et Environnement",
        "Gestion de la chaîne de valeur"
    ]
    
    # Supprimer les anciens départements
    departments_collection.delete_many({})
    
    # Créer chaque département pour chaque site avec des UUIDs aléatoirement générés
    all_departments = []
    
    for location_data in locations_data:
        for dept_name in standard_departments:
            department_doc = {
                "_id": str(uuid.uuid4()),  # UUID aléatoirement généré
                "name": dept_name,
                "location": location_data['name']
            }
            all_departments.append(department_doc)
        
        # Ajouter "Bureau d'études" uniquement pour Monastir
        if location_data['name'] == "Manzel Hayet (Monastir)":
            department_doc = {
                "_id": str(uuid.uuid4()),  # UUID aléatoirement généré
                "name": "Bureau d'études",
                "location": "Manzel Hayet (Monastir)"
            }
            all_departments.append(department_doc)
    # Insérer tous les départements
    dept_results = departments_collection.insert_many(all_departments)
    
    print(f"   ✅ {len(dept_results.inserted_ids)} départements créés")
    print(f"      • {len(standard_departments)} départements × {len(locations_data)} sites + Bureau d'études (Monastir)")
    
    # 3. Mettre à jour le compteur de départements dans les locations
    for location_id in location_ids:
        dept_count = len(standard_departments)
        if locations_data[location_ids.index(location_id)]['name'] == "Manzel Hayet (Monastir)":
            dept_count += 1  # +1 pour Bureau d'études
        
        locations_collection.update_one(
            {"_id": location_id},
            {"$set": {"departmentCount": dept_count}}
        )
    
    # 4. Créer les index pour la performance
    print("\n3. Création des index...")
    
    try:
        # Index pour locations
        locations_collection.create_index("code", unique=True)
        locations_collection.create_index("isActive")
        
        # Index pour departments (format simple)
        departments_collection.create_index([("name", 1), ("location", 1)], unique=True)
        departments_collection.create_index("location")
        
        print("   ✅ Index créés avec succès")
    except Exception as e:
        print(f"   ⚠️ Index déjà existants: {e}")
    
    # 5. Résumé
    print("\n📊 Résumé de la hiérarchie créée:")
    print("=" * 60)
    print("🏢 NIVEAU 1: Leoni Tunisia")
    print("📍 NIVEAU 2: Locations")
    for loc in locations_data:
        print(f"   • {loc['name']} ({loc['code']})")
    
    print("🏭 NIVEAU 3: Départements (par site)")
    for dept_name in standard_departments:
        print(f"   • {dept_name}")
    print("   • Bureau d'études (Monastir uniquement)")
    
    print(f"\n✅ Total: {len(locations_data)} sites × {len(standard_departments)} départements + Bureau d'études (Monastir)")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🚀 Configuration de la hiérarchie Leoni Tunisia")
    print("=" * 60)
    
    success = setup_leoni_hierarchy()
    
    if success:
        print("\n🎉 Hiérarchie Leoni Tunisia configurée avec succès !")
        print("Les utilisateurs peuvent maintenant s'inscrire avec:")
        print("• Leur site (Messadine, Mateur, Monastir)")
        print("• Leur département (Production, Logistique, Qualité, etc.)")
    else:
        print("\n❌ Erreur lors de la configuration")
