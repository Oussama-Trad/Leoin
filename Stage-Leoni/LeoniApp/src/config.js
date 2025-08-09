import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Liste des IPs possibles à tester (localhost uniquement)
const POSSIBLE_IPS = [
  'localhost',
  '127.0.0.1'
];

// Fonction pour tester la connectivité
const testConnection = async (ip) => {
  try {
    const response = await fetch(`http://${ip}:5000/health`, {
      method: 'GET',
      timeout: 2000
    });
    return response.ok;
  } catch (error) {
    return false;
  }
};

// Fonction pour détecter automatiquement l'IP du PC
const detectPCIP = () => {
  try {
    // Si on est sur le web, utiliser localhost
    if (Platform.OS === 'web') {
      return 'localhost';
    }

    // Essayer de récupérer l'IP depuis les constantes Expo
    if (Constants.manifest?.debuggerHost) {
      const ip = Constants.manifest.debuggerHost.split(':')[0];
      console.log('🔍 CONFIG: IP détectée depuis Expo debuggerHost:', ip);
      return ip;
    }

    if (Constants.manifest?.hostUri) {
      const ip = Constants.manifest.hostUri.split(':')[0];
      console.log('🔍 CONFIG: IP détectée depuis Expo hostUri:', ip);
      return ip;
    }

    // Expo SDK 49+
    if (Constants.expoConfig?.hostUri) {
      const ip = Constants.expoConfig.hostUri.split(':')[0];
      console.log('🔍 CONFIG: IP détectée depuis Expo expoConfig:', ip);
      return ip;
    }

    console.log('🔍 CONFIG: Impossible de détecter l\'IP automatiquement');
    return null;
  } catch (error) {
    console.log('🔍 CONFIG: Erreur détection IP:', error.message);
    return null;
  }
};

// Détection automatique de l'environnement
const getBaseURL = () => {
  // Toujours utiliser localhost
  console.log('✅ CONFIG: Utilisation de localhost par défaut');
  return 'http://localhost:5000';
};

export const BASE_URL = 'http://localhost:5000';

// Fonction pour trouver automatiquement la bonne IP
export const findWorkingIP = async () => {
  console.log('🔍 CONFIG: Test de connectivité localhost...');

  // Tester localhost en premier
  console.log(`🔍 CONFIG: Test de localhost...`);
  const works = await testConnection('localhost');
  if (works) {
    console.log(`✅ CONFIG: Serveur trouvé sur localhost`);
    await AsyncStorage.setItem('lastWorkingIP', 'localhost');
    return 'http://localhost:5000';
  }

  // Tester 127.0.0.1 en backup
  console.log(`🔍 CONFIG: Test de 127.0.0.1...`);
  const works2 = await testConnection('127.0.0.1');
  if (works2) {
    console.log(`✅ CONFIG: Serveur trouvé sur 127.0.0.1`);
    await AsyncStorage.setItem('lastWorkingIP', '127.0.0.1');
    return 'http://127.0.0.1:5000';
  }

  console.log('❌ CONFIG: Aucun serveur trouvé sur localhost');
  return null;
};

console.log('🔍 CONFIG: BASE_URL configuré sur:', BASE_URL, 'pour la plateforme:', Platform.OS);
