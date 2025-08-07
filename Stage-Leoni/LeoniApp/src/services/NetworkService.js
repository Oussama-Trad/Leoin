import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Service centralisé pour la détection automatique d'IP
class NetworkService {
  static workingURL = null;
  static isDetecting = false;

  // Fonction pour détecter automatiquement l'IP du PC
  static detectPCIP() {
    try {
      // Si on est sur le web, utiliser localhost
      if (Platform.OS === 'web') {
        return 'localhost';
      }

      // Essayer de récupérer l'IP depuis les constantes Expo
      if (Constants.manifest?.debuggerHost) {
        const ip = Constants.manifest.debuggerHost.split(':')[0];
        console.log('🔍 NETWORK: IP détectée depuis Expo debuggerHost:', ip);
        return ip;
      }

      if (Constants.manifest?.hostUri) {
        const ip = Constants.manifest.hostUri.split(':')[0];
        console.log('🔍 NETWORK: IP détectée depuis Expo hostUri:', ip);
        return ip;
      }

      // Expo SDK 49+
      if (Constants.expoConfig?.hostUri) {
        const ip = Constants.expoConfig.hostUri.split(':')[0];
        console.log('🔍 NETWORK: IP détectée depuis Expo expoConfig:', ip);
        return ip;
      }

      console.log('🔍 NETWORK: Impossible de détecter l\'IP automatiquement');
      return null;
    } catch (error) {
      console.log('🔍 NETWORK: Erreur détection IP:', error.message);
      return null;
    }
  }

  // Fonction pour tester la connectivité
  static async testConnection(ip) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      
      const response = await fetch(`http://${ip}:5000/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Fonction principale pour trouver l'URL qui fonctionne
  static async findWorkingURL() {
    // Si on a déjà une URL qui fonctionne et qu'on n'est pas en train de détecter
    if (this.workingURL && !this.isDetecting) {
      return this.workingURL;
    }

    // Éviter les détections multiples simultanées
    if (this.isDetecting) {
      // Attendre que la détection en cours se termine
      let attempts = 0;
      while (this.isDetecting && attempts < 50) {
        await new Promise(resolve => setTimeout(resolve, 100));
        attempts++;
      }
      return this.workingURL;
    }

    this.isDetecting = true;
    console.log('🔍 NETWORK: Recherche de l\'URL du serveur...');

    try {
      // 1. Essayer l'IP détectée automatiquement
      const detectedIP = this.detectPCIP();
      if (detectedIP) {
        console.log(`🔍 NETWORK: Test de l'IP détectée: ${detectedIP}...`);
        const works = await this.testConnection(detectedIP);
        if (works) {
          console.log(`✅ NETWORK: Serveur trouvé sur l'IP détectée: ${detectedIP}`);
          this.workingURL = `http://${detectedIP}:5000`;
          await AsyncStorage.setItem('lastWorkingIP', detectedIP);
          return this.workingURL;
        }
      }

      // 2. Essayer la dernière IP qui a fonctionné
      try {
        const lastWorkingIP = await AsyncStorage.getItem('lastWorkingIP');
        if (lastWorkingIP) {
          console.log(`🔍 NETWORK: Test de la dernière IP: ${lastWorkingIP}...`);
          const works = await this.testConnection(lastWorkingIP);
          if (works) {
            console.log(`✅ NETWORK: Serveur trouvé sur la dernière IP: ${lastWorkingIP}`);
            this.workingURL = `http://${lastWorkingIP}:5000`;
            return this.workingURL;
          }
        }
      } catch (error) {
        console.log('🔍 NETWORK: Impossible de récupérer la dernière IP');
      }

      // 3. Tester une liste d'IPs communes
      const commonIPs = [
        'localhost',
        '127.0.0.1',
        '10.0.2.2', // Émulateur Android
        '192.168.1.15', // IP actuelle du serveur
        '192.168.1.16', // Votre ancienne IP
        '192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4', '192.168.0.5',
        '192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5',
        '10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4', '10.0.0.5'
      ];

      for (const ip of commonIPs) {
        console.log(`🔍 NETWORK: Test de ${ip}...`);
        const works = await this.testConnection(ip);
        if (works) {
          console.log(`✅ NETWORK: Serveur trouvé sur ${ip}`);
          this.workingURL = `http://${ip}:5000`;
          await AsyncStorage.setItem('lastWorkingIP', ip);
          return this.workingURL;
        }
      }

      console.log('❌ NETWORK: Aucun serveur trouvé');
      return null;

    } finally {
      this.isDetecting = false;
    }
  }

  // Fonction pour réinitialiser la détection (utile si le serveur change)
  static resetDetection() {
    this.workingURL = null;
    this.isDetecting = false;
  }

  // Fonction pour forcer une nouvelle détection et vider le cache
  static async forceRedetection() {
    console.log('🔄 NETWORK: Forcer une nouvelle détection...');
    this.workingURL = null;
    this.isDetecting = false;
    
    // Supprimer l'IP mise en cache
    try {
      await AsyncStorage.removeItem('lastWorkingIP');
      console.log('🗑️ NETWORK: Cache IP supprimé');
    } catch (error) {
      console.log('⚠️ NETWORK: Erreur suppression cache:', error);
    }
    
    // Forcer une nouvelle détection
    return await this.findWorkingURL();
  }

  // Fonction pour faire une requête avec détection automatique d'URL
  static async fetch(endpoint, options = {}) {
    const baseURL = await this.findWorkingURL();
    
    if (!baseURL) {
      console.error('❌ NETWORK: Aucun serveur backend accessible. Vérifiez que le serveur est démarré.');
      throw new Error('Aucun serveur backend accessible. Vérifiez que le serveur est démarré.');
    }

    const url = `${baseURL}${endpoint}`;
    console.log(`🔍 NETWORK: Requête vers ${url}`);
    console.log(`🔍 NETWORK: URL de base détectée: ${baseURL}`);
    
    return fetch(url, options);
  }
}

export default NetworkService;
