from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
import re
import os
import smtplib
import random
import secrets
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            'timestamp': datetime.now().isoformat()
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
            'role': 'EMPLOYEE',  # Rôle par défaut
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
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
            'exp': datetime.now() + timedelta(hours=24)
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
            'exp': datetime.now() + timedelta(hours=24)
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
                'department': user.get('department', 'Non spécifié'),
                'role': user.get('role', 'EMPLOYEE')
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

# ==============================================
# ENREGISTREMENT DES ROUTES EXTERNES
# ==============================================

# Enregistrer les routes des modules externes
try:
    from news_routes_simple import register_news_routes_simple
    print("📰 Enregistrement des nouvelles routes News simplifiées...")
    register_news_routes_simple(app, db, users_collection, news_collection, verify_token)
    print("✅ Routes News simplifiées enregistrées")
    
    from news_chat_routes_fixed import register_chat_routes
    print("💬 Enregistrement des routes Chat...")
    register_chat_routes(app, db, users_collection, chats_collection, chat_messages_collection, verify_token)
    print("✅ Routes Chat enregistrées avec succès")
    
    from admin_routes import register_admin_routes
    register_admin_routes(app, db, users_collection, document_requests_collection, verify_token)
    print("✅ Routes admin enregistrées avec succès")
    
    print("✅ Routes News simplifiées, Chat et Admin enregistrées avec succès")
    
except ImportError as e:
    print(f"⚠️ Erreur d'import des routes: {e}")
    print("📰 Fonctionnement avec routes de base seulement")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    try:
        print(f"🚀 Serveur démarré sur le port {port}")
        app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur du serveur: {e}")
