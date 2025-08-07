import requests
import json

BASE_URL = "http://localhost:5000"

def test_create_and_filter():
    # Créer un nouvel utilisateur de test
    user_data = {
        "firstName": "TestAdmin",
        "lastName": "Leoni",
        "adresse1": "testadmin@leoni.com",
        "adresse2": "parent@leoni.com",
        "phoneNumber": "12345678",
        "parentalPhoneNumber": "87654321",
        "password": "test123",
        "confirmPassword": "test123",
        "location": "Messadine",
        "department": "IT"
    }
    
    print("🔍 Création d'un utilisateur de test...")
    try:
        # Créer l'utilisateur
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        print(f"Register Status: {response.status_code}")
        register_data = response.json()
        print(f"Register Response: {register_data}")
        
        if register_data.get('success'):
            token = register_data.get('token')
            print(f"✅ Utilisateur créé et token obtenu: {token[:20]}...")
            
            # Test du filtrage d'employés
            print("\\n🔍 Test filtrage employés (IT/Messadine)...")
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "department": "IT",
                "location": "Messadine", 
                "role": "ADMIN"
            }
            
            filter_response = requests.get(
                f"{BASE_URL}/api/admin/employees/filtered",
                headers=headers,
                params=params
            )
            print(f"Filter Status: {filter_response.status_code}")
            filter_data = filter_response.json()
            print(f"Employees found: {filter_data.get('count', 0)}")
            
            if filter_data.get('employees'):
                print("📋 Employés trouvés:")
                for emp in filter_data['employees'][:3]:
                    name = f"{emp.get('firstName', '')} {emp.get('lastName', '')}"
                    dept = emp.get('department', 'N/A')
                    loc = emp.get('location', 'N/A')
                    print(f"  - {name} ({dept}/{loc})")
                    
        else:
            print(f"❌ Création échouée: {register_data.get('message')}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_create_and_filter()
