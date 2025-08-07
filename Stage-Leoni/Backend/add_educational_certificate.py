#!/usr/bin/env python3
"""
Script pour ajouter 'Educational Certificate' aux types de documents côté serveur
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def add_educational_certificate_type():
    try:
        # Connexion MongoDB
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client['LeoniApp']
        
        print("🔍 Vérification des types de documents existants...")
        
        # Vérifier si Educational Certificate existe déjà
        existing = db.document_types.find_one({"name": "Educational Certificate"})
        
        if existing:
            print("✅ 'Educational Certificate' existe déjà !")
            if not existing.get('isActive', True):
                # Réactiver si inactif
                db.document_types.update_one(
                    {"name": "Educational Certificate"},
                    {"$set": {"isActive": True, "updatedAt": datetime.utcnow()}}
                )
                print("✅ 'Educational Certificate' réactivé !")
        else:
            # Ajouter le nouveau type
            new_type = {
                "name": "Educational Certificate",
                "description": "Certificat d'éducation ou attestation scolaire",
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = db.document_types.insert_one(new_type)
            print(f"✅ 'Educational Certificate' ajouté avec l'ID: {result.inserted_id}")
        
        # Afficher tous les types actifs
        print("\n📋 Types de documents actifs:")
        types = list(db.document_types.find({"isActive": True}))
        for i, doc_type in enumerate(types, 1):
            print(f"   {i}. {doc_type['name']}")
        
        print(f"\n🎉 Total: {len(types)} types de documents disponibles")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ajout du type 'Educational Certificate'...")
    success = add_educational_certificate_type()
    
    if success:
        print("\n✅ SUCCÈS! Maintenant testez dans votre app mobile!")
    else:
        print("\n❌ ÉCHEC! Vérifiez la connexion MongoDB.")
