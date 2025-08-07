import { BASE_URL } from '../config';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const fetchFromAPI = async (endpoint, options = {}) => {
  try {
    // Récupérer le token d'authentification
    const token = await AsyncStorage.getItem('userToken');
    
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      },
    });

    if (!response.ok) {
      let errorData = {};
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: await response.text() };
      }
      const error = new Error(errorData.message || `HTTP error! status: ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', {
      endpoint,
      error: error.message,
      status: error.status,
      data: error.data
    });
    throw error;
  }
};

// ========================================
// API NEWS
// ========================================

export const newsAPI = {
  // Récupérer toutes les actualités pour l'utilisateur
  getNews: async () => {
    return await fetchFromAPI('/api/news');
  },

  // Récupérer le détail d'une actualité
  getNewsDetail: async (newsId) => {
    return await fetchFromAPI(`/api/news/${newsId}`);
  },

  // Marquer une actualité comme vue
  markAsViewed: async (newsId) => {
    return await fetchFromAPI(`/api/news/${newsId}/view`, {
      method: 'POST'
    });
  },

  // Liker/déliker une actualité
  toggleLike: async (newsId) => {
    return await fetchFromAPI(`/api/news/${newsId}/like`, {
      method: 'POST'
    });
  },

  // Ajouter un commentaire
  addComment: async (newsId, text) => {
    return await fetchFromAPI(`/api/news/${newsId}/comment`, {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  },

  // Récupérer les commentaires
  getComments: async (newsId) => {
    return await fetchFromAPI(`/api/news/${newsId}/comments`);
  }
};

// ========================================
// API CHAT
// ========================================

export const chatAPI = {
  // Récupérer les services disponibles
  getServices: async () => {
    return await fetchFromAPI('/api/services');
  },

  // Récupérer toutes les conversations de l'utilisateur
  getChats: async () => {
    return await fetchFromAPI('/api/chats');
  },

  // Créer une nouvelle conversation
  createChat: async (serviceId, subject, priority = 'normal') => {
    return await fetchFromAPI('/api/chats', {
      method: 'POST',
      body: JSON.stringify({
        serviceId,
        subject,
        priority
      })
    });
  },

  // Récupérer le détail d'une conversation
  getChatDetail: async (chatId) => {
    return await fetchFromAPI(`/api/chats/${chatId}`);
  },

  // Récupérer les messages d'une conversation
  getChatMessages: async (chatId) => {
    return await fetchFromAPI(`/api/chats/${chatId}/messages`);
  },

  // Envoyer un message
  sendMessage: async (chatId, text) => {
    return await fetchFromAPI(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  },

  // Fermer une conversation
  closeChat: async (chatId) => {
    return await fetchFromAPI(`/api/chats/${chatId}/close`, {
      method: 'PUT'
    });
  },

  // Évaluer une conversation
  rateChat: async (chatId, score, feedback = '') => {
    return await fetchFromAPI(`/api/chats/${chatId}/rate`, {
      method: 'POST',
      body: JSON.stringify({
        score,
        feedback
      })
    });
  }
};

// ========================================
// API LEGACY (Maintenir la compatibilité)
// ========================================

// Garder les fonctions existantes pour la compatibilité
export const testConnection = async () => {
  return await fetchFromAPI('/test');
};

export const loginUser = async (credentials) => {
  return await fetchFromAPI('/login', {
    method: 'POST',
    body: JSON.stringify(credentials)
  });
};

export const registerUser = async (userData) => {
  return await fetchFromAPI('/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  });
};