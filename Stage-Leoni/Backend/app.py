from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
from dotenv import load_dotenv
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import base64
from news_routes_simple import register_news_routes_simple
# Commenté temporairement pour éviter l'erreur d'import
# from news_chat_routes import register_news_routes, register_chat_routes

app = Flask(__name__)
# Configuration CORS pour développement local - Permettre toutes les origines pour le développement
CORS(app, origins="*", methods=["GET", "POST", "PUT", "OPTIONS"], allow_headers=["*"])

# Middleware pour gérer les requêtes OPTIONS et éviter les doublons headers CORS
@app.after_request
def after_request(response):
    # Supprimer ces headers car ils sont déjà gérés par CORS(app)
    return response

# Charger les variables d'environnement
load_dotenv()
MONGODB_ATLAS_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
MONGODB_LOCAL_URI = 'mongodb://localhost:27017/LeoniApp'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '123')

# Configuration email pour la réinitialisation de mot de passe
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@leoniapp.com')

# Fonction pour essayer de se connecter à MongoDB avec fallback
def connect_to_mongodb():
    # Essayer d'abord MongoDB Atlas (cloud)
    try:
        print("🔍 Tentative de connexion à MongoDB Atlas...")
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=10000)
        client.server_info()  # Test de connexion
        print("✅ Connexion MongoDB Atlas réussie")
        return client, "Atlas"
    except Exception as e:
        print(f"❌ Échec connexion MongoDB Atlas: {str(e)}")

    # Fallback : essayer MongoDB local
    try:
        print("🔍 Tentative de connexion à MongoDB local...")
        client = MongoClient(MONGODB_LOCAL_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test de connexion
        print("✅ Connexion MongoDB local réussie")
        return client, "Local"
    except Exception as e:
        print(f"❌ Échec connexion MongoDB local: {str(e)}")

    # Si aucune connexion ne fonctionne, utiliser une base de données en mémoire (fallback ultime)
    print("⚠️ Utilisation d'une base de données temporaire en mémoire")
    return None, "Memory"

# Établir la connexion MongoDB
client, db_type = connect_to_mongodb()

if client:
    # Configuration de la base de données
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'LeoniApp')
    USERS_COLLECTION = os.getenv('USERS_COLLECTION', 'users')
    DOCUMENTS_COLLECTION = os.getenv('DOCUMENTS_COLLECTION', 'document_requests')

    db = client[DATABASE_NAME]
    users_collection = db[USERS_COLLECTION]
    document_requests_collection = db[DOCUMENTS_COLLECTION]
    password_reset_collection = db['password_resets']
    
    # COLLECTION POUR LES TYPES DE DOCUMENTS
    document_types_collection = db['document_types']
    
    # NOUVELLES COLLECTIONS POUR NEWS & CHAT
    locations_collection = db['locations']
    departments_collection = db['departments']
    news_collection = db['news']
    news_interactions_collection = db['news_interactions']
    services_collection = db['services']
    chats_collection = db['chats']
    chat_messages_collection = db['chat_messages']

    # Créer les index pour optimiser les requêtes (seulement si pas en mémoire)
    try:
        users_collection.create_index([("adresse1", 1)], unique=True)
        # Index partiel pour adresse2 - unique seulement si pas null
        users_collection.create_index(
            [("adresse2", 1)], 
            unique=True, 
            partialFilterExpression={"adresse2": {"$ne": None, "$ne": ""}}
        )
        users_collection.create_index([("employeeId", 1)], unique=True)
        document_requests_collection.create_index([("userId", 1)])
        document_requests_collection.create_index([("status", 1)])
        password_reset_collection.create_index([("email", 1)])
        password_reset_collection.create_index([("token", 1)], unique=True)
        password_reset_collection.create_index([("expiresAt", 1)], expireAfterSeconds=0)
        print(f"✅ Index créés pour la base {db_type}")
    except Exception as index_error:
        print(f"⚠️ Impossible de créer les index: {index_error}")

else:
    # Mode mémoire : utiliser des dictionnaires Python comme fallback
    print("⚠️ Mode base de données temporaire activé")
    users_collection = {}
    document_requests_collection = {}
    password_reset_collection = {}
    db_type = "Memory"

# Validation de l'email
def is_valid_email(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email) is not None

# Fonction pour envoyer un email
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

# Générer un token de réinitialisation
def generate_reset_token():
    return secrets.token_urlsafe(32)

# Validation du numéro de téléphone
def is_valid_phone(phone):
    # Accepter les formats internationaux et locaux
    phone_regex = r'^\+?[\d\s\-\(\)]{8,15}$'
    return re.match(phone_regex, phone.strip()) is not None

# Validation de l'employeeId (8 chiffres)
def is_valid_employee_id(employee_id):
    if not employee_id:
        return True  # employeeId est optionnel
    employee_id_regex = r'^\d{8}$'
    return re.match(employee_id_regex, str(employee_id).strip()) is not None

# Générer un employeeId unique (nombre à 8 chiffres)
def generate_employee_id():
    try:
        # Trouver le plus grand employeeId existant
        existing_ids = users_collection.find({}, {'employeeId': 1}).sort('employeeId', -1).limit(1)
        
        max_id = 10000000  # Commencer à 10000000 (8 chiffres)
        
        for user in existing_ids:
            employee_id = user.get('employeeId', '')
            # Si c'est un nombre, le convertir
            if employee_id.isdigit() and len(employee_id) == 8:
                max_id = max(max_id, int(employee_id) + 1)
            elif employee_id.startswith('EMP'):
                # Migration des anciens IDs - ignorer ou convertir
                continue
        
        # Vérifier que l'ID n'existe pas déjà
        employee_id = str(max_id)
        while users_collection.find_one({'employeeId': employee_id}):
            max_id += 1
            employee_id = str(max_id)
        
        return employee_id
    except Exception as e:
        print(f"Erreur lors de la génération de l'employeeId: {e}")
        # Fallback: générer un ID basé sur timestamp
        import random
        timestamp_id = str(int(datetime.now().timestamp()))[-8:]
        random_suffix = str(random.randint(10, 99))
        return timestamp_id[:6] + random_suffix

# Middleware pour vérifier le token JWT
def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Route pour tester la connexion
@app.route('/health', methods=['GET'])
def health_check():
    try:
        mongodb_status = "Déconnecté"

        if client:
            try:
                client.server_info()
                mongodb_status = f"Connecté ({db_type})"
            except:
                mongodb_status = f"Erreur ({db_type})"
        else:
            mongodb_status = "Mode mémoire temporaire"

        return jsonify({
            'success': True,
            'message': 'Serveur en ligne',
            'mongodb': mongodb_status,
            'database_type': db_type,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur serveur',
            'error': str(e)
        }), 500

