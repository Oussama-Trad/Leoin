import AuthService from '../services/AuthService';
import UserService from '../services/UserService';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Contrôleur pour l'authentification
 */
class AuthController {
  
  /**
   * Gérer la connexion d'un utilisateur
   */
  static async handleLogin(adresse1, password) {
    try {
      // Validation des entrées
      if (!adresse1 || !password) {
        return {
          success: false,
          message: 'Adresse1 et mot de passe requis'
        };
      }

      // Validation format adresse1
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(adresse1)) {
        return {
          success: false,
          message: 'Format d\'adresse1 invalide'
        };
      }

      console.log('🔐 AuthController: Tentative de connexion pour', adresse1);
      
      // Appel du service d'authentification
      const result = await AuthService.login(adresse1, password);
      
      if (result.success) {
        console.log('✅ AuthController: Connexion réussie');
        // Le token et les données sont déjà sauvegardés par AuthService
        return {
          success: true,
          user: result.user,
          message: 'Connexion réussie'
        };
      }

      console.log('❌ AuthController: Échec de connexion -', result.message);
      return result;
    } catch (error) {
      console.error('❌ AuthController: Erreur lors de la connexion:', error);
      return {
        success: false,
        message: 'Erreur de connexion. Vérifiez votre réseau.'
      };
    }
  }

  /**
   * Gérer l'inscription d'un utilisateur
   */
  static async handleRegister(userData) {
    try {
      console.log('📝 AuthController: Tentative d\'inscription');
      
      // Validation mot de passe
      if (!userData.password || userData.password.length < 6) {
        return {
          success: false,
          message: 'Le mot de passe doit contenir au moins 6 caractères'
        };
      }

      // Utiliser UserService pour créer l'utilisateur
      const result = await UserService.createUser(userData);
      
      if (result.success) {
        console.log('✅ AuthController: Inscription réussie');
        // Sauvegarder le token si fourni
        if (result.token) {
          await AsyncStorage.setItem('userToken', result.token);
          await AsyncStorage.setItem('userData', JSON.stringify(result.user));
        }
      }

      return result;
    } catch (error) {
      console.error('❌ AuthController: Erreur lors de l\'inscription:', error);
      return {
        success: false,
        message: 'Erreur d\'inscription. Vérifiez votre réseau.'
      };
    }
  }

  /**
   * Gérer la déconnexion
   */
  static async handleLogout() {
    try {
      console.log('🔓 AuthController: Déconnexion en cours');
      
      const result = await AuthService.logout();
      
      if (result.success) {
        console.log('✅ AuthController: Déconnexion réussie');
      }
      
      return result;
    } catch (error) {
      console.error('❌ AuthController: Erreur lors de la déconnexion:', error);
      return {
        success: false,
        message: 'Erreur de déconnexion'
      };
    }
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  static async checkAuthStatus() {
    try {
      return await AuthService.isLoggedIn();
    } catch (error) {
      console.error('❌ AuthController: Erreur vérification auth:', error);
      return false;
    }
  }

  /**
   * Récupérer les données utilisateur stockées
   */
  static async getCurrentUser() {
    try {
      return await AuthService.getUserData();
    } catch (error) {
      console.error('❌ AuthController: Erreur récupération utilisateur:', error);
      return null;
    }
  }

  /**
   * Rafraîchir les données utilisateur depuis le serveur
   */
  static async refreshUserData() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return { success: false, message: 'Non connecté' };
      }

      const result = await UserService.getUserProfile(token);
      
      if (result.success) {
        // Mettre à jour les données stockées
        await AsyncStorage.setItem('userData', JSON.stringify(result.user));
      }

      return result;
    } catch (error) {
      console.error('❌ AuthController: Erreur refresh données:', error);
      return {
        success: false,
        message: 'Erreur de rafraîchissement'
      };
    }
  }

  /**
   * Valider le token actuel
   */
  static async validateToken() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) return false;

      // Tenter de récupérer le profil pour valider le token
      const result = await UserService.getUserProfile(token);
      return result.success;
    } catch (error) {
      console.error('❌ AuthController: Erreur validation token:', error);
      return false;
    }
  }

  /**
   * Déconnecter l'utilisateur
   */
  static async logout() {
    try {
      console.log('🚪 AuthController: Déconnexion en cours...');
      
      // Supprimer toutes les données stockées
      await AsyncStorage.multiRemove([
        'userToken',
        'userData'
      ]);
      
      console.log('✅ AuthController: Déconnexion réussie');
      return { success: true };
    } catch (error) {
      console.error('❌ AuthController: Erreur lors de la déconnexion:', error);
      return {
        success: false,
        message: 'Erreur lors de la déconnexion'
      };
    }
  }

  /**
   * Vérifier si le token contient user_id (nouveau format)
   */
  static async hasValidTokenFormat() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) return false;

      // Décoder le token pour vérifier s'il contient user_id
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.hasOwnProperty('user_id');
    } catch (error) {
      console.error('❌ AuthController: Erreur vérification format token:', error);
      return false;
    }
  }
}

export default AuthController;
