#!/usr/bin/env python3
"""
Script pour restructurer la collection departments dans la base LeoniApp existante
"""

from pymongo import MongoClient
import os
from datetime import datetime

# Configuration MongoDB
MONGO_URI = "mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp"

def main():
    try:
        # Connexion à MongoDB
        print("🔗 Connexion à MongoDB...")
        client = MongoClient(MONGO_URI)
        
        # Utiliser la base de données existante LeoniApp
        db = client.LeoniApp  # <-- Votre base existante !
        
        print(f"✅ Connecté à la base de données: {db.name}")
        
        # Supprimer l'ancienne collection departments
        print("🗑️ Suppression de l'ancienne collection departments...")
        db.departments.drop()
        print("✅ Ancienne collection supprimée")
        
        # Créer les nouveaux départements avec la structure demandée
        departments_data = [
            # Messadine
            {"name": "Maintenance", "location": "Messadine", "createdAt": datetime.now()},
            {"name": "Production", "location": "Messadine", "createdAt": datetime.now()},
            {"name": "Qualité", "location": "Messadine", "createdAt": datetime.now()},
            {"name": "Logistique", "location": "Messadine", "createdAt": datetime.now()},
            
            # Mateur
            {"name": "Maintenance", "location": "Mateur", "createdAt": datetime.now()},
            {"name": "Production", "location": "Mateur", "createdAt": datetime.now()},
            {"name": "RH", "location": "Mateur", "createdAt": datetime.now()},
            
            # Menzel Hayet (Monastir)
            {"name": "Production", "location": "Manzel Hayet (Monastir)", "createdAt": datetime.now()},
            {"name": "Qualité", "location": "Manzel Hayet (Monastir)", "createdAt": datetime.now()},
            {"name": "Bureau d'études", "location": "Manzel Hayet (Monastir)", "createdAt": datetime.now()},
        ]
        
        # Insérer les nouveaux départements
        print("📝 Création des nouveaux départements...")
        result = db.departments.insert_many(departments_data)
        print(f"✅ {len(result.inserted_ids)} départements créés avec succès")
        
        # Vérification
        total_departments = db.departments.count_documents({})
        print(f"📊 Total départements dans la base: {total_departments}")
        
        # Afficher les départements par location
        print("\n📍 Départements par location:")
        for location in ["Messadine", "Mateur", "Manzel Hayet (Monastir)"]:
            count = db.departments.count_documents({"location": location})
            print(f"  - {location}: {count} départements")
            
        # Vérifier aussi les collections existantes
        collections = db.list_collection_names()
        print(f"\n📁 Collections dans la base LeoniApp: {collections}")
        
        print("\n🎉 Restructuration terminée avec succès!")
        print("Les départements sont maintenant liés aux locations par nom au lieu d'ID")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
