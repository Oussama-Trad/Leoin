import React, { useState, useEffect, useContext } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { View, Text, StyleSheet, TouchableOpacity, Alert, SafeAreaView, Image, Modal, FlatList } from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useNavigation, useNavigationState } from '@react-navigation/native';
import { AuthContext } from '../contexts/AuthContext';
import { getProfile } from '../controllers/ProfileController';
import DocumentController from '../controllers/DocumentController';
import AuthController from '../controllers/AuthController';
import UserModel from '../models/UserModel';

// Screens
import ProfileScreenSimple from './ProfileScreenSimple';
import DocumentsScreen from './DocumentsScreen';
import NewsScreenNew from './NewsScreenNew';
import DocumentRequestScreen from './DocumentRequestScreen';
import ChatsScreenDepartment from './ChatsScreenDepartment';
// Écrans de test temporaires
import TestDocumentRequestScreen from './TestDocumentRequestScreen';
import TestChatsScreen from './TestChatsScreen';
import DebugScreen from './DebugScreen';

const Tab = createBottomTabNavigator();
const Drawer = createDrawerNavigator();

// Composant pour l'en-tête avec informations utilisateur complètes
const CustomHeader = ({ navigation, title, showHamburger = true }) => {
  const { currentUser, logout: contextLogout } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [freshUserData, setFreshUserData] = useState(null);
  
  // Utiliser les données fraîches ou currentUser du contexte
  const userDataToUse = freshUserData || currentUser;

  // Récupérer les données fraîches de l'utilisateur au chargement
  useEffect(() => {
    const fetchFreshUserData = async () => {
      try {
        console.log('🔄 CustomHeader: Récupération des données fraîches...');
        const response = await getProfile();
        if (response.success && response.user) {
          console.log('✅ CustomHeader: Données fraîches récupérées:', response.user.department);
          setFreshUserData(response.user);
        }
      } catch (error) {
        console.error('❌ CustomHeader: Erreur lors de la récupération des données fraîches:', error);
      }
    };

    fetchFreshUserData();
  }, []);

  // Vérifier les notifications
  useEffect(() => {
    const checkNotifications = async () => {
      try {
        const result = await DocumentController.getDocumentRequests();
        if (result.success && result.data) {
          const newNotifications = [];
          
          result.data.forEach(doc => {
            if (!doc || typeof doc !== 'object') return;
            
            if (doc.status?.current && doc.status.current !== 'en attente') {
              const docId = doc.id || doc._id;
              const docType = doc.type || doc.documentType;
              
              if (docId && docType && typeof docId === 'string' && typeof docType === 'string') {
                const notificationId = `${docId}_${doc.status.current}`;
                
                newNotifications.push({
                  id: notificationId,
                  documentId: docId,
                  documentType: docType,
                  status: doc.status.current,
                  message: `Votre demande de "${docType}" est maintenant "${doc.status.current}"`,
                  timestamp: doc.updatedAt || doc.createdAt || new Date(),
                  isRead: false
                });
              }
            }
          });
          
          const validNotifications = newNotifications.filter(n => 
            n && typeof n === 'object' && n.id && n.message
          );
          
          setNotifications(validNotifications);
          setUnreadCount(validNotifications.filter(n => !n.isRead).length);
        }
      } catch (error) {
        console.error('Erreur vérification notifications:', error);
      }
    };

    if (userDataToUse) {
      checkNotifications();
      const interval = setInterval(checkNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [userDataToUse]);

  if (!userDataToUse) {
    return (
      <SafeAreaView style={styles.headerSafeArea}>
        <View style={styles.header}>
          {showHamburger && (
            <TouchableOpacity 
              style={styles.hamburgerButton}
              onPress={() => navigation.openDrawer()}
            >
              <Ionicons name="menu" size={24} color="#ffffff" />
            </TouchableOpacity>
          )}
          <Text style={styles.headerTitle}>{title}</Text>
          <View style={styles.headerSpacer} />
        </View>
      </SafeAreaView>
    );
  }

  const user = new UserModel(userDataToUse);

  const getProfileImage = () => {
    if (user.profilePicture) {
      if (user.profilePicture.startsWith('http')) {
        return { uri: user.profilePicture };
      }
      return { uri: user.profilePicture };
    }
    return require('../../assets/leoni_tunisia_logo.png');
  };

  const markNotificationAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  return (
    <SafeAreaView style={styles.headerSafeArea}>
      <View style={styles.fullHeader}>
        <View style={styles.profileSection}>
          <View style={styles.profileImageContainer}>
            <Image
              source={getProfileImage()}
              style={styles.profileImage}
              defaultSource={require('../../assets/leoni_tunisia_logo.png')}
            />
          </View>
          <View style={styles.userInfo}>
            <Text style={styles.userName} numberOfLines={1}>
              {(user.getFullName() && user.getFullName().trim()) || 'Utilisateur'}
            </Text>
            <Text style={styles.userDepartment} numberOfLines={1}>
              {(user.department && user.department !== 'Non spécifié') ? user.department : 'IT'} • {(user.location && user.location !== 'Non spécifié') ? user.location : 'Sousse'}
            </Text>
          </View>
        </View>
        <View style={styles.rightSection}>
          <TouchableOpacity 
            style={styles.notificationButton}
            onPress={() => setShowNotifications(!showNotifications)}
          >
            <MaterialIcons name="notifications" size={28} color="#ffffff" />
            {unreadCount > 0 && (
              <View style={styles.notificationBadge}>
                <Text style={styles.badgeText}>{String(unreadCount)}</Text>
              </View>
            )}
          </TouchableOpacity>
          {showHamburger && (
            <TouchableOpacity
              style={styles.menuButton}
              onPress={() => navigation.openDrawer()}
            >
              <Ionicons name="menu" size={28} color="#ffffff" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Modal des notifications */}
      <Modal
        visible={showNotifications}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowNotifications(false)}
      >
        <TouchableOpacity 
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setShowNotifications(false)}
        >
          <View style={styles.notificationModal}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Notifications</Text>
              <TouchableOpacity onPress={() => setShowNotifications(false)}>
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            {notifications.length > 0 ? (
              <FlatList
                data={notifications}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                  <TouchableOpacity
                    style={[styles.notificationItem, !item.isRead && styles.unreadNotification]}
                    onPress={() => markNotificationAsRead(item.id)}
                  >
                    <View style={styles.notificationContent}>
                      <Text style={styles.notificationText}>{item.message || 'Notification'}</Text>
                      <Text style={styles.notificationTime}>
                        {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : 'Maintenant'}
                      </Text>
                    </View>
                    <View style={[
                      styles.statusIndicator,
                      item.status === 'accepté' && styles.acceptedIndicator,
                      item.status === 'refusé' && styles.rejectedIndicator,
                      item.status === 'en cours' && styles.inProgressIndicator,
                    ]} />
                  </TouchableOpacity>
                )}
                style={styles.notificationList}
                showsVerticalScrollIndicator={false}
              />
            ) : (
              <View style={styles.emptyNotifications}>
                <Ionicons name="notifications-off" size={40} color="#ccc" />
                <Text style={styles.emptyText}>Aucune notification</Text>
              </View>
            )}
          </View>
        </TouchableOpacity>
      </Modal>
    </SafeAreaView>
  );
};

