#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer les départements manquants dans chaque location
"""

from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

def connect_to_mongodb():
    """Connexion à MongoDB Atlas"""
    try:
        # URL de connexion MongoDB Atlas
        MONGODB_URI = "mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp"
        
        client = MongoClient(MONGODB_URI)
        db = client['LeoniApp']
        
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion MongoDB Atlas réussie")
        
        return db
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def create_departments():
    """Créer les départements standard pour chaque location"""
    print("🏭 Création des départements standard")
    print("=" * 60)
    
    db = connect_to_mongodb()
    if not db:
        return
    
    # Départements standard à créer
    departments_to_create = [
        "IT",
        "RH", 
        "Production",
        "Qualité",
        "Maintenance",
        "Logistique",
        "Administration",
        "Sécurité"
    ]
    
    # Récupérer toutes les locations
    locations = list(db.locations.find({}))
    print(f"📍 {len(locations)} locations trouvées")
    
    for location in locations:
        location_id = location['_id']
        location_name = location.get('name', 'Unknown')
        
        print(f"\n🏢 Création des départements pour: {location_name}")
        print("-" * 40)
        
        departments_created = 0
        
        for dept_name in departments_to_create:
            # Vérifier si le département existe déjà
            existing_dept = db.departments.find_one({
                'name': dept_name,
                'locationId': location_id
            })
            
            if existing_dept:
                print(f"   ⚠️  {dept_name} existe déjà")
                continue
            
            # Créer le nouveau département
            new_department = {
                '_id': ObjectId(),
                'name': dept_name,
                'locationId': location_id,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            try:
                result = db.departments.insert_one(new_department)
                if result.inserted_id:
                    print(f"   ✅ {dept_name} créé (ID: {result.inserted_id})")
                    departments_created += 1
                else:
                    print(f"   ❌ Échec création {dept_name}")
            except Exception as e:
                print(f"   ❌ Erreur création {dept_name}: {e}")
        
        print(f"   📊 {departments_created} départements créés pour {location_name}")
    
    print(f"\n🎉 Création des départements terminée!")

def show_final_structure():
    """Afficher la structure finale des locations et départements"""
    print("\n📋 Structure finale des locations et départements")
    print("=" * 60)
    
    db = connect_to_mongodb()
    if not db:
        return
    
    locations = list(db.locations.find({}))
    
    for location in locations:
        location_id = location['_id']
        location_name = location.get('name', 'Unknown')
        
        departments = list(db.departments.find({'locationId': location_id}))
        
        print(f"\n🏢 {location_name}")
        print(f"   ID: {location_id}")
        print(f"   📋 Départements ({len(departments)}):")
        
        for dept in departments:
            print(f"      • {dept['name']} (ID: {dept['_id']})")

if __name__ == "__main__":
    print("🏭 Création des départements pour toutes les locations")
    print("=" * 60)
    
    create_departments()
    show_final_structure()
