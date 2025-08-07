import requests
import json

BASE_URL = "http://localhost:5000"

def test_superadmin_access():
    # Test avec le super admin (sans filtrage)
    print("🔍 Test avec SUPERADMIN...")
    
    # Test direct de l'API avec role SUPERADMIN
    test_token = "fake-token-for-demo"  # Juste pour tester la logique
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test 1: Filtrage par département IT
    print("\\n📋 Test 1: Employés IT (tous sites)")
    params = {
        "department": "IT",
        "role": "SUPERADMIN"  # SuperAdmin peut voir tous les IT peu importe la location
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/employees/filtered", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 401:
            print("🔒 Token requis (normal)")
        else:
            print(f"Résultat: {data}")
            
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 2: Filtrage par location seulement
    print("\\n📋 Test 2: Employés Mateur (tous départements)")
    params = {
        "location": "Mateur",
        "role": "SUPERADMIN"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/employees/filtered", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 401:
            print("🔒 Token requis (normal)")
        else:
            print(f"Résultat: {data}")
            
    except Exception as e:
        print(f"Erreur: {e}")

    # Test 3: Sans filtres (SuperAdmin voit tout)
    print("\\n📋 Test 3: Tous les employés (SuperAdmin)")
    params = {
        "role": "SUPERADMIN"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/employees/filtered", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 401:
            print("🔒 Token requis (normal)")
        else:
            print(f"Nombre total d'employés visibles: {data.get('count', 0)}")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_superadmin_access()
