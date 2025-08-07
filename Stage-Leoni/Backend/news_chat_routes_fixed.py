from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Décorateur pour vérifier l'authentification JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            # Décoder le token JWT
            data = jwt.decode(token, '123', algorithms=['HS256'])  # Utiliser la même clé que dans app.py
            current_user_id = data['user_id']
            current_user_email = data.get('email', '')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalide'}), 401
        
        return f(current_user_id, current_user_email, *args, **kwargs)
    
    return decorated

def register_news_routes(app, db):
    """Enregistrer toutes les routes liées aux actualités"""
    
    print("📰 Enregistrement des routes News...")
    
    @app.route('/api/news', methods=['GET'])
    @token_required
    def get_user_news(current_user_id, current_user_email):
        """Obtenir les actualités visibles pour l'utilisateur connecté"""
        try:
            print(f"🔍 GET_USER_NEWS: Utilisateur ID = {current_user_id}", flush=True)
            
            # Récupérer l'utilisateur pour connaître sa location et département
            user = db.users.find_one({"_id": ObjectId(current_user_id)})
            if not user:
                print(f"❌ GET_USER_NEWS: Utilisateur introuvable", flush=True)
                return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
            
            print(f"🔍 GET_USER_NEWS: User locationRef={user.get('locationRef')}, departmentRef={user.get('departmentRef')}", flush=True)
            
            # Construire la requête de visibilité (version corrigée)
            current_time = datetime.now()
            
            # Étape 1: Récupérer les actualités publiées et non expirées
            base_query = {
                'status': 'published',
                '$or': [
                    {'expiryAt': {'$exists': False}},
                    {'expiryAt': None},
                    {'expiryAt': {'$gte': current_time}}
                ]
            }
            
            # Étape 2: Filtrer par visibilité
            visibility_filter = {
                '$or': [
                    {'visibility.type': 'company'},  # Actualités pour toute l'entreprise
                    {
                        'visibility.type': 'location',
                        'visibility.targetIds': user.get('locationRef')
                    },
                    {
                        'visibility.type': 'department',
                        'visibility.targetIds': user.get('departmentRef')
                    }
                ]
            }
            
            # Combiner les deux requêtes
            final_query = {**base_query, **visibility_filter}
            
            print(f"🔍 GET_USER_NEWS: Requête MongoDB = {final_query}", flush=True)
            
            # Récupérer les actualités
            news_cursor = db.news.find(final_query).sort('publishedAt', -1).limit(50)
            news_list = []
            
            for news_item in news_cursor:
                print(f"🔍 GET_USER_NEWS: Actualité trouvée = {news_item.get('title')}", flush=True)
                
                news_data = {
                    '_id': str(news_item['_id']),
                    'title': news_item['title'],
                    'content': news_item['content'],
                    'summary': news_item.get('summary', ''),
                    'authorName': news_item.get('authorName', 'Inconnu'),
                    'category': news_item.get('category', 'general'),
                    'priority': news_item.get('priority', 'normal'),
                    'publishedAt': news_item.get('publishedAt').isoformat() if news_item.get('publishedAt') else None,
                    'createdAt': news_item.get('createdAt').isoformat() if news_item.get('createdAt') else None,
                    'stats': news_item.get('stats', {'views': 0, 'likes': 0, 'comments': 0}),
                    'attachments': news_item.get('attachments', []),
                    'expiryAt': news_item.get('expiryAt').isoformat() if news_item.get('expiryAt') else None
                }
                news_list.append(news_data)
            
            print(f"✅ GET_USER_NEWS: {len(news_list)} actualités trouvées", flush=True)
            
            return jsonify({
                'success': True,
                'data': news_list,
                'count': len(news_list),
                'message': f'{len(news_list)} actualités récupérées avec succès'
            })
            
        except Exception as e:
            print(f"❌ GET_USER_NEWS: Exception = {e}", flush=True)
            return jsonify({'success': False, 'message': 'Erreur serveur'}), 500
    
    # Création des index pour optimiser les performances
    try:
        if 'news' not in db.list_collection_names():
            db.create_collection('news')
        if 'news_interactions' not in db.list_collection_names():
            db.create_collection('news_interactions')
            
        news_collection = db['news']
        news_interactions_collection = db['news_interactions']
        
        # Index pour les news
        news_collection.create_index([("status", 1), ("publishedAt", -1)])
        news_collection.create_index([("visibility.type", 1), ("visibility.targetIds", 1)])
        news_collection.create_index([("authorRef", 1)])
        
        # Index pour les interactions
        news_interactions_collection.create_index([("newsRef", 1), ("userRef", 1)], unique=True)
        
        print("✅ Index News créés avec succès")
    except Exception as e:
        print(f"⚠️ Erreur création index News: {e}")
    
    print("✅ Routes News enregistrées avec succès")

def register_chat_routes(app, db):
    """Enregistrer toutes les routes liées aux conversations"""
    
    print("💬 Enregistrement des routes Chat...")
    
    @app.route('/api/services', methods=['GET'])
    @token_required
    def get_available_services(current_user_id, current_user_email):
        """Obtenir les services disponibles pour l'utilisateur"""
        try:
            # Pour l'instant, retourner une liste de services basiques
            services_list = [
                {
                    '_id': 'it_support',
                    'name': 'Support IT',
                    'code': 'IT',
                    'description': 'Support technique et informatique',
                    'stats': {'totalChats': 0, 'activeChats': 0}
                },
                {
                    '_id': 'hr_service',
                    'name': 'Ressources Humaines',
                    'code': 'HR',
                    'description': 'Questions liées aux ressources humaines',
                    'stats': {'totalChats': 0, 'activeChats': 0}
                }
            ]
            
            return jsonify({
                'success': True,
                'data': services_list,
                'count': len(services_list),
                'message': 'Module Chat initialisé avec succès'
            })
            
        except Exception as e:
            print(f"Erreur récupération services: {e}")
            return jsonify({'success': False, 'message': 'Erreur serveur'}), 500
    
    # Création des index pour optimiser les performances
    try:
        if 'services' not in db.list_collection_names():
            db.create_collection('services')
        if 'chats' not in db.list_collection_names():
            db.create_collection('chats')
        if 'chat_messages' not in db.list_collection_names():
            db.create_collection('chat_messages')
            
        services_collection = db['services']
        chats_collection = db['chats']
        chat_messages_collection = db['chat_messages']
        
        # Index pour les services
        services_collection.create_index([("code", 1)], unique=True)
        services_collection.create_index([("departmentRef", 1)])
        services_collection.create_index([("isActive", 1)])
        
        # Index pour les chats
        chats_collection.create_index([("participants.employee.userId", 1)])
        chats_collection.create_index([("participants.service.serviceId", 1)])
        chats_collection.create_index([("status", 1), ("lastActivityAt", -1)])
        
        # Index pour les messages
        chat_messages_collection.create_index([("chatRef", 1), ("createdAt", -1)])
        chat_messages_collection.create_index([("senderId", 1), ("createdAt", -1)])
        
        print("✅ Index Chat créés avec succès")
    except Exception as e:
        print(f"⚠️ Erreur création index Chat: {e}")
    
    print("✅ Routes Chat enregistrées avec succès")
