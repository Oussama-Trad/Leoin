#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester l'endpoint des actualités
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_login_and_news():
    """Test de connexion puis récupération des news"""
    
    # 1. Connexion pour récupérer un token
    print("🔍 Test de connexion...")
    login_data = {
        "email": "oussama.trad@leoni.com",  # Remplacez par un email valide
        "password": "password123"  # Remplacez par le mot de passe
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"📡 Réponse login: {login_response.status_code}")
        print(f"📡 Contenu login: {login_response.text}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            
            if token:
                print(f"✅ Token récupéré: {token[:50]}...")
                
                # 2. Test de récupération des news avec le token
                print("\n🔍 Test de récupération des news...")
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                news_response = requests.get(f"{BASE_URL}/api/news", headers=headers)
                print(f"📡 Réponse news: {news_response.status_code}")
                print(f"📡 Contenu news: {news_response.text}")
                
                if news_response.status_code == 200:
                    news_result = news_response.json()
                    print(f"✅ News récupérées: {news_result}")
                else:
                    print(f"❌ Erreur récupération news: {news_response.text}")
            else:
                print("❌ Pas de token dans la réponse")
        else:
            print(f"❌ Erreur de connexion: {login_response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_login_and_news()
