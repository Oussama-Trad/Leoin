from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt

app = Flask(__name__)

# CORS ULTRA SIMPLE - ACCEPTE TOUT + HEADERS EXPLICITES
CORS(app, 
     origins="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
     expose_headers=["*"],
     supports_credentials=True)

# MongoDB simple
MONGODB_URI = 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp'
JWT_SECRET = '123'

try:
    client = MongoClient(MONGODB_URI)
    db = client.LeoniApp
    users_collection = db.users
    print("✅ MongoDB connecté")
except Exception as e:
    print(f"❌ MongoDB error: {e}")

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({'status': 'OK', 'message': 'Server running'}), 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    print(f"🔥 LOGIN REQUEST - Method: {request.method}")
    print(f"🔥 Origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        print("🔥 Handling OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        print(f"🔥 Login data: {data}")
        
        # Accept both 'email' and 'adresse1' for compatibility
        email = data.get('email', '') or data.get('adresse1', '')
        email = email.strip().lower() if email else ''
        password = data.get('password', '')
        
        print(f"🔥 Extracted email: '{email}', password length: {len(password) if password else 0}")
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email et mot de passe requis'}), 400
        
        # Chercher l'utilisateur
        user = users_collection.find_one({'adresse1': email})
        if not user:
            # Essayer avec le champ email pour compatibility
            user = users_collection.find_one({'email': email})
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401
        
        # Vérifier le mot de passe
        stored_password = user.get('password', b'')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            print(f"❌ Wrong password for: {email}")
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401
        
        # Créer le token JWT
        token = jwt.encode({
            'user_id': str(user['_id']),
            'email': user.get('adresse1', user.get('email', email)),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        user_data = {
            'id': str(user['_id']),
            'email': user.get('adresse1', user.get('email', email)),
            'firstName': user.get('firstName', ''),
            'lastName': user.get('lastName', ''),
            'department': user.get('department', ''),
            'location': user.get('location', ''),
            'approved': user.get('approved', False)
        }
        
        print(f"✅ LOGIN SUCCESS: {email}")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user_data,
            'message': 'Connexion réussie'
        })
        
    except Exception as e:
        print(f"💥 LOGIN ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        data = request.get_json()
        
        # Champs requis de base
        required_fields = ['firstName', 'lastName', 'email', 'password', 'department', 'location']
        
        # Vérifier que tous les champs requis sont présents
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        email = data['email'].strip().lower()
        
        # Vérifier si l'utilisateur existe déjà
        if users_collection.find_one({"email": email}):
            return jsonify({'success': False, 'message': 'Un utilisateur avec cet email existe déjà'}), 400
        
        # Hasher le mot de passe
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Créer l'utilisateur
        user_data = {
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'email': email,
            'password': hashed_password,
            'department': data['department'].strip(),
            'location': data['location'].strip(),
            'approved': False,  # En attente d'approbation
            'createdAt': datetime.utcnow(),
            'phoneNumber': data.get('phoneNumber', '').strip(),
            'employeeId': data.get('employeeId', '').strip()
        }
        
        result = users_collection.insert_one(user_data)
        
        print(f"✅ REGISTER SUCCESS: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Inscription réussie. En attente d\'approbation.',
            'userId': str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"💥 REGISTER ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/me', methods=['GET', 'OPTIONS'])
def get_me():
    print(f"🔥 ME REQUEST - Method: {request.method}")
    print(f"🔥 Origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        print("🔥 Handling ME OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode JWT token
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # Get user from database
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
        
        user_data = {
            'id': str(user['_id']),
            'email': user.get('adresse1', user.get('email', '')),
            'firstName': user.get('firstName', ''),
            'lastName': user.get('lastName', ''),
            'department': user.get('department', ''),
            'location': user.get('location', ''),
            'approved': user.get('approved', False),
            'phoneNumber': user.get('phoneNumber', ''),
            'employeeId': user.get('employeeId', '')
        }
        
        print(f"✅ ME SUCCESS: {user.get('adresse1', user.get('email', ''))}")
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        print(f"💥 ME ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/document-requests', methods=['GET', 'OPTIONS'])
def get_document_requests():
    print(f"🔥 DOCUMENT-REQUESTS REQUEST - Method: {request.method}")
    print(f"🔥 Origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        print("🔥 Handling DOCUMENT-REQUESTS OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode JWT token
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # For now, return empty documents list since we don't have document management in simple server
        print(f"✅ DOCUMENT-REQUESTS SUCCESS for user: {user_id}")
        return jsonify({
            'success': True,
            'documents': [],
            'message': 'Aucun document trouvé'
        })
        
    except Exception as e:
        print(f"💥 DOCUMENT-REQUESTS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/chats/department', methods=['POST', 'OPTIONS'])
def create_chat_with_department():
    print(f"🔥 CREATE CHAT WITH DEPARTMENT REQUEST - Method: {request.method}")
    print(f"🔥 Origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        print("🔥 Handling CHAT OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode JWT token
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # Get user from database
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
        
        data = request.get_json()
        department = data.get('department', '')
        initial_message = data.get('initialMessage', '')
        
        print(f"🔥 Creating chat for department: {department}")
        
        # Create a simple chat response
        chat_data = {
            '_id': str(ObjectId()),
            'department': department,
            'userId': user_id,
            'userName': f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
            'userEmail': user.get('adresse1', user.get('email', '')),
            'status': 'open',
            'createdAt': datetime.utcnow().isoformat(),
            'messages': []
        }
        
        if initial_message:
            message_data = {
                '_id': str(ObjectId()),
                'text': initial_message,
                'sender': 'user',
                'senderName': chat_data['userName'],
                'timestamp': datetime.utcnow().isoformat()
            }
            chat_data['messages'].append(message_data)
        
        print(f"✅ CHAT CREATED SUCCESS for department: {department}")
        return jsonify({
            'success': True,
            'chat': chat_data,
            'message': 'Chat créé avec succès'
        })
        
    except Exception as e:
        print(f"💥 CREATE CHAT ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/chats', methods=['GET', 'OPTIONS'])
def get_user_chats():
    print(f"🔥 GET USER CHATS REQUEST - Method: {request.method}")
    print(f"🔥 Origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        print("🔥 Handling GET CHATS OPTIONS preflight")
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Decode JWT token
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # For now, return empty chats list
        print(f"✅ GET CHATS SUCCESS for user: {user_id}")
        return jsonify({
            'success': True,
            'chats': [],
            'message': 'Aucun chat trouvé'
        })
        
    except Exception as e:
        print(f"💥 GET CHATS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

if __name__ == '__main__':
    print("🔥🔥🔥 SERVEUR SIMPLE LOCALHOST ONLY 🔥🔥🔥")
    print("🔗 http://localhost:5000")
    print("🔗 http://localhost:5000/health")
    print("🔗 http://localhost:5000/login")
    print("🔥🔥🔥 CORS = ACCEPTE TOUT 🔥🔥🔥")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
