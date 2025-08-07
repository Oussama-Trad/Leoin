import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

const LoginTestScreen = ({ navigation }) => {
  const [adresse1, setAdresse1] = useState('oussama.trad@eleve.isep.fr');
  const [password, setPassword] = useState('Password123!');
  const [loading, setLoading] = useState(false);

  const testLogin = async () => {
    try {
      setLoading(true);
      
      console.log('🔐 Test de connexion...');
      
      const response = await fetch('http://192.168.1.15:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          adresse1: adresse1,
          password: password,
        }),
      });

      const result = await response.json();
      console.log('📡 Réponse login:', result);

      if (response.ok && result.success) {
        // Sauvegarder le token
        await AsyncStorage.setItem('userToken', result.token);
        await AsyncStorage.setItem('userData', JSON.stringify(result.user));
        
        Alert.alert(
          'Connexion réussie !',
          `Bienvenue ${result.user?.prenom || 'Utilisateur'}\nToken sauvegardé`,
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack()
            }
          ]
        );
      } else {
        Alert.alert('Erreur de connexion', result.message || 'Identifiants incorrects');
      }
    } catch (error) {
      console.error('❌ Erreur login:', error);
      Alert.alert('Erreur', 'Impossible de se connecter au serveur');
    } finally {
      setLoading(false);
    }
  };

  const checkStoredData = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userData = await AsyncStorage.getItem('userData');
      
      let message = 'Données stockées:\n\n';
      message += `Token: ${token ? token.substring(0, 30) + '...' : 'Aucun'}\n\n`;
      message += `User Data: ${userData ? 'Présent' : 'Aucun'}`;
      
      Alert.alert('AsyncStorage', message);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de lire AsyncStorage');
    }
  };

  const clearStorage = async () => {
    try {
      await AsyncStorage.clear();
      Alert.alert('Succès', 'AsyncStorage vidé');
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de vider AsyncStorage');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#0066CC" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Test de Connexion</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.content}>
        <Text style={styles.title}>🔐 Connexion Test</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Email (adresse1)</Text>
          <TextInput
            style={styles.input}
            value={adresse1}
            onChangeText={setAdresse1}
            placeholder="email@example.com"
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Mot de passe</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="Mot de passe"
            secureTextEntry
          />
        </View>

        <TouchableOpacity 
          style={[styles.button, styles.loginButton]} 
          onPress={testLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Ionicons name="log-in" size={20} color="white" />
              <Text style={styles.buttonText}>Se connecter</Text>
            </>
          )}
        </TouchableOpacity>

        <View style={styles.separator} />

        <TouchableOpacity 
          style={[styles.button, styles.checkButton]} 
          onPress={checkStoredData}
        >
          <Ionicons name="information-circle" size={20} color="white" />
          <Text style={styles.buttonText}>Vérifier les données</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.clearButton]} 
          onPress={clearStorage}
        >
          <Ionicons name="trash" size={20} color="white" />
          <Text style={styles.buttonText}>Vider le cache</Text>
        </TouchableOpacity>
      </View>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 30,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  loginButton: {
    backgroundColor: '#0066CC',
  },
  checkButton: {
    backgroundColor: '#28A745',
  },
  clearButton: {
    backgroundColor: '#DC3545',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  separator: {
    height: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    marginBottom: 20,
  },
});

export default LoginTestScreen;