// Bottom Tab Navigator avec les sections principales
const MainTabNavigator = () => {
  const navigation = useNavigation();
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else if (route.name === 'Documents') {
            iconName = focused ? 'documents' : 'documents-outline';
          } else if (route.name === 'News') {
            iconName = focused ? 'newspaper' : 'newspaper-outline';
          } else if (route.name === 'DocumentRequest') {
            iconName = focused ? 'document-text' : 'document-text-outline';
          } else if (route.name === 'Chats') {
            iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#002857',
        tabBarInactiveTintColor: '#8e8e93',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e1e1e1',
          height: 70,
          paddingBottom: 10,
          paddingTop: 10,
          elevation: 8,
          shadowColor: '#000',
          shadowOffset: {
            width: 0,
            height: -2,
          },
          shadowOpacity: 0.1,
          shadowRadius: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
          marginTop: 4,
        },
        headerShown: true,
        header: ({ navigation, route }) => (
          <CustomHeader 
            navigation={navigation} 
            title={getHeaderTitle(route.name)}
            showHamburger={true}
          />
        ),
      })}
    >
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreenSimple}
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
        name="News" 
        component={NewsScreenNew}
        options={{
          title: 'Actualités',
        }}
      />
      
      {/* Tabs cachés - accessibles via le drawer seulement */}
      <Tab.Screen 
        name="DocumentRequest" 
        component={DocumentRequestScreen}
        options={{
          title: 'Demander un document',
          tabBarButton: () => null, // Cache ce tab de la bottom navigation
        }}
      />
      <Tab.Screen 
        name="Chats" 
        component={ChatsScreenDepartment}
        options={{
          title: 'Chat avec service',
          tabBarButton: () => null, // Cache ce tab de la bottom navigation
        }}
      />
    </Tab.Navigator>
  );
};

