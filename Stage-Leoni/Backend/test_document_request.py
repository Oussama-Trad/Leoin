#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester la création d'une demande de document
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2ODhiOGYyMTlmZmU2MmI2YTNjNmJkMjUiLCJ1c2VyX2lkIjoiNjg4YjhmMjE5ZmZlNjJiNmEzYzZiZDI1IiwiZW1haWwiOiJvdXNzYW1hdHJ6ZDE5QGdtYWlsLmNvbSIsImV4cCI6MTc1NDA2NDEyNH0.8sKpOi6n9ZFmJdG7VW6S3UmW0pqjHJOtGnHlbZcNM6I"  # Token d'exemple

def test_document_request(document_type):
    print(f"🔍 Test création demande de document: {document_type}")
    
    url = f"{BASE_URL}/document-request"
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "documentType": document_type,
        "description": f"Demande de {document_type} pour test"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"📋 Réponse: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"✅ Succès pour: {document_type}")
            else:
                print(f"❌ Échec pour: {document_type}")
                print(f"   Erreur: {result.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Réponse non-JSON: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("-" * 50)

def main():
    print("🧪 Test des demandes de documents")
    print("=" * 50)
    
    # Types de documents à tester
    document_types = [
        "Identity Card",
        "Employment Contract", 
        "Medical Certificate",
        "Educational Certificate",
        "Background Check",
        "Tax Documents",
        "Type Invalide"  # Pour tester la validation
    ]
    
    for doc_type in document_types:
        test_document_request(doc_type)

if __name__ == "__main__":
    main()
