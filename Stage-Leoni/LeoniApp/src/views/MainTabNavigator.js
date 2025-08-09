import React, { useState, useEffect } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useNavigationState } from '@react-navigation/native';
import ProfileScreen from './ProfileScreen';
import DocumentRequestScreen from './DocumentRequestScreen';
import DocumentsScreen from './DocumentsScreen';
import NewsScreenNew from './NewsScreenNew';
import ChatsScreenDepartment from './ChatsScreenDepartment';

const Tab = createBottomTabNavigator();

const MainTabNavigator = ({ route }) => {
  const { userData } = route.params || {};
  const navigation = useNavigation();
  const [currentRoute, setCurrentRoute] = useState('Profile');

  // Obtenir la route active
  const navigationState = useNavigationState(state => state);

  useEffect(() => {
    if (navigationState) {
      const activeRoute = navigationState.routes[navigationState.index];
      if (activeRoute && activeRoute.state) {
        const tabState = activeRoute.state;
        const activeTab = tabState.routes[tabState.index];
        setCurrentRoute(activeTab.name);
      }
    }
  }, [navigationState]);

  return (
    <View style={styles.container}>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Profile') {
              iconName = focused ? 'person' : 'person-outline';
            } else if (route.name === 'News') {
              iconName = focused ? 'newspaper' : 'newspaper-outline';
            } else if (route.name === 'Chats') {
              iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
            } else if (route.name === 'DocumentRequest') {
              iconName = focused ? 'document-text' : 'document-text-outline';
            } else if (route.name === 'Documents') {
              iconName = focused ? 'documents' : 'documents-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#6c5ce7',
          tabBarInactiveTintColor: '#8e8e93',
          tabBarStyle: {
            backgroundColor: '#fff',
            borderTopWidth: 1,
            borderTopColor: '#e1e1e1',
            height: 60,
            paddingBottom: 8,
            paddingTop: 8,
          },
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '600',
          },
          // Masquer l'header par défaut car on utilise TopBar
          headerShown: false,
        })}
        screenListeners={{
          state: (e) => {
            // Détecte le changement d'onglet
            const currentTab = e.data.state.routes[e.data.state.index].name;
            setCurrentRoute(currentTab);
          },
        }}
      >
        <Tab.Screen 
          name="News" 
          component={NewsScreenNew}
          options={{
            title: 'Actualités',
          }}
        />
        <Tab.Screen 
          name="Chats" 
          component={ChatsScreenDepartment}
          options={{
            title: 'Conversations',
          }}
        />
        <Tab.Screen 
          name="Profile" 
          component={ProfileScreen}
          options={{
            title: 'Profil',
          }}
        />
        <Tab.Screen 
          name="Documents" 
          component={DocumentsScreen}
          options={{
            title: 'Mes Documents',
          }}
        />
        <Tab.Screen 
          name="DocumentRequest" 
          component={DocumentRequestScreen}
          options={{
            title: 'Demande de document',
          }}
        />
      </Tab.Navigator>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});

export default MainTabNavigator;
