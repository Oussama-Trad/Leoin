import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Liste des IPs possibles à tester
const POSSIBLE_IPS = [
  'localhost',
  '192.168.1.16',
  '192.168.1.15',
  '192.168.1.17',
  '192.168.1.18',
  '192.168.1.19',
  '192.168.1.20',
  '10.0.2.2', // IP par défaut pour l'émulateur Android
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
  // Essayer de détecter automatiquement l'IP
  const detectedIP = detectPCIP();

  if (detectedIP) {
    console.log('✅ CONFIG: IP détectée automatiquement:', detectedIP);
    return `http://${detectedIP}:5000`;
  }

  // Fallback : utiliser localhost par défaut
  console.log('🔍 CONFIG: Utilisation de localhost par défaut');
  return 'http://localhost:5000';
};

export const BASE_URL = 'http://localhost:5000';

// Fonction pour trouver automatiquement la bonne IP
export const findWorkingIP = async () => {
  console.log('🔍 CONFIG: Recherche de l\'IP du serveur...');

  // D'abord, essayer l'IP détectée automatiquement
  const detectedIP = detectPCIP();
  if (detectedIP) {
    console.log(`🔍 CONFIG: Test de l'IP détectée: ${detectedIP}...`);
    const works = await testConnection(detectedIP);
    if (works) {
      console.log(`✅ CONFIG: Serveur trouvé sur l'IP détectée: ${detectedIP}`);
      // Sauvegarder cette IP pour les prochaines fois
      await AsyncStorage.setItem('lastWorkingIP', detectedIP);
      return `http://${detectedIP}:5000`;
    }
  }

  // Essayer la dernière IP qui a fonctionné
  try {
    const lastWorkingIP = await AsyncStorage.getItem('lastWorkingIP');
    if (lastWorkingIP) {
      console.log(`🔍 CONFIG: Test de la dernière IP qui a fonctionné: ${lastWorkingIP}...`);
      const works = await testConnection(lastWorkingIP);
      if (works) {
        console.log(`✅ CONFIG: Serveur trouvé sur la dernière IP: ${lastWorkingIP}`);
        return `http://${lastWorkingIP}:5000`;
      }
    }
  } catch (error) {
    console.log('🔍 CONFIG: Impossible de récupérer la dernière IP');
  }

  // Fallback : tester la liste des IPs possibles
  for (const ip of POSSIBLE_IPS) {
    console.log(`🔍 CONFIG: Test de ${ip}...`);
    const works = await testConnection(ip);
    if (works) {
      console.log(`✅ CONFIG: Serveur trouvé sur ${ip}`);
      // Sauvegarder cette IP pour les prochaines fois
      await AsyncStorage.setItem('lastWorkingIP', ip);
      return `http://${ip}:5000`;
    }
  }

  console.log('❌ CONFIG: Aucun serveur trouvé');
  return null;
};

console.log('🔍 CONFIG: BASE_URL configuré sur:', BASE_URL, 'pour la plateforme:', Platform.OS);
