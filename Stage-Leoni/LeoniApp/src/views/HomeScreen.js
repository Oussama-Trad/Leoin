import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions, Animated, Image, Alert } from 'react-native';

import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const buttonScale1 = useRef(new Animated.Value(0.9)).current;
  const buttonScale2 = useRef(new Animated.Value(0.9)).current;
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    // Simuler une actualisation
    setTimeout(() => {
      setRefreshing(false);
      Alert.alert('Succès', 'Page actualisée');
    }, 1000);
  };

  useEffect(() => {
    // Animation d'entrée
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 1000,
        useNativeDriver: true,
      }),
    ]).start();

    // Animation des boutons
    setTimeout(() => {
      Animated.parallel([
        Animated.spring(buttonScale1, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
        Animated.spring(buttonScale2, {
          toValue: 1,
          tension: 50,
          friction: 7,
          delay: 200,
          useNativeDriver: true,
        }),
      ]).start();
    }, 500);
  }, []);

  const handleLogin = () => {
    navigation.navigate('Login');
  };

  const handleRegister = () => {
    navigation.navigate('Register');
  };

  return (
    <View style={[styles.container, { backgroundColor: '#002857' }]}
   
    >
      {/* Bouton d'actualisation */}
      <TouchableOpacity 
        style={styles.refreshButton} 
        onPress={handleRefresh}
        disabled={refreshing}
      >
        <Ionicons 
          name={refreshing ? "refresh" : "refresh-outline"} 
          size={24} 
          color="#fff" 
        />
      </TouchableOpacity>

      <Animated.View
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        {/* Header avec logo */}
       <View style={styles.header}>
  <View style={styles.logoContainer}>
    <View style={styles.logoCircle}>
      <Image
        source={require('../../assets/leoni_tunisia_logo.png')} // adapte le chemin si besoin
        style={styles.logoImage}
        resizeMode="contain"
      />
    </View>
    <Text style={styles.welcomeTitle}>Bienvenue sur</Text>
    <Text style={styles.appName}>LeoniApp</Text>
  </View>
</View>

        {/* Description */}
        <View style={styles.descriptionContainer}>
          <Text style={styles.description}>
            Votre plateforme dédiée pour simplifier vos démarches administratives
          </Text>
          <Text style={styles.subDescription}>
            Demandez vos documents en quelques clics
          </Text>
        </View>

        {/* Boutons d'action */}
        <View style={styles.buttonContainer}>
          <Animated.View style={{ transform: [{ scale: buttonScale1 }] }}>
            <TouchableOpacity
              style={[styles.button, styles.loginButton]}
              onPress={handleLogin}
              activeOpacity={0.8}
            >
              <Ionicons name="log-in-outline" size={24} color="#ffffff" />
              <Text style={styles.buttonText}>Se connecter</Text>
            </TouchableOpacity>
          </Animated.View>

          <Animated.View style={{ transform: [{ scale: buttonScale2 }] }}>
            <TouchableOpacity
              style={[styles.button, styles.registerButton]}
              onPress={handleRegister}
              activeOpacity={0.8}
            >
              <Ionicons name="person-add-outline" size={24} color="#667eea" />
              <Text style={[styles.buttonText, styles.registerButtonText]}>
                S'inscrire
              </Text>
            </TouchableOpacity>
          </Animated.View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            © 2024 Leoni. Tous droits réservés.
          </Text>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  refreshButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 10,
    borderRadius: 25,
    zIndex: 1000,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 30,
    paddingVertical: 60,
  },
  header: {
    alignItems: 'center',
    marginTop: 40,
  },
  logoContainer: {
    alignItems: 'center',
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    marginBottom: 20,
  },
  logoText: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#667eea',
  },
  welcomeTitle: {
    fontSize: 18,
    color: '#ffffff',
    marginBottom: 5,
    opacity: 0.9,
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    letterSpacing: 1,
  },
  descriptionContainer: {
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  description: {
    fontSize: 16,
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 10,
    opacity: 0.9,
    lineHeight: 24,
  },
  subDescription: {
    fontSize: 14,
    color: '#ffffff',
    textAlign: 'center',
    opacity: 0.8,
    fontStyle: 'italic',
  },
  buttonContainer: {
    alignItems: 'center',
    gap: 20,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 30,
    width: width * 0.7,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    gap: 10,
  },
  loginButton: {
    backgroundColor: '#4c51bf',
  },
  registerButton: {
    backgroundColor: '#ffffff',
  },
  buttonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
  },
  registerButtonText: {
    color: '#667eea',
  },
  footer: {
    alignItems: 'center',
    marginTop: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#ffffff',
    opacity: 0.7,
  },
  logoImage: {
  width: 80,              // tu peux mettre 60 ou 50 selon ta préférence
  height: 80,
  borderRadius: 40,       // moitié de la largeur/hauteur
  borderWidth: 2,         // optionnel, pour un cadre autour
  borderColor: '#fff',    // optionnel, couleur du cadre
},
});