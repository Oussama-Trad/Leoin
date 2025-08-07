#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de migration des employeeId
Convertit les anciens formats (EMP001, EMP002, etc.) vers le nouveau format (nombres à 8 chiffres)
"""

from pymongo import MongoClient
import os
from datetime import datetime

def connect_to_mongodb():
    try:
        connection_string = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
        client = MongoClient(connection_string)
        client.admin.command('ping')
        print("🔗 Connexion MongoDB réussie!")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return None

def migrate_employee_ids():
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🔄 Migration des employeeId vers le nouveau format...")
    print("=" * 60)
    
    # Trouver tous les utilisateurs avec des employeeId au format EMP
    users_with_old_format = list(users_collection.find({
        'employeeId': {'$regex': '^EMP', '$options': 'i'}
    }))
    
    if not users_with_old_format:
        print("✅ Aucun utilisateur avec l'ancien format d'employeeId trouvé")
        client.close()
        return True
    
    print(f"📊 {len(users_with_old_format)} utilisateur(s) à migrer:")
    
    # Générer les nouveaux IDs en commençant par 10000001
    next_id = 10000001
    
    # Vérifier les IDs déjà utilisés au nouveau format
    existing_new_ids = users_collection.find({
        'employeeId': {'$regex': r'^\d{8}$'}
    }).sort('employeeId', -1).limit(1)
    
    for user in existing_new_ids:
        current_max = int(user['employeeId'])
        if current_max >= next_id:
            next_id = current_max + 1
    
    # Migrer chaque utilisateur
    migration_count = 0
    for user in users_with_old_format:
        old_id = user['employeeId']
        new_id = str(next_id)
        
        try:
            # Vérifier que le nouvel ID n'existe pas déjà
            while users_collection.find_one({'employeeId': new_id}):
                next_id += 1
                new_id = str(next_id)
            
            # Effectuer la mise à jour
            result = users_collection.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'employeeId': new_id,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ {user['firstName']} {user['lastName']}: {old_id} → {new_id}")
                migration_count += 1
            else:
                print(f"⚠️ Échec migration pour {user['firstName']} {user['lastName']}")
            
            next_id += 1
            
        except Exception as e:
            print(f"❌ Erreur migration {old_id}: {e}")
    
    print(f"\n📋 Résumé de la migration:")
    print(f"   • Utilisateurs traités: {len(users_with_old_format)}")
    print(f"   • Migrations réussies: {migration_count}")
    print(f"   • Prochain ID disponible: {next_id}")
    
    client.close()
    return migration_count == len(users_with_old_format)

def verify_migration():
    """Vérifier que la migration s'est bien passée"""
    client = connect_to_mongodb()
    if not client:
        return False
    
    db = client['LeoniApp']
    users_collection = db['users']
    
    print("\n🔍 Vérification post-migration...")
    print("=" * 40)
    
    # Compter les anciens formats
    old_format_count = users_collection.count_documents({
        'employeeId': {'$regex': '^EMP', '$options': 'i'}
    })
    
    # Compter les nouveaux formats
    new_format_count = users_collection.count_documents({
        'employeeId': {'$regex': r'^\d{8}$'}
    })
    
    # Compter les formats invalides
    invalid_format_count = users_collection.count_documents({
        'employeeId': {
            '$exists': True,
            '$not': {'$regex': r'^(EMP|\d{8})'}
        }
    })
    
    print(f"📊 Statistiques employeeId:")
    print(f"   • Ancien format (EMP): {old_format_count}")
    print(f"   • Nouveau format (8 chiffres): {new_format_count}")
    print(f"   • Formats invalides: {invalid_format_count}")
    
    if old_format_count > 0:
        print("\n⚠️ Il reste des employeeId à l'ancien format:")
        remaining = users_collection.find({
            'employeeId': {'$regex': '^EMP', '$options': 'i'}
        })
        for user in remaining:
            print(f"   • {user['firstName']} {user['lastName']}: {user['employeeId']}")
    
    client.close()
    return old_format_count == 0

if __name__ == "__main__":
    print("🚀 Script de migration des employeeId")
    print("Conversion: EMP001, EMP002... → 10000001, 10000002...")
    
    # Effectuer la migration
    success = migrate_employee_ids()
    
    if success:
        print("\n✅ Migration terminée avec succès!")
        
        # Vérification
        verify_migration()
    else:
        print("\n❌ La migration a échoué")
    
    print("\n" + "=" * 60)
    print("Script terminé.")
