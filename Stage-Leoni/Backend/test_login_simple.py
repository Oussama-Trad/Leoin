#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_login_simple():
    try:
        print("🧪 TEST DE CONNEXION SIMPLE")
        print("=" * 35)
        
        # URL du backend
        base_url = "http://127.0.0.1:5000"
        
        # Test avec les utilisateurs
        users_to_test = [
            "oussamatrzd19@gmail.com",
            "test@example.com"
        ]
        
        for email in users_to_test:
            print(f"\n🔐 Test connexion: {email}")
            
            login_data = {
                "email": email,
                "password": "123456"
            }
            
            try:
                response = requests.post(f"{base_url}/login", json=login_data, timeout=10)
                print(f"   Status: {response.status_code}")
                print(f"   Réponse: {response.text[:200]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    token = result.get('token')
                    if token:
                        print(f"   ✅ Token obtenu!")
                        
                        # Test /me
                        headers = {'Authorization': f'Bearer {token}'}
                        me_response = requests.get(f"{base_url}/me", headers=headers)
                        
                        if me_response.status_code == 200:
                            user_data = me_response.json()
                            user_info = user_data.get('user', {})
                            print(f"   👤 Nom: {user_info.get('name')}")
                            print(f"   📧 Email: {user_info.get('email')}")
                            print(f"   🏢 Département: {user_info.get('department')}")
                            print(f"   🏗️ Location: {user_info.get('location')}")
                            print(f"   💼 Position: {user_info.get('position')}")
                            print(f"   📞 Téléphone: {user_info.get('phone')}")
                        else:
                            print(f"   ❌ Erreur /me: {me_response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erreur requête: {e}")
                
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_login_simple()
