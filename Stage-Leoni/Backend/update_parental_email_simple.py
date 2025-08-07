#!/usr/bin/env python3
"""
Script simple pour tester la connexion et mettre à jour parentalEmail
"""

try:
    from pymongo import MongoClient
    import sys
    from datetime import datetime
    
    # Configuration
    MONGO_URI = "mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp"
    DATABASE_NAME = "LeoniApp"
    
    print("🔍 Tentative de connexion à MongoDB...")
    
    # Connexion
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    users_collection = db.users
    
    # Test de la connexion
    client.admin.command('ping')
    print("✅ Connexion réussie!")
    
    # Compter les utilisateurs
    total_users = users_collection.count_documents({})
    print(f"📊 Total utilisateurs: {total_users}")
    
    # Compter ceux sans parentalEmail
    users_without_parental = users_collection.count_documents({
        "$or": [
            {"parentalEmail": {"$exists": False}},
            {"parentalEmail": None},
            {"parentalEmail": ""},
        ]
    })
    
    print(f"📊 Utilisateurs sans parentalEmail: {users_without_parental}")
    
    # Si il y en a, les mettre à jour
    if users_without_parental > 0:
        print("🔄 Mise à jour en cours...")
        
        # Trouver les utilisateurs à mettre à jour
        users_to_update = list(users_collection.find({
            "$or": [
                {"parentalEmail": {"$exists": False}},
                {"parentalEmail": None},
                {"parentalEmail": ""},
            ]
        }))
        
        updated_count = 0
        for user in users_to_update:
            user_id = user.get('_id')
            first_name = user.get('firstName', 'user')
            last_name = user.get('lastName', 'unknown')
            current_email = user.get('email', 'no-email')
            
            # Générer une adresse2 simple
            if '@' in current_email:
                email_parts = current_email.split('@')
                default_parental_email = f"{email_parts[0]}.adresse2@{email_parts[1]}"
            else:
                default_parental_email = f"{first_name.lower()}.{last_name.lower()}.adresse2@leoni.com"
            
            # Mettre à jour
            result = users_collection.update_one(
                {"_id": user_id},
                {"$set": {"parentalEmail": default_parental_email}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"✅ {first_name} {last_name}: {default_parental_email}")
        
        print(f"🎉 {updated_count} utilisateurs mis à jour!")
    else:
        print("✅ Tous les utilisateurs ont déjà un parentalEmail")
    
    # Vérification finale
    final_count = users_collection.count_documents({
        "$or": [
            {"parentalEmail": {"$exists": False}},
            {"parentalEmail": None},
            {"parentalEmail": ""},
        ]
    })
    
    if final_count == 0:
        print("✅ Succès: Tous les utilisateurs ont maintenant un parentalEmail")
    else:
        print(f"⚠️ Il reste {final_count} utilisateurs sans parentalEmail")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
