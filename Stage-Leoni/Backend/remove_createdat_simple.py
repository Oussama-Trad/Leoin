#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def remove_createdat_from_departments():
    """
    Supprime le champ createdAt de tous les documents de la collection departments
    """
    try:
        # Configuration MongoDB Atlas (données hardcodées pour simplicité)
        username = 'oussamatrad99'
        password = 'Trad2000'
        cluster_url = 'cluster0.b3sav.mongodb.net'
        database_name = 'LeoniApp'
        
        # Construction de l'URI MongoDB
        mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority&appName=Cluster0"
        
        print("🔗 Connexion à MongoDB Atlas...")
        client = MongoClient(mongo_uri)
        
        # Sélectionner la base de données
        db = client[database_name]
        
        # Vérifier la connexion
        db.admin.command('ping')
        print("✅ Connexion réussie à MongoDB Atlas")
        
        # Accéder à la collection departments
        departments_collection = db.departments
        
        # Vérifier combien de documents ont le champ createdAt
        count_with_createdat = departments_collection.count_documents({"createdAt": {"$exists": True}})
        print(f"📊 Nombre de départements avec createdAt: {count_with_createdat}")
        
        if count_with_createdat == 0:
            print("ℹ️ Aucun document avec le champ createdAt trouvé")
        else:
            # Supprimer le champ createdAt de tous les documents
            result = departments_collection.update_many(
                {"createdAt": {"$exists": True}},  # Filtre: documents qui ont le champ createdAt
                {"$unset": {"createdAt": ""}}      # Opération: supprimer le champ createdAt
            )
            
            print(f"✅ Champ createdAt supprimé de {result.modified_count} département(s)")
        
        # Vérifier que la suppression a bien fonctionné
        remaining_count = departments_collection.count_documents({"createdAt": {"$exists": True}})
        print(f"📊 Nombre de départements avec createdAt après suppression: {remaining_count}")
        
        # Afficher quelques exemples de documents pour vérification
        print("\n📋 Exemples de départements après suppression:")
        sample_docs = list(departments_collection.find({}, {"name": 1, "location": 1, "createdAt": 1}).limit(3))
        for i, doc in enumerate(sample_docs, 1):
            print(f"  {i}. {doc}")
        
        client.close()
        print("\n🎉 Suppression du champ createdAt terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression du champ createdAt: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🗑️ Suppression du champ createdAt de la collection departments")
    print("=" * 60)
    
    success = remove_createdat_from_departments()
    
    if success:
        print("\n✅ Script terminé avec succès")
    else:
        print("\n❌ Le script a échoué")
