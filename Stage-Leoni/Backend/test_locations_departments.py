#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_locations_departments():
    print("🧪 Test des nouvelles routes Locations et Departments")
    print("=" * 60)
    
    # 1. Tester la route locations
    print("1. Test GET /locations")
    try:
        response = requests.get(f"{BASE_URL}/locations")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                locations = data.get('locations', [])
                print(f"   ✅ {len(locations)} sites trouvés:")
                for loc in locations:
                    print(f"      • {loc['name']} ({loc['code']})")
                
                # 2. Tester les départements pour chaque location
                print("\n2. Test GET /locations/<id>/departments")
                for location in locations[:2]:  # Tester les 2 premiers
                    location_id = location['_id']
                    print(f"\n   Test pour {location['name']} (ID: {location_id})")
                    
                    dept_response = requests.get(f"{BASE_URL}/locations/{location_id}/departments")
                    print(f"   Status: {dept_response.status_code}")
                    
                    if dept_response.status_code == 200:
                        dept_data = dept_response.json()
                        if dept_data.get('success'):
                            departments = dept_data.get('departments', [])
                            print(f"   ✅ {len(departments)} départements trouvés:")
                            for dept in departments[:5]:  # Afficher les 5 premiers
                                print(f"      • {dept['name']} ({dept['code']})")
                        else:
                            print(f"   ❌ Erreur: {dept_data.get('message')}")
                    else:
                        print(f"   ❌ HTTP Error {dept_response.status_code}")
            else:
                print(f"   ❌ Erreur: {data.get('message')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 3. Tester tous les départements
    print("\n3. Test GET /departments")
    try:
        response = requests.get(f"{BASE_URL}/departments")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                departments = data.get('departments', [])
                print(f"   ✅ {len(departments)} départements totaux trouvés")
                
                # Grouper par site
                sites = {}
                for dept in departments:
                    site_name = dept['location']['name']
                    if site_name not in sites:
                        sites[site_name] = []
                    sites[site_name].append(dept['name'])
                
                for site_name, dept_names in sites.items():
                    print(f"      📍 {site_name}: {len(dept_names)} départements")
            else:
                print(f"   ❌ Erreur: {data.get('message')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test des routes terminé !")

if __name__ == "__main__":
    test_locations_departments()
