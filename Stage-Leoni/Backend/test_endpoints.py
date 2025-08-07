#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester les endpoints de locations et départements
"""

import requests
import json

# URL du serveur
BASE_URL = "http://192.168.1.15:5000"

def test_locations_endpoint():
    print("🔍 Test de l'endpoint /api/locations")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/locations", timeout=10)
        print(f"📊 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint /api/locations fonctionne")
            print(f"📝 Nombre de locations: {len(data.get('locations', []))}")
            for location in data.get('locations', []):
                print(f"   • {location.get('name')} (ID: {location.get('_id')})")
            return data.get('locations', [])
        else:
            print("❌ Endpoint /api/locations échoué")
            print(f"📝 Réponse: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def test_departments_endpoint(location_id, location_name):
    print(f"\n🔍 Test de l'endpoint /api/locations/{location_id}/departments")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/locations/{location_id}/departments", timeout=10)
        print(f"📊 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint départements fonctionne pour {location_name}")
            print(f"📝 Nombre de départements: {len(data.get('departments', []))}")
            for dept in data.get('departments', []):
                print(f"   • {dept.get('name')} (ID: {dept.get('_id')})")
        else:
            print(f"❌ Endpoint départements échoué pour {location_name}")
            print(f"📝 Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🧪 Test des endpoints locations et départements")
    print("=" * 60)
    
    # Test locations
    locations = test_locations_endpoint()
    
    # Test départements pour chaque location
    for location in locations[:2]:  # Tester seulement les 2 premières
        test_departments_endpoint(location['_id'], location['name'])
