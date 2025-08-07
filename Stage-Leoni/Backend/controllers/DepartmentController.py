#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contrôleur pour les départements
"""

from flask import jsonify, request
from models.Department import Department

class DepartmentController:
    def __init__(self):
        self.department_model = Department()
    
    def get_all_departments(self):
        """Récupérer tous les départements"""
        try:
            print("🔍 CONTROLLER_DEPARTMENTS: Récupération de tous les départements", flush=True)
            
            result = self.department_model.find_all(active_only=True)
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: {result['count']} départements trouvés", flush=True)
                return jsonify({
                    'success': True,
                    'departments': result['departments'],
                    'count': result['count']
                }), 200
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message'],
                    'departments': [],
                    'count': 0
                }), 500
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la récupération des départements',
                'error': str(e),
                'departments': [],
                'count': 0
            }), 500
        finally:
            self.department_model.close_connection()
    
    def get_departments_by_location(self, location_id):
        """Récupérer les départements par location"""
        try:
            print(f"🔍 CONTROLLER_DEPARTMENTS: Récupération des départements pour location {location_id}", flush=True)
            
            result = self.department_model.find_by_location(location_id)
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: {result['count']} départements trouvés pour la location", flush=True)
                return jsonify({
                    'success': True,
                    'departments': result['departments'],
                    'count': result['count'],
                    'location_id': location_id
                }), 200
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message'],
                    'departments': [],
                    'count': 0,
                    'location_id': location_id
                }), 500
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la récupération des départements',
                'error': str(e),
                'departments': [],
                'count': 0,
                'location_id': location_id
            }), 500
        finally:
            self.department_model.close_connection()
    
    def get_department_by_id(self, department_id):
        """Récupérer un département par ID"""
        try:
            print(f"🔍 CONTROLLER_DEPARTMENTS: Récupération du département {department_id}", flush=True)
            
            result = self.department_model.find_by_id(department_id)
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: Département trouvé", flush=True)
                return jsonify({
                    'success': True,
                    'department': result['department']
                }), 200
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 404
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la récupération du département',
                'error': str(e)
            }), 500
        finally:
            self.department_model.close_connection()
    
    def create_department(self):
        """Créer un nouveau département"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Le nom du département est requis'
                }), 400
            
            print(f"🔍 CONTROLLER_DEPARTMENTS: Création du département {data['name']}", flush=True)
            
            result = self.department_model.create(
                name=data['name'],
                description=data.get('description'),
                location_ref=data.get('locationRef'),
                active=data.get('active', True)
            )
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: Département créé avec ID {result['department_id']}", flush=True)
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'department_id': result['department_id']
                }), 201
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 500
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la création du département',
                'error': str(e)
            }), 500
        finally:
            self.department_model.close_connection()
    
    def update_department(self, department_id):
        """Mettre à jour un département"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Aucune donnée fournie'
                }), 400
            
            print(f"🔍 CONTROLLER_DEPARTMENTS: Mise à jour du département {department_id}", flush=True)
            
            result = self.department_model.update(
                department_id=department_id,
                name=data.get('name'),
                description=data.get('description'),
                location_ref=data.get('locationRef'),
                active=data.get('active')
            )
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: Département mis à jour", flush=True)
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 404 if 'non trouvé' in result['message'] else 500
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la mise à jour du département',
                'error': str(e)
            }), 500
        finally:
            self.department_model.close_connection()
    
    def delete_department(self, department_id):
        """Supprimer un département"""
        try:
            print(f"🔍 CONTROLLER_DEPARTMENTS: Suppression du département {department_id}", flush=True)
            
            result = self.department_model.delete(department_id)
            
            if result['success']:
                print(f"✅ CONTROLLER_DEPARTMENTS: Département supprimé", flush=True)
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                print(f"❌ CONTROLLER_DEPARTMENTS: {result['message']}", flush=True)
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 404 if 'non trouvé' in result['message'] else 500
                
        except Exception as e:
            print(f"❌ CONTROLLER_DEPARTMENTS: Exception = {str(e)}", flush=True)
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la suppression du département',
                'error': str(e)
            }), 500
        finally:
            self.department_model.close_connection()
