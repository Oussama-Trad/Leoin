#!/usr/bin/env python3
"""
Script pour supprimer le champ 'createdAt' de tous les documents dans la collection 'departments'
de la base de données MongoDB Atlas LeoniApp
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# URI de connexion MongoDB Atlas
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')

def remove_createdat_from_departments():
    try:
        print("🔍 Connexion à MongoDB Atlas...")
        
        # Se connecter à MongoDB Atlas
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        
        # Tester la connexion
        client.server_info()
        print("✅ Connexion MongoDB Atlas réussie")
        
        # Accéder à la base de données
        db = client['LeoniApp']
        
        # Accéder à la collection departments
        departments_collection = db['departments']
        
        # Compter le nombre de documents avant modification
        total_docs = departments_collection.count_documents({})
        print(f"📊 Nombre total de départements: {total_docs}")
        
        # Compter le nombre de documents avec le champ createdAt
        docs_with_createdat = departments_collection.count_documents({"createdAt": {"$exists": True}})
        print(f"📊 Départements avec champ 'createdAt': {docs_with_createdat}")
        
        if docs_with_createdat == 0:
            print("✅ Aucun document avec le champ 'createdAt' trouvé. Rien à faire.")
            return
        
        # Afficher quelques exemples avant suppression
        print("\n📋 Exemples de documents avant modification:")
        sample_docs = departments_collection.find({"createdAt": {"$exists": True}}).limit(3)
        for i, doc in enumerate(sample_docs, 1):
            print(f"  {i}. {doc.get('name', 'Sans nom')} - createdAt: {doc.get('createdAt', 'N/A')}")
        
        # Demander confirmation
        confirmation = input(f"\n❓ Voulez-vous supprimer le champ 'createdAt' de {docs_with_createdat} documents? (oui/non): ").lower().strip()
        
        if confirmation not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée par l'utilisateur.")
            return
        
        print("\n🔄 Suppression du champ 'createdAt' en cours...")
        
        # Supprimer le champ createdAt de tous les documents qui l'ont
        result = departments_collection.update_many(
            {"createdAt": {"$exists": True}},  # Filtre: documents qui ont le champ createdAt
            {"$unset": {"createdAt": ""}}      # Opération: supprimer le champ createdAt
        )
        
        print(f"✅ Opération terminée!")
        print(f"📊 Documents modifiés: {result.modified_count}")
        print(f"📊 Documents correspondants: {result.matched_count}")
        
        # Vérification finale
        remaining_docs_with_createdat = departments_collection.count_documents({"createdAt": {"$exists": True}})
        print(f"📊 Documents restants avec 'createdAt': {remaining_docs_with_createdat}")
        
        if remaining_docs_with_createdat == 0:
            print("🎉 Tous les champs 'createdAt' ont été supprimés avec succès!")
        else:
            print(f"⚠️  Il reste encore {remaining_docs_with_createdat} documents avec le champ 'createdAt'")
        
        # Afficher quelques exemples après suppression
        print("\n📋 Exemples de documents après modification:")
        sample_docs_after = departments_collection.find({}).limit(3)
        for i, doc in enumerate(sample_docs_after, 1):
            has_createdat = "createdAt" in doc
            print(f"  {i}. {doc.get('name', 'Sans nom')} - a createdAt: {has_createdat}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'opération: {str(e)}")
        print(f"❌ Type d'erreur: {type(e).__name__}")
    
    finally:
        try:
            client.close()
            print("🔒 Connexion MongoDB fermée")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Script de suppression du champ 'createdAt' des départements")
    print("=" * 60)
    remove_createdat_from_departments()
    print("=" * 60)
    print("✅ Script terminé")
