import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';

const NetworkDiagnostic = () => {
  const [results, setResults] = useState({});
  const [testing, setTesting] = useState(false);

  const testUrls = [
    'http://localhost:5000',
    'http://127.0.0.1:5000'
  ];

  const testConnection = async (url) => {
    try {
      const startTime = Date.now();
      const response = await fetch(`${url}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 5000,
      });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;

      if (response.ok) {
        const data = await response.json();
        return {
          status: 'success',
          responseTime,
          data,
          statusCode: response.status
        };
      } else {
        return {
          status: 'error',
          responseTime,
          error: `HTTP ${response.status}`,
          statusCode: response.status
        };
      }
    } catch (error) {
      return {
        status: 'failed',
        error: error.message,
        responseTime: null
      };
    }
  };

  const runDiagnostic = async () => {
    setTesting(true);
    const newResults = {};

    for (const url of testUrls) {
      console.log(`Testing ${url}...`);
      const result = await testConnection(url);
      newResults[url] = result;
    }

    setResults(newResults);
    setTesting(false);

    // Trouver le premier serveur qui fonctionne
    const workingServer = Object.entries(newResults).find(([url, result]) => result.status === 'success');
    if (workingServer) {
      Alert.alert(
        'Serveur trouvé !',
        `Le serveur backend est accessible sur:\n${workingServer[0]}\n\nTemps de réponse: ${workingServer[1].responseTime}ms`,
        [
          { text: 'OK' },
          { 
            text: 'Utiliser cette adresse', 
            onPress: () => {
              Alert.alert('Configuration', `Modifiez config.js pour utiliser:\nBASE_URL = '${workingServer[0]}'`);
            }
          }
        ]
      );
    } else {
      Alert.alert('Aucun serveur trouvé', 'Aucun serveur backend n\'a pu être contacté. Vérifiez que le serveur Python est démarré.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#4CAF50';
      case 'error': return '#FF9800';
      case 'failed': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (result) => {
    switch (result.status) {
      case 'success': return `✅ OK (${result.responseTime}ms)`;
      case 'error': return `⚠️ ${result.error}`;
      case 'failed': return `❌ ${result.error}`;
      default: return '⏳ En attente...';
    }
  };

  useEffect(() => {
    runDiagnostic();
  }, []);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🔧 Diagnostic Réseau</Text>
        <Text style={styles.subtitle}>Test de connectivité Backend</Text>
      </View>

      <TouchableOpacity 
        style={[styles.button, testing && styles.buttonDisabled]} 
        onPress={runDiagnostic}
        disabled={testing}
      >
        <Text style={styles.buttonText}>
          {testing ? '⏳ Test en cours...' : '🔄 Relancer le test'}
        </Text>
      </TouchableOpacity>

      <View style={styles.results}>
        {testUrls.map((url) => {
          const result = results[url] || {};
          return (
            <View key={url} style={styles.resultItem}>
              <View style={styles.resultHeader}>
                <Text style={styles.url}>{url}</Text>
                <Text style={[styles.status, { color: getStatusColor(result.status) }]}>
                  {getStatusText(result)}
                </Text>
              </View>
              {result.data && (
                <Text style={styles.details}>
                  Service: {result.data.service || 'LeoniApp Backend'}
                </Text>
              )}
              {result.error && (
                <Text style={styles.error}>Erreur: {result.error}</Text>
              )}
            </View>
          );
        })}
      </View>

      <View style={styles.info}>
        <Text style={styles.infoTitle}>ℹ️ Information</Text>
        <Text style={styles.infoText}>
          Ce diagnostic teste la connectivité vers différentes adresses IP où le serveur Python pourrait être accessible.
          {'\n\n'}
          Si aucun serveur n'est trouvé, vérifiez que:
          {'\n'}• Le serveur Python est démarré (python app_with_access_control.py)
          {'\n'}• Le port 5000 n'est pas bloqué par le firewall
          {'\n'}• Votre connexion réseau fonctionne
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  button: {
    backgroundColor: '#4CAF50',
    margin: 20,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#9E9E9E',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  results: {
    margin: 20,
  },
  resultItem: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  url: {
    fontSize: 14,
    fontWeight: 'bold',
    flex: 1,
  },
  status: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  details: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  error: {
    fontSize: 12,
    color: '#F44336',
    marginTop: 5,
  },
  info: {
    margin: 20,
    padding: 15,
    backgroundColor: '#E3F2FD',
    borderRadius: 10,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#666',
  },
});

export default NetworkDiagnostic;
