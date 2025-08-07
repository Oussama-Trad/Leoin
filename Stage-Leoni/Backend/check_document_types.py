#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour vérifier les types de documents dans la base de données
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration MongoDB
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

def check_document_types():
    try:
        print("🔍 Connexion à MongoDB Atlas...")
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        client.server_info()  # Test de connexion
        print("✅ Connexion MongoDB Atlas réussie")
        
        db = client['LeoniApp']
        document_types_collection = db['document_types']
        
        print("\n📋 Types de documents dans la base de données:")
        print("=" * 60)
        
        document_types = list(document_types_collection.find({}))
        
        if not document_types:
            print("❌ Aucun type de document trouvé dans la base de données")
        else:
            for i, doc_type in enumerate(document_types, 1):
                print(f"{i}. Nom: {doc_type.get('name', 'UNNAMED')}")
                print(f"   ID: {doc_type.get('_id')}")
                print(f"   Actif: {doc_type.get('active', 'N/A')}")
                print(f"   Description: {doc_type.get('description', 'N/A')}")
                print("-" * 40)
        
        print(f"\n📊 Total: {len(document_types)} types de documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification des types de documents")
    print("=" * 60)
    
    check_document_types()
