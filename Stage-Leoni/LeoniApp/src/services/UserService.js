import { BASE_URL } from '../config';
import UserModel from '../models/UserModel';

/**
 * Service pour la gestion des utilisateurs
 */
class UserService {
  
  /**
   * Créer un nouvel utilisateur (inscription)
   */
  static async createUser(userData) {
    try {
      // Valider les données avec le modèle
      const validation = UserModel.validate(userData);
      if (!validation.isValid) {
        return {
          success: false,
          message: validation.errors.join(', ')
        };
      }

      const userModel = new UserModel(userData);
      const response = await fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...userModel.toApiObject(),
          password: userData.password,
          confirmPassword: userData.confirmPassword
        })
      });

      const data = await response.json();
      
      if (data.success && data.user) {
        data.user = UserModel.fromApiResponse(data.user);
      }

      return data;
    } catch (error) {
      console.error('Erreur création utilisateur:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }

  /**
   * Obtenir les informations d'un utilisateur
   */
  static async getUserProfile(token) {
    try {
      const response = await fetch(`${BASE_URL}/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success && data.user) {
        data.user = UserModel.fromApiResponse(data.user);
      }

      return data;
    } catch (error) {
      console.error('Erreur récupération profil:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }

  /**
   * Mettre à jour le profil utilisateur
   */
  static async updateProfile(token, userData) {
    try {
      // Valider les données avec le modèle
      const validation = UserModel.validate(userData);
      if (!validation.isValid) {
        return {
          success: false,
          message: validation.errors.join(', ')
        };
      }

      const userModel = new UserModel(userData);
      const response = await fetch(`${BASE_URL}/update-profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userModel.toApiObject())
      });

      const data = await response.json();
      
      if (data.success && data.user) {
        data.user = UserModel.fromApiResponse(data.user);
      }

      return data;
    } catch (error) {
      console.error('Erreur mise à jour profil:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }

  /**
   * Uploader une photo de profil
   */
  static async uploadProfilePicture(token, imageData) {
    try {
      if (!imageData || !imageData.startsWith('data:image/')) {
        return {
          success: false,
          message: 'Image invalide'
        };
      }

      const response = await fetch(`${BASE_URL}/upload-profile-picture`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageData })
      });

      return await response.json();
    } catch (error) {
      console.error('Erreur upload photo:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }
}

export default UserService;
