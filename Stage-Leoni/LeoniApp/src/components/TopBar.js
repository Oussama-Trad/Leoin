import React, { useContext, useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
  SafeAreaView,
  Modal,
  FlatList
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import UserModel from '../models/UserModel';
import AuthController from '../controllers/AuthController';
import DocumentController from '../controllers/DocumentController';
import { AuthContext } from '../contexts/AuthContext';
import { getProfile } from '../controllers/ProfileController';

const TopBar = ({ userData, navigation, hideOnProfile = false, currentRoute }) => {
  const { currentUser, logout: contextLogout } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [freshUserData, setFreshUserData] = useState(null);
  
  // Utiliser userData des props ou currentUser du contexte, ou les données fraîches
  const userDataToUse = freshUserData || userData || currentUser;

  // Récupérer les données fraîches de l'utilisateur au chargement
  useEffect(() => {
    const fetchFreshUserData = async () => {
      try {
        console.log('🔄 TopBar: Récupération des données fraîches...');
        const response = await getProfile();
        if (response.success && response.user) {
          console.log('✅ TopBar: Données fraîches récupérées:', response.user.department);
          setFreshUserData(response.user);
        }
      } catch (error) {
        console.error('❌ TopBar: Erreur lors de la récupération des données fraîches:', error);
        // En cas d'erreur, utiliser les données existantes
      }
    };

    fetchFreshUserData();
  }, []);

  // Vérifier les notifications de changement de statut
  useEffect(() => {
    const checkNotifications = async () => {
      try {
        const result = await DocumentController.getDocumentRequests();
        if (result.success && result.data) {
          const newNotifications = [];
          
          result.data.forEach(doc => {
            // Validation stricte des propriétés du document
            if (!doc || typeof doc !== 'object') return;
            
            if (doc.status?.current && doc.status.current !== 'en attente') {
              const docId = doc.id || doc._id;
              const docType = doc.type || doc.documentType;
              
              // Validation stricte des propriétés requises
              if (docId && docType && typeof docId === 'string' && typeof docType === 'string') {
                const notificationId = `${docId}_${doc.status.current}`;
                
                // Vérifier si cette notification a déjà été vue
                const isRead = false; // TODO: implémenter le stockage des notifications lues
                
                newNotifications.push({
                  id: notificationId,
                  documentId: docId,
                  documentType: docType,
                  status: doc.status.current,
                  message: `Votre demande de "${docType}" est maintenant "${doc.status.current}"`,
                  timestamp: doc.updatedAt || doc.createdAt || new Date(),
                  isRead
                });
              }
            }
          });
          
          // Validation des notifications avant de les définir
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
      // Vérifier les notifications toutes les 30 secondes
      const interval = setInterval(checkNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [userDataToUse]);

  // Ne pas afficher la barre sur la page "Mon profil"
  if (hideOnProfile && currentRoute === 'Profile') {
    return null;
  }

  if (!userDataToUse) {
    return null; // Ne pas afficher si pas de données utilisateur
  }

  // Vérification de sécurité pour les données utilisateur
  if (typeof userDataToUse !== 'object' || userDataToUse === null) {
    console.warn('TopBar: userData invalide:', userDataToUse);
    return null;
  }

  const user = new UserModel(userDataToUse);

  // Protection supplémentaire pour éviter les erreurs de rendu
  try {
    if (!user.getFullName || typeof user.getFullName !== 'function') {
      console.error('TopBar: UserModel getFullName invalid:', user);
      return null;
    }
  } catch (error) {
    console.error('TopBar: Erreur lors de la validation user:', error);
    return null;
  }

  const markNotificationAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const renderNotification = ({ item }) => (
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
  );

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
              // Déconnexion côté serveur/stockage
              await AuthController.logout();
              
              // Mettre à jour le contexte
              contextLogout();
              
              // Navigation vers la page de connexion
              navigation.reset({
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

  const getProfileImage = () => {
    if (user.profilePicture) {
      // Si c'est une URL complète
      if (user.profilePicture.startsWith('http')) {
        return { uri: user.profilePicture };
      }
      // Si c'est un chemin local
      return { uri: user.profilePicture };
    }
    // Image par défaut si pas de photo de profil
    return require('../../assets/leoni_tunisia_logo.png');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
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
            {unreadCount > 0 ? (
              <View style={styles.notificationBadge}>
                <Text style={styles.badgeText}>{String(unreadCount)}</Text>
              </View>
            ) : null}
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => navigation?.openDrawer()}
          >
            <Ionicons name="menu" size={28} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Modal des notifications */}
      <Modal
        visible={showNotifications}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowNotifications(false)}
      >
        <View style={styles.notificationModalOverlay}>
          <View style={styles.notificationModalContent}>
            <View style={styles.notificationHeader}>
              <Text style={styles.notificationTitle}>Notifications</Text>
              <TouchableOpacity onPress={() => setShowNotifications(false)}>
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            {notifications.length > 0 ? (
              <FlatList
                data={notifications}
                renderItem={renderNotification}
                keyExtractor={(item) => item.id}
                style={styles.notificationList}
                showsVerticalScrollIndicator={false}
              />
            ) : (
              <View style={styles.emptyNotifications}>
                <MaterialIcons name="notifications-none" size={48} color="#ccc" />
                <Text style={styles.emptyNotificationsText}>
                  Aucune notification pour le moment
                </Text>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: '#002857', // Couleur Leoni
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    zIndex: 1000,
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#002857', // Couleur Leoni
    paddingHorizontal: 15,
    paddingVertical: 12,
    minHeight: 60, // Hauteur réduite pour un meilleur centrage
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
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  userDepartment: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    marginTop: 2,
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuButton: {
    padding: 8,
    marginLeft: 5,
  },
  logoutButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 10,
    borderRadius: 20,
    marginLeft: 10,
  },
  notificationButton: {
    position: 'relative',
    padding: 8,
    marginRight: 10,
  },
  notificationBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#ff3333',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  notificationModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  notificationModalContent: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '70%',
    paddingBottom: 20,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  notificationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  notificationList: {
    paddingHorizontal: 15,
  },
  notificationItem: {
    flexDirection: 'row',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    backgroundColor: '#ffffff',
  },
  unreadNotification: {
    backgroundColor: '#f8f9ff',
  },
  notificationContent: {
    flex: 1,
    marginRight: 10,
  },
  notificationText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5,
  },
  notificationTime: {
    fontSize: 12,
    color: '#666',
  },
  statusIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#ccc',
    alignSelf: 'center',
  },
  acceptedIndicator: {
    backgroundColor: '#28a745',
  },
  rejectedIndicator: {
    backgroundColor: '#dc3545',
  },
  inProgressIndicator: {
    backgroundColor: '#ffc107',
  },
  emptyNotifications: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyNotificationsText: {
    fontSize: 16,
    color: '#999',
    marginTop: 10,
    textAlign: 'center',
  },
});

export default TopBar;
