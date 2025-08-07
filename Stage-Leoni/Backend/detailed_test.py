#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test détaillé pour déboguer l'endpoint /me
"""

import requests
import json

# URL du serveur
BASE_URL = "http://192.168.1.15:5000"

def detailed_test():
    print("🔍 Test détaillé de l'endpoint /me")
    print("=" * 60)
    
    # Étape 1: Connexion
    print("📝 Étape 1: Connexion...")
    login_data = {
        "email": "aa@gmail.com",
        "password": "123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login", json=login_data, timeout=10)
        print(f"   Statut login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Échec de connexion")
            return
            
        login_result = login_response.json()
        token = login_result.get('token')
        user_info = login_result.get('user', {})
        
        print(f"✅ Connexion réussie")
        print(f"   Token: {token[:50]}..." if token else "   Token: None")
        print(f"   User ID: {user_info.get('id')}")
        print(f"   Email: {user_info.get('email')}")
        
        # Étape 2: Test /me
        print(f"\n📝 Étape 2: Test endpoint /me...")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        me_response = requests.get(f"{BASE_URL}/me", headers=headers, timeout=10)
        print(f"   Statut /me: {me_response.status_code}")
        print(f"   Headers envoyés: {headers}")
        
        if me_response.status_code == 200:
            me_result = me_response.json()
            print("✅ Endpoint /me réussi")
            print(f"   Données reçues:")
            user_data = me_result.get('user', {})
            for key, value in user_data.items():
                if key != 'password':  # Ne pas afficher le password
                    print(f"      • {key}: {value}")
        else:
            print("❌ Échec endpoint /me")
            try:
                error_result = me_response.json()
                print(f"   Message d'erreur: {error_result.get('message', 'Aucun message')}")
            except:
                print(f"   Réponse brute: {me_response.text[:200]}...")
                
        # Étape 3: Test direct avec MongoDB pour comparaison
        print(f"\n📝 Étape 3: Vérification directe MongoDB...")
        test_mongo_direct()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def test_mongo_direct():
    """Test direct de MongoDB pour voir les données utilisateur"""
    try:
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
        
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=5000)
        db = client['LeoniApp']
        users_collection = db['users']
        
        user = users_collection.find_one({'email': 'aa@gmail.com'})
        if user:
            print("✅ Utilisateur trouvé dans MongoDB:")
            for key, value in user.items():
                if key != 'password':
                    print(f"      • {key}: {value}")
        else:
            print("❌ Utilisateur non trouvé dans MongoDB")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur MongoDB direct: {e}")

if __name__ == "__main__":
    detailed_test()
