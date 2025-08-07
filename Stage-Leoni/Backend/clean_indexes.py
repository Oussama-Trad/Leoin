#!/usr/bin/env python3
"""
Script pour nettoyer les index problématiques avant l'initialisation
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

def clean_indexes():
    load_dotenv()
    MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

    try:
        print("🔗 Connexion à MongoDB...")
        client = MongoClient(MONGODB_ATLAS_URI)
        db = client['LeoniApp']
        
        # Supprimer l'index problématique sur le champ code
        try:
            db['locations'].drop_index('code_1')
            print('✅ Index code_1 supprimé')
        except Exception as e:
            print(f'ℹ️ Index code_1: {e}')
        
        # Supprimer toutes les locations avec code null
        result = db['locations'].delete_many({'code': None})
        print(f'✅ {result.deleted_count} locations avec code null supprimées')
        
        # Recréer l'index avec partial filter pour éviter les null
        try:
            db['locations'].create_index('code', unique=True, partialFilterExpression={'code': {'$ne': None}})
            print('✅ Index code recréé avec filtre partiel')
        except Exception as e:
            print(f'⚠️ Création index: {e}')
        
        client.close()
        print('✅ Nettoyage terminé')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')

if __name__ == "__main__":
    clean_indexes()
