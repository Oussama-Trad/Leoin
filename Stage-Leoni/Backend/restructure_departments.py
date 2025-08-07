#!/usr/bin/env python3
"""
Script pour supprimer et recréer la collection departments
avec la structure demandée : départements liés aux locations par nom
"""

import os
from pymongo import MongoClient
from datetime import datetime

# Configuration MongoDB
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

def main():
    try:
        # Connexion à MongoDB
        print("🔗 Connexion à MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client.LeoniApp
        
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion MongoDB réussie")
        
        # Supprimer l'ancienne collection departments
        print("🗑️ Suppression de l'ancienne collection departments...")
        db.departments.drop()
        print("✅ Collection departments supprimée")
        
        # Définir les départements par localisation
        departments_data = [
            # Messadine
            {"name": "Maintenance", "location": "Messadine", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Production", "location": "Messadine", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Qualité", "location": "Messadine", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Logistique", "location": "Messadine", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            
            # Mateur
            {"name": "Maintenance", "location": "Mateur", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Production", "location": "Mateur", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "RH", "location": "Mateur", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            
            # Menzel Hayet (Monastir)
            {"name": "Production", "location": "Menzel Hayet (Monastir)", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Qualité", "location": "Menzel Hayet (Monastir)", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
            {"name": "Bureau d'études", "location": "Menzel Hayet (Monastir)", "active": True, "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()},
        ]
        
        # Insérer les nouveaux départements
        print("📝 Création des nouveaux départements...")
        result = db.departments.insert_many(departments_data)
        print(f"✅ {len(result.inserted_ids)} départements créés")
        
        # Afficher un résumé
        print("\n📊 Résumé des départements créés :")
        locations = {}
        for dept in departments_data:
            location = dept['location']
            if location not in locations:
                locations[location] = []
            locations[location].append(dept['name'])
        
        for location, dept_names in locations.items():
            print(f"  📍 {location}: {', '.join(dept_names)}")
        
        # Mettre à jour la collection users pour ajouter les champs location et department si nécessaire
        print("\n🔄 Vérification de la structure des utilisateurs...")
        sample_user = db.users.find_one()
        if sample_user:
            user_fields = list(sample_user.keys())
            if 'location' not in user_fields:
                print("⚠️ Champ 'location' manquant dans users - à ajouter lors de l'inscription")
            if 'department' not in user_fields:
                print("⚠️ Champ 'department' manquant dans users - à ajouter lors de l'inscription")
        
        print("\n🎉 Script terminé avec succès !")
        print("Les utilisateurs pourront maintenant :")
        print("1. Sélectionner une localisation")
        print("2. Voir les départements disponibles pour cette localisation")
        print("3. S'inscrire avec ces informations")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        
    finally:
        if 'client' in locals():
            client.close()
            print("🔗 Connexion MongoDB fermée")

if __name__ == "__main__":
    main()
