import AsyncStorage from '@react-native-async-storage/async-storage';

class AppController {
  constructor() {
    // Remplacez par votre IP locale pour le développement
    // Pour obtenir votre IP: ipconfig (Windows) ou ifconfig (Mac/Linux)
    this.apiBaseUrl = 'http://192.168.1.100:5000'; // Remplacez par votre IP
    // Alternative: this.apiBaseUrl = 'http://localhost:5000'; // Pour émulateur Android
  }

  // Méthode pour tester la connexion au serveur
  async testConnection() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 secondes timeout
      
      const response = await fetch(`${this.apiBaseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Test de connexion réussi:', result);
      return result;
    } catch (error) {
      console.error('Erreur de test de connexion:', error);
      if (error.name === 'AbortError') {
        return { success: false, message: 'Timeout - Impossible de se connecter au serveur' };
      }
      return { success: false, message: 'Impossible de se connecter au serveur: ' + error.message };
    }
  }

  async login(email, password) {
    try {
      // Tester la connexion d'abord
      const healthCheck = await this.testConnection();
      if (!healthCheck.success) {
        return { success: false, message: 'Serveur inaccessible. Vérifiez que le backend est démarré.' };
      }

      console.log('Tentative de connexion avec:', { email: email.trim(), passwordLength: password.length });
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 secondes timeout

      const response = await fetch(`${this.apiBaseUrl}/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          email: email.trim().toLowerCase(), 
          password: password 
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const result = await response.json();
      
      console.log('Réponse du serveur:', { 
        status: response.status, 
        success: result.success,
        message: result.message 
      });
      
      if (result.success) {
        console.log('Connexion réussie:', result.user);
        // Stocker le token avec la clé 'userToken'
        await AsyncStorage.setItem('userToken', result.token);
        await AsyncStorage.setItem('userData', JSON.stringify(result.user));
      } else {
        console.error('Erreur de connexion:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau login:', error);
      if (error.name === 'AbortError') {
        return { success: false, message: 'Timeout - Vérifiez votre connexion' };
      }
      return { 
        success: false, 
        message: 'Erreur réseau. Vérifiez votre connexion et que le serveur est démarré.' 
      };
    }
  }

  async register(userData) {
    try {
      // Tester la connexion d'abord
      const healthCheck = await this.testConnection();
      if (!healthCheck.success) {
        return { success: false, message: 'Serveur inaccessible. Vérifiez que le backend est démarré.' };
      }

      // Nettoyer les données avant l'envoi
      const cleanedData = {
        firstName: userData.firstName.trim(),
        lastName: userData.lastName.trim(),
        email: userData.email.trim().toLowerCase(),
        parentalEmail: userData.parentalEmail.trim().toLowerCase(),
        phoneNumber: userData.phoneNumber.trim(),
        parentalPhoneNumber: userData.parentalPhoneNumber.trim(),
        password: userData.password,
        confirmPassword: userData.confirmPassword,
      };

      console.log('Données d\'inscription envoyées:', {
        ...cleanedData,
        password: '[MASQUÉ]',
        confirmPassword: '[MASQUÉ]'
      });

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.apiBaseUrl}/register`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(cleanedData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const result = await response.json();
      
      if (result.success) {
        console.log('Inscription réussie:', result.user);
        // Stocker automatiquement le token après inscription
        await AsyncStorage.setItem('userToken', result.token);
        await AsyncStorage.setItem('userData', JSON.stringify(result.user));
      } else {
        console.error('Erreur d\'inscription:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau register:', error);
      if (error.name === 'AbortError') {
        return { success: false, message: 'Timeout - Vérifiez votre connexion' };
      }
      return { 
        success: false, 
        message: 'Erreur réseau. Vérifiez votre connexion et que le serveur est démarré.' 
      };
    }
  }

  async submitDocumentRequest(token, requestData) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.apiBaseUrl}/document-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const result = await response.json();
      
      if (result.success) {
        console.log('Demande de document soumise:', result.request);
      } else {
        console.error('Erreur de soumission:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau submitDocumentRequest:', error);
      if (error.name === 'AbortError') {
        return { success: false, message: 'Timeout lors de la soumission' };
      }
      return { 
        success: false, 
        message: 'Erreur réseau lors de la soumission de la demande.' 
      };
    }
  }

  async getDocumentRequests(token) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.apiBaseUrl}/document-requests`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      const result = await response.json();
      
      if (result.success) {
        console.log('Demandes récupérées:', result.requests.length);
      } else {
        console.error('Erreur de récupération:', result.message);
      }
      
      return result;
    } catch (error) {
      console.error('Erreur réseau getDocumentRequests:', error);
      if (error.name === 'AbortError') {
        return { success: false, message: 'Timeout lors de la récupération' };
      }
      return { 
        success: false, 
        message: 'Erreur réseau lors de la récupération des demandes.' 
      };
    }
  }

  async logout() {
    try {
      // Nettoyer le token localement
      await AsyncStorage.multiRemove(['userToken', 'userData']);
      
      console.log('Déconnexion effectuée');
      return { success: true, message: 'Déconnexion réussie' };
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      return { success: false, message: 'Erreur lors de la déconnexion' };
    }
  }

  async getProfile() {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.apiBaseUrl}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || 'Une erreur est survenue');
      }
      return data;
    } catch (error) {
      console.error('Erreur getProfile:', error);
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (!token) throw new Error('Aucun token trouvé');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${this.apiBaseUrl}/update-profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(profileData),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || 'Une erreur est survenue');
      }
      
      // Mettre à jour les données locales
      await AsyncStorage.setItem('userData', JSON.stringify(data.user));
      
      return data;
    } catch (error) {
      console.error('Erreur updateProfile:', error);
      throw error;
    }
  }

  // Méthode utilitaire pour obtenir l'IP locale
  getLocalIP() {
    return `
Pour React Native, vous devez remplacer 'localhost' par l'IP de votre machine:
1. Ouvrez un terminal/invite de commande
2. Tapez: ipconfig (Windows) ou ifconfig (Mac/Linux)
3. Trouvez votre adresse IP locale (ex: 192.168.1.100)
4. Remplacez l'IP dans apiBaseUrl: this.apiBaseUrl = 'http://VOTRE_IP:5000'

Exemple: this.apiBaseUrl = 'http://192.168.1.100:5000'

Pour le web/émulateur Android, utilisez: http://localhost:5000
Pour émulateur iOS, utilisez: http://localhost:5000
    `;
  }
}

export default AppController;