import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider } from './src/contexts/AuthContext';
import { StatusBar, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import SplashScreen from './src/views/SplashScreen';
import HomeScreen from './src/views/HomeScreen';
import LoginScreen from './src/views/LoginScreen';
import RegisterScreen from './src/views/RegisterScreen';
import MainNavigator from './src/views/MainNavigator';
import NewsDetailScreenNew from './src/views/NewsDetailScreenNew';
import ChatDetailScreenNew from './src/views/ChatDetailScreenNew';
import DocumentRequestScreen from './src/views/DocumentRequestScreen';
import ChatsScreenDepartment from './src/views/ChatsScreenDepartment';

const Stack = createStackNavigator();

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
      <StatusBar barStyle="light-content" backgroundColor="#002857" />
      <Stack.Navigator 
        initialRouteName="Splash"
        screenOptions={{
          headerShown: true,
          headerStyle: {
            backgroundColor: '#002857',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          cardStyle: { backgroundColor: '#f5f5f5' }
        }}
      >
        <Stack.Screen 
          name="Splash" 
          component={SplashScreen} 
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ 
            title: 'Accueil',
            headerShown: true
          }} 
        />
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ 
            title: 'Connexion',
            headerShown: true
          }} 
        />
        <Stack.Screen
          name="Register"
          component={RegisterScreen}
          options={{
            title: 'Inscription',
            headerShown: true
          }}
        />
        <Stack.Screen
          name="MainTabs"
          component={MainNavigator}
          options={{
            headerShown: false
          }}
        />
        <Stack.Screen
          name="DocumentRequestStack"
          component={DocumentRequestScreen}
          options={{
            title: '📝 Demander un document',
            headerStyle: {
              backgroundColor: '#002857',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        />
        <Stack.Screen
          name="ChatsStack"
          component={ChatsScreenDepartment}
          options={{
            headerShown: false
          }}
        />
        <Stack.Screen
          name="NewsDetail"
          component={NewsDetailScreenNew}
          options={{
            headerShown: false
          }}
        />
        <Stack.Screen
          name="ChatDetail"
          component={ChatDetailScreenNew}
          options={{
            headerShown: false
          }}
        />
      </Stack.Navigator>
      </NavigationContainer>
    </AuthProvider>
  );
}
