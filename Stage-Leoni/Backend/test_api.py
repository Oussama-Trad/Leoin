#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester l'API et voir ce qui est renvoyé
"""

import requests
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Test avec un utilisateur existant
def test_api():
    # D'abord, regardons les utilisateurs dans la DB
    MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
    client = MongoClient(MONGODB_ATLAS_URI)
    db = client['LeoniApp']
    
    # Prendre l'utilisateur ww@gmail.com spécifiquement
    user = db['users'].find_one({'email': 'ww@gmail.com'})
    if not user:
        print("❌ Utilisateur ww@gmail.com non trouvé")
        return
    print(f"🔍 Test avec utilisateur: {user['firstName']} {user['lastName']} ({user['email']})")
    print(f"📍 Dans DB - Location: {user.get('location', 'N/A')}")
    print(f"🏢 Dans DB - Department: {user.get('department', 'N/A')}")
    print(f"🔗 LocationRef: {user.get('locationRef', 'N/A')}")
    print(f"🔗 DepartmentRef: {user.get('departmentRef', 'N/A')}")
    
    # Test de connexion via API
    login_data = {
        "email": user['email'],
        "password": "aaaaaa"  # Le mot de passe par défaut que vous utilisez
    }
    
    print(f"\n🔍 Tentative de connexion via API...")
    try:
        response = requests.post('http://localhost:5000/login', 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data = data.get('user', {})
                token = data.get('token')
                print(f"✅ Connexion réussie!")
                print(f"📍 API Response - Location: {user_data.get('location', 'N/A')}")
                print(f"🏢 API Response - Department: {user_data.get('department', 'N/A')}")
                
                # Test de l'API /me
                print(f"\n🔍 Test API /me...")
                me_response = requests.get('http://localhost:5000/me',
                                         headers={'Authorization': f'Bearer {token}'})
                
                print(f"📊 /me Status Code: {me_response.status_code}")
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    if me_data.get('success'):
                        me_user = me_data.get('user', {})
                        print(f"✅ /me réussie!")
                        print(f"📍 /me Response - Location: {me_user.get('location', 'N/A')}")
                        print(f"🏢 /me Response - Department: {me_user.get('department', 'N/A')}")
                    else:
                        print(f"❌ /me échec: {me_data.get('message')}")
                else:
                    print(f"❌ /me erreur: {me_response.text}")
            else:
                print(f"❌ Connexion échec: {data.get('message')}")
        else:
            print(f"❌ Erreur HTTP: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    client.close()

if __name__ == "__main__":
    print("🧪 Test API - Connexion et récupération profil")
    print("=" * 60)
    test_api()
