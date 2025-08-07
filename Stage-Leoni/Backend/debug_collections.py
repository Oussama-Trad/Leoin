#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
from bson import ObjectId

# Configuration MongoDB Atlas
MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    MONGO_URI = 'mongodb+srv://oussama:0000@clusteryoussef.oy3h8.mongodb.net/leoni_app?retryWrites=true&w=majority&appName=ClusterYoussef'

def main():
    print("🔍 DEBUT DÉBOGAGE COLLECTIONS")
    
    try:
        # Connexion MongoDB Atlas
        client = MongoClient(MONGO_URI)
        db = client['leoni_app']
        
        # Lister toutes les collections
        collections = db.list_collection_names()
        print(f"📚 Collections disponibles: {collections}")
        
        # Pour chaque collection, compter les documents
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"  📁 {collection_name}: {count} documents")
        
        # Vérifier spécifiquement 'departments'
        if 'departments' in collections:
            print("\n🔍 ANALYSE COLLECTION 'departments':")
            departments = list(db['departments'].find({}).limit(3))
            print(f"   Premiers départements: {departments}")
        else:
            print("\n❌ COLLECTION 'departments' N'EXISTE PAS")
            
        # Chercher les collections qui pourraient contenir des départements
        print("\n🔍 RECHERCHE COLLECTIONS AVEC 'depart' DANS LE NOM:")
        for collection_name in collections:
            if 'depart' in collection_name.lower():
                count = db[collection_name].count_documents({})
                print(f"  📁 {collection_name}: {count} documents")
                if count > 0:
                    sample = db[collection_name].find_one({})
                    print(f"     Exemple: {sample}")
        
        print("\n✅ DÉBOGAGE TERMINÉ")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == "__main__":
    main()
