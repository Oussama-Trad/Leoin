import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { BASE_URL, testConnection } from '../config';

export default function ConnectionTest() {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, type, timestamp }]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const runConnectionTest = async () => {
    setIsLoading(true);
    clearLogs();
    
    addLog('🔄 Début des tests de connectivité');
    addLog(`📍 URL de base configurée: ${BASE_URL}`);

    // Test 1: Ping de base
    addLog('📡 Test 1: Vérification de l\'endpoint /health...');
    try {
      const isHealthy = await testConnection();
      if (isHealthy) {
        addLog('✅ Test 1 réussi: Serveur accessible', 'success');
      } else {
        addLog('❌ Test 1 échoué: Serveur non accessible', 'error');
      }
    } catch (error) {
      addLog(`❌ Test 1 erreur: ${error.message}`, 'error');
    }

    // Test 2: Test login endpoint
    addLog('📡 Test 2: Vérification de l\'endpoint /login...');
    try {
      const response = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@test.com',
          password: 'wrongpassword'
        })
      });
      
      if (response.status === 401 || response.status === 400) {
        addLog('✅ Test 2 réussi: Endpoint /login répond (erreur attendue)', 'success');
      } else {
        addLog(`⚠️ Test 2 inattendu: Status ${response.status}`, 'warning');
      }
    } catch (error) {
      addLog(`❌ Test 2 erreur: ${error.message}`, 'error');
    }

    // Test 3: Test register endpoint
    addLog('📡 Test 3: Vérification de l\'endpoint /register...');
    try {
      const response = await fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          // Données incomplètes pour tester la validation
          email: 'test@test.com'
        })
      });
      
      if (response.status === 400) {
        addLog('✅ Test 3 réussi: Endpoint /register répond (erreur de validation attendue)', 'success');
      } else {
        addLog(`⚠️ Test 3 inattendu: Status ${response.status}`, 'warning');
      }
    } catch (error) {
      addLog(`❌ Test 3 erreur: ${error.message}`, 'error');
    }

    addLog('🏁 Tests terminés');
    setIsLoading(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Test de Connectivité</Text>
        <TouchableOpacity 
          style={[styles.testButton, isLoading && styles.disabled]} 
          onPress={runConnectionTest}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            {isLoading ? '🔄 Test en cours...' : '🧪 Lancer les tests'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.logContainer}>
        {logs.map((log, index) => (
          <View key={index} style={styles.logItem}>
            <Text style={styles.timestamp}>{log.timestamp}</Text>
            <Text style={[styles.logMessage, styles[log.type]]}>
              {log.message}
            </Text>
          </View>
        ))}
      </ScrollView>

      {logs.length > 0 && (
        <TouchableOpacity style={styles.clearButton} onPress={clearLogs}>
          <Text style={styles.clearButtonText}>🗑️ Effacer les logs</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#002857',
    marginBottom: 15,
    textAlign: 'center',
  },
  testButton: {
    backgroundColor: '#667eea',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  disabled: {
    backgroundColor: '#9ca3af',
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  logContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  logItem: {
    marginBottom: 10,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e5e5',
  },
  timestamp: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  logMessage: {
    fontSize: 14,
    lineHeight: 20,
  },
  info: {
    color: '#333',
  },
  success: {
    color: '#10b981',
  },
  error: {
    color: '#ef4444',
  },
  warning: {
    color: '#f59e0b',
  },
  clearButton: {
    backgroundColor: '#6b7280',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  clearButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});
