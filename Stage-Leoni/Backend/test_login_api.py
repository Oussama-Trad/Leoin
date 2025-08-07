#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester la connexion avec l'utilisateur existant
"""

import requests
import json

# URL du serveur
BASE_URL = "http://192.168.1.15:5000"

def test_login():
    print("🔍 Test de connexion...")
    print("=" * 50)
    
    # Données de connexion pour l'utilisateur aa aa
    login_data = {
        "email": "aa@gmail.com",
        "password": "123456"  # Supposons que c'est le mot de passe
    }
    
    print(f"📧 Email: {login_data['email']}")
    print(f"🔑 Password: {'*' * len(login_data['password'])}")
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data, timeout=10)
        
        print(f"\n📊 Statut de réponse: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie !")
            print(f"📝 Données utilisateur:")
            user_data = data.get('user', {})
            for key, value in user_data.items():
                print(f"   • {key}: {value}")
        else:
            print("❌ Connexion échouée")
            try:
                error_data = response.json()
                print(f"📝 Message d'erreur: {error_data.get('message', 'Erreur inconnue')}")
            except:
                print(f"📝 Erreur HTTP: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion au serveur: {e}")

def test_profile():
    print("\n🔍 Test de récupération du profil...")
    print("=" * 50)
    
    # D'abord se connecter pour obtenir le token
    login_data = {
        "email": "aa@gmail.com", 
        "password": "123456"
    }
    
    try:
        # Connexion
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        if login_response.status_code == 200:
            login_data_response = login_response.json()
            token = login_data_response.get('token')
            user_id = login_data_response.get('user', {}).get('id')
            
            print(f"✅ Connexion OK, token obtenu")
            print(f"👤 User ID: {user_id}")
            
            # Test récupération profil
            headers = {'Authorization': f'Bearer {token}'}
            profile_response = requests.get(f"{BASE_URL}/me", headers=headers)
            
            print(f"📊 Statut profil: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Profil récupéré avec succès !")
                print(f"📝 Données profil:")
                for key, value in profile_data.items():
                    print(f"   • {key}: {value}")
            else:
                print("❌ Échec récupération profil")
                try:
                    error_data = profile_response.json()
                    print(f"📝 Message d'erreur: {error_data.get('message', 'Erreur inconnue')}")
                except:
                    print(f"📝 Erreur HTTP: {profile_response.text}")
        else:
            print("❌ Impossible de se connecter pour tester le profil")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    print("🧪 Test de l'API d'authentification")
    print("=" * 60)
    
    test_login()
    test_profile()
