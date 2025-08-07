import AsyncStorage from '@react-native-async-storage/async-storage';
import NetworkService from '../services/NetworkService';
import { BASE_URL } from '../config';

export const getProfile = async () => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    console.log('🔍 PROFILE_CONTROLLER: Appel API /me...');

    const response = await NetworkService.fetch('/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    });

    console.log('🔍 PROFILE_CONTROLLER: Réponse reçue, status =', response.status);

    if (!response.ok) {
      if (response.status === 500) {
        throw new Error('Serveur indisponible. Vérifiez que le backend est démarré.');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('🔍 PROFILE_CONTROLLER: Données reçues:', data);

    if (data.success) {
      return data;
    } else {
      throw new Error(data.message || 'Erreur lors de la récupération du profil');
    }
  } catch (error) {
    console.error('❌ PROFILE_CONTROLLER: Erreur:', error);

    // Gestion spécifique des erreurs de réseau
    if (error.message.includes('fetch') || error.message.includes('Network request failed')) {
      throw new Error('Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur http://localhost:5000');
    }

    if (error.message.includes('Failed to fetch')) {
      throw new Error('Erreur de connexion réseau. Le serveur backend n\'est peut-être pas accessible.');
    }

    throw new Error(error.message || 'Erreur lors de la récupération du profil');
  }
};

export const updateProfile = async (profileData) => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    console.log('🔍 UPDATE_PROFILE_CONTROLLER: Données à envoyer:', profileData);

    // S'assurer que tous les champs requis sont présents (compatibilité avec l'ancienne version du serveur)
    const requestBody = {
      firstName: profileData.firstName || '',
      lastName: profileData.lastName || '',
      email: profileData.email || '',
      phoneNumber: profileData.phoneNumber || '12345678', // Valeur par défaut si vide
      address: profileData.address || '',
      department: profileData.department || 'Non spécifié',
      position: profileData.position || 'Non spécifié',
      parentalEmail: profileData.parentalEmail || '',
      parentalPhoneNumber: profileData.parentalPhoneNumber || '',
      ...profileData,
      updatedAt: new Date()
    };

    console.log('🔍 UPDATE_PROFILE_CONTROLLER: Corps de la requête final:', requestBody);

    const response = await NetworkService.fetch('/update-profile', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    console.log('🔍 UPDATE_PROFILE_CONTROLLER: Réponse status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ UPDATE_PROFILE_CONTROLLER: Erreur serveur:', errorData);
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('🔍 UPDATE_PROFILE_CONTROLLER: Réponse reçue:', data);

    if (data.success) {
      // Mettre à jour les données utilisateur locales si elles incluent une photo de profil
      if (data.user) {
        await AsyncStorage.setItem('userData', JSON.stringify(data.user));
        console.log('✅ UPDATE_PROFILE_CONTROLLER: Données locales mises à jour');
      }
      return data;
    } else {
      throw new Error(data.message || 'Erreur lors de la mise à jour du profil');
    }
  } catch (error) {
    console.error('❌ UPDATE_PROFILE_CONTROLLER: Erreur:', error);
    throw new Error(error.message || 'Failed to update profile');
  }
};

export const uploadProfilePicture = async (imageUri) => {
  try {
    const token = await AsyncStorage.getItem('userToken');
    if (!token) {
      throw new Error('Token non trouvé');
    }

    // Convertir l'image en base64
    const response = await fetch(imageUri);
    const blob = await response.blob();

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64data = reader.result;

          const uploadResponse = await fetch(`${BASE_URL}/upload-profile-picture`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              imageData: base64data
            })
          });

          if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
          }

          const data = await uploadResponse.json();
          if (data.success) {
            resolve(data);
          } else {
            throw new Error(data.message || 'Erreur lors de l\'upload');
          }
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Erreur lecture fichier'));
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    throw new Error(error.message || 'Erreur lors de l\'upload de l\'image');
  }
};

export const logout = async () => {
  try {
    await AsyncStorage.multiRemove(['userToken', 'userData']);
    return { success: true };
  } catch (error) {
    throw new Error('Erreur lors de la déconnexion');
  }
};
