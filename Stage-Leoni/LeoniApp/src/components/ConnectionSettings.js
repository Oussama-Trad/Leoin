import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { BASE_URL, updateNgrokUrl, testConnection } from '../config';

export default function ConnectionSettings({ visible, onClose }) {
  const [ngrokUrl, setNgrokUrl] = useState('');
  const [currentUrl, setCurrentUrl] = useState(BASE_URL);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    setCurrentUrl(BASE_URL);
  }, []);

  const testCurrentConnection = async () => {
    setIsLoading(true);
    try {
      const isConnected = await testConnection();
      setConnectionStatus(isConnected);
      
      if (isConnected) {
        Alert.alert('Succès', 'Connexion au serveur réussie!');
      } else {
        Alert.alert('Erreur', 'Impossible de se connecter au serveur');
      }
    } catch (error) {
      console.error('Test connection error:', error);
      setConnectionStatus(false);
      Alert.alert('Erreur', 'Erreur lors du test de connexion');
    } finally {
      setIsLoading(false);
    }
  };

  const updateUrl = () => {
    if (!ngrokUrl.trim()) {
      Alert.alert('Erreur', 'Veuillez entrer une URL ngrok valide');
      return;
    }

    let formattedUrl = ngrokUrl.trim();
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = 'https://' + formattedUrl;
    }

    updateNgrokUrl(formattedUrl);
    setCurrentUrl(formattedUrl);
    Alert.alert('Succès', 'URL mise à jour! Testez la connexion.');
  };

  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <View style={styles.modal}>
        <Text style={styles.title}>Configuration de la connexion</Text>
        
        <View style={styles.section}>
          <Text style={styles.label}>URL actuelle:</Text>
          <Text style={styles.currentUrl}>{currentUrl}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Statut de connexion:</Text>
          <View style={styles.statusContainer}>
            {isLoading ? (
              <ActivityIndicator color="#667eea" />
            ) : (
              <Text style={[styles.status, { color: connectionStatus ? '#10b981' : '#ef4444' }]}>
                {connectionStatus === null ? 'Non testé' : connectionStatus ? 'Connecté' : 'Déconnecté'}
              </Text>
            )}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>URL Ngrok:</Text>
          <TextInput
            style={styles.input}
            placeholder="https://your-app.ngrok.io"
            value={ngrokUrl}
            onChangeText={setNgrokUrl}
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.testButton} onPress={testCurrentConnection}>
            <Text style={styles.buttonText}>Tester la connexion</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.updateButton} onPress={updateUrl}>
            <Text style={styles.buttonText}>Mettre à jour l'URL</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>Fermer</Text>
        </TouchableOpacity>

        <View style={styles.instructions}>
          <Text style={styles.instructionsTitle}>Instructions:</Text>
          <Text style={styles.instructionsText}>
            1. Démarrez ngrok: ngrok http 5000{'\n'}
            2. Copiez l'URL https générée{'\n'}
            3. Collez l'URL ci-dessus{'\n'}
            4. Cliquez sur "Mettre à jour l'URL"{'\n'}
            5. Testez la connexion
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 10,
    width: '90%',
    maxHeight: '80%',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#002857',
  },
  section: {
    marginBottom: 15,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 5,
    color: '#374151',
  },
  currentUrl: {
    fontSize: 12,
    color: '#667eea',
    backgroundColor: '#f3f4f6',
    padding: 10,
    borderRadius: 5,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  status: {
    fontSize: 14,
    fontWeight: '600',
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#f9fafb',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 10,
  },
  testButton: {
    backgroundColor: '#667eea',
    padding: 12,
    borderRadius: 8,
    flex: 1,
    marginRight: 5,
  },
  updateButton: {
    backgroundColor: '#10b981',
    padding: 12,
    borderRadius: 8,
    flex: 1,
    marginLeft: 5,
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: '600',
  },
  closeButton: {
    backgroundColor: '#6b7280',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  closeButtonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: '600',
  },
  instructions: {
    marginTop: 15,
    padding: 10,
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
  },
  instructionsTitle: {
    fontWeight: '600',
    marginBottom: 5,
    color: '#002857',
  },
  instructionsText: {
    fontSize: 12,
    color: '#374151',
    lineHeight: 16,
  },
});
