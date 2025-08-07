#!/usr/bin/env python3
"""
Script pour renommer les champs dans la base de données MongoDB:
- email → adresse1
- parentalEmail → adresse2
"""

try:
    from pymongo import MongoClient
    import sys
    from datetime import datetime
    
    # Configuration
    MONGO_URI = "mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp"
    DATABASE_NAME = "LeoniApp"
    
    print("🔄 MIGRATION: Renommer les champs email dans la base de données")
    print("=" * 60)
    print("📋 email → adresse1")
    print("📋 parentalEmail → adresse2")
    print("=" * 60)
    
    # Connexion
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    users_collection = db.users
    
    # Test de la connexion
    client.admin.command('ping')
    print("✅ Connexion à MongoDB réussie!")
    
    # Statistiques avant migration
    total_users = users_collection.count_documents({})
    users_with_email = users_collection.count_documents({"email": {"$exists": True}})
    users_with_parental = users_collection.count_documents({"parentalEmail": {"$exists": True}})
    
    print(f"\n📊 AVANT MIGRATION:")
    print(f"   👥 Total utilisateurs: {total_users}")
    print(f"   📧 Avec champ 'email': {users_with_email}")
    print(f"   📧 Avec champ 'parentalEmail': {users_with_parental}")
    
    # Demander confirmation
    response = input(f"\n❓ Procéder à la migration des champs? Cette opération est IRREVERSIBLE! (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Migration annulée")
        sys.exit(0)
    
    print("\n🔄 MIGRATION EN COURS...")
    
    # Étape 1: Renommer 'email' en 'adresse1'
    print("\n1️⃣ Renommage 'email' → 'adresse1'...")
    result_email = users_collection.update_many(
        {"email": {"$exists": True}},
        {"$rename": {"email": "adresse1"}}
    )
    print(f"   ✅ {result_email.modified_count} documents mis à jour")
    
    # Étape 2: Renommer 'parentalEmail' en 'adresse2' 
    print("\n2️⃣ Renommage 'parentalEmail' → 'adresse2'...")
    result_parental = users_collection.update_many(
        {"parentalEmail": {"$exists": True}},
        {"$rename": {"parentalEmail": "adresse2"}}
    )
    print(f"   ✅ {result_parental.modified_count} documents mis à jour")
    
    # Vérification après migration
    print("\n🔍 VÉRIFICATION POST-MIGRATION...")
    users_with_adresse1 = users_collection.count_documents({"adresse1": {"$exists": True}})
    users_with_adresse2 = users_collection.count_documents({"adresse2": {"$exists": True}})
    users_with_old_email = users_collection.count_documents({"email": {"$exists": True}})
    users_with_old_parental = users_collection.count_documents({"parentalEmail": {"$exists": True}})
    
    print(f"\n📊 APRÈS MIGRATION:")
    print(f"   👥 Total utilisateurs: {total_users}")
    print(f"   📧 Avec champ 'adresse1': {users_with_adresse1}")
    print(f"   📧 Avec champ 'adresse2': {users_with_adresse2}")
    print(f"   ⚠️  Avec ancien champ 'email': {users_with_old_email}")
    print(f"   ⚠️  Avec ancien champ 'parentalEmail': {users_with_old_parental}")
    
    # Afficher quelques exemples
    print(f"\n📋 EXEMPLES D'UTILISATEURS APRÈS MIGRATION:")
    sample_users = list(users_collection.find({}, {
        "firstName": 1, 
        "lastName": 1, 
        "adresse1": 1, 
        "adresse2": 1,
        "email": 1,  # Pour vérifier qu'il n'existe plus
        "parentalEmail": 1  # Pour vérifier qu'il n'existe plus
    }).limit(3))
    
    for i, user in enumerate(sample_users, 1):
        print(f"   {i}. {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}:")
        print(f"      adresse1: {user.get('adresse1', 'MANQUANT')}")
        print(f"      adresse2: {user.get('adresse2', 'MANQUANT')}")
        if 'email' in user:
            print(f"      ⚠️  ANCIEN email encore présent: {user['email']}")
        if 'parentalEmail' in user:
            print(f"      ⚠️  ANCIEN parentalEmail encore présent: {user['parentalEmail']}")
    
    if users_with_adresse1 == users_with_email and users_with_adresse2 == users_with_parental:
        if users_with_old_email == 0 and users_with_old_parental == 0:
            print(f"\n🎉 MIGRATION RÉUSSIE!")
            print(f"✅ Tous les champs ont été renommés correctement")
        else:
            print(f"\n⚠️  MIGRATION PARTIELLEMENT RÉUSSIE")
            print(f"❌ Certains anciens champs existent encore")
    else:
        print(f"\n❌ PROBLÈME LORS DE LA MIGRATION")
        print(f"⚠️  Vérifiez les données manuellement")
    
    print(f"\n💡 PROCHAINES ÉTAPES:")
    print(f"   1. Mettre à jour le code pour utiliser 'adresse1' et 'adresse2'")
    print(f"   2. Tester l'application")
    print(f"   3. Supprimer les anciens champs si la migration est complète")

except Exception as e:
    print(f"❌ Erreur lors de la migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
