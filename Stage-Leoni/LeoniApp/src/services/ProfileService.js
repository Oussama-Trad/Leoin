import UserService from './UserService';
import ProfileModel from '../models/ProfileModel';

/**
 * Service spécialisé pour la gestion des profils
 */
class ProfileService {
  
  /**
   * Obtenir le profil complet d'un utilisateur
   */
  static async getProfile(token) {
    try {
      const result = await UserService.getUserProfile(token);
      
      if (result.success && result.user) {
        // Convertir en ProfileModel pour avoir les méthodes spécifiques au profil
        const profileData = ProfileModel.fromUserData(result.user);
        return {
          success: true,
          profile: profileData
        };
      }

      return result;
    } catch (error) {
      console.error('Erreur récupération profil:', error);
      return {
        success: false,
        message: 'Erreur de récupération du profil'
      };
    }
  }

  /**
   * Mettre à jour les informations du profil
   */
  static async updateProfile(token, profileData) {
    try {
      // Valider les données du profil
      const validation = ProfileModel.validate(profileData);
      if (!validation.isValid) {
        return {
          success: false,
          message: validation.errors.join(', ')
        };
      }

      // Utiliser UserService pour la mise à jour
      const result = await UserService.updateProfile(token, profileData);
      
      if (result.success && result.user) {
        const profileData = ProfileModel.fromUserData(result.user);
        return {
          success: true,
          profile: profileData
        };
      }

      return result;
    } catch (error) {
      console.error('Erreur mise à jour profil:', error);
      return {
        success: false,
        message: 'Erreur de mise à jour du profil'
      };
    }
  }

  /**
   * Uploader une photo de profil
   */
  static async uploadProfilePhoto(token, imageData) {
    try {
      return await UserService.uploadProfilePicture(token, imageData);
    } catch (error) {
      console.error('Erreur upload photo profil:', error);
      return {
        success: false,
        message: 'Erreur d\'upload de la photo'
      };
    }
  }

  /**
   * Vérifier si le profil est complet
   */
  static isProfileComplete(profileData) {
    const profile = new ProfileModel(profileData);
    return profile.isComplete();
  }

  /**
   * Obtenir le pourcentage de complétion du profil
   */
  static getProfileCompletionPercentage(profileData) {
    const profile = new ProfileModel(profileData);
    return profile.getCompletionPercentage();
  }

  /**
   * Obtenir les champs manquants du profil
   */
  static getMissingProfileFields(profileData) {
    const profile = new ProfileModel(profileData);
    return profile.getMissingFields();
  }

  /**
   * Formater les données du profil pour l'affichage
   */
  static formatProfileForDisplay(profileData) {
    const profile = new ProfileModel(profileData);
    return profile.getDisplayData();
  }
}

export default ProfileService;
