/**
 * NewsService - Service pour gérer les actualités
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import NewsModel from '../models/NewsModel';

const BASE_URL = 'http://192.168.1.15:5000';

class NewsService {
  
  /**
   * Récupérer le token d'authentification
   */
  async getAuthToken() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      return token;
    } catch (error) {
      console.error('❌ Erreur récupération token:', error);
      return null;
    }
  }

  /**
   * Récupérer les actualités filtrées pour l'utilisateur connecté
   */
  async getUserNews() {
    try {
      const token = await this.getAuthToken();
      if (!token) {
        throw new Error('Token d\'authentification manquant');
      }

      console.log('📰 Récupération des actualités filtrées...');

      // Utiliser la nouvelle route filtrée
      const response = await fetch(`${BASE_URL}/api/news/user`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `Erreur ${response.status}`);
      }

      if (result.success) {
        console.log(`✅ ${result.count} actualités filtrées récupérées`);
        console.log(`📍 Filtrage: ${result.userInfo?.department} - ${result.userInfo?.location}`);
        
        return {
          success: true,
          news: result.news || [],
          count: result.count || 0,
          userInfo: result.userInfo
        };
      } else {
        throw new Error(result.message || 'Erreur lors de la récupération des actualités');
      }

    } catch (error) {
      console.error('❌ Erreur NewsService.getUserNews:', error);
      return {
        success: false,
        message: error.message,
        news: []
      };
    }
  }

  /**
   * Créer une nouvelle actualité (admin seulement)
   */
  async createNews(newsData) {
    try {
      const token = await this.getAuthToken();
      if (!token) {
        throw new Error('Token d\'authentification manquant');
      }

      console.log('📝 Création d\'une actualité...');

      const response = await fetch(`${BASE_URL}/api/news`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newsData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `Erreur ${response.status}`);
      }

      if (result.success) {
        console.log('✅ Actualité créée avec succès');
        return {
          success: true,
          newsId: result.newsId,
          message: result.message
        };
      } else {
        throw new Error(result.message || 'Erreur lors de la création');
      }

    } catch (error) {
      console.error('❌ Erreur NewsService.createNews:', error);
      return {
        success: false,
        message: error.message
      };
    }
  }

  /**
   * Mettre à jour une actualité
   */
  async updateNews(newsId, newsData) {
    try {
      const token = await this.getAuthToken();
      if (!token) {
        throw new Error('Token d\'authentification manquant');
      }

      console.log(`📝 Mise à jour de l'actualité ${newsId}...`);

      const response = await fetch(`${BASE_URL}/api/news/${newsId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newsData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `Erreur ${response.status}`);
      }

      if (result.success) {
        console.log('✅ Actualité mise à jour avec succès');
        return {
          success: true,
          message: result.message
        };
      } else {
        throw new Error(result.message || 'Erreur lors de la mise à jour');
      }

    } catch (error) {
      console.error('❌ Erreur NewsService.updateNews:', error);
      return {
        success: false,
        message: error.message
      };
    }
  }

  /**
   * Supprimer une actualité
   */
  async deleteNews(newsId) {
    try {
      const token = await this.getAuthToken();
      if (!token) {
        throw new Error('Token d\'authentification manquant');
      }

      console.log(`🗑️ Suppression de l'actualité ${newsId}...`);

      const response = await fetch(`${BASE_URL}/api/news/${newsId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `Erreur ${response.status}`);
      }

      if (result.success) {
        console.log('✅ Actualité supprimée avec succès');
        return {
          success: true,
          message: result.message
        };
      } else {
        throw new Error(result.message || 'Erreur lors de la suppression');
      }

    } catch (error) {
      console.error('❌ Erreur NewsService.deleteNews:', error);
      return {
        success: false,
        message: error.message
      };
    }
  }
}

export default new NewsService();
