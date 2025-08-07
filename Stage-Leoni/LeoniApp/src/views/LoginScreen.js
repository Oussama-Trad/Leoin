import React, { useState, useEffect, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AuthController from '../controllers/AuthController';
import { AuthContext } from '../contexts/AuthContext';
import NetworkService from '../services/NetworkService';

export default function LoginScreen({ navigation }) {
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setEmail('');
    setPassword('');
    setShowPassword(false);
    setTimeout(() => {
      setRefreshing(false);
      Alert.alert('Succès', 'Formulaire réinitialisé');
    }, 1000);
  };

  // Vérifier si l'utilisateur est déjà connecté au démarrage
  useEffect(() => {
    checkExistingSession();
  }, []);

  const checkExistingSession = async () => {
    try {
      const isLoggedIn = await AuthController.checkAuthStatus();
      if (isLoggedIn) {
        // Vérifier si le token a le bon format
        const hasValidFormat = await AuthController.hasValidTokenFormat();
        if (!hasValidFormat) {
          console.warn('⚠️ LoginScreen: Token ancien format détecté - Déconnexion automatique');
          await AuthController.logout();
          Alert.alert(
            'Session expirée',
            'Votre session utilise un ancien format. Veuillez vous reconnecter.',
            [{ text: 'OK' }]
          );
          return;
        }

        const userData = await AuthController.getCurrentUser();
        if (userData) {
          // Mettre à jour le contexte
          login(userData);
          
          navigation.reset({
            index: 0,
            routes: [{ name: 'MainTabs', params: { userData } }],
          });
        }
      }
    } catch (error) {
      console.error('Erreur vérification session:', error);
    }
  };

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Attempting login with adresse1:', email.trim().toLowerCase());

      // Forcer la réinitialisation de la détection réseau pour s'assurer qu'on utilise la bonne IP
      console.log('🔄 Forcer la réinitialisation de la détection réseau...');
      await NetworkService.forceRedetection();

      const result = await AuthController.handleLogin(email.trim().toLowerCase(), password);

      console.log('Login response:', result);

      if (result.success) {
        // Mettre à jour le contexte avec les données utilisateur
        login(result.user);
        
        // Rediriger vers les onglets principaux avec les données utilisateur
        navigation.reset({
          index: 0,
          routes: [{ name: 'MainTabs', params: { userData: result.user } }],
        });
      } else {
        Alert.alert('Erreur de connexion', result.message || 'Adresse1 ou mot de passe incorrect');
      }
    } catch (error) {
      console.error('Login failed:', error);
      Alert.alert('Erreur de connexion', 'Une erreur est survenue lors de la connexion');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: '#002857' }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <Ionicons name="arrow-back" size={24} color="#ffffff" />
            </TouchableOpacity>
            <Text style={styles.title}>Se connecter</Text>
            <TouchableOpacity
              style={styles.refreshButton}
              onPress={handleRefresh}
              disabled={refreshing}
            >
              <Ionicons 
                name={refreshing ? "refresh" : "refresh-outline"} 
                size={20} 
                color="#ffffff" 
              />
            </TouchableOpacity>
          </View>

          {/* Formulaire */}
          <View style={styles.form}>
            <View style={styles.inputContainer}>
              <Ionicons name="mail-outline" size={20} color="#667eea" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Adresse1"
                placeholderTextColor="#9ca3af"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                editable={!isLoading}
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="lock-closed-outline" size={20} color="#667eea" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Mot de passe"
                placeholderTextColor="#9ca3af"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                editable={!isLoading}
              />
              <TouchableOpacity 
                style={styles.eyeIcon}
                onPress={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                <Ionicons 
                  name={showPassword ? "eye-off" : "eye"} 
                  size={20} 
                  color="#667eea" 
                />
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.disabledButton]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <ActivityIndicator size="small" color="#ffffff" style={{ marginRight: 10 }} />
                  <Text style={styles.loginButtonText}>Connexion...</Text>
                </>
              ) : (
                <>
                  <Ionicons name="log-in-outline" size={20} color="#ffffff" />
                  <Text style={styles.loginButtonText}>Se connecter</Text>
                </>
              )}
            </TouchableOpacity>
          </View>

          {/* Lien d'inscription */}
          <View style={styles.footer}>
            <TouchableOpacity
              onPress={() => navigation.navigate('Register')}
              disabled={isLoading}
            >
              <Text style={styles.registerLinkText}>
                Pas encore de compte ? <Text style={styles.registerLinkTextBold}>S'inscrire</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 30,
    paddingVertical: 60,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 40,
  },
  backButton: {
    marginRight: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    flex: 1,
  },
  refreshButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 8,
    borderRadius: 20,
  },
  form: {
    flex: 1,
    justifyContent: 'center',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 15,
    paddingHorizontal: 15,
    paddingVertical: 12,
    marginBottom: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#374151',
  },
  eyeIcon: {
    padding: 5,
  },
  loginButton: {
    backgroundColor: '#667eea',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 15,
    marginTop: 30,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  disabledButton: {
    backgroundColor: '#9ca3af',
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  footer: {
    alignItems: 'center',
    marginTop: 30,
  },
  registerLinkText: {
    color: '#ffffff',
    fontSize: 16,
    textAlign: 'center',
  },
  registerLinkTextBold: {
    fontWeight: 'bold',
    textDecorationLine: 'underline',
  },
});