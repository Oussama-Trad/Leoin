#!/usr/bin/env python3
"""
Script pour rendre le champ parentalEmail (Adresse2) obligatoire
- Ajouter une adresse2 par défaut pour les utilisateurs qui n'en ont pas
- Vérifier l'intégrité des données
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient

# Configuration de la base de données
MONGO_URI = "mongodb+srv://oussama:oussama123@cluster0.xdkgf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "LeoniApp"

def connect_to_mongodb():
    """Connexion à MongoDB Atlas"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        
        # Tester la connexion
        client.admin.command('ping')
        print("✅ Connexion à MongoDB Atlas réussie")
        
        return db
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        sys.exit(1)

def make_parental_email_required():
    """Rendre parentalEmail obligatoire en ajoutant une valeur par défaut"""
    try:
        db = connect_to_mongodb()
        users_collection = db.users
        
        print("🔍 Recherche des utilisateurs sans parentalEmail...")
        
        # Trouver les utilisateurs sans parentalEmail
        users_without_parental = list(users_collection.find({
            "$or": [
                {"parentalEmail": {"$exists": False}},
                {"parentalEmail": None},
                {"parentalEmail": ""},
                {"parentalEmail": {"$regex": "^\\s*$"}}  # Seulement des espaces
            ]
        }))
        
        print(f"📊 {len(users_without_parental)} utilisateur(s) trouvé(s) sans parentalEmail")
        
        if len(users_without_parental) == 0:
            print("✅ Tous les utilisateurs ont déjà un parentalEmail")
            return
        
        # Compteur pour les mises à jour
        updated_count = 0
        
        for user in users_without_parental:
            user_id = user.get('_id')
            first_name = user.get('firstName', 'user')
            last_name = user.get('lastName', 'unknown')
            current_email = user.get('email', 'no-email')
            
            print(f"\n👤 Traitement de {first_name} {last_name}...")
            print(f"   📧 Email actuel: {current_email}")
            
            # Générer une adresse2 par défaut basée sur l'email principal
            if current_email and current_email != 'no-email':
                # Extraire le domaine de l'email principal
                email_parts = current_email.split('@')
                if len(email_parts) == 2:
                    local_part = email_parts[0]
                    domain = email_parts[1]
                    # Créer une adresse2 avec un suffixe
                    default_parental_email = f"{local_part}.adresse2@{domain}"
                else:
                    # Fallback si l'email principal est malformé
                    default_parental_email = f"{first_name.lower()}.{last_name.lower()}.adresse2@leoni.com"
            else:
                # Fallback si pas d'email principal
                default_parental_email = f"{first_name.lower()}.{last_name.lower()}.adresse2@leoni.com"
            
            print(f"   📧 Adresse2 générée: {default_parental_email}")
            
            # Vérifier que cette adresse2 n'existe pas déjà
            existing_with_same_parental = users_collection.find_one({
                "parentalEmail": default_parental_email,
                "_id": {"$ne": user_id}
            })
            
            if existing_with_same_parental:
                # Ajouter un timestamp pour l'unicité
                timestamp = int(datetime.now().timestamp())
                default_parental_email = f"{first_name.lower()}.{last_name.lower()}.{timestamp}@leoni.com"
                print(f"   ⚠️  Conflit détecté, nouvelle adresse2: {default_parental_email}")
            
            # Mettre à jour l'utilisateur
            result = users_collection.update_one(
                {"_id": user_id},
                {"$set": {"parentalEmail": default_parental_email}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"   ✅ Utilisateur mis à jour avec succès")
            else:
                print(f"   ❌ Échec de mise à jour")
        
        print(f"\n🎉 {updated_count} utilisateur(s) mis à jour avec succès")
        print(f"📊 parentalEmail est maintenant obligatoire pour tous les utilisateurs")
        
        # Vérification finale
        remaining_without_parental = users_collection.count_documents({
            "$or": [
                {"parentalEmail": {"$exists": False}},
                {"parentalEmail": None},
                {"parentalEmail": ""},
                {"parentalEmail": {"$regex": "^\\s*$"}}
            ]
        })
        
        if remaining_without_parental == 0:
            print("✅ Vérification finale: Tous les utilisateurs ont maintenant un parentalEmail")
        else:
            print(f"⚠️  {remaining_without_parental} utilisateur(s) n'ont toujours pas de parentalEmail")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        sys.exit(1)

def display_statistics():
    """Afficher les statistiques de la base de données"""
    try:
        db = connect_to_mongodb()
        users_collection = db.users
        
        total_users = users_collection.count_documents({})
        users_with_email = users_collection.count_documents({"email": {"$exists": True, "$ne": ""}})
        users_with_parental = users_collection.count_documents({"parentalEmail": {"$exists": True, "$ne": ""}})
        
        print(f"\n📊 STATISTIQUES DE LA BASE DE DONNÉES:")
        print(f"   👥 Total utilisateurs: {total_users}")
        print(f"   📧 Avec email principal: {users_with_email}")
        print(f"   📧 Avec adresse2: {users_with_parental}")
        print(f"   📊 Taux de complétude adresse2: {(users_with_parental/total_users*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des statistiques: {e}")

if __name__ == "__main__":
    print("🚀 SCRIPT: Rendre parentalEmail (Adresse2) obligatoire")
    print("="*60)
    
    # Afficher les statistiques actuelles
    display_statistics()
    
    # Demander confirmation
    response = input(f"\n❓ Voulez-vous procéder à la mise à jour? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        make_parental_email_required()
        
        # Afficher les statistiques après mise à jour
        display_statistics()
    else:
        print("❌ Opération annulée")
