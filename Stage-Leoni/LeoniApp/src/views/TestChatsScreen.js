import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const TestChatsScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>💬 Test - Chat avec service</Text>
      <Text style={styles.subtitle}>Cette page de test fonctionne !</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f4f8',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#002857',
    marginBottom: 20,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});

export default TestChatsScreen;
