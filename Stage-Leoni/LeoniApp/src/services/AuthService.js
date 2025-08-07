import AsyncStorage from '@react-native-async-storage/async-storage';
import NetworkService from './NetworkService';

class AuthService {
  // Vérifier si l'utilisateur est connecté
  static async isLoggedIn() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userData = await AsyncStorage.getItem('userData');
      
      if (!token || !userData) {
        return false;
      }
      
      // Vérifier si le token est encore valide
      const isValid = await this.validateToken(token);
      if (!isValid) {
        await this.logout();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Erreur vérification connexion:', error);
      return false;
    }
  }
  
  // Valider le token avec le serveur
  static async validateToken(token) {
    try {
      const response = await NetworkService.fetch('/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      return response.ok;
    } catch (error) {
      console.error('Erreur validation token:', error);
      // En cas d'erreur réseau, considérer le token comme valide localement
      // pour permettre l'utilisation hors ligne
      if (error.message.includes('fetch') || error.message.includes('Network')) {
        console.log('Mode hors ligne détecté, token considéré comme valide');
        return true;
      }
      return false;
    }
  }
  
  // Récupérer les données utilisateur
  static async getUserData() {
    try {
      const userData = await AsyncStorage.getItem('userData');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Erreur récupération données utilisateur:', error);
      return null;
    }
  }
  
  // Récupérer le token
  static async getToken() {
    try {
      return await AsyncStorage.getItem('userToken');
    } catch (error) {
      console.error('Erreur récupération token:', error);
      return null;
    }
  }
  
  // Sauvegarder les données de connexion
  static async saveAuthData(token, userData) {
    try {
      // Récupérer les données existantes pour préserver les modifications
      const existingData = await AsyncStorage.getItem('userData');
      let existingUserData = {};

      if (existingData) {
        existingUserData = JSON.parse(existingData);
        console.log('🔍 AUTH: Données existantes trouvées:', existingUserData);
      }

      // Fusionner les nouvelles données avec les existantes (préserver les modifications)
      const completeUserData = {
        // Données de base du serveur
        ...userData,
        // Compléter avec les valeurs par défaut si manquantes
        phoneNumber: userData.phoneNumber || existingUserData.phoneNumber || '12345678',
        adresse2: userData.adresse2 || existingUserData.adresse2 || 'aa@gmail.com',
        parentalPhoneNumber: userData.parentalPhoneNumber || existingUserData.parentalPhoneNumber || '12345899',
        // Pour le département, utiliser en priorité la valeur du serveur, puis existante, puis par défaut
        department: userData.department || existingUserData.department || 'Non spécifié',
        position: userData.position || existingUserData.position || 'Non spécifié',
        address: userData.address || existingUserData.address || '',
        // Préserver la photo de profil existante si pas de nouvelle
        profilePicture: userData.profilePicture || existingUserData.profilePicture || null
      };

      await AsyncStorage.setItem('userToken', token);
      await AsyncStorage.setItem('userData', JSON.stringify(completeUserData));
      console.log('✅ AUTH: Données complètes sauvegardées (avec préservation):', completeUserData);
      return true;
    } catch (error) {
      console.error('Erreur sauvegarde données auth:', error);
      return false;
    }
  }
  
  // Déconnexion
  static async logout() {
    try {
      await AsyncStorage.multiRemove(['userToken', 'userData']);
      return true;
    } catch (error) {
      console.error('Erreur déconnexion:', error);
      return false;
    }
  }
  
  // Connexion
  static async login(adresse1, password) {
    try {
      const response = await NetworkService.fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          adresse1: adresse1.trim().toLowerCase(),
          password: password
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        await this.saveAuthData(data.token, data.user);
        return { success: true, user: data.user, token: data.token };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error('Erreur connexion:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
  
  // Demande de réinitialisation de mot de passe
  static async requestPasswordReset(email) {
    try {
      const response = await NetworkService.fetch('/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email.trim().toLowerCase() })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur demande reset password:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
  
  // Réinitialisation de mot de passe avec token
  static async resetPassword(token, newPassword) {
    try {
      const response = await NetworkService.fetch('/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, newPassword })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur reset password:', error);
      return { success: false, message: 'Erreur de connexion' };
    }
  }
}

export default AuthService;
