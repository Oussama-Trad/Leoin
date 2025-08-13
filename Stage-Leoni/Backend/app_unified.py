#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application Flask unifiée pour la synchronisation avec l'interface admin Spring Boot
"""

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

# Import des routes unifiées
from routes.chat_routes_unified import chat_routes
from routes.news_routes_unified import news_routes
from routes.document_routes_unified import document_routes

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS Configuration - Allow all origins for mobile app and admin interface
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
    documents_collection = db.document_requests
    news_collection = db.news
    departments_collection = db.departments
    admins_collection = db.admins
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# Décorateur pour vérifier l'authentification JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(None, None, *args, **kwargs)
            
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_email = data.get('email', '')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        return f(current_user_id, current_user_email, *args, **kwargs)
    
    return decorated

# Enregistrer les blueprints
app.register_blueprint(chat_routes)
app.register_blueprint(news_routes)
app.register_blueprint(document_routes)

# Health check endpoint
@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    return jsonify({'status': 'OK', 'message': 'Server running', 'service': 'Unified Backend'}), 200

# Authentication Routes
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    print(f"🔥 LOGIN REQUEST - Method: {request.method}")
    
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        
        email = data.get('email', '') or data.get('adresse1', '')
        email = email.strip().lower() if email else ''
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email et mot de passe requis'}), 400
        
        # Find user by adresse1 field (primary) or email field (fallback)
        user = users_collection.find_one({'adresse1': email})
        if not user:
            user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401
        
        # Check password
        stored_password = user.get('password', b'')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
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
            'adresse1': email,
            'password': hashed_password,
            'department': data['department'].strip(),
            'location': data['location'].strip(),
            'approved': True,  # Auto-approve for demo
            'createdAt': datetime.utcnow(),
            'phoneNumber': data.get('phoneNumber', '').strip(),
            'employeeId': data.get('employeeId', '').strip(),
            'status': 'approved'
        }
        
        result = users_collection.insert_one(user_data)
        
        return jsonify({
            'success': True,
            'message': 'Inscription réussie.',
            'userId': str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"💥 REGISTER ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# User profile endpoint
@app.route('/me', methods=['GET', 'OPTIONS'])
@token_required
def get_me(current_user_id, current_user_email):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Get user from database
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
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
            'employeeId': user.get('employeeId', ''),
            'status': user.get('status', 'approved')
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        print(f"💥 ME ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Departments endpoint for mobile app
@app.route('/api/departments', methods=['GET', 'OPTIONS'])
@token_required
def get_departments(current_user_id, current_user_email):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        # Récupérer tous les départements
        departments = list(departments_collection.find({}))
        
        if len(departments) == 0:
            # Créer les départements par défaut si aucun n'existe
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
        
        departments_list = []
        for dept in departments:
            dept_data = {
                '_id': str(dept['_id']),
                'name': dept.get('name', ''),
                'location': dept.get('location', ''),
                'description': f"Département {dept.get('name', '')} - Location {dept.get('location', '')}"
            }
            departments_list.append(dept_data)
        
        return jsonify({
            'success': True,
            'data': departments_list,
            'count': len(departments_list)
        })
        
    except Exception as e:
        print(f"💥 GET DEPARTMENTS ERROR: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# Créer les index pour optimiser les performances
try:
    # Index pour les conversations
    chats_collection.create_index([("userId", 1), ("lastActivityAt", -1)])
    chats_collection.create_index([("targetDepartment", 1), ("targetLocation", 1)])
    chats_collection.create_index([("status", 1)])
    
    # Index pour les messages
    chat_messages_collection.create_index([("chatRef", 1), ("createdAt", 1)])
    chat_messages_collection.create_index([("senderId", 1)])
    
    # Index pour les demandes de documents
    documents_collection.create_index([("userId", 1), ("createdAt", -1)])
    documents_collection.create_index([("userDepartment", 1), ("userLocation", 1)])
    documents_collection.create_index([("status.current", 1)])
    
    # Index pour les actualités
    news_collection.create_index([("targetDepartment", 1), ("targetLocation", 1)])
    news_collection.create_index([("isActive", 1), ("createdAt", -1)])
    
    print("✅ Index créés avec succès")
except Exception as e:
    print(f"⚠️ Erreur création index: {e}")

if __name__ == '__main__':
    print("🔥🔥🔥 LEONI UNIFIED BACKEND SERVER 🔥🔥🔥")
    print("🔗 http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("🔥🔥🔥 SYNCHRONISATION MOBILE + ADMIN ACTIVÉE 🔥🔥🔥")
    
    app.run(host='127.0.0.1', port=5000, debug=True)