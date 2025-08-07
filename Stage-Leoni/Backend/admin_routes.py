from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
import os

# Collection pour les admins
def register_admin_routes(app, db):
    """
    Enregistre les routes pour la gestion des admins
    """
    
    # Collections
    admins_collection = db['admins']
    users_collection = db['users']
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '123')
    
    def verify_admin_token(token):
        """Vérifier et décoder un token admin"""
        try:
            decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return decoded
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # Route pour l'authentification admin
    @app.route('/api/admin/auth/login', methods=['POST', 'OPTIONS'])
    def admin_login():
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response

        print("🔍 ADMIN_LOGIN: Requête reçue", flush=True)
        try:
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'success': False, 'message': 'Username et password requis'}), 400

            username = data['username'].lower().strip()
            password = data['password']

            print(f"🔍 ADMIN_LOGIN: Recherche admin {username}", flush=True)
            
            # Rechercher l'admin
            admin = admins_collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ],
                'active': True
            })

            if not admin:
                print("❌ ADMIN_LOGIN: Admin non trouvé", flush=True)
                return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

            # Vérifier le mot de passe
            stored_password = admin['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
                print("❌ ADMIN_LOGIN: Mot de passe incorrect", flush=True)
                return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

            print("✅ ADMIN_LOGIN: Authentification réussie", flush=True)

            # Générer un token JWT
            token_payload = {
                'admin_id': str(admin['_id']),
                'username': admin['username'],
                'role': admin.get('role', 'ADMIN'),
                'department': admin.get('department', ''),
                'location': admin.get('location', ''),
                'exp': datetime.utcnow() + timedelta(hours=8)  # Token valide 8h
            }
            
            token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')

            # Mettre à jour la dernière connexion
            admins_collection.update_one(
                {'_id': admin['_id']},
                {
                    '$set': {
                        'lastLogin': datetime.utcnow(),
                        'updatedAt': datetime.utcnow()
                    }
                }
            )

            return jsonify({
                'success': True,
                'message': 'Connexion admin réussie',
                'token': token,
                'admin': {
                    'id': str(admin['_id']),
                    'username': admin['username'],
                    'role': admin.get('role', 'ADMIN'),
                    'department': admin.get('department', ''),
                    'location': admin.get('location', ''),
                    'firstName': admin.get('firstName', ''),
                    'lastName': admin.get('lastName', ''),
                    'email': admin.get('email', '')
                }
            }), 200

        except Exception as e:
            print(f"❌ ADMIN_LOGIN: Exception = {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Erreur serveur lors de la connexion'
            }), 500

    # Route pour créer un admin
    @app.route('/api/admin/create', methods=['POST', 'OPTIONS'])
    def create_admin():
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response

        print("🔍 CREATE_ADMIN: Requête reçue", flush=True)
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Données manquantes'}), 400

            # Champs requis
            required_fields = ['username', 'password', 'department', 'location']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return jsonify({
                    'success': False, 
                    'message': f'Champs manquants: {", ".join(missing_fields)}'
                }), 400

            username = data['username'].lower().strip()
            
            # Vérifier si l'admin existe déjà
            existing_admin = admins_collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': data.get('email', '').lower().strip()} if data.get('email') else {'username': username}
                ]
            })
            
            if existing_admin:
                return jsonify({'success': False, 'message': 'Cet admin existe déjà'}), 400

            # Hasher le mot de passe
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

            # Créer l'admin
            admin_data = {
                'username': username,
                'password': hashed_password,
                'email': data.get('email', '').lower().strip(),
                'firstName': data.get('firstName', '').strip(),
                'lastName': data.get('lastName', '').strip(),
                'department': data['department'].strip(),
                'location': data['location'].strip(),
                'role': data.get('role', 'ADMIN'),  # ADMIN ou SUPERADMIN
                'active': True,
                'permissions': data.get('permissions', {
                    'manageEmployees': True,
                    'manageDocuments': True,
                    'publishNews': True,
                    'manageChats': True
                }),
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'lastLogin': None
            }

            result = admins_collection.insert_one(admin_data)
            
            if result.inserted_id:
                print(f"✅ Admin créé: {username} - {data['department']}/{data['location']}")
                return jsonify({
                    'success': True,
                    'message': 'Admin créé avec succès',
                    'admin': {
                        'id': str(result.inserted_id),
                        'username': username,
                        'department': data['department'],
                        'location': data['location'],
                        'role': data.get('role', 'ADMIN')
                    }
                }), 201
            else:
                return jsonify({'success': False, 'message': 'Erreur lors de la création'}), 500
                
        except Exception as e:
            print(f"❌ CREATE_ADMIN: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur serveur lors de la création de l\'admin',
                'error': str(e)
            }), 500

    # Route pour récupérer les informations de l'admin connecté
    @app.route('/api/admin/me', methods=['GET', 'OPTIONS'])
    def get_current_admin():
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': 'Token admin requis'}), 401

            token = auth_header.split(' ')[1]
            payload = verify_admin_token(token)
            
            if not payload:
                return jsonify({'success': False, 'message': 'Token admin invalide'}), 401

            admin_id = payload.get('admin_id')
            admin = admins_collection.find_one(
                {'_id': ObjectId(admin_id)},
                {'password': 0}  # Exclure le mot de passe
            )
            
            if not admin:
                return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404

            admin_data = {
                'id': str(admin['_id']),
                'username': admin['username'],
                'email': admin.get('email', ''),
                'firstName': admin.get('firstName', ''),
                'lastName': admin.get('lastName', ''),
                'department': admin.get('department', ''),
                'location': admin.get('location', ''),
                'role': admin.get('role', 'ADMIN'),
                'permissions': admin.get('permissions', {}),
                'active': admin.get('active', True),
                'lastLogin': admin.get('lastLogin'),
                'createdAt': admin.get('createdAt'),
                'updatedAt': admin.get('updatedAt')
            }
            
            # Formater les dates
            for date_field in ['lastLogin', 'createdAt', 'updatedAt']:
                if admin_data[date_field] and hasattr(admin_data[date_field], 'isoformat'):
                    admin_data[date_field] = admin_data[date_field].isoformat()

            return jsonify({
                'success': True,
                'admin': admin_data
            }), 200

        except Exception as e:
            print(f"❌ GET_CURRENT_ADMIN: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur serveur'
            }), 500

    # Route pour lister tous les admins (SUPERADMIN seulement)
    @app.route('/api/admin/list', methods=['GET', 'OPTIONS'])
    def list_admins():
        if request.method == 'OPTIONS':
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response

        try:
            # Vérifier le token SUPERADMIN
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': 'Token admin requis'}), 401

            token = auth_header.split(' ')[1]
            payload = verify_admin_token(token)
            
            if not payload or payload.get('role') != 'SUPERADMIN':
                return jsonify({'success': False, 'message': 'Accès réservé aux SUPERADMIN'}), 403

            # Récupérer tous les admins
            admins = list(admins_collection.find(
                {},
                {'password': 0}  # Exclure les mots de passe
            ).sort('createdAt', -1))
            
            formatted_admins = []
            for admin in admins:
                admin_data = {
                    'id': str(admin['_id']),
                    'username': admin['username'],
                    'email': admin.get('email', ''),
                    'firstName': admin.get('firstName', ''),
                    'lastName': admin.get('lastName', ''),
                    'department': admin.get('department', ''),
                    'location': admin.get('location', ''),
                    'role': admin.get('role', 'ADMIN'),
                    'active': admin.get('active', True),
                    'lastLogin': admin.get('lastLogin'),
                    'createdAt': admin.get('createdAt'),
                    'updatedAt': admin.get('updatedAt')
                }
                
                # Formater les dates
                for date_field in ['lastLogin', 'createdAt', 'updatedAt']:
                    if admin_data[date_field] and hasattr(admin_data[date_field], 'isoformat'):
                        admin_data[date_field] = admin_data[date_field].isoformat()
                
                formatted_admins.append(admin_data)

            return jsonify({
                'success': True,
                'admins': formatted_admins,
                'count': len(formatted_admins)
            }), 200

        except Exception as e:
            print(f"❌ LIST_ADMINS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur serveur'
            }), 500

    print("✅ Routes admin enregistrées avec succès")
