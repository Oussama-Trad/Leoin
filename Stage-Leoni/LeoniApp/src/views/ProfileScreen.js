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

const ProfileScreen = () => {
  const navigation = useNavigation();
  const { currentUser, logout: authLogout } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [tempProfileImage, setTempProfileImage] = useState(null); // Image temporaire en mode édition
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
    // Vider le cache au démarrage pour forcer le rechargement
    clearCacheAndFetchProfile();
  }, []);

  const clearCacheAndFetchProfile = async () => {
    try {
      // Vider complètement les données locales corrompues
      await AsyncStorage.removeItem('userData');
      console.log('🗑️ PROFILE: Cache vidé - rechargement depuis le serveur');
      
      // Recharger depuis le serveur
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

        // Utiliser DIRECTEMENT les données du serveur (elles sont correctes)
        const userData = response.user;

        // Sauvegarder les données du serveur
        await AsyncStorage.setItem('userData', JSON.stringify(userData));
        console.log('✅ PROFILE: Données du serveur sauvegardées:', userData);

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
      // Charger les données locales en cas d'erreur serveur
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

        // Utiliser les données locales telles quelles (ne pas forcer "Non spécifié")
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

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };



  const handleUpdate = async () => {
    try {
      // Validation côté client
      if (!formData.firstName.trim()) {
        Alert.alert('Erreur', 'Le prénom est requis');
        return;
      }
      if (!formData.lastName.trim()) {
        Alert.alert('Erreur', 'Le nom est requis');
        return;
      }
      if (!formData.email.trim()) {
        Alert.alert('Erreur', 'L\'adresse1 est requise');
        return;
      }
      if (!validateEmail(formData.email.trim())) {
        Alert.alert('Erreur', 'Format d\'adresse1 invalide');
        return;
      }

      console.log('🔍 PROFILE_SCREEN: Données du formulaire:', formData);

      // Préparer les données à mettre à jour, incluant la photo de profil si elle a changé
      const updateData = {
        firstName: formData.firstName.trim(),
        lastName: formData.lastName.trim(),
        email: formData.email.trim(),
        phoneNumber: formData.phone ? formData.phone.trim() : (profile?.phoneNumber || ''), // Utiliser la valeur existante ou vide
        address: formData.address ? formData.address.trim() : (profile?.address || ''),
        location: formData.location ? formData.location.trim() : (profile?.location || ''),
        department: formData.department ? formData.department.trim() : (profile?.department || ''),
        position: formData.position ? formData.position.trim() : (profile?.position || ''),
        // Préserver les champs parentaux existants
        parentalEmail: profile?.parentalEmail || '',
        parentalPhoneNumber: profile?.parentalPhoneNumber || ''
      };

      // Si une nouvelle image a été sélectionnée, l'inclure dans la mise à jour
      if (tempProfileImage && tempProfileImage !== profileImage) {
        updateData.profilePicture = tempProfileImage;
      }

      console.log('🔍 PROFILE_SCREEN: Données à envoyer:', updateData);

      await updateProfile(updateData);

      // Mettre à jour l'image de profil locale si elle a changé
      if (tempProfileImage && tempProfileImage !== profileImage) {
        setProfileImage(tempProfileImage);
      }

      setEditMode(false);
      setTempProfileImage(null); // Réinitialiser l'image temporaire
      fetchProfile();
      Alert.alert('Succès', 'Profil mis à jour avec succès');
    } catch (error) {
      console.error('❌ PROFILE_SCREEN: Erreur mise à jour profil:', error);
      Alert.alert('Erreur', error.message || 'Impossible de mettre à jour le profil');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      authLogout();
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    } catch (error) {
      console.error('Erreur déconnexion:', error);
      Alert.alert('Erreur', 'Impossible de se déconnecter');
    }
  };

  // Fonction pour sélectionner une image
  const pickImage = async () => {
    // Ne permettre la sélection d'image qu'en mode édition
    if (!editMode) {
      Alert.alert('Information', 'Veuillez d\'abord appuyer sur "Modifier mes informations" pour changer votre photo de profil.');
      return;
    }

    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Nous avons besoin de la permission pour accéder à vos photos');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled) {
        const imageUri = result.assets[0].uri;

        // Convertir l'image en base64 pour la stocker temporairement
        try {
          const response = await fetch(imageUri);
          const blob = await response.blob();

          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = reader.result;
            setTempProfileImage(base64data);
            Alert.alert('Information', 'Photo sélectionnée. Appuyez sur "Sauvegarder" pour confirmer les modifications.');
          };
          reader.readAsDataURL(blob);
        } catch (error) {
          console.error('Erreur conversion image:', error);
          Alert.alert('Erreur', 'Impossible de traiter l\'image sélectionnée');
        }
      }
    } catch (error) {
      console.error('Erreur sélection image:', error);
      Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Indicateur de statut de connexion */}
      <ConnectionStatus />

      {/* Header avec gradient */}
      <View style={styles.header}>
        <View style={styles.profileImageContainer}>
          <TouchableOpacity onPress={pickImage} style={styles.imageWrapper}>
            {(editMode && tempProfileImage) || profileImage || profile?.profilePicture ? (
              <Image
                source={{ uri: (editMode && tempProfileImage) || profileImage || profile.profilePicture }}
                style={styles.profileImage}
              />
            ) : (
              <View style={styles.defaultAvatar}>
                <Ionicons name="person" size={50} color="#fff" />
              </View>
            )}
            <View style={styles.cameraIcon}>
              <Ionicons name="camera" size={20} color="#fff" />
            </View>
          </TouchableOpacity>
          
          {profile && (
            <View style={styles.userInfo}>
              <Text style={styles.userName}>
                {profile.firstName} {profile.lastName}
              </Text>
              <Text style={styles.userRole}>
                {profile.position || 'Employé'} • {profile.employeeId}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Contenu principal */}
      <View style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#002857" />
            <Text style={styles.loadingText}>Chargement du profil...</Text>
          </View>
        ) : profile ? (
          <>
            {editMode ? (
              <View style={styles.editForm}>
                <Text style={styles.sectionTitle}>Modifier le profil</Text>
                
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Prénom</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.firstName}
                    onChangeText={(value) => handleInputChange('firstName', value)}
                    placeholder="Entrez votre prénom"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Nom</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.lastName}
                    onChangeText={(value) => handleInputChange('lastName', value)}
                    placeholder="Entrez votre nom"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Adresse1</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.email}
                    onChangeText={(value) => handleInputChange('email', value)}
                    placeholder="Entrez votre adresse1"
                    keyboardType="email-address"
                    autoCapitalize="none"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Téléphone</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.phone}
                    onChangeText={(value) => handleInputChange('phone', value)}
                    placeholder="Entrez votre téléphone"
                    keyboardType="phone-pad"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Adresse</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.address}
                    onChangeText={(value) => handleInputChange('address', value)}
                    placeholder="Entrez votre adresse"
                    multiline
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Site de travail</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.location}
                    onChangeText={(value) => handleInputChange('location', value)}
                    placeholder="Entrez votre site de travail"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Département</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.department}
                    onChangeText={(value) => handleInputChange('department', value)}
                    placeholder="Entrez votre département"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Poste</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.position}
                    onChangeText={(value) => handleInputChange('position', value)}
                    placeholder="Entrez votre poste"
                  />
                </View>
                
                <View style={styles.buttonGroup}>
                  <TouchableOpacity style={styles.saveButton} onPress={handleUpdate}>
                    <Ionicons name="checkmark" size={20} color="#fff" />
                    <Text style={styles.buttonText}>Sauvegarder</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.cancelButton} onPress={() => {
                    setEditMode(false);
                    setTempProfileImage(null); // Réinitialiser l'image temporaire
                  }}>
                    <Ionicons name="close" size={20} color="#666" />
                    <Text style={styles.cancelButtonText}>Annuler</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <View style={styles.profileInfo}>
                <Text style={styles.sectionTitle}>Informations personnelles</Text>
                
                <View style={styles.infoCard}>
                  <View style={styles.infoRow}>
                    <Ionicons name="person-outline" size={20} color="#002857" />
                    <View style={styles.infoContent}>
                      <Text style={styles.infoLabel}>Nom complet</Text>
                      <Text style={styles.infoValue}>
                        {profile.firstName} {profile.lastName}
                      </Text>
                    </View>
                  </View>

                  <View style={styles.infoRow}>
                    <Ionicons name="mail-outline" size={20} color="#002857" />
                    <View style={styles.infoContent}>
                      <Text style={styles.infoLabel}>Adresse1</Text>
                      <Text style={styles.infoValue}>{profile.email}</Text>
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
                    <Ionicons name="mail-outline" size={20} color="#002857" />
                    <View style={styles.infoContent}>
                      <Text style={styles.infoLabel}>Adresse2</Text>
                      <Text style={styles.infoValue}>
                        {profile.parentalEmail || 'Non renseigné'}
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
                    <Ionicons name="id-card-outline" size={20} color="#002857" />
                    <View style={styles.infoContent}>
                      <Text style={styles.infoLabel}>ID employé</Text>
                      <Text style={styles.infoValue}>{profile.employeeId}</Text>
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
                    <Ionicons name="location-outline" size={20} color="#002857" />
                    <View style={styles.infoContent}>
                      <Text style={styles.infoLabel}>Adresse</Text>
                      <Text style={styles.infoValue}>
                        {profile.address || 'Non renseigné'}
                      </Text>
                    </View>
                  </View>
                </View>

                <View style={styles.actionButtons}>
                  <TouchableOpacity style={styles.editButton} onPress={() => setEditMode(true)}>
                    <Ionicons name="create-outline" size={20} color="#fff" />
                    <Text style={styles.buttonText}>Modifier le profil</Text>
                  </TouchableOpacity>

                  <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                    <Ionicons name="log-out-outline" size={20} color="#fff" />
                    <Text style={styles.buttonText}>Se déconnecter</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}
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
  header: {
    backgroundColor: '#002857',
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    paddingBottom: 30,
    paddingHorizontal: 20,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  profileImageContainer: {
    alignItems: 'center',
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
    borderColor: '#fff',
  },
  defaultAvatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#fff',
  },
  cameraIcon: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    backgroundColor: '#28a745',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#fff',
  },
  userInfo: {
    alignItems: 'center',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  userRole: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  offlineText: {
    marginTop: 10,
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  editForm: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#f8f9fa',
  },
  buttonGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  saveButton: {
    backgroundColor: '#28a745',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
    flex: 0.48,
  },
  cancelButton: {
    backgroundColor: '#f8f9fa',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    flex: 0.48,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 5,
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 5,
  },
  profileInfo: {
    flex: 1,
  },
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoContent: {
    marginLeft: 15,
    flex: 1,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  actionButtons: {
    gap: 15,
  },
  editButton: {
    backgroundColor: '#002857',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
});

export default ProfileScreen;
