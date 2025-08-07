import requests
import json

BASE_URL = "http://localhost:5000"

def test_login_and_filter():
    # Test avec un utilisateur existant
    login_data = {
        "adresse1": "pp@gmail.com",
        "password": "123456"  # Mot de passe par défaut
    }
    
    print("🔍 Test connexion utilisateur...")
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if data.get('success'):
            token = data.get('token')
            print(f"✅ Token obtenu: {token[:20]}...")
            
            # Test du filtrage d'employés
            print("\n🔍 Test filtrage employés (Production/Mateur)...")
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "department": "Production",
                "location": "Mateur", 
                "role": "ADMIN"
            }
            
            filter_response = requests.get(
                f"{BASE_URL}/api/admin/employees/filtered",
                headers=headers,
                params=params
            )
            print(f"Filter Status: {filter_response.status_code}")
            filter_data = filter_response.json()
            print(f"Filter Response: {filter_data}")
            
        else:
            print(f"❌ Connexion échouée: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_login_and_filter()