// Fonction helper pour les titres d'en-tête
const getHeaderTitle = (routeName) => {
  switch (routeName) {
    case 'Profile':
      return '🧍‍♂️ Profil';
    case 'Documents':
      return '📄 Mes Documents';
    case 'News':
      return '📰 Actualités';
    case 'DocumentRequest':
      return '📝 Demander un document';
    case 'Chats':
      return '💬 Chat avec service';
    default:
      return 'Leoni App';
  }
};

// Composant personnalisé pour le contenu du Drawer
const CustomDrawerContent = ({ navigation }) => {
  const { logout } = useContext(AuthContext);

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        {
          text: 'Annuler',
          style: 'cancel',
        },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            try {
              await logout();
              // Naviguer vers l'écran de connexion via le root navigator
              const rootNavigation = navigation.getParent?.() || navigation;
              rootNavigation.reset({
                index: 0,
                routes: [{ name: 'Login' }],
              });
            } catch (error) {
              console.error('Erreur lors de la déconnexion:', error);
              Alert.alert('Erreur', 'Impossible de se déconnecter');
            }
          },
        },
      ]
    );
  };

  const menuItems = [
    {
      icon: 'document-text-outline',
      title: 'Demander un document',
      onPress: () => {
        console.log('🔍 Navigation vers DocumentRequest...');
        // Naviguer vers le tab DocumentRequest (caché) via MainTabs
        navigation.navigate('MainTabs', { screen: 'DocumentRequest' });
        navigation.closeDrawer();
        console.log('✅ Navigation DocumentRequest lancée');
      },
    },
    {
      icon: 'chatbubbles-outline',
      title: 'Chat avec service',
      onPress: () => {
        console.log('🔍 Navigation vers Chats...');
        // Naviguer vers le tab Chats (caché) via MainTabs
        navigation.navigate('MainTabs', { screen: 'Chats' });
        navigation.closeDrawer();
        console.log('✅ Navigation Chats lancée');
      },
    },
    {
      icon: 'log-out-outline',
      title: 'Déconnexion',
      onPress: handleLogout,
      isDestructive: true,
    },
  ];

  return (
    <View style={styles.drawerContent}>
      <View style={styles.drawerHeader}>
        <Ionicons name="business" size={40} color="#002857" />
        <Text style={styles.drawerTitle}>Leoni App</Text>
        <Text style={styles.drawerSubtitle}>Menu secondaire</Text>
      </View>

      <View style={styles.drawerItems}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.drawerItem,
              item.isDestructive && styles.drawerItemDestructive
            ]}
            onPress={item.onPress}
          >
            <Ionicons 
              name={item.icon} 
              size={24} 
              color={item.isDestructive ? '#ff6b6b' : '#002857'} 
            />
            <Text style={[
              styles.drawerItemText,
              item.isDestructive && styles.drawerItemTextDestructive
            ]}>
              {item.title}
            </Text>
            <Ionicons 
              name="chevron-forward" 
              size={20} 
              color={item.isDestructive ? '#ff6b6b' : '#8e8e93'} 
            />
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.drawerFooter}>
        <Text style={styles.drawerFooterText}>Leoni Tunisia</Text>
        <Text style={styles.drawerFooterSubtext}>Version 1.0</Text>
      </View>
    </View>
  );
};

