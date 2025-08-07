#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Routes API simplifiées pour le nouveau système de News
- GET /api/news : Récupérer les news ciblées pour l'utilisateur
- POST /api/news : Créer une nouvelle news (admin seulement)
- PUT /api/news/:id : Modifier une news (admin seulement)
- DELETE /api/news/:id : Supprimer une news (admin seulement)
"""

from flask import request, jsonify
from bson import ObjectId
from datetime import datetime
import re

def register_news_routes_simple(app, db):
    """Enregistrer les nouvelles routes news simplifiées"""
    
    print("📰 Enregistrement des nouvelles routes News simplifiées...")
    
    @app.route('/api/news', methods=['GET'])
    def get_user_news_simple():
        """Récupérer les news ciblées pour l'utilisateur connecté"""
        try:
            # Vérifier le token JWT
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': 'Token manquant'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Décoder le token
            import jwt
            import os
            JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '123')
            
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                print(f"🔍 Payload JWT décodé: {payload}")
                print(f"🔍 Clés disponibles dans le payload: {list(payload.keys())}")
                
                # Essayer différentes clés possibles pour l'ID utilisateur
                current_user_id = None
                current_user_email = None
                
                # Essayer toutes les clés possibles d'ID utilisateur
                possible_id_keys = ['userId', 'user_id', 'id', '_id', 'uid', 'user', 'sub']
                for key in possible_id_keys:
                    if key in payload and payload[key]:
                        current_user_id = payload[key]
                        print(f"✅ ID utilisateur trouvé avec la clé '{key}': {current_user_id}")
                        break
                
                if not current_user_id:
                    print(f"❌ Aucune clé userId trouvée dans le payload: {list(payload.keys())}")
                    # Essayer de prendre la première valeur qui ressemble à un ID
                    for key, value in payload.items():
                        if isinstance(value, str) and len(value) == 24:  # Format ObjectId MongoDB
                            current_user_id = value
                            print(f"🔄 Tentative avec la clé '{key}' qui ressemble à un ObjectId: {current_user_id}")
                            break
                    
                    if not current_user_id:
                        return jsonify({'success': False, 'message': f'Token invalide - userId manquant. Clés disponibles: {list(payload.keys())}'}), 401
                
                # Essayer différentes clés possibles pour l'email utilisateur
                possible_email_keys = ['email', 'adresse1', 'mail', 'e_mail', 'userEmail']
                for key in possible_email_keys:
                    if key in payload and payload[key]:
                        current_user_email = payload[key]
                        print(f"✅ Email utilisateur trouvé avec la clé '{key}': {current_user_email}")
                        break
                
                if not current_user_email:
                    current_user_email = 'Inconnue'
                    
                print(f"✅ Utilisateur identifié: ID={current_user_id}, Email={current_user_email}")
                
            except jwt.ExpiredSignatureError:
                return jsonify({'success': False, 'message': 'Token expiré'}), 401
            except jwt.InvalidTokenError as e:
                print(f"❌ Erreur décodage JWT: {e}")
                return jsonify({'success': False, 'message': 'Token invalide'}), 401
            except Exception as e:
                print(f"❌ Erreur inattendue JWT: {e}")
                return jsonify({'success': False, 'message': f'Erreur serveur: {str(e)}'}), 500
            
            print(f"📰 GET_NEWS: Demande pour utilisateur {current_user_email}")
            
            # Récupérer les informations de l'utilisateur
            try:
                # Vérifier que current_user_id est un ObjectId valide
                if isinstance(current_user_id, str) and len(current_user_id) == 24:
                    user_object_id = ObjectId(current_user_id)
                elif isinstance(current_user_id, ObjectId):
                    user_object_id = current_user_id
                else:
                    print(f"❌ Format d'ID utilisateur invalide: {current_user_id} (type: {type(current_user_id)})")
                    return jsonify({'success': False, 'message': f'Format d\'ID utilisateur invalide: {current_user_id}'}), 400
                
                user = db.users.find_one({'_id': user_object_id})
            except Exception as e:
                print(f"❌ Erreur lors de la conversion ObjectId: {e}")
                return jsonify({'success': False, 'message': f'Erreur ID utilisateur: {str(e)}'}), 400
            
            if not user:
                print(f"❌ Utilisateur non trouvé avec l'ID: {current_user_id}")
                return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
            user_location = user.get('location')
            user_department = user.get('department')
            
            print(f"👤 Utilisateur: Location='{user_location}' / Department='{user_department}'")
            
            # Construire la requête de ciblage
            # Une news est visible si :
            # 1. Elle cible la location de l'utilisateur OU targetLocation est null/All/vide
            # 2. Elle cible le département de l'utilisateur OU targetDepartment est null/All/vide
            # 3. isActive n'est pas False
            visibility_query = {
                '$and': [
                    # Condition pour isActive
                    {
                        '$or': [
                            {'isActive': {'$ne': False}},
                            {'isActive': {'$exists': False}},
                            {'isActive': True}
                        ]
                    },
                    # Condition pour targetLocation
                    {
                        '$or': [
                            {'targetLocation': user_location},
                            {'targetLocation': None},
                            {'targetLocation': {'$exists': False}},
                            {'targetLocation': 'All'},
                            {'targetLocation': ''},
                            {'targetLocation': {'$in': [None, '', 'All']}}
                        ]
                    },
                    # Condition pour targetDepartment
                    {
                        '$or': [
                            {'targetDepartment': user_department},
                            {'targetDepartment': None},
                            {'targetDepartment': {'$exists': False}},
                            {'targetDepartment': 'All'},
                            {'targetDepartment': ''},
                            {'targetDepartment': {'$in': [None, '', 'All']}}
                        ]
                    }
                ]
            }
            
            print(f"🔍 Requête de visibilité: {visibility_query}")
            
            # DEBUG: Compter toutes les news avant filtrage
            total_news = db.news.count_documents({})
            print(f"📊 Total des news dans la base: {total_news}")
            
            # DEBUG: Compter les news actives
            active_news = db.news.count_documents({'isActive': {'$ne': False}})
            print(f"📊 News actives: {active_news}")
            
            # Récupérer les news - essayer d'abord sans tri pour voir si le problème vient de là
            try:
                news_cursor = db.news.find(visibility_query).sort('createdAt', -1).limit(50)
                print("📊 Tri par createdAt utilisé")
            except Exception as sort_error:
                print(f"⚠️ Erreur de tri par createdAt: {sort_error}")
                try:
                    news_cursor = db.news.find(visibility_query).sort('_id', -1).limit(50)
                    print("📊 Tri par _id utilisé en fallback")
                except Exception as fallback_error:
                    print(f"⚠️ Erreur de tri par _id: {fallback_error}")
                    news_cursor = db.news.find(visibility_query).limit(50)
                    print("📊 Aucun tri utilisé")
            
            news_list = []
            
            # DEBUG: Compter les résultats de la requête
            news_count_with_filter = db.news.count_documents(visibility_query)
            print(f"📊 News correspondant aux filtres: {news_count_with_filter}")
            
            # DEBUG: Afficher quelques exemples de news dans la base
            sample_news = list(db.news.find({}).limit(3))
            for i, sample in enumerate(sample_news):
                print(f"📄 News {i+1}: title='{sample.get('title', 'N/A')}', targetLocation='{sample.get('targetLocation', 'N/A')}', targetDepartment='{sample.get('targetDepartment', 'N/A')}', isActive={sample.get('isActive', 'N/A')}")
            
            for news_item in news_cursor:
                # Gérer les différents formats de données (ancien et nouveau)
                
                # Gestion de l'image - prendre imageUrl ou construire l'URL depuis imageName
                image_url = None
                base_url = request.host_url.rstrip('/')  # http://192.168.1.15:5000
                
                if news_item.get('imageUrl'):
                    # Si imageUrl existe, vérifier si elle est complète ou relative
                    original_url = news_item.get('imageUrl')
                    if original_url.startswith('http'):
                        # URL complète
                        image_url = original_url
                    else:
                        # URL relative, ajouter le domaine
                        image_url = f"{base_url}{original_url}"
                elif news_item.get('imageName'):
                    # Si seulement imageName existe, construire l'URL complète
                    image_url = f"{base_url}/uploads/news-images/{news_item.get('imageName')}"
                
                # Gestion des photos (format ancien)
                photos = news_item.get('photos', [])
                if image_url and image_url not in photos:
                    photos.append(image_url)
                
                # Date de publication - essayer différents champs
                published_date = None
                if news_item.get('publishedAt'):
                    published_date = news_item['publishedAt']
                elif news_item.get('createdAt'):
                    published_date = news_item['createdAt']
                elif news_item.get('updatedAt'):
                    published_date = news_item['updatedAt']
                
                news_data = {
                    '_id': str(news_item['_id']),
                    'title': news_item.get('title', 'Sans titre'),
                    'description': news_item.get('description', news_item.get('summary', '')),
                    'summary': news_item.get('summary', news_item.get('description', '')),
                    'content': news_item.get('content', ''),
                    'photos': photos,
                    'imageUrl': image_url,
                    'imageName': news_item.get('imageName'),
                    'authorName': news_item.get('authorName', 'Système'),
                    'authorRef': news_item.get('authorRef'),
                    'publishedAt': published_date.isoformat() if published_date else '',
                    'createdAt': news_item.get('createdAt').isoformat() if news_item.get('createdAt') else '',
                    'updatedAt': news_item.get('updatedAt').isoformat() if news_item.get('updatedAt') else '',
                    'priority': news_item.get('priority', 'normal'),
                    'category': news_item.get('category', 'general'),
                    'targetLocation': news_item.get('targetLocation'),
                    'targetDepartment': news_item.get('targetDepartment'),
                    'isActive': news_item.get('isActive', True),
                    'visibility': news_item.get('visibility', {})
                }
                news_list.append(news_data)
                
                # Log détaillé pour comprendre pourquoi cette news est visible
                visibility_reason = []
                if news_item.get('targetLocation') == user_location:
                    visibility_reason.append(f"Location match: {user_location}")
                elif news_item.get('targetLocation') in [None, '', 'All'] or not news_item.get('targetLocation'):
                    visibility_reason.append("Location: globale (visible par tous)")
                
                if news_item.get('targetDepartment') == user_department:
                    visibility_reason.append(f"Department match: {user_department}")
                elif news_item.get('targetDepartment') in [None, '', 'All'] or not news_item.get('targetDepartment'):
                    visibility_reason.append("Department: globale (visible par tous)")
                
                print(f"📰 News ajoutée: {news_data['title']} - Image: {image_url} - Raison: {', '.join(visibility_reason)}")
            
            print(f"✅ {len(news_list)} news trouvées pour l'utilisateur")
            
            return jsonify({
                'success': True,
                'data': news_list,
                'count': len(news_list),
                'userInfo': {
                    'location': user_location,
                    'department': user_department
                }
            }), 200
            
        except Exception as e:
            print(f"❌ Erreur GET_NEWS: {e}")
            return jsonify({'success': False, 'message': f'Erreur serveur: {str(e)}'}), 500

    print("✅ Routes News simplifiées enregistrées")
