import { BASE_URL } from '../config';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Test de connectivité au serveur
const testServerConnection = async (url) => {
  try {
    console.log(`🔍 API SERVICE: Test de connectivité vers ${url}/health...`);
    const response = await fetch(`${url}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 3000,
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ API SERVICE: Serveur connecté sur ${url}:`, data);
      return true;
    } else {
      console.log(`❌ API SERVICE: Serveur non accessible sur ${url} (status: ${response.status})`);
      return false;
    }
  } catch (error) {
    console.log(`❌ API SERVICE: Erreur de connexion vers ${url}:`, error.message);
    return false;
  }
};

// Variable globale pour l'URL de base avec détection automatique
let currentBaseURL = BASE_URL;

// Essayer plusieurs URLs pour trouver le serveur
const findWorkingServer = async () => {
  const urls = [
    'http://localhost:5000',
    'http://127.0.0.1:5000'
  ];

  console.log('🔍 API SERVICE: Recherche du serveur actif...');
  
  for (const url of urls) {
    const isWorking = await testServerConnection(url);
    if (isWorking) {
      console.log(`✅ API SERVICE: Serveur trouvé! Utilisation de: ${url}`);
      currentBaseURL = url;
      return url;
    }
  }
  
  console.log('❌ API SERVICE: Aucun serveur trouvé!');
  return null;
};

export const fetchFromAPI = async (endpoint, options = {}) => {
  const maxRetries = 2;
  let lastError = null;

  for (let retry = 0; retry <= maxRetries; retry++) {
    try {
      // Si c'est le premier échec, essayer de trouver un serveur qui fonctionne
      if (retry === 1) {
        console.log('🔄 API SERVICE: Tentative de reconnexion...');
        const workingServer = await findWorkingServer();
        if (!workingServer) {
          throw new Error('Aucun serveur backend accessible');
        }
      }

      // Récupérer le token d'authentification
      const token = await AsyncStorage.getItem('userToken');
      
      console.log(`🌐 API Call (tentative ${retry + 1}): ${endpoint}`, {
        url: `${currentBaseURL}${endpoint}`,
        method: options.method || 'GET',
        hasToken: !!token,
        tokenPreview: token ? token.substring(0, 20) + '...' : 'No token'
      });

      const response = await fetch(`${currentBaseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Origin': 'http://localhost:8088',
          ...(token && { 'Authorization': `Bearer ${token}` }),
          ...options.headers
        },
      });

      console.log(`📊 Response: ${endpoint}`, {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        let errorData = {};
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { message: await response.text() };
        }
        console.error(`❌ API Error: ${endpoint}`, errorData);
        const error = new Error(errorData.message || `HTTP error! status: ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      const data = await response.json();
      console.log(`✅ API Success: ${endpoint}`, data);
      return data;

    } catch (error) {
      lastError = error;
      console.error(`💥 API call failed (tentative ${retry + 1}/${maxRetries + 1}):`, {
        endpoint,
        error: error.message,
        status: error.status,
        data: error.data,
        name: error.name,
        currentURL: currentBaseURL
      });

      if (retry === maxRetries) {
        break;
      }
      
      // Attendre un peu avant de réessayer
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  throw lastError;
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
  // Récupérer les départements disponibles pour chat
  getDepartments: async () => {
    return await fetchFromAPI('/api/departments');
  },

  // Récupérer les services disponibles (legacy)
  getServices: async () => {
    return await fetchFromAPI('/api/services');
  },

  // Récupérer toutes les conversations de l'utilisateur
  getChats: async () => {
    return await fetchFromAPI('/api/chats');
  },

  // Créer une nouvelle conversation avec un département
  createChatWithDepartment: async (targetDepartment, targetLocation, subject, priority = 'normal') => {
    return await fetchFromAPI('/api/chats/department', {
      method: 'POST',
      body: JSON.stringify({
        department: targetDepartment,
        location: targetLocation,
        initialMessage: subject,
        priority
      })
    });
  },

  // Créer une nouvelle conversation (legacy)
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
    return await fetchFromAPI(`/api/chat/conversation/${chatId}/messages`);
  },

  // Envoyer un message
  sendMessage: async (chatId, content) => {
    return await fetchFromAPI(`/api/chat/conversation/${chatId}/message`, {
      method: 'POST',
      body: JSON.stringify({ content })
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