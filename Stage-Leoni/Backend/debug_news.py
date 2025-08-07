#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour déboguer les actualités
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

def debug_news():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    news_collection = db['news']
    users_collection = db['users']
    
    print("\n🔍 Analyse des actualités...")
    print("=" * 60)
    
    # 1. Vérifier toutes les news
    all_news = list(news_collection.find({}))
    print(f"📊 Nombre total d'actualités: {len(all_news)}")
    
    if len(all_news) > 0:
        print("\n📰 Détails des actualités:")
        for i, news in enumerate(all_news, 1):
            print(f"\n   {i}. {news.get('title', 'SANS TITRE')}")
            print(f"      • Status: {news.get('status', 'N/A')}")
            print(f"      • Visibility: {news.get('visibility', 'N/A')}")
            print(f"      • Publishé le: {news.get('publishedAt', 'N/A')}")
            print(f"      • Expire le: {news.get('expiryAt', 'N/A')}")
            print(f"      • Catégorie: {news.get('category', 'N/A')}")
    
    # 2. Vérifier les critères de l'endpoint
    current_time = datetime.utcnow()
    published_news = list(news_collection.find({'status': 'published'}))
    print(f"\n📊 Actualités publiées: {len(published_news)}")
    
    # 3. Vérifier les actualités non expirées
    non_expired_query = {
        'status': 'published',
        '$or': [
            {'expiryAt': {'$exists': False}},
            {'expiryAt': None},
            {'expiryAt': {'$gt': current_time}}
        ]
    }
    non_expired_news = list(news_collection.find(non_expired_query))
    print(f"📊 Actualités publiées et non expirées: {len(non_expired_news)}")
    
    # 4. Tester avec un utilisateur spécifique
    user = users_collection.find_one({})
    if user:
        print(f"\n👤 Test avec utilisateur: {user.get('email', 'N/A')}")
        print(f"   • LocationRef: {user.get('locationRef', 'N/A')}")
        print(f"   • DepartmentRef: {user.get('departmentRef', 'N/A')}")
        
        # Simuler la requête de l'endpoint
        visibility_query = {
            'status': 'published',
            '$or': [
                {'visibility.type': 'company'},  # Actualités pour toute l'entreprise
                {
                    'visibility.type': 'location',
                    'visibility.targetIds': user.get('locationRef')
                },
                {
                    'visibility.type': 'department',
                    'visibility.targetIds': user.get('departmentRef')
                }
            ]
        }
        
        visible_news = list(news_collection.find(visibility_query))
        print(f"📊 Actualités visibles pour cet utilisateur: {len(visible_news)}")
        
        if visible_news:
            print("   📰 Actualités visibles:")
            for news in visible_news:
                print(f"      • {news.get('title', 'SANS TITRE')}")
    
    client.close()
    return True

if __name__ == "__main__":
    print("🔍 Debug des actualités")
    print("=" * 60)
    
    debug_news()
