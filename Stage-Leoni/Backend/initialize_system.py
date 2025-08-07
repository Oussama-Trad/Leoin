#!/usr/bin/env python3
"""
Script pour initialiser les données de base du système Leoni
- Création des locations (sites)
- Création des départements
- Création d'un super admin
- Création d'admins par département et location
"""

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
MONGODB_LOCAL_URI = 'mongodb://localhost:27017/LeoniApp'

def connect_to_mongodb():
    """Connexion à MongoDB avec fallback"""
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

def create_locations_and_departments(db):
    """Créer les locations et départements de base"""
    
    locations_collection = db['locations']
    departments_collection = db['departments']
    
    # Définir les locations (sites Leoni)
    locations_data = [
        {
            'name': 'Mateur',
            'code': 'MAT',
            'country': 'Tunisie',
            'address': 'Zone Industrielle Mateur, Bizerte, Tunisie',
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        },
        {
            'name': 'Sousse',
            'code': 'SOU',
            'country': 'Tunisie', 
            'address': 'Zone Industrielle Sousse, Tunisie',
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        },
        {
            'name': 'Bizerte',
            'code': 'BIZ',
            'country': 'Tunisie',
            'address': 'Zone Industrielle Bizerte, Tunisie',
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
    ]
    
    # Définir les départements par location
    departments_data = [
        # Mateur
        {'name': 'Production', 'location': 'Mateur', 'description': 'Ligne de production des câbles', 'active': True},
        {'name': 'Qualité', 'location': 'Mateur', 'description': 'Contrôle qualité', 'active': True},
        {'name': 'Logistique', 'location': 'Mateur', 'description': 'Gestion des stocks et expéditions', 'active': True},
        {'name': 'IT', 'location': 'Mateur', 'description': 'Technologies de l\'information', 'active': True},
        {'name': 'RH', 'location': 'Mateur', 'description': 'Ressources humaines', 'active': True},
        
        # Sousse
        {'name': 'Production', 'location': 'Sousse', 'description': 'Ligne de production des câbles', 'active': True},
        {'name': 'Qualité', 'location': 'Sousse', 'description': 'Contrôle qualité', 'active': True},
        {'name': 'Maintenance', 'location': 'Sousse', 'description': 'Maintenance des équipements', 'active': True},
        {'name': 'Finance', 'location': 'Sousse', 'description': 'Gestion financière', 'active': True},
        {'name': 'IT', 'location': 'Sousse', 'description': 'Technologies de l\'information', 'active': True},
        
        # Bizerte
        {'name': 'Production', 'location': 'Bizerte', 'description': 'Ligne de production des câbles', 'active': True},
        {'name': 'Qualité', 'location': 'Bizerte', 'description': 'Contrôle qualité', 'active': True},
        {'name': 'Export', 'location': 'Bizerte', 'description': 'Gestion des exportations', 'active': True},
        {'name': 'RH', 'location': 'Bizerte', 'description': 'Ressources humaines', 'active': True}
    ]
    
    print("🔄 Création des locations...")
    
    # Supprimer et recréer les locations
    locations_collection.drop()
    for location in locations_data:
        result = locations_collection.insert_one(location)
        print(f"✅ Location créée: {location['name']} (ID: {result.inserted_id})")
    
    print("🔄 Création des départements...")
    
    # Supprimer et recréer les départements
    departments_collection.drop()
    for dept in departments_data:
        dept['createdAt'] = datetime.utcnow()
        dept['updatedAt'] = datetime.utcnow()
        result = departments_collection.insert_one(dept)
        print(f"✅ Département créé: {dept['name']} @ {dept['location']} (ID: {result.inserted_id})")

def create_super_admin(db):
    """Créer le super admin principal"""
    
    admins_collection = db['admins']
    
    # Données du super admin
    superadmin_data = {
        'username': 'superadmin',
        'password': bcrypt.hashpw('SuperAdmin123!'.encode('utf-8'), bcrypt.gensalt()),
        'email': 'superadmin@leoni.com',
        'firstName': 'Super',
        'lastName': 'Admin',
        'department': 'ALL',  # Accès à tous les départements
        'location': 'ALL',    # Accès à toutes les locations
        'role': 'SUPERADMIN',
        'active': True,
        'permissions': {
            'manageEmployees': True,
            'manageDocuments': True,
            'publishNews': True,
            'manageChats': True,
            'manageAdmins': True,
            'viewAllData': True,
            'systemConfig': True
        },
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
        'lastLogin': None
    }
    
    # Vérifier si le super admin existe déjà
    existing = admins_collection.find_one({'username': 'superadmin'})
    if existing:
        print("⚠️ Super admin existe déjà")
        return existing['_id']
    
    result = admins_collection.insert_one(superadmin_data)
    print(f"✅ Super admin créé (ID: {result.inserted_id})")
    print("   Username: superadmin")
    print("   Password: SuperAdmin123!")
    
    return result.inserted_id

def create_department_admins(db):
    """Créer des admins pour chaque département/location"""
    
    admins_collection = db['admins']
    departments_collection = db['departments']
    
    # Récupérer tous les départements
    departments = list(departments_collection.find({'active': True}))
    
    admins_to_create = [
        # Admins Mateur
        {
            'username': 'admin_production_mateur',
            'password': 'Admin123!',
            'email': 'admin.production.mateur@leoni.com',
            'firstName': 'Admin',
            'lastName': 'Production Mateur',
            'department': 'Production',
            'location': 'Mateur'
        },
        {
            'username': 'admin_it_mateur',
            'password': 'Admin123!',
            'email': 'admin.it.mateur@leoni.com',
            'firstName': 'Admin',
            'lastName': 'IT Mateur',
            'department': 'IT',
            'location': 'Mateur'
        },
        {
            'username': 'admin_rh_mateur',
            'password': 'Admin123!',
            'email': 'admin.rh.mateur@leoni.com',
            'firstName': 'Admin',
            'lastName': 'RH Mateur',
            'department': 'RH',
            'location': 'Mateur'
        },
        
        # Admins Sousse
        {
            'username': 'admin_production_sousse',
            'password': 'Admin123!',
            'email': 'admin.production.sousse@leoni.com',
            'firstName': 'Admin',
            'lastName': 'Production Sousse',
            'department': 'Production',
            'location': 'Sousse'
        },
        {
            'username': 'admin_it_sousse',
            'password': 'Admin123!',
            'email': 'admin.it.sousse@leoni.com',
            'firstName': 'Admin',
            'lastName': 'IT Sousse',
            'department': 'IT',
            'location': 'Sousse'
        },
        
        # Admins Bizerte
        {
            'username': 'admin_production_bizerte',
            'password': 'Admin123!',
            'email': 'admin.production.bizerte@leoni.com',
            'firstName': 'Admin',
            'lastName': 'Production Bizerte',
            'department': 'Production',
            'location': 'Bizerte'
        }
    ]
    
    print("🔄 Création des admins de département...")
    
    for admin_data in admins_to_create:
        # Vérifier si l'admin existe déjà
        existing = admins_collection.find_one({'username': admin_data['username']})
        if existing:
            print(f"⚠️ Admin existe déjà: {admin_data['username']}")
            continue
        
        # Hasher le mot de passe
        admin_data['password'] = bcrypt.hashpw(admin_data['password'].encode('utf-8'), bcrypt.gensalt())
        admin_data['role'] = 'ADMIN'
        admin_data['active'] = True
        admin_data['permissions'] = {
            'manageEmployees': True,
            'manageDocuments': True,
            'publishNews': True,
            'manageChats': True
        }
        admin_data['createdAt'] = datetime.utcnow()
        admin_data['updatedAt'] = datetime.utcnow()
        admin_data['lastLogin'] = None
        
        result = admins_collection.insert_one(admin_data)
        print(f"✅ Admin créé: {admin_data['username']} - {admin_data['department']}@{admin_data['location']} (ID: {result.inserted_id})")

def create_sample_users(db):
    """Créer des utilisateurs d'exemple pour tester le système"""
    
    users_collection = db['users']
    
    sample_users = [
        # Employés Mateur
        {
            'firstName': 'Ahmed',
            'lastName': 'Ben Ali',
            'adresse1': 'ahmed.benali@leoni.com',
            'adresse2': 'ahmed.benali.parent@gmail.com',
            'phoneNumber': '+21623456789',
            'parentalPhoneNumber': '+21623456788',
            'password': bcrypt.hashpw('Employee123!'.encode('utf-8'), bcrypt.gensalt()),
            'employeeId': '10000001',
            'department': 'Production',
            'location': 'Mateur',
            'position': 'Opérateur de production',
            'role': 'EMPLOYEE'
        },
        {
            'firstName': 'Fatma',
            'lastName': 'Trabelsi',
            'adresse1': 'fatma.trabelsi@leoni.com',
            'adresse2': 'fatma.trabelsi.parent@gmail.com',
            'phoneNumber': '+21623456790',
            'parentalPhoneNumber': '+21623456791',
            'password': bcrypt.hashpw('Employee123!'.encode('utf-8'), bcrypt.gensalt()),
            'employeeId': '10000002',
            'department': 'IT',
            'location': 'Mateur',
            'position': 'Développeur',
            'role': 'EMPLOYEE'
        },
        
        # Employés Sousse
        {
            'firstName': 'Mohamed',
            'lastName': 'Hammami',
            'adresse1': 'mohamed.hammami@leoni.com',
            'adresse2': 'mohamed.hammami.parent@gmail.com',
            'phoneNumber': '+21623456792',
            'parentalPhoneNumber': '+21623456793',
            'password': bcrypt.hashpw('Employee123!'.encode('utf-8'), bcrypt.gensalt()),
            'employeeId': '10000003',
            'department': 'Production',
            'location': 'Sousse',
            'position': 'Superviseur production',
            'role': 'EMPLOYEE'
        },
        {
            'firstName': 'Sarra',
            'lastName': 'Bouzid',
            'adresse1': 'sarra.bouzid@leoni.com',
            'adresse2': 'sarra.bouzid.parent@gmail.com',
            'phoneNumber': '+21623456794',
            'parentalPhoneNumber': '+21623456795',
            'password': bcrypt.hashpw('Employee123!'.encode('utf-8'), bcrypt.gensalt()),
            'employeeId': '10000004',
            'department': 'Finance',
            'location': 'Sousse',
            'position': 'Comptable',
            'role': 'EMPLOYEE'
        },
        
        # Employés Bizerte
        {
            'firstName': 'Karim',
            'lastName': 'Sassi',
            'adresse1': 'karim.sassi@leoni.com',
            'adresse2': 'karim.sassi.parent@gmail.com',
            'phoneNumber': '+21623456796',
            'parentalPhoneNumber': '+21623456797',
            'password': bcrypt.hashpw('Employee123!'.encode('utf-8'), bcrypt.gensalt()),
            'employeeId': '10000005',
            'department': 'Production',
            'location': 'Bizerte',
            'position': 'Technicien qualité',
            'role': 'EMPLOYEE'
        }
    ]
    
    print("🔄 Création des utilisateurs d'exemple...")
    
    for user_data in sample_users:
        # Vérifier si l'utilisateur existe déjà
        existing = users_collection.find_one({'adresse1': user_data['adresse1']})
        if existing:
            print(f"⚠️ Utilisateur existe déjà: {user_data['adresse1']}")
            continue
        
        user_data['createdAt'] = datetime.utcnow()
        user_data['updatedAt'] = datetime.utcnow()
        
        result = users_collection.insert_one(user_data)
        print(f"✅ Utilisateur créé: {user_data['firstName']} {user_data['lastName']} - {user_data['department']}@{user_data['location']} (ID: {result.inserted_id})")

def create_document_types(db):
    """Créer les types de documents disponibles"""
    
    document_types_collection = db['document_types']
    
    document_types = [
        {
            'name': 'Certificat de travail',
            'description': 'Certificat attestant de l\'emploi du salarié',
            'category': 'RH',
            'processingTime': '5 jours ouvrés',
            'requiredInfo': ['Période d\'emploi', 'Poste occupé'],
            'active': True
        },
        {
            'name': 'Attestation de salaire',
            'description': 'Document attestant du salaire mensuel',
            'category': 'Finance',
            'processingTime': '3 jours ouvrés',
            'requiredInfo': ['Mois concerné'],
            'active': True
        },
        {
            'name': 'Congé maladie',
            'description': 'Demande de congé pour raisons médicales',
            'category': 'RH',
            'processingTime': '1 jour ouvré',
            'requiredInfo': ['Dates de congé', 'Certificat médical'],
            'active': True
        },
        {
            'name': 'Bon de formation',
            'description': 'Demande de participation à une formation',
            'category': 'Formation',
            'processingTime': '7 jours ouvrés',
            'requiredInfo': ['Type de formation', 'Dates souhaitées'],
            'active': True
        },
        {
            'name': 'Attestation de stage',
            'description': 'Certificat de fin de stage',
            'category': 'RH',
            'processingTime': '5 jours ouvrés',
            'requiredInfo': ['Période de stage', 'Département'],
            'active': True
        }
    ]
    
    print("🔄 Création des types de documents...")
    
    # Supprimer et recréer les types de documents
    document_types_collection.drop()
    for doc_type in document_types:
        doc_type['createdAt'] = datetime.utcnow()
        doc_type['updatedAt'] = datetime.utcnow()
        result = document_types_collection.insert_one(doc_type)
        print(f"✅ Type de document créé: {doc_type['name']} (ID: {result.inserted_id})")

def main():
    """Fonction principale d'initialisation"""
    
    print("🚀 Initialisation du système Leoni")
    print("=" * 50)
    
    # Connexion à MongoDB
    client, db_type = connect_to_mongodb()
    if not client:
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    db = client['LeoniApp']
    print(f"✅ Connecté à la base de données LeoniApp ({db_type})")
    
    try:
        # 1. Créer les locations et départements
        create_locations_and_departments(db)
        print()
        
        # 2. Créer le super admin
        create_super_admin(db)
        print()
        
        # 3. Créer les admins de département
        create_department_admins(db)
        print()
        
        # 4. Créer les types de documents
        create_document_types(db)
        print()
        
        # 5. Créer des utilisateurs d'exemple
        create_sample_users(db)
        print()
        
        print("✅ Initialisation terminée avec succès!")
        print()
        print("📋 Comptes créés:")
        print("   Super Admin:")
        print("     Username: superadmin")
        print("     Password: SuperAdmin123!")
        print()
        print("   Admins (tous ont le mot de passe: Admin123!):")
        print("     - admin_production_mateur (Production@Mateur)")
        print("     - admin_it_mateur (IT@Mateur)")
        print("     - admin_rh_mateur (RH@Mateur)")
        print("     - admin_production_sousse (Production@Sousse)")
        print("     - admin_it_sousse (IT@Sousse)")
        print("     - admin_production_bizerte (Production@Bizerte)")
        print()
        print("   Employés (tous ont le mot de passe: Employee123!):")
        print("     - ahmed.benali@leoni.com (Production@Mateur)")
        print("     - fatma.trabelsi@leoni.com (IT@Mateur)")
        print("     - mohamed.hammami@leoni.com (Production@Sousse)")
        print("     - sarra.bouzid@leoni.com (Finance@Sousse)")
        print("     - karim.sassi@leoni.com (Production@Bizerte)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
        print("🔒 Connexion fermée")

if __name__ == "__main__":
    main()
