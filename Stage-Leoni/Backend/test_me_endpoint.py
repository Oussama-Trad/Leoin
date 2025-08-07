#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_me_endpoint():
    try:
        print("🧪 TEST DE L'ENDPOINT /me")
        print("=" * 30)
        
        # URL du backend
        base_url = "http://127.0.0.1:5000"
        
        # 1. Test de connexion avec oussamatrzd19@gmail.com
        login_data = {
            "email": "oussamatrzd19@gmail.com",
            "password": "123456"  # Password par défaut
        }
        
        print("🔐 Tentative de connexion...")
        login_response = requests.post(f"{base_url}/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            print(f"✅ Connexion réussie! Token obtenu.")
            
            # 2. Test endpoint /me avec le token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("\n👤 Test endpoint /me...")
            me_response = requests.get(f"{base_url}/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Réponse /me:")
                print(json.dumps(user_data, indent=2, ensure_ascii=False))
                
                # Vérifier les champs importants
                user_info = user_data.get('user', {})
                print(f"\n📋 INFORMATIONS UTILISATEUR:")
                print(f"   Email: {user_info.get('email')}")
                print(f"   Nom: {user_info.get('name')}")
                print(f"   Téléphone: {user_info.get('phone')}")
                print(f"   Département: {user_info.get('department')}")
                print(f"   Site de travail: {user_info.get('workSite')}")
                print(f"   Poste: {user_info.get('position')}")
                
            else:
                print(f"❌ Erreur /me: {me_response.status_code}")
                print(f"   Réponse: {me_response.text}")
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            print(f"   Réponse: {login_response.text}")
            
            # Essayer avec un autre utilisateur
            print("\n🔄 Essai avec test@example.com...")
            login_data2 = {
                "email": "test@example.com", 
                "password": "123456"
            }
            
            login_response2 = requests.post(f"{base_url}/login", json=login_data2)
            if login_response2.status_code == 200:
                login_result2 = login_response2.json()
                token2 = login_result2.get('token')
                print(f"✅ Connexion test@example.com réussie!")
                
                headers2 = {'Authorization': f'Bearer {token2}'}
                me_response2 = requests.get(f"{base_url}/me", headers=headers2)
                
                if me_response2.status_code == 200:
                    user_data2 = me_response2.json()
                    print("✅ Réponse /me pour test@example.com:")
                    print(json.dumps(user_data2, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_me_endpoint()