# Route pour l'inscription
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        print(f"🔍 DEBUG REGISTER - Données reçues: {data}", flush=True)
        
        if not data:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400
        
        # Support des anciens et nouveaux noms de champs
        # Convertir les anciens noms vers les nouveaux noms uniquement
        if 'email' in data and 'adresse1' not in data:
            data['adresse1'] = data['email']
        if 'parentalEmail' in data and 'adresse2' not in data:
            data['adresse2'] = data['parentalEmail']
        
        # Utiliser les nouveaux noms de champs comme standard
        required_fields = ['firstName', 'lastName', 'adresse1', 'adresse2', 'phoneNumber', 'parentalPhoneNumber', 'password', 'confirmPassword', 'location', 'department']
        
        print(f"🔍 DEBUG REGISTER - Champs requis: {required_fields}", flush=True)
        print(f"🔍 DEBUG REGISTER - Champs reçus: {list(data.keys())}", flush=True)
        
        # Vérifier que tous les champs requis sont présents
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        if missing_fields:
            print(f"❌ DEBUG REGISTER - Champs manquants: {missing_fields}", flush=True)
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Validation des données
        if not is_valid_email(data['adresse1']):
            return jsonify({'success': False, 'message': 'Format adresse1 invalide'}), 400
        
        if not is_valid_email(data['adresse2']):
            return jsonify({'success': False, 'message': 'Format adresse2 invalide'}), 400
        
        if data['adresse1'].lower() == data['adresse2'].lower():
            return jsonify({'success': False, 'message': 'Les adresses doivent être différentes'}), 400
        
        if not is_valid_phone(data['phoneNumber']):
            return jsonify({'success': False, 'message': 'Format numéro de téléphone personnel invalide'}), 400
        
        if not is_valid_phone(data['parentalPhoneNumber']):
            return jsonify({'success': False, 'message': 'Format numéro de téléphone parental invalide'}), 400
        
        # Validation employeeId si fourni
        if data.get('employeeId') and not is_valid_employee_id(data['employeeId']):
            return jsonify({'success': False, 'message': 'L\'ID employé doit être un nombre à 8 chiffres'}), 400
        
        if data['password'] != data['confirmPassword']:
            return jsonify({'success': False, 'message': 'Les mots de passe ne correspondent pas'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400

        # Validation des location et department
        try:
            location_name = data.get('location')
            department_name = data.get('department')
            
            # Vérifier si le département existe pour cette localisation
            department = departments_collection.find_one({
                "name": department_name,
                "location": location_name
            })
            
            if not department:
                return jsonify({'success': False, 'message': 'Département non trouvé pour cette localisation'}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'message': 'Erreur de validation des données de localisation'}), 400

        # Vérifier si l'email existe déjà
        if users_collection.find_one({'adresse1': data['adresse1'].lower()}):
            return jsonify({'success': False, 'message': 'Un compte avec cette adresse1 existe déjà'}), 400
        
        if users_collection.find_one({'adresse2': data['adresse2'].lower()}):
            return jsonify({'success': False, 'message': 'Un compte avec cette adresse2 existe déjà'}), 400

        # Hacher le mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # Générer un employeeId unique
        employee_id = generate_employee_id()

        # Créer l'utilisateur
        user = {
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'adresse1': data['adresse1'].lower().strip(),
            'adresse2': data['adresse2'].lower().strip(),
            'phoneNumber': data['phoneNumber'].strip(),
            'parentalPhoneNumber': data['parentalPhoneNumber'].strip(),
            'password': hashed_password,
            'employeeId': employee_id,
            'department': data['department'],  # Nom du département
            'position': 'Non spécifié',
            'location': data['location'],  # Nom de la location
            'profilePicture': None,  # Ajout du champ photo de profil
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        # Insérer l'utilisateur dans la base de données
        result = users_collection.insert_one(user)
        
        # Vérifier que l'insertion a réussi
        if not result.inserted_id:
            return jsonify({'success': False, 'message': 'Erreur lors de la création du compte'}), 500

        # Générer un token JWT
        token = jwt.encode({
            '_id': str(result.inserted_id),
            'user_id': str(result.inserted_id),  # Standardisé
            'userId': str(result.inserted_id),  # Keep for backwards compatibility
            'adresse1': user['adresse1'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET_KEY, algorithm='HS256')

        print(f"✅ Nouvel utilisateur créé: {user['adresse1']} (ID: {employee_id})")

        return jsonify({
            'success': True,
            'message': 'Inscription réussie',
            'user': {
                'id': str(result.inserted_id),
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'adresse1': user['adresse1'],
                'adresse2': user['adresse2'],
                'phoneNumber': user['phoneNumber'],
                'parentalPhoneNumber': user['parentalPhoneNumber'],
                'employeeId': user['employeeId'],
                'department': user['department'],
                'location': user['location']
            },
            'token': token
        }), 201

    except Exception as e:
        print(f"❌ Erreur lors de l'inscription: {e}")
        return jsonify({
            'success': False, 
            'message': 'Erreur serveur lors de l\'inscription',
            'error': str(e)
        }), 500

# Route pour la connexion
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        return response

    print("🔍 LOGIN: Requête reçue", flush=True)

    try:
        data = request.get_json()
        print(f"🔍 LOGIN: Données = {data}", flush=True)

        if not data:
            print("❌ LOGIN: Pas de données JSON", flush=True)
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        if 'adresse1' not in data or 'password' not in data:
            print("❌ LOGIN: Adresse1 ou password manquant", flush=True)
            return jsonify({'success': False, 'message': 'Adresse1 et mot de passe requis'}), 400

        adresse1 = data['adresse1'].lower().strip()
        password = data['password']

        print(f"🔍 LOGIN: Recherche user {adresse1}", flush=True)
        user = users_collection.find_one({'adresse1': adresse1})

        if not user:
            print("❌ LOGIN: User non trouvé", flush=True)
            return jsonify({'success': False, 'message': 'Adresse1 ou mot de passe incorrect'}), 401

        print("🔍 LOGIN: User trouvé, vérif password", flush=True)
        
        # S'assurer que le password stocké est en bytes
        stored_password = user['password']
        if isinstance(stored_password, str):
            # Si c'est une string, la convertir en bytes
            stored_password = stored_password.encode('utf-8')
        
        print(f"🔍 LOGIN: Type password stocké = {type(stored_password)}", flush=True)

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            print("❌ LOGIN: Password incorrect", flush=True)
            return jsonify({'success': False, 'message': 'Adresse1 ou mot de passe incorrect'}), 401

        print("🔍 LOGIN: Password OK, génération token", flush=True)

        # Token JWT simple
        token = jwt.encode({
            '_id': str(user['_id']),
            'user_id': str(user['_id']),  # Standardisé pour tous les endpoints
            'adresse1': user['adresse1'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET_KEY, algorithm='HS256')

        print("✅ LOGIN: Succès", flush=True)

        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': str(user['_id']),
                'firstName': user.get('firstName', ''),
                'lastName': user.get('lastName', ''),
                'adresse1': user['adresse1'],
                'employeeId': user.get('employeeId', ''),
                'location': user.get('location', 'Non spécifié'),
                'department': user.get('department', 'Non spécifié')
            },
            'token': token
        })

    except Exception as e:
        print(f"❌ LOGIN: Exception = {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

# Route pour soumettre une demande de document
@app.route('/document-request', methods=['POST', 'OPTIONS'])
def submit_document_request():
    # Gérer les requêtes OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        return response, 200
    
    print("🔍 SUBMIT_DOC: Début de la fonction", flush=True)
    try:
        data = request.get_json()
        print(f"🔍 SUBMIT_DOC: Données reçues = {data}", flush=True)
        
        if not data:
            print("❌ SUBMIT_DOC: Aucune donnée reçue", flush=True)
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        # Vérifier le token d'authentification
        auth_header = request.headers.get('Authorization')
        print(f"🔍 SUBMIT_DOC: Auth header = {auth_header[:20] if auth_header else 'None'}...", flush=True)
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print("❌ SUBMIT_DOC: Token manquant", flush=True)
            return jsonify({'success': False, 'message': 'Token manquant'}), 401

        token = auth_header.split(' ')[1]
        decoded_token = verify_token(token)
        print(f"🔍 SUBMIT_DOC: Token décodé = {decoded_token}", flush=True)
        
        if not decoded_token:
            print("❌ SUBMIT_DOC: Token invalide", flush=True)
            return jsonify({'success': False, 'message': 'Token invalide'}), 401

        user_id = decoded_token['user_id']
        print(f"🔍 SUBMIT_DOC: User ID extrait = {user_id}", flush=True)

        # Vérifier les champs requis
        required_fields = ['documentType']
        missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
        print(f"🔍 SUBMIT_DOC: Champs requis vérifiés, manquants = {missing_fields}", flush=True)
        
        if missing_fields:
            print(f"❌ SUBMIT_DOC: Champs manquants détectés = {missing_fields}", flush=True)
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Vérifier que l'utilisateur existe
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        request_data = {
            'userId': user_id,
            'documentType': data['documentType'].strip(),
            'description': data.get('description', '').strip() if data.get('description') else '',
            'status': {
                'current': 'en attente',
                'progress': [
                    {'step': 'en attente', 'date': None, 'completed': False},
                    {'step': 'en cours', 'date': None, 'completed': False}, 
                    {'step': 'accepté', 'date': None, 'completed': False},
                    {'step': 'refusé', 'date': None, 'completed': False}
                ]
            },
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        result = document_requests_collection.insert_one(request_data)

        print(f"✅ Nouvelle demande de document: {data['documentType']} par {user_id}")

        return jsonify({
            'success': True,
            'message': 'Demande enregistrée'
        }), 201

    except Exception as e:
        print(f"❌ Erreur lors de la soumission de demande: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la soumission',
            'error': str(e)
        }), 500

# Route pour récupérer les demandes de documents
@app.route('/document-requests', methods=['GET', 'OPTIONS'])
def get_document_requests():
    # Gérer les requêtes OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        return response, 200
    
    print("🔍 GET_DOCUMENTS: Requête reçue", flush=True)
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("❌ GET_DOCUMENTS: Token manquant", flush=True)
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(" ")[1]
        decoded = verify_token(token)
        if not decoded:
            print("❌ GET_DOCUMENTS: Token invalide", flush=True)
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        print(f"🔍 GET_DOCUMENTS: Token décodé = {decoded}", flush=True)

        # Migration des anciens documents avec status en string vers le nouveau format
        # Seulement si il y a des documents à migrer
        docs_to_migrate = document_requests_collection.count_documents({'status': {'$type': 'string'}})
        if docs_to_migrate > 0:
            print(f"🔄 Migration de {docs_to_migrate} documents avec statuts en string...", flush=True)
            document_requests_collection.update_many(
                {'status': {'$type': 'string'}},
                [{'$set': {
                    'status': {
                        'current': '$status',
                        'progress': {
                            '$switch': {
                                'branches': [
                                    {
                                        'case': {'$eq': ['$status', 'en attente']},
                                        'then': [
                                            {'step': 'en attente', 'date': None, 'completed': True},
                                            {'step': 'en cours', 'date': None, 'completed': False},
                                            {'step': 'accepté', 'date': None, 'completed': False},
                                            {'step': 'refusé', 'date': None, 'completed': False}
                                        ]
                                    },
                                    {
                                        'case': {'$eq': ['$status', 'en cours']}, 
                                        'then': [
                                            {'step': 'en attente', 'date': None, 'completed': True},
                                            {'step': 'en cours', 'date': None, 'completed': True},
                                            {'step': 'accepté', 'date': None, 'completed': False},
                                            {'step': 'refusé', 'date': None, 'completed': False}
                                        ]
                                    },
                                    {
                                        'case': {'$eq': ['$status', 'accepté']},
                                        'then': [
                                            {'step': 'en attente', 'date': None, 'completed': True},
                                            {'step': 'en cours', 'date': None, 'completed': True},
                                            {'step': 'accepté', 'date': None, 'completed': True},
                                            {'step': 'refusé', 'date': None, 'completed': False}
                                        ]
                                    },
                                    {
                                        'case': {'$eq': ['$status', 'refusé']},
                                        'then': [
                                            {'step': 'en attente', 'date': None, 'completed': True},
                                            {'step': 'en cours', 'date': None, 'completed': False},
                                            {'step': 'accepté', 'date': None, 'completed': False},
                                            {'step': 'refusé', 'date': None, 'completed': True}
                                        ]
                                    }
                                ],
                                # AJOUT DE LA BRANCHE DEFAULT POUR ÉVITER L'ERREUR
                                'default': [
                                    {'step': 'en attente', 'date': None, 'completed': True},
                                    {'step': 'en cours', 'date': None, 'completed': False},
                                    {'step': 'accepté', 'date': None, 'completed': False},
                                    {'step': 'refusé', 'date': None, 'completed': False}
                                ]
                            }
                        }
                    }
                }}]
            )
            print(f"✅ Migration terminée pour {docs_to_migrate} documents", flush=True)
        
        # Utiliser user_id du token décodé pour chercher les documents (cohérent avec la création)
        user_id = decoded.get('user_id')
        if not user_id:
            print("❌ GET_DOCUMENTS: user_id manquant dans le token", flush=True)
            return jsonify({'success': False, 'message': 'Token invalide - user_id manquant'}), 401
            
        print(f"🔍 GET_DOCUMENTS: Recherche documents pour user_id = {user_id}", flush=True)

        requests = list(document_requests_collection.find({'userId': user_id}))
        print(f"🔍 GET_DOCUMENTS: Trouvé {len(requests)} documents", flush=True)

        for req in requests:
            req['_id'] = str(req['_id'])
            req['userId'] = str(req['userId'])
            if req.get('createdAt'):
                req['createdAt'] = req['createdAt'].isoformat()
            if req.get('updatedAt'):
                req['updatedAt'] = req['updatedAt'].isoformat()

        print("✅ GET_DOCUMENTS: Succès", flush=True)
        return jsonify({
            'success': True,
            'documents': requests,  # Renommé pour cohérence avec le service
            'requests': requests   # Gardé pour rétrocompatibilité
        }), 200

    except Exception as e:
        print(f"❌ GET_DOCUMENTS: Exception = {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération',
            'error': str(e)
        }), 500

# Route pour récupérer les types de documents disponibles
@app.route('/document-types', methods=['GET', 'OPTIONS'])
def get_document_types():
    # Gérer les requêtes OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_DOCUMENT_TYPES: Requête reçue", flush=True)
    try:
        # Optionnel: vérifier l'authentification
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
            decoded = verify_token(token)
            if not decoded:
                print("⚠️ GET_DOCUMENT_TYPES: Token invalide, mais continuons sans auth", flush=True)
        
        # Récupérer seulement les types de documents actifs
        document_types = list(document_types_collection.find(
            {'active': True},
            {'_class': 0}  # Exclure le champ _class qui n'est pas nécessaire
        ).sort('name', 1))  # Trier par nom alphabétiquement
        
        print(f"🔍 GET_DOCUMENT_TYPES: Trouvé {len(document_types)} types actifs", flush=True)
        
        # Convertir les ObjectId en string et formater les dates
        for doc_type in document_types:
            doc_type['_id'] = str(doc_type['_id'])
            if doc_type.get('createdAt'):
                doc_type['createdAt'] = doc_type['createdAt'].isoformat()
            if doc_type.get('updatedAt'):
                doc_type['updatedAt'] = doc_type['updatedAt'].isoformat()
        
        print("✅ GET_DOCUMENT_TYPES: Succès", flush=True)
        return jsonify({
            'success': True,
            'documentTypes': document_types,
            'count': len(document_types)
        }), 200
        
    except Exception as e:
        print(f"❌ GET_DOCUMENT_TYPES: Exception = {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération des types de documents',
            'error': str(e)
        }), 500

# Route pour lister tous les utilisateurs (pour debug)
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find({}, {'password': 0}))  # Exclure les mots de passe
        for user in users:
            user['_id'] = str(user['_id'])
            if user.get('createdAt'):
                user['createdAt'] = user['createdAt'].isoformat()
            if user.get('updatedAt'):
                user['updatedAt'] = user['updatedAt'].isoformat()
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des utilisateurs',
            'error': str(e)
        }), 500

