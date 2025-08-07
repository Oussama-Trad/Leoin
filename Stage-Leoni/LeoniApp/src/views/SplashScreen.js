import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, StyleSheet, Dimensions } from 'react-native';


const { width, height } = Dimensions.get('window');

export default function SplashScreen({ navigation }) {
  const logoScale = useRef(new Animated.Value(0)).current;
  const logoOpacity = useRef(new Animated.Value(0)).current;
  const textOpacity = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Animation du logo
    Animated.sequence([
      // Apparition du logo avec scale et opacity
      Animated.parallel([
        Animated.timing(logoScale, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(logoOpacity, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ]),
      // Apparition du texte
      Animated.timing(textOpacity, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();

    // Animation de pulsation continue
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Naviguer vers Home après 3 secondes
    const timer = setTimeout(() => {
      navigation.replace('Home');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <View style={[styles.container, { backgroundColor: '#002857' }]}

    >
      <View style={styles.logoContainer}>
        <Animated.View
          style={[
            styles.logoWrapper,
            {
              transform: [
                { scale: Animated.multiply(logoScale, pulseAnim) }
              ],
              opacity: logoOpacity,
            },
          ]}
        >
          <View style={styles.logoCircle}>
            <Text style={styles.logoText}>L</Text>
          </View>
        </Animated.View>
        
        <Animated.Text
          style={[
            styles.companyName,
            { opacity: textOpacity }
          ]}
        >
          LEONI
        </Animated.Text>
        
        <Animated.Text
          style={[
            styles.tagline,
            { opacity: textOpacity }
          ]}
        >
          Connecting Excellence
        </Animated.Text>
      </View>
      
      <View style={styles.loadingContainer}>
        <View style={styles.loadingBar}>
          <Animated.View
            style={[
              styles.loadingProgress,
              { opacity: textOpacity }
            ]}
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 80,
  },
  logoWrapper: {
    marginBottom: 20,
  },
  logoCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  logoText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#1e3c72',
    fontFamily: 'System',
  },
  companyName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
    letterSpacing: 3,
  },
  tagline: {
    fontSize: 16,
    color: '#e2e8f0',
    fontStyle: 'italic',
  },
  loadingContainer: {
    position: 'absolute',
    bottom: 100,
    width: width * 0.6,
  },
  loadingBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  loadingProgress: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 2,
    width: '100%',
  },
});