// Main Drawer Navigator
const MainNavigator = ({ route }) => {
  const { userData } = route.params || {};
  
  return (
    <Drawer.Navigator
      drawerContent={(props) => <CustomDrawerContent {...props} />}
      screenOptions={{
        headerShown: false,
        drawerStyle: {
          backgroundColor: '#f8f9fa',
          width: 280,
        },
        drawerType: 'slide',
        overlayColor: 'rgba(0, 0, 0, 0.5)',
      }}
    >
      {/* Écran principal avec les tabs - TOUJOURS visible avec bottom navigation */}
      <Drawer.Screen name="MainTabs" component={MainTabNavigator} />
    </Drawer.Navigator>
  );
};

const styles = StyleSheet.create({
  // Header styles
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#002857',
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  hamburgerButton: {
    padding: 8,
    marginRight: 15,
  },
  headerTitle: {
    flex: 1,
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
  },
  headerSpacer: {
    width: 40, // Pour équilibrer avec le bouton hamburger
  },

  // Drawer styles
  drawerContent: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  drawerHeader: {
    backgroundColor: '#ffffff',
    padding: 30,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e1e1',
    marginBottom: 20,
  },
  drawerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#002857',
    marginTop: 15,
  },
  drawerSubtitle: {
    fontSize: 14,
    color: '#8e8e93',
    marginTop: 5,
  },
  drawerItems: {
    flex: 1,
    paddingHorizontal: 10,
  },
  drawerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    padding: 20,
    marginVertical: 5,
    borderRadius: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  drawerItemDestructive: {
    backgroundColor: '#ffe6e6',
    borderWidth: 1,
    borderColor: '#ffcccc',
  },
  drawerItemText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#002857',
    marginLeft: 15,
  },
  drawerItemTextDestructive: {
    color: '#ff6b6b',
  },
  drawerFooter: {
    padding: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e1e1e1',
    marginTop: 20,
  },
  drawerFooterText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#002857',
  },
  drawerFooterSubtext: {
    fontSize: 12,
    color: '#8e8e93',
    marginTop: 5,
  },
  // Styles pour le nouvel en-tête enrichi
  headerSafeArea: {
    backgroundColor: '#002857',
  },
  fullHeader: {
    backgroundColor: '#002857',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  profileSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  profileImageContainer: {
    marginRight: 12,
  },
  profileImage: {
    width: 42,
    height: 42,
    borderRadius: 21,
    borderWidth: 2,
    borderColor: '#ffffff',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 2,
  },
  userDepartment: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  notificationButton: {
    position: 'relative',
    marginRight: 15,
    padding: 8,
  },
  notificationBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#ff6b6b',
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  menuButton: {
    padding: 8,
  },
  // Styles pour les notifications
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-start',
    paddingTop: 90,
  },
  notificationModal: {
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    borderRadius: 12,
    maxHeight: 400,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e1e1',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  notificationList: {
    maxHeight: 320,
  },
  notificationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  unreadNotification: {
    backgroundColor: '#f8f9ff',
  },
  notificationContent: {
    flex: 1,
  },
  notificationText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  notificationTime: {
    fontSize: 12,
    color: '#666',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ccc',
    marginLeft: 12,
  },
  acceptedIndicator: {
    backgroundColor: '#4CAF50',
  },
  rejectedIndicator: {
    backgroundColor: '#F44336',
  },
  inProgressIndicator: {
    backgroundColor: '#FF9800',
  },
  emptyNotifications: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginTop: 12,
  },
});

export default MainNavigator;
