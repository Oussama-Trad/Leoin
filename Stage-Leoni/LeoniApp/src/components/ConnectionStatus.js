import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BASE_URL } from '../config';

const ConnectionStatus = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = async () => {
    setIsChecking(true);
    try {
      const response = await fetch(`${BASE_URL}/health`, {
        method: 'GET',
        timeout: 3000
      });
      setIsOnline(response.ok);
    } catch (error) {
      console.log('Serveur hors ligne:', error.message);
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkConnection();
    // Vérifier la connexion toutes les 30 secondes
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isOnline) {
    return null; // Ne rien afficher si tout va bien
  }

  return (
    <View style={styles.container}>
      <Ionicons 
        name={isChecking ? "sync" : "cloud-offline"} 
        size={16} 
        color="#fff" 
        style={isChecking ? styles.spinning : null}
      />
      <Text style={styles.text}>
        {isChecking ? 'Vérification...' : 'Mode hors ligne'}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#ff6b6b',
    paddingVertical: 8,
    paddingHorizontal: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 20,
    margin: 10,
  },
  text: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 6,
  },
  spinning: {
    // Animation de rotation pour l'icône de synchronisation
  }
});

export default ConnectionStatus;
