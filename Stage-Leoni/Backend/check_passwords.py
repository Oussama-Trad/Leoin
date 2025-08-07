#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import bcrypt

def check_passwords():
    try:
        # Connexion à MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['LeoniApp']
        
        print("🔍 VÉRIFICATION DES MOTS DE PASSE")
        print("=" * 40)
        
        # Récupérer les utilisateurs avec mot de passe
        users = list(db.users.find({"password": {"$exists": True}}, {"email": 1, "password": 1}))
        
        for user in users:
            email = user.get('email')
            password_hash = user.get('password')
            
            print(f"\n👤 {email}:")
            print(f"   Type password: {type(password_hash)}")
            print(f"   Length: {len(password_hash) if password_hash else 0}")
            print(f"   Starts with $2b$: {password_hash.startswith('$2b$') if isinstance(password_hash, str) else False}")
            
            # Test du mot de passe "123456"
            test_password = "123456"
            
            try:
                if isinstance(password_hash, str):
                    password_bytes = password_hash.encode('utf-8')
                else:
                    password_bytes = password_hash
                
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_bytes)
                print(f"   Test '123456': {'✅ Valide' if is_valid else '❌ Invalide'}")
                
            except Exception as e:
                print(f"   ❌ Erreur test: {e}")
        
        # Créer un nouveau hash pour comparaison
        print(f"\n🔧 CRÉATION D'UN NOUVEAU HASH:")
        new_hash = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"   Nouveau hash: {new_hash}")
        print(f"   Type: {type(new_hash)}")
        print(f"   Test: {'✅ Valide' if bcrypt.checkpw('123456'.encode('utf-8'), new_hash.encode('utf-8')) else '❌ Invalide'}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_passwords()
