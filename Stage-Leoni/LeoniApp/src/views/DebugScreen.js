import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

const DebugScreen = ({ navigation }) => {
  const [debugInfo, setDebugInfo] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDebugInfo();
  }, []);

  const loadDebugInfo = async () => {
    try {
      setLoading(true);
      
      const info = {};
      
      // Récupérer toutes les clés AsyncStorage
      const keys = await AsyncStorage.getAllKeys();
      info.asyncStorageKeys = keys;
      
      // Récupérer des données spécifiques
      for (const key of keys) {
        try {
          const value = await AsyncStorage.getItem(key);
          info[`storage_${key}`] = value;
        } catch (error) {
          info[`storage_${key}`] = `Erreur: ${error.message}`;
        }
      }
      
      // Informations réseau
      info.baseURL = 'http://192.168.1.15:5000';
      
      setDebugInfo(info);
    } catch (error) {
      console.error('Erreur debug:', error);
      Alert.alert('Erreur', 'Impossible de charger les informations de debug');
    } finally {
      setLoading(false);
    }
  };

  const testNewsAPI = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      
      if (!token) {
        Alert.alert('Erreur', 'Aucun token d\'authentification trouvé');
        return;
      }

      console.log('🧪 Test API News avec token:', token.substring(0, 20) + '...');

      const response = await fetch('http://192.168.1.15:5000/api/news', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      Alert.alert(
        'Résultat API',
        `Status: ${response.status}\nSuccess: ${result.success}\nMessage: ${result.message || 'Aucun message'}\nNews: ${result.news?.length || 0} éléments`,
        [{ text: 'OK' }]
      );

    } catch (error) {
      Alert.alert('Erreur Test', error.message);
    }
  };

  const clearStorage = async () => {
    try {
      await AsyncStorage.clear();
      Alert.alert('Succès', 'AsyncStorage vidé');
      loadDebugInfo();
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de vider AsyncStorage');
    }
  };

  const renderDebugItem = (key, value) => (
    <View key={key} style={styles.debugItem}>
      <Text style={styles.debugKey}>{key}:</Text>
      <Text style={styles.debugValue} numberOfLines={3}>
        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#0066CC" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Debug Info</Text>
        <TouchableOpacity onPress={loadDebugInfo}>
          <Ionicons name="refresh" size={24} color="#0066CC" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔧 Actions</Text>
          
          <TouchableOpacity style={styles.actionButton} onPress={testNewsAPI}>
            <Ionicons name="flask" size={20} color="white" />
            <Text style={styles.actionButtonText}>Tester API News</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.actionButton, styles.dangerButton]} onPress={clearStorage}>
            <Ionicons name="trash" size={20} color="white" />
            <Text style={styles.actionButtonText}>Vider AsyncStorage</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📱 Informations Debug</Text>
          
          {loading ? (
            <Text style={styles.loadingText}>Chargement...</Text>
          ) : (
            Object.entries(debugInfo).map(([key, value]) => renderDebugItem(key, value))
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0066CC',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  dangerButton: {
    backgroundColor: '#FF4444',
  },
  actionButtonText: {
    color: 'white',
    fontWeight: '600',
    marginLeft: 10,
  },
  debugItem: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#0066CC',
  },
  debugKey: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  debugValue: {
    fontSize: 12,
    color: '#666',
    fontFamily: 'monospace',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
  },
});

export default DebugScreen;