# Route pour récupérer les informations du profil utilisateur connecté
@app.route('/me', methods=['GET', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    print("🔍 GET_ME: Requête reçue", flush=True)
    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("❌ GET_ME: Token manquant", flush=True)
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            print("❌ GET_ME: Token invalide", flush=True)
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        print(f"🔍 GET_ME: Token décodé = {payload}", flush=True)

        # Utiliser user_id du payload
        user_id = payload.get('user_id') or payload.get('_id')
        print(f"🔍 GET_ME: Recherche user avec ID = {user_id}", flush=True)

        # Récupérer l'utilisateur depuis la base de données
        user = users_collection.find_one({
            '_id': ObjectId(user_id)
        }, {'password': 0})  # Exclure le mot de passe

        if not user:
            print("❌ GET_ME: Utilisateur non trouvé", flush=True)
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Utiliser directement les champs department et location s'ils existent
        user_data = {
            '_id': str(user['_id']),
            'id': str(user['_id']),
            'firstName': user.get('firstName', ''),
            'lastName': user.get('lastName', ''),
            'adresse1': user.get('adresse1', ''),
            'phoneNumber': user.get('phoneNumber', ''),
            'adresse2': user.get('adresse2', ''),
            'parentalPhoneNumber': user.get('parentalPhoneNumber', ''),
            'employeeId': user.get('employeeId', ''),
            'department': user.get('department', 'Non spécifié'),
            'location': user.get('location', 'Non spécifié'),
            'position': user.get('position', 'Non spécifié'),
            'profilePicture': user.get('profilePicture'),
            'role': user.get('role', 'EMPLOYEE'),  # Nouveau champ pour les rôles
            'createdAt': user.get('createdAt'),
            'updatedAt': user.get('updatedAt')
        }
        
        print(f"✅ GET_ME: Département final = {user_data['department']}")
        print(f"✅ GET_ME: Location finale = {user_data['location']}")

        print(f"✅ GET_ME: Succès - Location: {user_data['location']}, Département: {user_data['department']}", flush=True)
        return jsonify({
            'success': True,
            'user': user_data
        })

    except jwt.ExpiredSignatureError:
        print("❌ GET_ME: Token expiré", flush=True)
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"❌ GET_ME: Exception = {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour récupérer les informations du profil utilisateur par ID
@app.route('/users/<user_id>', methods=['GET', 'OPTIONS'])
def get_user_by_id(user_id):
    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401
        
        # Récupérer l'utilisateur depuis la base de données
        user = users_collection.find_one({
            '_id': ObjectId(user_id)
        }, {'password': 0})  # Exclure le mot de passe
        
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
        # Convertir l'ObjectId en string pour le JSON
        user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"Erreur get_profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour mettre à jour le profil utilisateur
@app.route('/update-profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    print("🔍 UPDATE_PROFILE: Requête reçue", flush=True)
    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("❌ UPDATE_PROFILE: Token manquant", flush=True)
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            print("❌ UPDATE_PROFILE: Token invalide", flush=True)
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        data = request.get_json()
        print(f"🔍 UPDATE_PROFILE: Données reçues = {data}", flush=True)

        # Validation des données - seulement les champs essentiels
        required_fields = ['firstName', 'lastName', 'adresse1']
        for field in required_fields:
            if not data.get(field) or not data.get(field).strip():
                print(f"❌ UPDATE_PROFILE: Champ manquant = {field}", flush=True)
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400
        
        # Validation de l'adresse1
        if not is_valid_email(data['adresse1']):
            print(f"❌ UPDATE_PROFILE: Adresse1 invalide = {data['adresse1']}", flush=True)
            return jsonify({'success': False, 'message': 'Format d\'adresse1 invalide'}), 400

        # Utiliser _id du payload
        user_id = payload.get('userId') or payload.get('_id')
        print(f"🔍 UPDATE_PROFILE: User ID = {user_id}", flush=True)

        # Vérifier si l'adresse1 existe déjà pour un autre utilisateur
        existing_user = users_collection.find_one({
            'adresse1': data['adresse1'],
            '_id': {'$ne': ObjectId(user_id)}
        })

        if existing_user:
            print(f"❌ UPDATE_PROFILE: Adresse1 déjà utilisée = {data['adresse1']}", flush=True)
            return jsonify({'success': False, 'message': 'Cette adresse1 est déjà utilisée'}), 400

        # Validation du numéro de téléphone (optionnel)
        if data.get('phoneNumber') and not is_valid_phone(data['phoneNumber']):
            print(f"❌ UPDATE_PROFILE: Téléphone invalide = {data['phoneNumber']}", flush=True)
            return jsonify({'success': False, 'message': 'Format de numéro de téléphone invalide'}), 400
        
        # Validation de l'employeeId (optionnel)
        if data.get('employeeId') and not is_valid_employee_id(data['employeeId']):
            print(f"❌ UPDATE_PROFILE: EmployeeId invalide = {data['employeeId']}", flush=True)
            return jsonify({'success': False, 'message': 'L\'ID employé doit être un nombre à 8 chiffres'}), 400
        
        # Mise à jour des informations de l'utilisateur
        update_data = {
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'adresse1': data['adresse1'].strip().lower(),
            'updatedAt': datetime.utcnow()
        }

        # Ajouter le téléphone s'il est fourni
        if data.get('phoneNumber') and data['phoneNumber'].strip():
            update_data['phoneNumber'] = data['phoneNumber'].strip()

        # Ajouter les champs optionnels s'ils sont présents
        if data.get('address') and data['address'].strip():
            update_data['address'] = data['address'].strip()
        if data.get('department') and data['department'].strip():
            update_data['department'] = data['department'].strip()
        if data.get('position') and data['position'].strip():
            update_data['position'] = data['position'].strip()
        if data.get('employeeId') and data['employeeId'].strip():
            update_data['employeeId'] = data['employeeId'].strip()

        print(f"🔍 UPDATE_PROFILE: Données à mettre à jour = {update_data}", flush=True)
        
        # Ajouter les champs parentaux s'ils sont présents
        if data.get('adresse2'):
            if data['adresse2'].strip() and not is_valid_email(data['adresse2'].strip()):
                print(f"❌ UPDATE_PROFILE: Adresse2 invalide = {data['adresse2']}", flush=True)
                return jsonify({'success': False, 'message': 'Format d\'adresse2 invalide'}), 400
            update_data['adresse2'] = data['adresse2'].strip()

        if data.get('parentalPhoneNumber'):
            if data['parentalPhoneNumber'].strip() and not is_valid_phone(data['parentalPhoneNumber'].strip()):
                print(f"❌ UPDATE_PROFILE: Téléphone parental invalide = {data['parentalPhoneNumber']}", flush=True)
                return jsonify({'success': False, 'message': 'Format de numéro de téléphone parental invalide'}), 400
            update_data['parentalPhoneNumber'] = data['parentalPhoneNumber'].strip()

        # Gérer la photo de profil si elle est présente
        if 'profilePicture' in data and data['profilePicture']:
            # Vérifier que c'est une image base64 valide
            if not data['profilePicture'].startswith('data:image/'):
                return jsonify({'success': False, 'message': 'Format d\'image invalide'}), 400
            update_data['profilePicture'] = data['profilePicture']
            print(f"✅ Photo de profil mise à jour pour: {payload.get('email', 'utilisateur')}")

        # Mettre à jour l'utilisateur dans la base de données
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            print(f"❌ UPDATE_PROFILE: Utilisateur non trouvé = {user_id}", flush=True)
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        print(f"✅ UPDATE_PROFILE: Mise à jour réussie pour {user_id}", flush=True)

        # Récupérer les données mises à jour
        updated_user = users_collection.find_one(
            {'_id': ObjectId(user_id)},
            {'password': 0}  # Exclure le mot de passe
        )

        if updated_user:
            updated_user['_id'] = str(updated_user['_id'])
            updated_user['id'] = str(updated_user['_id'])  # Ajouter aussi 'id' pour compatibilité

        print("✅ UPDATE_PROFILE: Succès complet", flush=True)
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'user': updated_user
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except Exception as e:
        print(f"Erreur update_profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour mettre à jour le statut d'un document
@app.route('/update-document-status', methods=['PUT'])
def update_document_status():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(" ")[1]
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        data = request.get_json()
        if not data or not all(field in data for field in ['documentId', 'newStatus']):
            return jsonify({'success': False, 'message': 'ID document et nouveau statut requis'}), 400

        # Vérifier que le nouveau statut est valide
        valid_status = ['en attente', 'en cours', 'accepté', 'refusé']
        if data['newStatus'] not in valid_status:
            return jsonify({'success': False, 'message': 'Statut invalide'}), 400

        # Mettre à jour le statut et marquer l'étape comme complétée
        result = document_requests_collection.update_one(
            {'_id': ObjectId(data['documentId'])},
            {'$set': {
                'status.current': data['newStatus'],
                'status.progress.$[elem].completed': True,
                'status.progress.$[elem].date': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }},
            array_filters=[{'elem.step': data['newStatus']}]
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Document non trouvé'}), 404
            
        return jsonify({
            'success': True,
            'message': 'Statut mis à jour avec succès'
        }), 200

    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du statut: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la mise à jour',
            'error': str(e)
        }), 500

# Route pour uploader la photo de profil
@app.route('/upload-profile-picture', methods=['POST', 'OPTIONS'])
def upload_profile_picture():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        # Vérifier le token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant ou invalide'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)

        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 401

        data = request.get_json()

        if not data or not data.get('imageData'):
            return jsonify({'success': False, 'message': 'Image manquante'}), 400

        image_data = data['imageData']

        # Vérifier que c'est une image base64 valide
        if not image_data.startswith('data:image/'):
            return jsonify({'success': False, 'message': 'Format d\'image invalide'}), 400

        # Utiliser _id du payload
        user_id = payload.get('userId') or payload.get('_id')

        # Mettre à jour la photo de profil dans la base de données
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'profilePicture': image_data,
                'updatedAt': datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        print(f"✅ Photo de profil mise à jour pour: {payload.get('email', 'utilisateur')}")

        return jsonify({
            'success': True,
            'message': 'Photo de profil mise à jour avec succès'
        }), 200

    except Exception as e:
        print(f"❌ Erreur upload photo profil: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

# Route pour demander la réinitialisation de mot de passe
@app.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        data = request.get_json()

        if not data or not data.get('email'):
            return jsonify({'success': False, 'message': 'Email requis'}), 400

        email = data['email'].lower().strip()

        if not is_valid_email(email):
            return jsonify({'success': False, 'message': 'Email invalide'}), 400

        # Vérifier si l'utilisateur existe
        user = users_collection.find_one({'adresse1': email})
        if not user:
            # Pour des raisons de sécurité, on ne révèle pas si l'email existe ou non
            return jsonify({
                'success': True,
                'message': 'Si cet email existe, vous recevrez un lien de réinitialisation'
            }), 200

        # Générer un token de réinitialisation
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Expire dans 1 heure

        # Sauvegarder le token dans la base de données
        password_reset_collection.delete_many({'email': email})  # Supprimer les anciens tokens
        password_reset_collection.insert_one({
            'email': email,
            'token': reset_token,
            'expiresAt': expires_at,
            'createdAt': datetime.utcnow()
        })

        # Créer le lien de réinitialisation
        reset_link = f"http://localhost:8085/reset-password?token={reset_token}"

        # Créer le contenu de l'email
        email_subject = "Réinitialisation de votre mot de passe - Leoni App"
        email_body = f"""
        <html>
        <body>
            <h2>Réinitialisation de mot de passe</h2>
            <p>Bonjour {user.get('firstName', '')},</p>
            <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Leoni App.</p>
            <p>Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :</p>
            <p><a href="{reset_link}" style="background-color: #002857; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Réinitialiser mon mot de passe</a></p>
            <p>Ce lien expire dans 1 heure.</p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
            <br>
            <p>Cordialement,<br>L'équipe Leoni App</p>
        </body>
        </html>
        """

        # Envoyer l'email
        if send_email(email, email_subject, email_body):
            print(f"✅ Email de réinitialisation envoyé à: {email}")
        else:
            print(f"❌ Échec envoi email à: {email}")

        return jsonify({
            'success': True,
            'message': 'Si cet email existe, vous recevrez un lien de réinitialisation'
        }), 200

    except Exception as e:
        print(f"❌ Erreur forgot password: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

# Route pour réinitialiser le mot de passe
@app.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        data = request.get_json()

        if not data or not data.get('token') or not data.get('newPassword'):
            return jsonify({'success': False, 'message': 'Token et nouveau mot de passe requis'}), 400

        token = data['token']
        new_password = data['newPassword']

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400

        # Vérifier le token
        reset_request = password_reset_collection.find_one({
            'token': token,
            'expiresAt': {'$gt': datetime.utcnow()}
        })

        if not reset_request:
            return jsonify({'success': False, 'message': 'Token invalide ou expiré'}), 400

        # Mettre à jour le mot de passe
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        result = users_collection.update_one(
            {'email': reset_request['email']},
            {'$set': {
                'password': hashed_password,
                'updatedAt': datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Supprimer le token utilisé
        password_reset_collection.delete_one({'token': token})

        print(f"✅ Mot de passe réinitialisé pour: {reset_request['email']}")

        return jsonify({
            'success': True,
            'message': 'Mot de passe réinitialisé avec succès'
        }), 200

    except Exception as e:
        print(f"❌ Erreur reset password: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur'
        }), 500

# ==============================================
# ROUTES POUR LA GESTION FILTREE PAR DEPARTEMENT ET LOCATION
# ==============================================

# Enregistrement des routes avec les modules externes
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Déterminer les cibles selon le rôle de l'admin
        admin_role = data['adminRole']
        admin_department = data['adminDepartment']
        admin_location = data['adminLocation']
        
        target_departments = []
        target_locations = []
        
        if admin_role == 'SUPERADMIN':
            # SuperAdmin peut cibler spécifiquement ou globalement
            if data.get('targetDepartments'):
                target_departments = data['targetDepartments']
            if data.get('targetLocations'):
                target_locations = data['targetLocations']
            # Si pas de cibles spécifiques, diffusion globale
            if not target_departments and not target_locations:
                target_departments = ['ALL']
                target_locations = ['ALL']
        else:
            # Admin normal : seulement son département et sa location
            target_departments = [admin_department]
            target_locations = [admin_location]

        # Créer l'actualité
        news_data = {
            'title': data['title'].strip(),
            'content': data['content'].strip(),
            'authorId': payload.get('user_id'),
            'authorRole': admin_role,
            'authorDepartment': admin_department,
            'authorLocation': admin_location,
            'targetDepartments': target_departments,
            'targetLocations': target_locations,
            'priority': data.get('priority', 'normal'),  # normal, high, urgent
            'status': 'published',
            'tags': data.get('tags', []),
            'attachments': data.get('attachments', []),
            'visibility': data.get('visibility', 'department_location'), # global, department, location, department_location
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'publishedAt': datetime.utcnow()
        }

        result = news_collection.insert_one(news_data)
        
        if result.inserted_id:
            print(f"✅ Actualité créée par {admin_role} pour dept: {target_departments}, loc: {target_locations}")
            return jsonify({
                'success': True,
                'message': 'Actualité publiée avec succès',
                'newsId': str(result.inserted_id),
                'targets': {
                    'departments': target_departments,
                    'locations': target_locations
                }
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Erreur lors de la création'}), 500
            
    except Exception as e:
        print(f"❌ CREATE_ADMIN_NEWS: Exception = {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la création de l\'actualité',
            'error': str(e)
        }), 500

# Route pour récupérer les actualités filtrées pour un utilisateur
@app.route('/api/news/user', methods=['GET', 'OPTIONS'])
def get_user_news():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_USER_NEWS: Requête reçue", flush=True)
    try:
        # Vérifier le token utilisateur
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token requis'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401

        # Récupérer les infos utilisateur
        user_id = payload.get('user_id')
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        user_department = user.get('department', '')
        user_location = user.get('location', '')
        
        print(f"🔍 GET_USER_NEWS: User dept: {user_department}, location: {user_location}", flush=True)
        
        # Construire le filtre pour les actualités
        # L'utilisateur voit les actualités :
        # 1. Globales (ALL)
        # 2. Ciblant son département
        # 3. Ciblant sa location
        # 4. Ciblant sa combinaison département+location
        filter_query = {
            'status': 'published',
            '$or': [
                {'targetDepartments': 'ALL'},
                {'targetLocations': 'ALL'},
                {'targetDepartments': user_department},
                {'targetLocations': user_location},
                {
                    '$and': [
                        {'targetDepartments': user_department},
                        {'targetLocations': user_location}
                    ]
                }
            ]
        }
        
        # Récupérer les actualités triées par date
        news_list = list(news_collection.find(
            filter_query
        ).sort('publishedAt', -1).limit(50))
        
        print(f"🔍 GET_USER_NEWS: Trouvé {len(news_list)} actualités", flush=True)
        
        # Formater les données
        formatted_news = []
        for news_item in news_list:
            formatted_item = {
                'id': str(news_item['_id']),
                'title': news_item.get('title', ''),
                'content': news_item.get('content', ''),
                'priority': news_item.get('priority', 'normal'),
                'tags': news_item.get('tags', []),
                'attachments': news_item.get('attachments', []),
                'authorRole': news_item.get('authorRole', 'ADMIN'),
                'authorDepartment': news_item.get('authorDepartment', ''),
                'authorLocation': news_item.get('authorLocation', ''),
                'targetDepartments': news_item.get('targetDepartments', []),
                'targetLocations': news_item.get('targetLocations', []),
                'createdAt': news_item.get('createdAt', ''),
                'publishedAt': news_item.get('publishedAt', ''),
                'updatedAt': news_item.get('updatedAt', '')
            }
            
            # Formater les dates
            for date_field in ['createdAt', 'publishedAt', 'updatedAt']:
                if formatted_item[date_field] and hasattr(formatted_item[date_field], 'isoformat'):
                    formatted_item[date_field] = formatted_item[date_field].isoformat()
            
            formatted_news.append(formatted_item)
        
        return jsonify({
            'success': True,
            'news': formatted_news,
            'count': len(formatted_news),
            'userInfo': {
                'department': user_department,
                'location': user_location
            }
        }), 200
        
    except Exception as e:
        print(f"❌ GET_USER_NEWS: Exception = {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération des actualités',
            'error': str(e)
        }), 500

# Route pour les demandes de documents filtrées par département et location (pour admin)
@app.route('/api/admin/documents/filtered', methods=['GET', 'OPTIONS'])
def get_filtered_document_requests():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_FILTERED_DOCUMENTS: Requête reçue", flush=True)
    try:
        # Vérifier le token admin
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token admin requis'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token admin invalide'}), 401

        # Récupérer les paramètres de filtre
        admin_department = request.args.get('department')
        admin_location = request.args.get('location') 
        admin_role = request.args.get('role', 'ADMIN')
        status_filter = request.args.get('status')  # en attente, en cours, accepté, refusé
        
        print(f"🔍 GET_FILTERED_DOCUMENTS: Filters - Dept: {admin_department}, Loc: {admin_location}, Role: {admin_role}", flush=True)
        
        # Construire le filtre pour trouver les utilisateurs concernés
        user_filter = {}
        if admin_role == 'ADMIN':
            # Admin normal : voir seulement les demandes de son département et sa location
            if admin_department:
                user_filter['department'] = admin_department
            if admin_location:
                user_filter['location'] = admin_location
        # SUPERADMIN : peut voir toutes les demandes
        
        # Récupérer les IDs des utilisateurs concernés
        if user_filter:
            concerned_users = list(users_collection.find(user_filter, {'_id': 1}))
            user_ids = [str(user['_id']) for user in concerned_users]
            print(f"🔍 GET_FILTERED_DOCUMENTS: Found {len(user_ids)} users in scope", flush=True)
        else:
            user_ids = None  # SuperAdmin voit tous les documents
        
        # Construire le filtre pour les demandes de documents
        doc_filter = {}
        if user_ids is not None:
            doc_filter['userId'] = {'$in': user_ids}
        if status_filter:
            doc_filter['status.current'] = status_filter
            
        # Récupérer les demandes de documents
        document_requests = list(document_requests_collection.find(
            doc_filter
        ).sort('createdAt', -1))
        
        print(f"🔍 GET_FILTERED_DOCUMENTS: Found {len(document_requests)} document requests", flush=True)
        
        # Enrichir avec les informations utilisateur
        formatted_requests = []
        for doc_req in document_requests:
            # Récupérer les infos utilisateur
            user = users_collection.find_one(
                {'_id': ObjectId(doc_req['userId'])},
                {'password': 0}
            )
            
            if user:
                formatted_req = {
                    'id': str(doc_req['_id']),
                    'userId': str(doc_req['userId']),
                    'documentType': doc_req.get('documentType', ''),
                    'description': doc_req.get('description', ''),
                    'status': doc_req.get('status', {}),
                    'createdAt': doc_req.get('createdAt', ''),
                    'updatedAt': doc_req.get('updatedAt', ''),
                    'user': {
                        'id': str(user['_id']),
                        'firstName': user.get('firstName', ''),
                        'lastName': user.get('lastName', ''),
                        'fullName': f"{user.get('firstName', '')} {user.get('lastName', '')}",
                        'adresse1': user.get('adresse1', ''),
                        'employeeId': user.get('employeeId', ''),
                        'department': user.get('department', ''),
                        'location': user.get('location', ''),
                        'position': user.get('position', '')
                    }
                }
                
                # Formater les dates
                for date_field in ['createdAt', 'updatedAt']:
                    if formatted_req[date_field] and hasattr(formatted_req[date_field], 'isoformat'):
                        formatted_req[date_field] = formatted_req[date_field].isoformat()
                
                formatted_requests.append(formatted_req)
        
        return jsonify({
            'success': True,
            'documentRequests': formatted_requests,
            'count': len(formatted_requests),
            'filters': {
                'department': admin_department,
                'location': admin_location,
                'status': status_filter,
                'role': admin_role
            }
        }), 200
        
    except Exception as e:
        print(f"❌ GET_FILTERED_DOCUMENTS: Exception = {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération des demandes',
            'error': str(e)
        }), 500

# ==============================================
# NOUVELLES ROUTES POUR NEWS & CHAT
# ==============================================

# Enregistrer les routes des modules News et Chat
try:
    # Import dynamique pour éviter les erreurs
    register_news_routes_simple(app, db)
    from news_chat_routes_fixed import register_chat_routes
    register_chat_routes(app, db)
    from admin_routes import register_admin_routes
    register_admin_routes(app, db)
    print("✅ Routes News simplifiées, Chat et Admin enregistrées avec succès")
except Exception as e:
    print(f"⚠️ Erreur enregistrement routes News/Chat/Admin: {e}")
    print("🔄 Serveur démarre sans certaines routes")

@app.route('/api/test/collections', methods=['GET'])
def test_collections():
    """Route de test pour vérifier que les nouvelles collections sont accessibles"""
    try:
        result = {
            'collections': {
                'locations': locations_collection.count_documents({}),
                'departments': departments_collection.count_documents({}),
                'news': news_collection.count_documents({}),
                'services': services_collection.count_documents({}),
                'chats': chats_collection.count_documents({}),
                'chat_messages': chat_messages_collection.count_documents({})
            },
            'message': 'Extension réussie - Nouvelles collections accessibles'
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur test_collections: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ==============================================
# Route simple pour tester les locations et départements
@app.route('/api/test-data', methods=['GET', 'OPTIONS'])
def test_data():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🧪 TEST_DATA: Vérification des données de test", flush=True)
    try:
        # Compter les documents
        locations_count = locations_collection.count_documents({})
        departments_count = departments_collection.count_documents({})
        users_count = users_collection.count_documents({})
        
        print(f"🧪 TEST_DATA: {locations_count} locations, {departments_count} départements, {users_count} users", flush=True)
        
        # Récupérer quelques exemples
        locations = list(locations_collection.find({}).limit(3))
        departments = list(departments_collection.find({}).limit(6))
        
        # Convertir ObjectId en string
        for loc in locations:
            loc['_id'] = str(loc['_id'])
            if loc.get('createdAt'):
                loc['createdAt'] = loc['createdAt'].isoformat()
            if loc.get('updatedAt'):
                loc['updatedAt'] = loc['updatedAt'].isoformat()
                
        for dept in departments:
            dept['_id'] = str(dept['_id'])
            if dept.get('locationRef'):
                dept['locationRef'] = str(dept['locationRef'])
            if dept.get('createdAt'):
                dept['createdAt'] = dept['createdAt'].isoformat()
            if dept.get('updatedAt'):
                dept['updatedAt'] = dept['updatedAt'].isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Données de test récupérées',
            'counts': {
                'locations': locations_count,
                'departments': departments_count,
                'users': users_count
            },
            'sample_locations': locations,
            'sample_departments': departments
        })
        
    except Exception as e:
        print(f"❌ TEST_DATA: Erreur = {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500

# ROUTES POUR LOCATIONS ET DEPARTMENTS
# ==============================================

# Route pour récupérer toutes les locations (sites)
@app.route('/api/locations', methods=['GET', 'OPTIONS'])
def get_locations():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_LOCATIONS: Requête reçue", flush=True)
    try:
        # Récupérer toutes les locations actives
        locations = list(locations_collection.find(
            {'isActive': True},
            {'adminUsers': 0}  # Exclure les champs non nécessaires
        ).sort('name', 1))
        
        print(f"🔍 GET_LOCATIONS: Trouvé {len(locations)} locations", flush=True)
        
        # Convertir les ObjectId en string
        for location in locations:
            location['_id'] = str(location['_id'])
            if location.get('createdAt'):
                location['createdAt'] = location['createdAt'].isoformat()
            if location.get('updatedAt'):
                location['updatedAt'] = location['updatedAt'].isoformat()
        
        print("✅ GET_LOCATIONS: Succès", flush=True)
        return jsonify({
            'success': True,
            'locations': locations,
            'count': len(locations)
        }), 200
        
    except Exception as e:
        print(f"❌ GET_LOCATIONS: Exception = {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération des sites',
            'error': str(e)
        }), 500

# Route pour récupérer les départements d'une location
@app.route('/api/locations/<location_id>/departments', methods=['GET', 'OPTIONS'])
def get_departments_by_location(location_id):
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print(f"🔍 GET_DEPARTMENTS: Requête pour location {location_id}", flush=True)
    try:
        # Vérifier que la location existe
        location = locations_collection.find_one({'_id': ObjectId(location_id)})
        if not location:
            return jsonify({
                'success': False,
                'message': 'Site non trouvé'
            }), 404
        
        # DÉBOGAGE: Vérifier les collections disponibles
        print(f"🔍 GET_DEPARTMENTS: Collections disponibles: {db.list_collection_names()}", flush=True)
        
        # DÉBOGAGE: Tester plusieurs noms de collection
        for test_collection_name in ['departments', 'department', 'Departments', 'departements']:
            test_collection = db[test_collection_name]
            count = test_collection.count_documents({})
            print(f"🔍 GET_DEPARTMENTS: Collection '{test_collection_name}': {count} documents", flush=True)
            if count > 0:
                sample = test_collection.find_one({})
                print(f"🔍 GET_DEPARTMENTS: Exemple dans '{test_collection_name}': {sample}", flush=True)
        
        # Récupérer les départements associés à cette location (par nom de location)
        location_name = location.get('name', '')
        print(f"🔍 GET_DEPARTMENTS: Recherche départements avec location = {location_name}", flush=True)
        departments = list(departments_collection.find(
            {'location': location_name},  # Filtrer par nom de location
            {}  # Récupérer tous les champs
        ).sort('name', 1))
        
        print(f"🔍 GET_DEPARTMENTS: Trouvé {len(departments)} départements pour location {location_name}", flush=True)
        
        # Convertir les ObjectId en string et formater les dates
        for department in departments:
            department['_id'] = str(department['_id'])
            if department.get('createdAt'):
                department['createdAt'] = department['createdAt'].isoformat()
            if department.get('updatedAt'):
                department['updatedAt'] = department['updatedAt'].isoformat()
        
        print("✅ GET_DEPARTMENTS: Succès", flush=True)
        return jsonify({
            'success': True,
            'location': {
                'id': str(location['_id']),
                'name': location['name'],
                'code': location['code']
            },
            'departments': departments,
            'count': len(departments)
        }), 200
        
    except Exception as e:
        print(f"❌ GET_DEPARTMENTS: Exception = {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur serveur lors de la récupération des départements',
            'error': str(e)
        }), 500

# Route pour récupérer tous les départements (optionnel)
@app.route('/api/departments', methods=['GET', 'OPTIONS'])
def get_all_departments():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_ALL_DEPARTMENTS: Requête reçue", flush=True)
    try:
        # D'abord, compter tous les départements sans filtre
        total_count = departments_collection.count_documents({})
        print(f"🔍 GET_ALL_DEPARTMENTS: Total départements dans la collection: {total_count}", flush=True)
        
        # Ensuite, récupérer les départements avec un filtre simple
        departments_cursor = departments_collection.find({})
        departments = list(departments_cursor)
        
        print(f"🔍 GET_ALL_DEPARTMENTS: Trouvé {len(departments)} départements sans filtre", flush=True)
        
        # Formater les données
        formatted_departments = []
        for department in departments:
            formatted_dept = {
                '_id': str(department['_id']),
                'name': department.get('name', 'Nom non défini'),
                'location': department.get('location', ''),
                'active': department.get('active', True),
                'createdAt': department.get('createdAt', ''),
                'updatedAt': department.get('updatedAt', '')
            }
            formatted_departments.append(formatted_dept)
        
        response = jsonify({
            'success': True,
            'count': len(formatted_departments),
            'departments': formatted_departments
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
        
    except Exception as e:
        print(f"❌ GET_ALL_DEPARTMENTS: Erreur: {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des départements'
        }), 500

# ==============================================
# ROUTES POUR LA GESTION FILTREE PAR DEPARTEMENT ET LOCATION
# ==============================================

# Route pour récupérer les employés par département et location (pour admin)
@app.route('/api/admin/employees/filtered', methods=['GET', 'OPTIONS'])
def get_filtered_employees():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response, 200
    
    print("🔍 GET_FILTERED_EMPLOYEES: Requête reçue", flush=True)
    try:
        # Vérifier le token admin
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401

        # Récupérer les paramètres de filtre
        admin_department = request.args.get('department')
        admin_location = request.args.get('location')
        admin_role = request.args.get('role', 'ADMIN')  # ADMIN ou SUPERADMIN
        
        print(f"🔍 GET_FILTERED_EMPLOYEES: Filters - Department: {admin_department}, Location: {admin_location}, Role: {admin_role}", flush=True)
        
        # Construire le filtre
        filter_query = {}
        
        if admin_role == 'ADMIN':
            # Admin normal : voir seulement son département et sa location
            if admin_department and admin_location:
                filter_query = {
                    'department': admin_department,
                    'location': admin_location
                }
            elif admin_department:
                filter_query = {'department': admin_department}
            elif admin_location:
                filter_query = {'location': admin_location}

        # SUPERADMIN : peut voir tous les employés sans filtre
        
        # Paramètres optionnels pour affinage
        status_filter = request.args.get('status')
        if status_filter:
            filter_query['status'] = status_filter
            
        # Récupérer les employés filtrés
        employees = list(users_collection.find(
            filter_query,
            {'password': 0}
        ).sort('lastName', 1))
        
        print(f"🔍 GET_FILTERED_EMPLOYEES: Trouvé {len(employees)} employés", flush=True)
        
        # Formater les données
        formatted_employees = []
        for emp in employees:
            formatted_employees.append({
                'id': str(emp['_id']),
                'firstName': emp.get('firstName', ''),
                'lastName': emp.get('lastName', ''),
                'adresse1': emp.get('adresse1', ''),
                'employeeId': emp.get('employeeId', ''),
                'department': emp.get('department', 'Non spécifié'),
                'location': emp.get('location', 'Non spécifié'),
                'position': emp.get('position', 'Non spécifié'),
                'phoneNumber': emp.get('phoneNumber', ''),
                'role': emp.get('role', 'EMPLOYEE'),
                'createdAt': emp.get('createdAt').isoformat() if emp.get('createdAt') else None
            })
        
        return jsonify({
            'success': True,
            'employees': formatted_employees,
            'count': len(formatted_employees),
            'filters': {
                'department': admin_department,
                'location': admin_location,
                'role': admin_role
            }
        }), 200
        
    except Exception as e:
        print(f"❌ GET_FILTERED_EMPLOYEES: Exception = {str(e)}", flush=True)
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Route pour créer/publier une actualité avec filtrage par département et location
@app.route('/api/admin/news/create', methods=['POST', 'OPTIONS'])
def create_admin_news():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
    
    print("🔍 CREATE_ADMIN_NEWS: Requête reçue", flush=True)
    try:
        # Vérifier le token admin
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        # Vérifier les champs requis
        required_fields = ['title', 'content', 'authorDepartment', 'authorLocation']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        # Créer l'actualité
        news_data = {
            'title': data['title'],
            'content': data['content'],
            'authorId': payload.get('user_id'),
            'authorRole': data.get('authorRole', 'ADMIN'),
            'authorDepartment': data['authorDepartment'],
            'authorLocation': data['authorLocation'],
            'targetDepartments': data.get('targetDepartments', [data['authorDepartment']]),
            'targetLocations': data.get('targetLocations', [data['authorLocation']]),
            'isGlobal': data.get('isGlobal', False),  # Pour les super admins
            'priority': data.get('priority', 'normal'),
            'status': 'published',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }

        result = news_collection.insert_one(news_data)
        
        print(f"✅ CREATE_ADMIN_NEWS: Actualité créée avec ID = {result.inserted_id}", flush=True)
        
        return jsonify({
            'success': True,
            'message': 'Actualité publiée avec succès',
            'newsId': str(result.inserted_id)
        }), 201
            
    except Exception as e:
        print(f"❌ CREATE_ADMIN_NEWS: Exception = {str(e)}", flush=True)
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# ROUTE DUPLIQUÉE - COMMENTÉE POUR ÉVITER LES CONFLITS
# Route pour récupérer les actualités filtrées pour un utilisateur
# @app.route('/api/news/user', methods=['GET', 'OPTIONS'])
# def get_user_news():
#     # Cette route est déjà définie dans news_routes_simple.py
#     pass

# ROUTE DUPLIQUÉE - COMMENTÉE POUR ÉVITER LES CONFLITS
# Route pour l'authentification des admins (web app)
# @app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
# def admin_login():
#     if request.method == 'OPTIONS':
#         response = jsonify({'success': True})
#         response.headers.add('Access-Control-Allow-Origin', '*')
#         response.headers.add('Access-Control-Allow-Headers', '*')
#         response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
#         return response, 200
#     
#     print("🔍 ADMIN_LOGIN: Requête reçue", flush=True)
#     try:
#         data = request.get_json()
#         
#         if not data or not data.get('username') or not data.get('password'):
#             return jsonify({'success': False, 'message': 'Username et password requis'}), 400

#         username = data['username'].strip()
#         password = data['password']

#         print(f"🔍 ADMIN_LOGIN: Tentative de connexion pour {username}", flush=True)

#         # Vérifier si c'est un super admin
#         if username == 'superadmin' and password == 'superadmin123':
#             token = jwt.encode({
#                 'user_id': 'superadmin',
#                 'username': username,
#                 'role': 'SUPERADMIN',
#                 'department': 'ALL',
#                 'location': 'ALL',
#                 'exp': datetime.utcnow() + timedelta(hours=8)
#             }, JWT_SECRET_KEY, algorithm='HS256')
#             
#             return jsonify({
#                 'success': True,
#                 'message': 'Connexion super admin réussie',
#                 'token': token,
#                 'user': {
#                     'id': 'superadmin',
#                     'username': username,
#                     'role': 'SUPERADMIN',
#                     'department': 'ALL',
#                     'location': 'ALL'
#                 }
#             }), 200

#         # Vérifier les admins normaux dans la base de données
#         # Chercher un utilisateur admin avec ce username
#         admin_user = users_collection.find_one({
#             '$or': [
#                 {'adresse1': username.lower()},
#                 {'employeeId': username}
#             ],
#             'role': 'ADMIN'
#         })

#         if admin_user:
#             # Vérifier le mot de passe
#             stored_password = admin_user['password']
#             if isinstance(stored_password, str):
#                 stored_password = stored_password.encode('utf-8')
#             
#             if bcrypt.checkpw(password.encode('utf-8'), stored_password):
#                 token = jwt.encode({
#                     'user_id': str(admin_user['_id']),
#                     'username': username,
#                     'role': 'ADMIN',
#                     'department': admin_user.get('department', ''),
#                     'location': admin_user.get('location', ''),
#                     'exp': datetime.utcnow() + timedelta(hours=8)
#                 }, JWT_SECRET_KEY, algorithm='HS256')
#                 
#                 return jsonify({
#                     'success': True,
#                     'message': 'Connexion admin réussie',
#                     'token': token,
#                     'user': {
#                         'id': str(admin_user['_id']),
#                         'username': username,
#                         'role': 'ADMIN',
#                         'department': admin_user.get('department', ''),
#                         'location': admin_user.get('location', ''),
#                         'firstName': admin_user.get('firstName', ''),
#                         'lastName': admin_user.get('lastName', '')
#                     }
#                 }), 200

#         print(f"❌ ADMIN_LOGIN: Échec de connexion pour {username}", flush=True)
#         return jsonify({'success': False, 'message': 'Identifiants invalides'}), 401

#     except Exception as e:
#         print(f"❌ ADMIN_LOGIN: Exception = {str(e)}", flush=True)
#         return jsonify({'success': False, 'message': 'Erreur serveur'}), 500
#     # Cette route est déjà définie dans admin_routes.py
#     pass

# ROUTE DUPLIQUÉE - COMMENTÉE POUR ÉVITER LES CONFLITS  
# Route pour récupérer les demandes de documents filtrées par département et location
# @app.route('/api/admin/document-requests/filtered', methods=['GET', 'OPTIONS'])
# def get_filtered_document_requests():
#     if request.method == 'OPTIONS':
#         response = jsonify({'success': True})
#         response.headers.add('Access-Control-Allow-Origin', '*')
#         response.headers.add('Access-Control-Allow-Headers', '*')
#         response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
#         return response, 200
#     
#     print("🔍 GET_FILTERED_DOCUMENT_REQUESTS: Requête reçue", flush=True)
#     try:
#         # Vérifier le token admin
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return jsonify({'success': False, 'message': 'Token manquant'}), 401

#         token = auth_header.split(' ')[1]
#         payload = verify_token(token)
#         if not payload:
#             return jsonify({'success': False, 'message': 'Token invalide'}), 401

#         admin_role = payload.get('role', 'ADMIN')
#         admin_department = payload.get('department')
#         admin_location = payload.get('location')
#         
#         print(f"🔍 GET_FILTERED_DOCUMENT_REQUESTS: Admin - Role: {admin_role}, Department: {admin_department}, Location: {admin_location}", flush=True)
#         
#         # Construire le filtre pour les utilisateurs
#         user_filter = {}
#         if admin_role == 'ADMIN':
#             if admin_department and admin_location:
#                 user_filter = {
#                     'department': admin_department,
#                     'location': admin_location
#                 }

#         # Récupérer les IDs des utilisateurs filtrés
#         if user_filter:
#             filtered_users = list(users_collection.find(user_filter, {'_id': 1}))
#             user_ids = [str(user['_id']) for user in filtered_users]
#             
#             # Récupérer les demandes de documents pour ces utilisateurs
#             requests = list(document_requests_collection.find({'userId': {'$in': user_ids}}))
#         else:
#             # Super admin peut voir toutes les demandes
#             requests = list(document_requests_collection.find({}))
#         
#         print(f"🔍 GET_FILTERED_DOCUMENT_REQUESTS: Trouvé {len(requests)} demandes", flush=True)
#         
#         # Enrichir avec les informations utilisateur
#         enriched_requests = []
#         for req in requests:
#             user = users_collection.find_one({'_id': ObjectId(req['userId'])})
#             if user:
#                 enriched_req = {
#                     'id': str(req['_id']),
#                     'documentType': req.get('documentType', ''),
#                     'description': req.get('description', ''),
#                     'status': req.get('status', {}),
#                     'createdAt': req.get('createdAt').isoformat() if req.get('createdAt') else None,
#                     'updatedAt': req.get('updatedAt').isoformat() if req.get('updatedAt') else None,
#                     'user': {
#                         'id': str(user['_id']),
#                         'firstName': user.get('firstName', ''),
#                         'lastName': user.get('lastName', ''),
#                         'employeeId': user.get('employeeId', ''),
#                         'department': user.get('department', ''),
#                         'location': user.get('location', ''),
#                         'adresse1': user.get('adresse1', '')
#                     }
#                 }
#                 enriched_requests.append(enriched_req)
#         
#         return jsonify({
#             'success': True,
#             'requests': enriched_requests,
#             'count': len(enriched_requests)
#         }), 200
#         
#     except Exception as e:
#         print(f"❌ GET_FILTERED_DOCUMENT_REQUESTS: Exception = {str(e)}", flush=True)
#         return jsonify({'success': False, 'message': 'Erreur serveur'}), 500
#     # Cette route est déjà définie plus haut dans le fichier (ligne 1466)
#     pass

# Route pour mettre à jour le statut d'une demande de document (admin)
@app.route('/api/admin/document-requests/update-status', methods=['PUT', 'OPTIONS'])
def update_document_request_status():
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        return response, 200
    
    print("🔍 UPDATE_DOCUMENT_REQUEST_STATUS: Requête reçue", flush=True)
    try:
        # Vérifier le token admin
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401

        data = request.get_json()
        if not data or not data.get('requestId') or not data.get('newStatus'):
            return jsonify({'success': False, 'message': 'ID de demande et nouveau statut requis'}), 400

        valid_statuses = ['en attente', 'en cours', 'accepté', 'refusé']
        if data['newStatus'] not in valid_statuses:
            return jsonify({'success': False, 'message': 'Statut invalide'}), 400

        # Mettre à jour le statut
        result = document_requests_collection.update_one(
            {'_id': ObjectId(data['requestId'])},
            {
                '$set': {
                    'status.current': data['newStatus'],
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Demande non trouvée'}), 404

        print(f"✅ UPDATE_DOCUMENT_REQUEST_STATUS: Statut mis à jour pour {data['requestId']}", flush=True)

        return jsonify({
            'success': True,
            'message': 'Statut mis à jour avec succès'
        }), 200

    except Exception as e:
        print(f"❌ UPDATE_DOCUMENT_REQUEST_STATUS: Exception = {str(e)}", flush=True)
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Importer et enregistrer les routes d'administration étendues
try:
    from admin_routes_extended import create_admin_routes_extended
    create_admin_routes_extended(app, db, JWT_SECRET_KEY)
    print("✅ Routes d'administration étendues enregistrées avec succès")
except ImportError as e:
    print(f"⚠️  Erreur d'import des routes étendues: {e}")
except Exception as e:
    print(f"❌ Erreur enregistrement routes étendues: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    try:
        print(f"🚀 Serveur démarré sur le port {port}")
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur du serveur: {e}")
