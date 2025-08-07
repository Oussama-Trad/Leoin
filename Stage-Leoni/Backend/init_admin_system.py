#!/usr/bin/env python3
"""
Script d'initialisation du système de gestion par département et localisation
- Crée les départements et localisations
- Crée des comptes admin pour chaque département/localisation
- Crée un super admin
- Met à jour les utilisateurs existants si nécessaire
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
MONGODB_LOCAL_URI = 'mongodb://localhost:27017/LeoniApp'

# Fonction pour se connecter à MongoDB
def connect_to_mongodb():
    try:
        print("🔍 Tentative de connexion à MongoDB Atlas...")
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        client.server_info()
        print("✅ Connexion MongoDB Atlas réussie")
        return client, "Atlas"
    except Exception as e:
        print(f"❌ Échec connexion MongoDB Atlas: {str(e)}")

    try:
        print("🔍 Tentative de connexion à MongoDB local...")
        client = MongoClient(MONGODB_LOCAL_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ Connexion MongoDB local réussie")
        return client, "Local"
    except Exception as e:
        print(f"❌ Échec connexion MongoDB local: {str(e)}")
        return None, None

# Données de base - Départements et localisations Leoni
DEPARTMENTS_DATA = [
    # Messadine
    {"name": "IT", "location": "Messadine", "description": "Technologies de l'information"},
    {"name": "HR", "location": "Messadine", "description": "Ressources humaines"},
    {"name": "Production", "location": "Messadine", "description": "Production et manufacturing"},
    {"name": "Quality", "location": "Messadine", "description": "Contrôle qualité"},
    {"name": "Maintenance", "location": "Messadine", "description": "Maintenance industrielle"},
    {"name": "Logistics", "location": "Messadine", "description": "Logistique et supply chain"},
    
    # Sousse
    {"name": "IT", "location": "Sousse", "description": "Technologies de l'information"},
    {"name": "HR", "location": "Sousse", "description": "Ressources humaines"},
    {"name": "Production", "location": "Sousse", "description": "Production et manufacturing"},
    {"name": "Quality", "location": "Sousse", "description": "Contrôle qualité"},
    {"name": "Finance", "location": "Sousse", "description": "Finance et comptabilité"},
    
    # Tunis (Siège)
    {"name": "IT", "location": "Tunis", "description": "Technologies de l'information"},
    {"name": "HR", "location": "Tunis", "description": "Ressources humaines"},
    {"name": "Finance", "location": "Tunis", "description": "Finance et comptabilité"},
    {"name": "Management", "location": "Tunis", "description": "Direction générale"},
    {"name": "R&D", "location": "Tunis", "description": "Recherche et développement"},
]

# Données des localisations
LOCATIONS_DATA = [
    {"name": "Messadine", "code": "MESS", "address": "Zone Industrielle Messadine, Monastir", "country": "Tunisia"},
    {"name": "Sousse", "code": "SOUS", "address": "Zone Industrielle Sousse", "country": "Tunisia"},
    {"name": "Tunis", "code": "TUNI", "address": "Centre ville Tunis", "country": "Tunisia"},
]

# Admins par défaut (un admin par département/localisation)
ADMIN_ACCOUNTS = [
    # Messadine
    {"username": "admin.it.messadine", "password": "admin123", "department": "IT", "location": "Messadine", "firstName": "Admin", "lastName": "IT Messadine"},
    {"username": "admin.hr.messadine", "password": "admin123", "department": "HR", "location": "Messadine", "firstName": "Admin", "lastName": "HR Messadine"},
    {"username": "admin.prod.messadine", "password": "admin123", "department": "Production", "location": "Messadine", "firstName": "Admin", "lastName": "Production Messadine"},
    {"username": "admin.quality.messadine", "password": "admin123", "department": "Quality", "location": "Messadine", "firstName": "Admin", "lastName": "Quality Messadine"},
    {"username": "admin.maint.messadine", "password": "admin123", "department": "Maintenance", "location": "Messadine", "firstName": "Admin", "lastName": "Maintenance Messadine"},
    {"username": "admin.log.messadine", "password": "admin123", "department": "Logistics", "location": "Messadine", "firstName": "Admin", "lastName": "Logistics Messadine"},
    
    # Sousse
    {"username": "admin.it.sousse", "password": "admin123", "department": "IT", "location": "Sousse", "firstName": "Admin", "lastName": "IT Sousse"},
    {"username": "admin.hr.sousse", "password": "admin123", "department": "HR", "location": "Sousse", "firstName": "Admin", "lastName": "HR Sousse"},
    {"username": "admin.prod.sousse", "password": "admin123", "department": "Production", "location": "Sousse", "firstName": "Admin", "lastName": "Production Sousse"},
    {"username": "admin.quality.sousse", "password": "admin123", "department": "Quality", "location": "Sousse", "firstName": "Admin", "lastName": "Quality Sousse"},
    {"username": "admin.finance.sousse", "password": "admin123", "department": "Finance", "location": "Sousse", "firstName": "Admin", "lastName": "Finance Sousse"},
    
    # Tunis
    {"username": "admin.it.tunis", "password": "admin123", "department": "IT", "location": "Tunis", "firstName": "Admin", "lastName": "IT Tunis"},
    {"username": "admin.hr.tunis", "password": "admin123", "department": "HR", "location": "Tunis", "firstName": "Admin", "lastName": "HR Tunis"},
    {"username": "admin.finance.tunis", "password": "admin123", "department": "Finance", "location": "Tunis", "firstName": "Admin", "lastName": "Finance Tunis"},
    {"username": "admin.mgmt.tunis", "password": "admin123", "department": "Management", "location": "Tunis", "firstName": "Admin", "lastName": "Management Tunis"},
    {"username": "admin.rd.tunis", "password": "admin123", "department": "R&D", "location": "Tunis", "firstName": "Admin", "lastName": "R&D Tunis"},
]

def init_locations(db):
    """Initialiser les localisations"""
    print("📍 Initialisation des localisations...")
    locations_collection = db['locations']
    
    for location_data in LOCATIONS_DATA:
        existing = locations_collection.find_one({"name": location_data["name"]})
        if not existing:
            location_data.update({
                "active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            })
            result = locations_collection.insert_one(location_data)
            print(f"✅ Localisation créée: {location_data['name']} (ID: {result.inserted_id})")
        else:
            print(f"ℹ️ Localisation existante: {location_data['name']}")

def init_departments(db):
    """Initialiser les départements"""
    print("🏢 Initialisation des départements...")
    departments_collection = db['departments']
    
    for dept_data in DEPARTMENTS_DATA:
        existing = departments_collection.find_one({
            "name": dept_data["name"],
            "location": dept_data["location"]
        })
        if not existing:
            dept_data.update({
                "active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            })
            result = departments_collection.insert_one(dept_data)
            print(f"✅ Département créé: {dept_data['name']} - {dept_data['location']} (ID: {result.inserted_id})")
        else:
            print(f"ℹ️ Département existant: {dept_data['name']} - {dept_data['location']}")

def create_admin_accounts(db):
    """Créer les comptes admin"""
    print("👥 Création des comptes admin...")
    users_collection = db['users']
    
    for admin_data in ADMIN_ACCOUNTS:
        existing = users_collection.find_one({"adresse1": admin_data["username"]})
        if not existing:
            # Générer un employeeId unique
            employee_id = generate_unique_employee_id(users_collection)
            
            hashed_password = bcrypt.hashpw(admin_data["password"].encode('utf-8'), bcrypt.gensalt())
            
            admin_user = {
                "firstName": admin_data["firstName"],
                "lastName": admin_data["lastName"],
                "adresse1": admin_data["username"],
                "adresse2": f"admin.{admin_data['department'].lower()}.{admin_data['location'].lower()}@leoni.com",
                "phoneNumber": "+216 12345678",
                "parentalPhoneNumber": "+216 87654321",
                "password": hashed_password,
                "employeeId": employee_id,
                "department": admin_data["department"],
                "location": admin_data["location"],
                "position": f"Admin {admin_data['department']}",
                "role": "ADMIN",
                "profilePicture": None,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = users_collection.insert_one(admin_user)
            print(f"✅ Admin créé: {admin_data['username']} (ID: {employee_id})")
        else:
            # Mettre à jour le rôle si ce n'est pas encore un admin
            if existing.get('role') != 'ADMIN':
                users_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "role": "ADMIN",
                        "updatedAt": datetime.utcnow()
                    }}
                )
                print(f"✅ Rôle admin ajouté à: {admin_data['username']}")
            else:
                print(f"ℹ️ Admin existant: {admin_data['username']}")

def generate_unique_employee_id(users_collection):
    """Générer un employeeId unique"""
    import random
    
    while True:
        employee_id = str(random.randint(10000000, 99999999))
        if not users_collection.find_one({"employeeId": employee_id}):
            return employee_id

def create_super_admin(db):
    """Créer le compte super admin"""
    print("👑 Création du compte super admin...")
    users_collection = db['users']
    
    existing = users_collection.find_one({"adresse1": "superadmin"})
    if not existing:
        employee_id = generate_unique_employee_id(users_collection)
        hashed_password = bcrypt.hashpw("superadmin123".encode('utf-8'), bcrypt.gensalt())
        
        super_admin = {
            "firstName": "Super",
            "lastName": "Admin",
            "adresse1": "superadmin",
            "adresse2": "superadmin@leoni.com",
            "phoneNumber": "+216 11111111",
            "parentalPhoneNumber": "+216 11111111",
            "password": hashed_password,
            "employeeId": employee_id,
            "department": "ALL",
            "location": "ALL",
            "position": "Super Administrator",
            "role": "SUPERADMIN",
            "profilePicture": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = users_collection.insert_one(super_admin)
        print(f"✅ Super Admin créé: superadmin (ID: {employee_id})")
    else:
        if existing.get('role') != 'SUPERADMIN':
            users_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "role": "SUPERADMIN",
                    "department": "ALL",
                    "location": "ALL",
                    "updatedAt": datetime.utcnow()
                }}
            )
            print("✅ Rôle super admin ajouté à l'utilisateur existant")
        else:
            print("ℹ️ Super Admin existant")

def init_document_types(db):
    """Initialiser les types de documents"""
    print("📄 Initialisation des types de documents...")
    document_types_collection = db['document_types']
    
    document_types = [
        {"name": "Attestation de travail", "description": "Attestation confirmant l'emploi", "active": True},
        {"name": "Attestation de salaire", "description": "Attestation du montant du salaire", "active": True},
        {"name": "Congé payé", "description": "Demande de congé payé", "active": True},
        {"name": "Congé maladie", "description": "Demande de congé maladie", "active": True},
        {"name": "Certificat médical", "description": "Validation d'un certificat médical", "active": True},
        {"name": "Demande de formation", "description": "Demande de formation professionnelle", "active": True},
        {"name": "Demande de matériel", "description": "Demande de matériel de travail", "active": True},
        {"name": "Autre", "description": "Autre type de demande", "active": True},
    ]
    
    for doc_type in document_types:
        existing = document_types_collection.find_one({"name": doc_type["name"]})
        if not existing:
            doc_type.update({
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            })
            result = document_types_collection.insert_one(doc_type)
            print(f"✅ Type de document créé: {doc_type['name']}")
        else:
            print(f"ℹ️ Type de document existant: {doc_type['name']}")

def update_existing_users(db):
    """Mettre à jour les utilisateurs existants sans rôle défini"""
    print("🔄 Mise à jour des utilisateurs existants...")
    users_collection = db['users']
    
    # Mettre à jour les utilisateurs sans rôle
    result = users_collection.update_many(
        {"role": {"$exists": False}},
        {"$set": {"role": "EMPLOYEE", "updatedAt": datetime.utcnow()}}
    )
    
    if result.modified_count > 0:
        print(f"✅ {result.modified_count} utilisateurs mis à jour avec le rôle EMPLOYEE")
    
    # Mettre à jour les utilisateurs avec rôle null ou vide
    result = users_collection.update_many(
        {"$or": [{"role": None}, {"role": ""}]},
        {"$set": {"role": "EMPLOYEE", "updatedAt": datetime.utcnow()}}
    )
    
    if result.modified_count > 0:
        print(f"✅ {result.modified_count} utilisateurs supplémentaires mis à jour")

def main():
    """Fonction principale"""
    print("🚀 Initialisation du système de gestion Leoni...")
    print("=" * 60)
    
    # Connexion à MongoDB
    client, db_type = connect_to_mongodb()
    if not client:
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    db = client['LeoniApp']
    print(f"📊 Connexion à la base de données: {db_type}")
    
    try:
        # Initialiser les données
        init_locations(db)
        init_departments(db)
        init_document_types(db)
        create_super_admin(db)
        create_admin_accounts(db)
        update_existing_users(db)
        
        print("\n" + "=" * 60)
        print("✅ Initialisation terminée avec succès!")
        print("\n📋 Comptes créés:")
        print("🔑 Super Admin: superadmin / superadmin123")
        print("🔑 Admins départementaux: admin.{dept}.{location} / admin123")
        print("\n📍 Localisations: Messadine, Sousse, Tunis")
        print("🏢 Départements: IT, HR, Production, Quality, etc.")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
