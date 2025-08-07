import React, { useState, useEffect, useContext } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Image,
  ScrollView,
  Platform
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getProfile, updateProfile, logout } from '../controllers/ProfileController';
import { AuthContext } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ConnectionStatus from '../components/ConnectionStatus';

const ProfileScreenSimple = () => {
  const navigation = useNavigation();
  const { currentUser, logout: authLogout } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [tempProfileImage, setTempProfileImage] = useState(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    address: '',
    location: '',
    department: '',
    position: ''
  });

  useEffect(() => {
    clearCacheAndFetchProfile();
  }, []);

  const clearCacheAndFetchProfile = async () => {
    try {
      await AsyncStorage.removeItem('userData');
      console.log('🗑️ PROFILE: Cache vidé - rechargement depuis le serveur');
      await fetchProfile();
    } catch (error) {
      console.error('❌ PROFILE: Erreur lors du vidage du cache:', error);
      await fetchProfile();
    }
  };

  const fetchProfile = async () => {
    setLoading(true);
    try {
      console.log('🔍 PROFILE: Chargement du profil...');
      const response = await getProfile();
      console.log('🔍 PROFILE: Réponse reçue:', response);

      if (response && response.user) {
        console.log('🔍 PROFILE: Données utilisateur reçues:', response.user);

        const userData = response.user;
        await AsyncStorage.setItem('userData', JSON.stringify(userData));
        console.log('✅ PROFILE: Données du serveur sauvegardées');

        // Log détaillé de chaque champ
        console.log('📋 PROFILE: Détail des champs:');
        console.log('   - firstName:', userData.firstName);
        console.log('   - lastName:', userData.lastName);
        console.log('   - adresse1:', userData.adresse1);
        console.log('   - phoneNumber:', userData.phoneNumber);
        console.log('   - adresse2:', userData.adresse2);
        console.log('   - parentalPhoneNumber:', userData.parentalPhoneNumber);
        console.log('   - employeeId:', userData.employeeId);
        console.log('   - location:', userData.location);
        console.log('   - department:', userData.department);
        console.log('   - position:', userData.position);
        console.log('   - address:', userData.address);

        setProfile(userData);
        setProfileImage(userData.profilePicture || null);
        setFormData({
          firstName: userData.firstName || '',
          lastName: userData.lastName || '',
          email: userData.adresse1 || '',
          phone: userData.phoneNumber || '',
          address: userData.address || '',
          location: userData.location || '',
          department: userData.department || '',
          position: userData.position || ''
        });
        console.log('✅ PROFILE: Profil chargé avec succès');
      } else {
        console.error('❌ PROFILE: Réponse invalide:', response);
        await loadLocalProfile();
      }
    } catch (error) {
      console.error('❌ PROFILE: Erreur lors du chargement du profil:', error);
      await loadLocalProfile();
      console.log('🔍 PROFILE: Utilisation des données locales en mode hors ligne');
    } finally {
      setLoading(false);
    }
  };

  const loadLocalProfile = async () => {
    try {
      console.log('🔍 PROFILE: Chargement des données locales...');
      const userData = await AsyncStorage.getItem('userData');
      if (userData) {
        const user = JSON.parse(userData);
        console.log('🔍 PROFILE: Données locales trouvées:', user);

        setProfile(user);
        setFormData({
          firstName: user.firstName || '',
          lastName: user.lastName || '',
          email: user.adresse1 || '',
          phone: user.phoneNumber || '',
          address: user.address || '',
          location: user.location || '',
          department: user.department || '',
          position: user.position || ''
        });
        console.log('✅ PROFILE: Profil chargé depuis les données locales');
      } else {
        console.log('❌ PROFILE: Aucune donnée locale trouvée');
        setProfile(null);
      }
    } catch (error) {
      console.error('❌ PROFILE: Erreur chargement données locales:', error);
      setProfile(null);
    }
  };

  const handleLogout = async () => {
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
              await authLogout();
              // Naviguer vers l'écran de connexion via le root navigator
              const rootNavigation = navigation.getParent?.()?.getParent?.() || navigation;
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

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#002857" />
        <Text style={styles.loadingText}>Chargement du profil...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {profile ? (
          <>
            {/* Section Image de profil */}
            <View style={styles.profileImageSection}>
              <View style={styles.imageWrapper}>
                {profileImage ? (
                  <Image source={{ uri: profileImage }} style={styles.profileImage} />
                ) : (
                  <View style={styles.defaultAvatar}>
                    <Ionicons name="person" size={50} color="#ffffff" />
                  </View>
                )}
              </View>
              <Text style={styles.userName}>
                {profile.firstName} {profile.lastName}
              </Text>
              <Text style={styles.userEmail}>{profile.adresse1}</Text>
            </View>

            {/* Informations du profil */}
            <View style={styles.infoSection}>
              <View style={styles.infoRow}>
                <Ionicons name="mail-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Adresse1</Text>
                  <Text style={styles.infoValue}>
                    {profile.adresse1 || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="call-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Téléphone</Text>
                  <Text style={styles.infoValue}>
                    {profile.phoneNumber || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="call-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Téléphone parental</Text>
                  <Text style={styles.infoValue}>
                    {profile.parentalPhoneNumber || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="mail-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Adresse2</Text>
                  <Text style={styles.infoValue}>
                    {profile.adresse2 || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="card-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>ID Employé</Text>
                  <Text style={styles.infoValue}>
                    {profile.employeeId || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="location-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Site de travail</Text>
                  <Text style={styles.infoValue}>
                    {profile.location || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="business-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Département</Text>
                  <Text style={styles.infoValue}>
                    {profile.department || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="briefcase-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Poste</Text>
                  <Text style={styles.infoValue}>
                    {profile.position || 'Non renseigné'}
                  </Text>
                </View>
              </View>

              <View style={styles.infoRow}>
                <Ionicons name="home-outline" size={20} color="#002857" />
                <View style={styles.infoContent}>
                  <Text style={styles.infoLabel}>Adresse</Text>
                  <Text style={styles.infoValue}>
                    {profile.address || 'Non renseigné'}
                  </Text>
                </View>
              </View>
            </View>

            {/* Boutons d'action */}
            <View style={styles.actionButtons}>
              <TouchableOpacity style={[styles.button, styles.editButton]} onPress={() => setEditMode(true)}>
                <Ionicons name="create-outline" size={20} color="#fff" />
                <Text style={styles.buttonText}>Modifier le profil</Text>
              </TouchableOpacity>

              <TouchableOpacity style={[styles.button, styles.logoutButton]} onPress={handleLogout}>
                <Ionicons name="log-out-outline" size={20} color="#fff" />
                <Text style={styles.buttonText}>Se déconnecter</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          <View style={styles.loadingContainer}>
            <Ionicons name="cloud-offline" size={48} color="#ccc" />
            <Text style={styles.loadingText}>Profil indisponible</Text>
            <Text style={styles.offlineText}>
              Aucune donnée disponible.{'\n'}
              Connectez-vous pour charger votre profil.
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  profileImageSection: {
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 30,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  imageWrapper: {
    position: 'relative',
    marginBottom: 15,
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 4,
    borderColor: '#002857',
  },
  defaultAvatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#002857',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#002857',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 16,
    color: '#6c757d',
  },
  infoSection: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f1f1',
  },
  infoContent: {
    marginLeft: 15,
    flex: 1,
  },
  infoLabel: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#343a40',
    fontWeight: '500',
  },
  actionButtons: {
    gap: 15,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
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
  editButton: {
    backgroundColor: '#002857',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 10,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    fontSize: 18,
    color: '#4A5568',
    marginTop: 16,
    fontWeight: '500',
  },
  offlineText: {
    fontSize: 14,
    color: '#718096',
    textAlign: 'center',
    marginTop: 10,
    lineHeight: 20,
  },
});

export default ProfileScreenSimple;
