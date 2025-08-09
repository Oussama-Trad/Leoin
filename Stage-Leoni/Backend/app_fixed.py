from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt
import os
from dotenv import load_dotenv

# Décorateur pour vérifier l'authentification JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Pour les requêtes OPTIONS (preflight), ne pas vérifier le token
        if request.method == 'OPTIONS':
            return f(None, None, *args, **kwargs)
            
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            # Décoder le token JWT
            data = jwt.decode(token, '123', algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_email = data.get('email', '')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        return f(current_user_id, current_user_email, *args, **kwargs)
    
    return decorated

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS Configuration - Allow all origins for mobile app
CORS(app, 
     origins="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
     expose_headers=["*"],
     supports_credentials=True)

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://oussamatrzd19:oussama123@leoniapp.grhnzgz.mongodb.net/LeoniApp')
JWT_SECRET = os.getenv('JWT_SECRET', '123')

try:
    client = MongoClient(MONGODB_URI)
    db = client.LeoniApp
    users_collection = db.users
    chats_collection = db.chats
    chat_messages_collection = db.chat_messages
    documents_collection = db.documents
    news_collection = db.news
    departments_collection = db.departments
    admins_collection = db.admins
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# Health check endpoint
@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return jsonify({'status': 'OK', 'message': 'Server running'}), 200

# Authentication Routes
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
        
        # Find user by adresse1 field (primary) or email field (fallback)
        user = users_collection.find_one({'adresse1': email})
        if not user:
            user = users_collection.find_one({'email': email})
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401
        
        # Check password
        stored_password = user.get('password', b'')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            print(f"❌ Wrong password for: {email}")
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401
        
        # Create JWT token
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
        
        # Required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'department', 'location']
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Champs manquants: {", ".join(missing_fields)}'
            }), 400

        email = data['email'].strip().lower()
        
        # Check if user already exists
        if users_collection.find_one({"adresse1": email}) or users_collection.find_one({"email": email}):
            return jsonify({'success': False, 'message': 'Un utilisateur avec cet email existe déjà'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_data = {
            'firstName': data['firstName'].strip(),
            'lastName': data['lastName'].strip(),
            'email': email,
            'adresse1': email,  # Use adresse1 as primary email field
            'password': hashed_password,
            'department': data['department'].strip(),
            'location': data['location'].strip(),
            'approved': False,  # Pending approval
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

# User profile endpoint
@app.route('/me', methods=['GET', 'OPTIONS'])
def get_me():
    print(f"🔥 ME REQUEST - Method: {request.method}")
    
    if request.method == 'OPTIONS':
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
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        print(f"💥 ME ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Chat Routes
@app.route('/api/chats/department', methods=['POST', 'OPTIONS'])
@token_required
def create_chat_with_department(current_user_id, current_user_email):
    """Créer une nouvelle conversation avec un département spécifique (pour app mobile)"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Validation du token et de l'utilisateur
        if not current_user_id or not current_user_email:
            return jsonify({
                'success': False,
                'message': 'Authentification requise'
            }), 401

        # Récupération et validation des données JSON
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Format de données invalide'
            }), 400

        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'message': 'Données invalides'
            }), 400

        # Extraction et validation des champs requis
        department = data.get('department', '').strip()
        initial_message = data.get('initialMessage', '').strip()
        subject = data.get('subject', 'Nouvelle conversation').strip()

        if not department:
            return jsonify({
                'success': False,
                'message': 'Le département est requis'
            }), 400
        
        # Récupérer l'utilisateur
        print("🔍 Recherche utilisateur:", current_user_id)
        user = users_collection.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            print("❌ Utilisateur non trouvé:", current_user_id)
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
        print("✅ Utilisateur trouvé:", user.get('firstName', ''), user.get('lastName', ''))
        
        # Obtenir la location de l'utilisateur
        user_location = user.get('location', '')
        user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
        print("📍 Location utilisateur:", user_location)
        
        print(f"📝 Création chat département: {department} pour {user.get('firstName', '')} de {user_location}")
        
        # Vérifier que le département existe dans la collection departments
        print("🔍 Recherche département:", department)
        target_dept = departments_collection.find_one({"name": department})
        
        if not target_dept:
            print(f"❌ Département {department} non trouvé dans la collection departments")
            
            # Lister tous les départements disponibles pour debug
            all_depts = list(departments_collection.find({}))
            print(f"📋 Départements disponibles en base: {[dept.get('name', 'Sans nom') for dept in all_depts]}")
            
            if len(all_depts) == 0:
                # Si pas de départements, les créer par défaut
                print("⚠️ Collection departments vide, création des départements par défaut")
                default_departments = [
                    {"name": "Production", "location": "Messadine", "active": True},
                    {"name": "Production", "location": "Mateur", "active": True},
                    {"name": "Production", "location": "Manzel Hayet", "active": True},
                    {"name": "Qualité", "location": "Messadine", "active": True},
                    {"name": "Qualité", "location": "Mateur", "active": True},
                    {"name": "Maintenance", "location": "Messadine", "active": True},
                    {"name": "Ingénierie", "location": "Messadine", "active": True},
                    {"name": "Support Technique", "location": "Messadine", "active": True},
                ]
                try:
                    departments_collection.insert_many(default_departments)
                    print("✅ Départements par défaut créés")
                    # Réessayer de trouver le département
                    target_dept = departments_collection.find_one({"name": department})
                except Exception as e:
                    print("❌ Erreur création départements par défaut:", str(e))
                    return jsonify({'success': False, 'message': 'Erreur lors de la création des départements'}), 500
            
            if not target_dept:
                return jsonify({
                    'success': False, 
                    'message': f'Le département "{department}" n\'existe pas'
                }), 400
                
        print("✅ Département trouvé:", target_dept)
        
        if not target_dept.get('active', True):
            return jsonify({
                'success': False,
                'message': 'Ce département n\'est pas disponible actuellement'
            }), 400

        # Création de la conversation
        current_time = datetime.utcnow()
        conversation_data = {
            'subject': subject,
            'title': subject,
            'description': initial_message if initial_message else subject,
            'department': department,
            'targetDepartment': department,
            'targetLocation': target_dept.get('location', ''),
            'status': 'pending',
            'priority': 'normal',
            'userId': ObjectId(current_user_id),
            'userEmail': current_user_email,
            'userName': user_name,
            'userDepartment': user.get('department', ''),
            'userLocation': user_location,
            'participants': [str(current_user_id)],
            'createdAt': current_time,
            'lastActivityAt': current_time,
            'messageCount': 0
        }

        try:
            # Insertion de la conversation
            result = chats_collection.insert_one(conversation_data)
            conversation_id = result.inserted_id
            print("✅ Conversation créée avec ID:", conversation_id)

            # Création du message initial si fourni
            if initial_message:
                message_data = {
                    'chatId': conversation_id,
                    'content': initial_message,
                    'message': initial_message,
                    'subject': subject,
                    'senderId': ObjectId(current_user_id),
                    'senderName': user_name,
                    'senderRole': 'employee',
                    'senderType': 'user',
                    'createdAt': current_time,
                    'isRead': False
                }
                
                chat_messages_collection.insert_one(message_data)
                print("✅ Message initial créé")
                
                # Mise à jour du compteur de messages
                chats_collection.update_one(
                    {'_id': conversation_id},
                    {'$inc': {'messageCount': 1}}
                )

            # Préparation de la réponse
            response_data = {
                '_id': str(conversation_id),
                'subject': subject,
                'department': department,
                'targetDepartment': department,
                'targetLocation': target_dept.get('location', ''),
                'status': 'pending',
                'priority': 'normal',
                'messageCount': 1 if initial_message else 0,
                'createdAt': current_time.isoformat(),
                'lastActivityAt': current_time.isoformat()
            }

            if initial_message:
                response_data['lastMessage'] = {
                    'content': initial_message,
                    'senderName': user_name,
                    'senderRole': 'employee',
                    'createdAt': current_time.isoformat()
                }

            return jsonify({
                'success': True,
                'message': f'Conversation créée avec le département {department}',
                'data': response_data
            })

        except Exception as e:
            print(f"💥 Erreur lors de la création: {str(e)}")
            # Si une conversation a été créée mais qu'il y a eu une erreur après,
            # on la supprime pour éviter les conversations orphelines
            if 'result' in locals():
                try:
                    chats_collection.delete_one({'_id': conversation_id})
                    print("✅ Nettoyage réussi - conversation supprimée")
                except Exception as cleanup_error:
                    print(f"⚠️ Erreur lors du nettoyage: {cleanup_error}")
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la création de la conversation'
            }), 500

    except Exception as e:
        print(f"💥 ERROR creating chat: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la création de la conversation'
        }), 500

@app.route('/api/chats', methods=['GET', 'OPTIONS'])
@token_required  
def get_user_chats_mobile(current_user_id, current_user_email):
    """Récupérer les conversations de l'utilisateur (format app mobile)"""
    
    # Gérer les requêtes OPTIONS (preflight)
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        print(f"💬 Récupération chats pour utilisateur: {current_user_id}")
        
        # Récupérer les conversations de l'utilisateur
        conversations = list(chats_collection.find({
            'userId': ObjectId(current_user_id)
        }).sort('lastActivityAt', -1))
        
        print(f"💬 Conversations trouvées: {len(conversations)}")
        
        conversations_list = []
        for conv in conversations:
            # Récupérer le dernier message
            last_message = chat_messages_collection.find_one(
                {'chatId': conv['_id']}, 
                sort=[('createdAt', -1)]
            )
            
            # Compter les messages non lus (messages d'admin non lus par l'utilisateur)
            unread_count = chat_messages_collection.count_documents({
                'chatId': conv['_id'],
                'senderRole': 'admin',
                'isRead': False
            })
            
            conv_data = {
                '_id': str(conv['_id']),
                'subject': conv.get('subject', ''),
                'targetDepartment': conv.get('targetDepartment', ''),
                'targetLocation': conv.get('targetLocation', ''),
                'status': conv.get('status', 'pending'),
                'priority': conv.get('priority', 'normal'),
                'createdAt': conv.get('createdAt').isoformat() if conv.get('createdAt') else None,
                'lastActivityAt': conv.get('lastActivityAt').isoformat() if conv.get('lastActivityAt') else None,
                'messageCount': conv.get('messageCount', 0),
                'unreadCount': unread_count
            }
            
            # Ajouter le dernier message s'il existe
            if last_message:
                conv_data['lastMessage'] = {
                    'content': last_message.get('content', last_message.get('message', '')),
                    'senderName': last_message.get('senderName', 'Inconnu'),
                    'senderRole': last_message.get('senderRole', 'user'),
                    'createdAt': last_message.get('createdAt').isoformat() if last_message.get('createdAt') else None
                }
            
            conversations_list.append(conv_data)
        
        print(f"💬 Retour de {len(conversations_list)} conversations à l'app mobile")
        
        return jsonify({
            'success': True,
            'data': conversations_list,
            'count': len(conversations_list)
        })
        
    except Exception as e:
        print(f"💥 GET CHATS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Document Routes
@app.route('/document-requests', methods=['GET', 'OPTIONS'])
def get_document_requests():
    print(f"🔥 DOCUMENT REQUESTS - Method: {request.method}")
    
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token and validate user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # Get user's document requests
        documents = list(documents_collection.find({'userId': user_id}).sort('createdAt', -1))
        
        # Convert ObjectIds to strings
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        
        return jsonify({
            'success': True,
            'documents': documents
        })
        
    except Exception as e:
        print(f"💥 DOCUMENT REQUESTS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Departments Routes
@app.route('/api/departments', methods=['GET', 'OPTIONS'])
@token_required
def get_available_departments_mobile(current_user_id, current_user_email):
    """Obtenir les départements disponibles pour l'app mobile"""
    
    # Gérer les requêtes OPTIONS (preflight)
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        user = users_collection.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
        print(f"📋 Recherche des départements pour l'app mobile...")
        
        # Récupérer tous les départements (avec ou sans filtre active)
        departments = list(departments_collection.find({}))
        print(f"📋 Départements trouvés en base: {len(departments)}")
        
        if len(departments) == 0:
            print("⚠️ Aucun département en base, création des départements par défaut")
            # Si pas de départements en base, créer les départements par défaut
            default_departments = [
                {"name": "Production", "location": "Messadine", "active": True},
                {"name": "Production", "location": "Mateur", "active": True},
                {"name": "Production", "location": "Manzel Hayet", "active": True},
                {"name": "Qualité", "location": "Messadine", "active": True},
                {"name": "Qualité", "location": "Mateur", "active": True},
                {"name": "Qualité", "location": "Manzel Hayet", "active": True},
                {"name": "Maintenance", "location": "Messadine", "active": True},
                {"name": "Maintenance", "location": "Mateur", "active": True},
                {"name": "Maintenance", "location": "Manzel Hayet", "active": True},
                {"name": "Logistique", "location": "Messadine", "active": True},
                {"name": "Logistique", "location": "Mateur", "active": True},
                {"name": "Logistique", "location": "Manzel Hayet", "active": True},
                {"name": "Ingénierie", "location": "Messadine", "active": True},
                {"name": "Planification", "location": "Messadine", "active": True},
                {"name": "Achat", "location": "Messadine", "active": True},
                {"name": "Ressources Humaines", "location": "Messadine", "active": True},
                {"name": "Finance", "location": "Messadine", "active": True},
                {"name": "Support Technique", "location": "Messadine", "active": True},
            ]
            departments_collection.insert_many(default_departments)
            departments = list(departments_collection.find({}))
            print(f"✅ {len(default_departments)} départements créés")
        
        departments_list = []
        for dept in departments:
            print(f"📋 Département trouvé: {dept.get('name', 'Unknown')} - {dept.get('location', 'Unknown')}")
            dept_data = {
                '_id': str(dept['_id']),
                'name': dept.get('name', ''),
                'location': dept.get('location', ''),
                'description': f"Département {dept.get('name', '')} - Location {dept.get('location', '')}"
            }
            departments_list.append(dept_data)
        
        print(f"📋 Retour de {len(departments_list)} départements à l'app mobile")
        
        return jsonify({
            'success': True,
            'data': departments_list,  # Format attendu par l'app mobile
            'count': len(departments_list)
        })
        
    except Exception as e:
        print(f"💥 GET DEPARTMENTS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Message routes
@app.route('/api/chat/conversation/<conversation_id>/messages', methods=['GET'])
@token_required
def get_conversation_messages(current_user_id, current_user_email, conversation_id):
    """Récupérer les messages d'une conversation"""
    try:
        # Vérifier que la conversation appartient à l'utilisateur
        conversation = chats_collection.find_one({
            '_id': ObjectId(conversation_id),
            'userId': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Récupérer les messages
        messages = list(chat_messages_collection.find({
            'chatId': ObjectId(conversation_id)
        }).sort('createdAt', 1))
        
        messages_list = []
        for msg in messages:
            msg_data = {
                '_id': str(msg['_id']),
                'content': msg.get('content', ''),
                'senderId': str(msg.get('senderId', '')),
                'senderName': msg.get('senderName', ''),
                'senderRole': msg.get('senderRole', 'employee'),
                'createdAt': msg.get('createdAt').isoformat() if msg.get('createdAt') else None,
                'isRead': msg.get('isRead', False)
            }
            messages_list.append(msg_data)
        
        return jsonify({
            'success': True,
            'messages': messages_list,
            'count': len(messages_list)
        })
        
    except Exception as e:
        print(f"Erreur récupération messages: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/chat/conversation/<conversation_id>/message', methods=['POST'])
@token_required
def send_message(current_user_id, current_user_email, conversation_id):
    """Envoyer un message dans une conversation"""
    try:
        data = request.get_json()
        
        if not data.get('content', '').strip():
            return jsonify({'success': False, 'message': 'Le message ne peut pas être vide'}), 400
        
        # Vérifier que la conversation appartient à l'utilisateur
        conversation = chats_collection.find_one({
            '_id': ObjectId(conversation_id),
            'userId': ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Récupérer l'utilisateur
        user = users_collection.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        # Créer le message
        message_data = {
            'chatId': ObjectId(conversation_id),
            'content': data['content'].strip(),
            'message': data['content'].strip(),
            'senderId': ObjectId(current_user_id),
            'senderName': user.get('firstName', '') + ' ' + user.get('lastName', ''),
            'senderRole': 'employee',
            'senderType': 'user',
            'createdAt': datetime.utcnow(),
            'isRead': False
        }
        
        # Insérer le message
        result = chat_messages_collection.insert_one(message_data)
        
        # Mettre à jour la conversation
        chats_collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$set': {'lastActivityAt': datetime.utcnow()},
                '$inc': {'messageCount': 1}
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé avec succès',
            'messageId': str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"Erreur envoi message: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# News Routes
@app.route('/api/admin/chat/conversations', methods=['GET', 'OPTIONS'])
def get_admin_conversations():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    """Récupérer les conversations pour un admin selon ses droits"""
    try:
        # Récupérer le token admin depuis les headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token admin requis'}), 401
        
        token = auth_header[7:]  # Enlever 'Bearer '
        
        # Pour cette implémentation simplifiée, on va récupérer l'admin depuis la base
        # En production, il faudrait décoder le JWT
        admin_username = request.args.get('admin_username')
        admin_role = request.args.get('admin_role', 'ADMIN')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        admin = admins_collection.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Construire le filtre selon les droits
        filter_query = {}
        
        if admin_role == 'SUPERADMIN':
            # Super admin voit toutes les conversations
            filter_query = {}
        else:
            # Admin normal voit seulement les conversations de son département et location
            admin_location = admin.get('location')
            admin_department = admin.get('department')
            
            if admin_location and admin_department:
                filter_query = {
                    'targetLocation': admin_location,
                    'targetDepartment': admin_department
                }
            elif admin_department:
                filter_query = {'targetDepartment': admin_department}
            else:
                # Si pas de location/département défini, ne voir aucune conversation
                filter_query = {'_id': None}
        
        # Récupérer les conversations
        conversations = list(chats_collection.find(filter_query).sort('lastActivityAt', -1).limit(100))
        
        conversations_list = []
        for conv in conversations:
            # Récupérer le dernier message
            last_message = chat_messages_collection.find_one(
                {'chatId': conv['_id']}, 
                sort=[('createdAt', -1)]
            )
            
            conv_data = {
                '_id': str(conv['_id']),
                'title': conv.get('title', ''),
                'description': conv.get('description', ''),
                'targetDepartment': conv.get('targetDepartment', ''),
                'targetLocation': conv.get('targetLocation', ''),
                'status': conv.get('status', 'pending'),
                'priority': conv.get('priority', 'normal'),
                'userName': conv.get('userName', ''),
                'userEmail': conv.get('userEmail', ''),
                'userDepartment': conv.get('userDepartment', ''),
                'userLocation': conv.get('userLocation', ''),
                'createdAt': conv.get('createdAt').isoformat() if conv.get('createdAt') else None,
                'lastActivityAt': conv.get('lastActivityAt').isoformat() if conv.get('lastActivityAt') else None,
                'messageCount': conv.get('messageCount', 0)
            }
            
            if last_message:
                conv_data['lastMessage'] = {
                    'content': last_message.get('content', ''),
                    'senderName': last_message.get('senderName', ''),
                    'senderRole': last_message.get('senderRole', ''),
                    'createdAt': last_message.get('createdAt').isoformat() if last_message.get('createdAt') else None
                }
            
            conversations_list.append(conv_data)
        
        return jsonify({
            'success': True,
            'conversations': conversations_list,
            'count': len(conversations_list),
            'filter': filter_query,
            'adminRole': admin_role
        })
        
    except Exception as e:
        print(f"💥 GET ADMIN CONVERSATIONS ERROR: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'conversations': [],
            'total': 0,
            'page': 0,
            'size': 10
        }), 500

@app.route('/api/news', methods=['GET', 'OPTIONS'])
def get_news():
    print(f"🔥 GET NEWS - Method: {request.method}")
    
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get token and validate user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        # Get latest news
        news = list(news_collection.find({}).sort('createdAt', -1).limit(20))
        
        # Convert ObjectIds to strings
        for article in news:
            article['_id'] = str(article['_id'])
        
        return jsonify({
            'success': True,
            'news': news
        })
        
    except Exception as e:
        print(f"💥 GET NEWS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Admin reply route
@app.route('/api/admin/chat/conversation/<conversation_id>/reply', methods=['POST'])
def admin_reply_to_conversation(conversation_id):
    """Admin répond à une conversation"""
    
    data = request.get_json()
    
    if not data.get('content', '').strip():
        return jsonify({'success': False, 'message': 'Le message ne peut pas être vide'}), 400
    
    # Récupérer le token admin
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'Token admin requis'}), 401
    
    admin_username = data.get('admin_username')
    admin_role = data.get('admin_role', 'ADMIN')
    
    if not admin_username:
        return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
    
    try:
        # Vérifier que la conversation existe
        conversation = chats_collection.find_one({'_id': ObjectId(conversation_id)})
        if not conversation:
            return jsonify({'success': False, 'message': 'Conversation non trouvée'}), 404
        
        # Vérifier les droits de l'admin
        admin = admins_collection.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Vérifier les permissions
        if admin_role != 'SUPERADMIN':
            admin_location = admin.get('location')
            admin_department = admin.get('department')
            conv_location = conversation.get('targetLocation')
            conv_department = conversation.get('targetDepartment')
            
            if admin_location != conv_location or admin_department != conv_department:
                return jsonify({'success': False, 'message': 'Droits insuffisants'}), 403
        
        # Créer le message de réponse
        message_data = {
            'chatId': ObjectId(conversation_id),
            'content': data['content'].strip(),
            'message': data['content'].strip(),
            'senderId': ObjectId(admin['_id']),
            'senderName': admin.get('username', 'Admin'),
            'senderRole': 'admin',
            'senderType': 'admin',
            'createdAt': datetime.utcnow(),
            'isRead': False
        }
        
        # Insérer le message
        result = chat_messages_collection.insert_one(message_data)
        
        # Mettre à jour la conversation
        update_data = {
            'lastActivityAt': datetime.utcnow(),
            'status': 'in_progress'
        }
        
        chats_collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$set': update_data,
                '$inc': {'messageCount': 1}
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Réponse envoyée avec succès',
            'messageId': str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"💥 ERROR admin reply: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de l\'envoi de la réponse'
        }), 500

@app.route('/api/admin/chat/statistics', methods=['GET'])
def get_admin_chat_statistics():
    """Récupérer les statistiques des conversations pour un admin"""
    try:
        # Récupérer les paramètres admin
        admin_username = request.args.get('admin_username')
        admin_role = request.args.get('admin_role', 'ADMIN')
        
        if not admin_username:
            return jsonify({'success': False, 'message': 'Nom admin requis'}), 400
        
        # Récupérer l'admin
        admin = admins_collection.find_one({'username': admin_username, 'active': True})
        if not admin:
            return jsonify({'success': False, 'message': 'Admin non trouvé'}), 404
        
        # Construire le filtre selon les droits
        filter_query = {}
        
        if admin_role == 'SUPERADMIN':
            # Super admin voit toutes les conversations
            filter_query = {}
        else:
            # Admin normal voit seulement les conversations de son département et location
            admin_location = admin.get('location')
            admin_department = admin.get('department')
            
            if admin_location and admin_department:
                filter_query = {
                    'targetLocation': admin_location,
                    'targetDepartment': admin_department
                }
            elif admin_department:
                filter_query = {'targetDepartment': admin_department}
            else:
                # Si pas de location/département défini, ne voir aucune conversation
                filter_query = {'_id': None}
        
        # Calculer les statistiques
        total_chats = chats_collection.count_documents(filter_query)
        
        # Conversations actives (ouvertes ou en cours)
        active_filter = dict(filter_query)
        active_filter['status'] = {'$in': ['open', 'in_progress']}
        active_chats = chats_collection.count_documents(active_filter)
        
        # Conversations fermées
        closed_filter = dict(filter_query)
        closed_filter['status'] = 'closed'
        closed_chats = chats_collection.count_documents(closed_filter)
        
        # Conversations des dernières 24h
        from datetime import timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_filter = dict(filter_query)
        recent_filter['createdAt'] = {'$gte': last_24h}
        chats_last_24h = chats_collection.count_documents(recent_filter)
        
        # Messages non lus (approximation basée sur les conversations avec activité récente)
        unread_filter = dict(filter_query)
        unread_filter['lastActivityAt'] = {'$gte': last_24h}
        unread_filter['status'] = {'$ne': 'closed'}
        unread_chats = chats_collection.count_documents(unread_filter)
        
        statistics = {
            'success': True,
            'totalChats': total_chats,
            'activeChats': active_chats,
            'closedChats': closed_chats,
            'unreadChats': unread_chats,
            'chatsLast24h': chats_last_24h,
            'adminRole': admin_role,
            'adminUsername': admin_username
        }
        
        return jsonify(statistics)
        
    except Exception as e:
        print(f"Erreur récupération statistiques chat admin: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/debug/chats', methods=['GET']) 
def debug_chats():
    try:
        all_chats = list(chats_collection.find({}))
        
        # Convert ObjectIds to strings
        for chat in all_chats:
            chat['_id'] = str(chat['_id'])
            for message in chat.get('messages', []):
                message['_id'] = str(message['_id'])
        
        return jsonify({
            'success': True,
            'total_chats': len(all_chats),
            'chats': all_chats
        })
    except Exception as e:
        print(f"💥 DEBUG CHATS ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Créer les index pour optimiser les performances
try:
    # Index pour les conversations
    chats_collection.create_index([("userId", 1), ("lastActivityAt", -1)])
    chats_collection.create_index([("targetDepartment", 1), ("targetLocation", 1)])
    chats_collection.create_index([("status", 1)])
    
    # Index pour les messages
    chat_messages_collection.create_index([("chatId", 1), ("createdAt", 1)])
    chat_messages_collection.create_index([("senderId", 1)])
    
    print("✅ Index Chat créés avec succès")
except Exception as e:
    print(f"⚠️ Erreur création index Chat: {e}")

if __name__ == '__main__':
    print("🔥🔥🔥 LEONI APP BACKEND SERVER 🔥🔥🔥")
    print("🔗 http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("🔥🔥🔥 CORS ENABLED FOR ALL ORIGINS 🔥🔥🔥")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
