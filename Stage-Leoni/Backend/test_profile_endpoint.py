#!/usr/bin/env python3
"""
Test de l'endpoint /api/profile pour vérifier les données renvoyées
"""

import requests
import json

def test_profile_endpoint():
    # Simuler une requête avec un token d'utilisateur
    base_url = "http://localhost:5000"
    
    print("🔍 TEST DE L'ENDPOINT /api/profile")
    print("=" * 40)
    
    # D'abord, récupérer un token en se connectant
    login_data = {
        "email": "hh@gmail.com",
        "password": "123456"  # Mot de passe de test
    }
    
    try:
        # Test de connexion
        print("1️⃣ Test de connexion...")
        login_response = requests.post(f"{base_url}/api/login", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            print(f"✅ Connexion réussie, token obtenu: {token[:20]}..." if token else "❌ Pas de token")
            
            if token:
                # Test de l'endpoint profile
                print("\n2️⃣ Test de l'endpoint /api/profile...")
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                profile_response = requests.get(f"{base_url}/api/profile", headers=headers, timeout=10)
                
                print(f"Status Code: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Réponse du profil reçue:")
                    print(json.dumps(profile_data, indent=2, ensure_ascii=False))
                    
                    # Vérifier les champs importants
                    user = profile_data.get('user', {})
                    print(f"\n🔍 Vérification des champs:")
                    print(f"   - Département: '{user.get('department', 'VIDE')}'")
                    print(f"   - DepartmentRef: '{user.get('departmentRef', 'VIDE')}'")
                    print(f"   - Location: '{user.get('location', 'VIDE')}'")
                    print(f"   - LocationRef: '{user.get('locationRef', 'VIDE')}'")
                    
                else:
                    print(f"❌ Erreur {profile_response.status_code}: {profile_response.text}")
            
        else:
            print(f"❌ Échec de connexion {login_response.status_code}: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Flask sur localhost:5000")
        print("   Vérifiez que le serveur est en cours d'exécution")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_profile_endpoint()
