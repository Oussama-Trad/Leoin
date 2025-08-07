#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de refactorisation des collections News
- Supprime les anciennes collections 'news' et 'news_interactions'
- Crée une nouvelle collection 'news' simplifiée pour le système admin
- Structure adaptée pour ciblage par département et localisation
"""

from pymongo import MongoClient
import os
from datetime import datetime

def connect_to_mongodb():
    try:
        connection_string = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
        client = MongoClient(connection_string)
        client.admin.command('ping')
        print("🔗 Connexion MongoDB réussie!")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def backup_existing_news():
    """Sauvegarder les anciennes données news avant suppression"""
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    
    try:
        # Sauvegarder les anciennes news
        old_news = list(db.news.find({}))
        old_interactions = list(db.news_interactions.find({}))
        
        print(f"📊 Anciennes données trouvées:")
        print(f"   • News: {len(old_news)} documents")
        print(f"   • Interactions: {len(old_interactions)} documents")
        
        if old_news:
            # Créer une collection de sauvegarde
            backup_collection = db.news_backup
            backup_collection.insert_many(old_news)
            print(f"✅ Sauvegarde créée dans 'news_backup'")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        client.close()
        return False

def drop_old_collections():
    """Supprimer les anciennes collections"""
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    
    try:
        # Supprimer les anciennes collections
        if 'news' in db.list_collection_names():
            db.news.drop()
            print("🗑️ Collection 'news' supprimée")
        
        if 'news_interactions' in db.list_collection_names():
            db.news_interactions.drop()
            print("🗑️ Collection 'news_interactions' supprimée")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        client.close()
        return False

def create_new_news_collection():
    """Créer la nouvelle collection news simplifiée"""
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    news_collection = db.news
    
    try:
        # Créer les index pour optimiser les requêtes
        print("🔧 Création des index...")
        
        # Index pour les requêtes par département et localisation
        news_collection.create_index([("targetDepartment", 1), ("targetLocation", 1)])
        news_collection.create_index([("publishedAt", -1)])  # Tri par date
        news_collection.create_index([("isActive", 1)])      # Filtrage actif/inactif
        news_collection.create_index([("authorId", 1)])      # Requêtes par auteur
        
        print("✅ Index créés avec succès")
        
        # Insérer quelques exemples de news pour test
        sample_news = [
            {
                "title": "Bienvenue dans le nouveau système de news",
                "description": "Cette news est visible par tous les employés IT de Sousse.",
                "content": "Le nouveau système de news permet aux administrateurs de cibler spécifiquement les employés par département et localisation. Plus de réactions complexes, juste de l'information claire et ciblée.",
                "photos": [],
                "targetLocation": "Sousse",
                "targetDepartment": "IT", 
                "authorId": None,  # À remplir par l'admin
                "authorName": "Système",
                "publishedAt": datetime.utcnow(),
                "isActive": True,
                "priority": "normal",  # low, normal, high, urgent
                "category": "general", # general, announcement, training, safety
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "title": "Nouvelle procédure de sécurité",
                "description": "Mise à jour des protocoles de sécurité pour tous les départements de Messadine.",
                "content": "Tous les employés de Messadine doivent prendre connaissance des nouvelles procédures de sécurité mises en place ce mois-ci.",
                "photos": [],
                "targetLocation": "Messadine",
                "targetDepartment": None,  # None = tous les départements
                "authorId": None,
                "authorName": "Sécurité",
                "publishedAt": datetime.utcnow(),
                "isActive": True,
                "priority": "high",
                "category": "safety",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        news_collection.insert_many(sample_news)
        print(f"✅ {len(sample_news)} exemples de news insérés")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        client.close()
        return False

def show_new_structure():
    """Afficher la nouvelle structure de la collection"""
    print("\n📋 Nouvelle structure de la collection 'news':")
    print("=" * 50)
    print("""
    {
        "_id": ObjectId,                    // ID unique MongoDB
        "title": String,                    // Titre de l'actualité
        "description": String,              // Description courte
        "content": String,                  // Contenu détaillé
        "photos": [String],                 // URLs des photos (optionnel)
        
        // Ciblage
        "targetLocation": String,           // Location ciblée (ex: "Sousse", "Messadine")
        "targetDepartment": String|null,    // Département ciblé (null = tous)
        
        // Auteur
        "authorId": ObjectId|null,          // ID de l'admin qui a posté
        "authorName": String,               // Nom de l'auteur
        
        // Métadonnées
        "publishedAt": Date,                // Date de publication
        "isActive": Boolean,                // Actif/inactif
        "priority": String,                 // "low", "normal", "high", "urgent"
        "category": String,                 // "general", "announcement", "training", "safety"
        
        // Timestamps
        "createdAt": Date,
        "updatedAt": Date
    }
    """)
    
    print("\n🎯 Logique de ciblage:")
    print("• targetLocation = 'Sousse' + targetDepartment = 'IT' → Seuls les employés IT de Sousse")
    print("• targetLocation = 'Messadine' + targetDepartment = null → Tous les employés de Messadine")
    print("• targetLocation = null + targetDepartment = 'HR' → Tous les employés HR (toutes locations)")
    print("• targetLocation = null + targetDepartment = null → Tous les employés")

if __name__ == "__main__":
    print("🚀 Refactorisation des collections News")
    print("=" * 60)
    
    # Étape 1: Sauvegarde
    print("\n1️⃣ Sauvegarde des données existantes...")
    if backup_existing_news():
        print("✅ Sauvegarde réussie")
    else:
        print("⚠️ Aucune donnée à sauvegarder ou erreur")
    
    # Étape 2: Suppression
    print("\n2️⃣ Suppression des anciennes collections...")
    if drop_old_collections():
        print("✅ Suppression réussie")
    else:
        print("❌ Erreur lors de la suppression")
        exit(1)
    
    # Étape 3: Création
    print("\n3️⃣ Création de la nouvelle structure...")
    if create_new_news_collection():
        print("✅ Nouvelle collection créée avec succès")
    else:
        print("❌ Erreur lors de la création")
        exit(1)
    
    # Étape 4: Documentation
    show_new_structure()
    
    print("\n" + "=" * 60)
    print("✅ Refactorisation terminée avec succès!")
    print("📝 Les anciennes données sont sauvegardées dans 'news_backup'")
