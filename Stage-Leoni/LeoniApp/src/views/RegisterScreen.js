import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  KeyboardAvoidingView, 
  Platform, 
  ScrollView, 
  Alert 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AuthController from '../controllers/AuthController';
import LocationService from '../services/LocationService';
import SimplePicker from '../components/SimplePicker';

export default function RegisterScreen({ navigation }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    adresse1: '',
    adresse2: '',
    phoneNumber: '',
    parentalPhoneNumber: '',
    password: '',
    confirmPassword: '',
    location: '',
    department: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [locations, setLocations] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDepartments, setLoadingDepartments] = useState(false);

  useEffect(() => {
    loadLocations();
  }, []);

  useEffect(() => {
    if (formData.location) {
      loadDepartments(formData.location);
    } else {
      setDepartments([]);
      setFormData(prev => ({ ...prev, department: '' }));
    }
  }, [formData.location]);

  const loadLocations = async () => {
    try {
      setLoading(true);
      const result = await LocationService.getLocations();
      
      if (result.success && result.locations) {
        const locationOptions = result.locations.map(location => ({
          label: location.name,
          value: location.name  // Utiliser le nom au lieu de l'ID
        }));
        setLocations(locationOptions);
        console.log('✅ RegisterScreen: Locations chargées:', locationOptions);
      } else {
        console.log('❌ RegisterScreen: Erreur chargement locations:', result.message);
        Alert.alert('Erreur', 'Impossible de charger les sites');
      }
    } catch (error) {
      console.error('❌ RegisterScreen: Exception locations:', error);
      Alert.alert('Erreur', 'Erreur lors du chargement des sites');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async (locationName) => {
    try {
      setLoadingDepartments(true);
      const result = await LocationService.getDepartmentsByLocationName(locationName);
      
      if (result.success && result.departments) {
        const departmentOptions = result.departments.map(dept => ({
          label: dept.name,
          value: dept.name  // Utiliser le nom au lieu de l'ID
        }));
        setDepartments(departmentOptions);
        console.log('✅ RegisterScreen: Départements chargés pour', locationName, ':', departmentOptions);
      } else {
        console.log('❌ RegisterScreen: Aucun département trouvé pour', locationName);
        setDepartments([]);
      }
    } catch (error) {
      console.error('❌ RegisterScreen: Exception départements:', error);
      setDepartments([]);
    } finally {
      setLoadingDepartments(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleRegister = async () => {
    // Validation simple
    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas');
      return;
    }

    // Validation des champs obligatoires
    if (!formData.firstName || !formData.lastName || !formData.adresse1 || !formData.adresse2 || !formData.phoneNumber || !formData.parentalPhoneNumber || !formData.password || !formData.location || !formData.department) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      console.log('Attempting registration with:', { ...formData, password: '***' });
      const result = await AuthController.handleRegister(formData);
      
      console.log('Registration response:', result);
      
      if (result.success) {
        Alert.alert('Succès', 'Inscription réussie !', [
          { text: 'OK', onPress: () => navigation.navigate('Login') }
        ]);
      } else {
        Alert.alert('Erreur', result.message || "Erreur lors de l'inscription");
      }
    } catch (error) {
      console.error('Registration error:', error);
      Alert.alert('Erreur', 'Une erreur est survenue lors de l\'inscription');
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: '#002857' }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          <View style={styles.content}>
            {/* Header */}
            <View style={styles.header}>
              <TouchableOpacity
                style={styles.backButton}
                onPress={() => navigation.goBack()}
              >
                <Ionicons name="arrow-back" size={24} color="#ffffff" />
              </TouchableOpacity>
              <Text style={styles.title}>S'inscrire</Text>
            </View>

            {/* Formulaire */}
            <View style={styles.form}>
              <View style={styles.inputContainer}>
                <Ionicons name="person-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Prénom"
                  placeholderTextColor="#9ca3af"
                  value={formData.firstName}
                  onChangeText={(value) => handleInputChange('firstName', value)}
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="person-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Nom"
                  placeholderTextColor="#9ca3af"
                  value={formData.lastName}
                  onChangeText={(value) => handleInputChange('lastName', value)}
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="mail-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Adresse1"
                  placeholderTextColor="#9ca3af"
                  value={formData.adresse1}
                  onChangeText={(value) => handleInputChange('adresse1', value)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="mail-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Adresse2"
                  placeholderTextColor="#9ca3af"
                  value={formData.adresse2}
                  onChangeText={(value) => handleInputChange('adresse2', value)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="call-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Numéro de téléphone"
                  placeholderTextColor="#9ca3af"
                  value={formData.phoneNumber}
                  onChangeText={(value) => handleInputChange('phoneNumber', value)}
                  keyboardType="phone-pad"
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="call-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Numéro de téléphone parental (optionnel)"
                  placeholderTextColor="#9ca3af"
                  value={formData.parentalPhoneNumber}
                  onChangeText={(value) => handleInputChange('parentalPhoneNumber', value)}
                  keyboardType="phone-pad"
                />
              </View>

              {/* Site de travail */}
              <View style={styles.inputContainer}>
                <Ionicons name="business-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <SimplePicker
                  data={locations}
                  selectedValue={formData.location}
                  onValueChange={(value) => handleInputChange('location', value)}
                  placeholder={loading ? "Chargement..." : "Sélectionnez votre site"}
                  disabled={loading}
                  style={styles.pickerWrapper}
                />
              </View>

              {/* Département */}
              <View style={styles.inputContainer}>
                <Ionicons name="layers-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <SimplePicker
                  data={departments}
                  selectedValue={formData.department}
                  onValueChange={(value) => handleInputChange('department', value)}
                  placeholder={loadingDepartments ? "Chargement..." : 
                             !formData.location ? "Sélectionnez d'abord un site" : 
                             "Sélectionnez votre département"}
                  disabled={!formData.location || loadingDepartments}
                  style={styles.pickerWrapper}
                />
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="lock-closed-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Mot de passe"
                  placeholderTextColor="#9ca3af"
                  value={formData.password}
                  onChangeText={(value) => handleInputChange('password', value)}
                  secureTextEntry={!showPassword}
                />
                <TouchableOpacity
                  style={styles.eyeIcon}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Ionicons
                    name={showPassword ? "eye-off-outline" : "eye-outline"}
                    size={20}
                    color="#667eea"
                  />
                </TouchableOpacity>
              </View>

              <View style={styles.inputContainer}>
                <Ionicons name="lock-closed-outline" size={20} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Confirmer le mot de passe"
                  placeholderTextColor="#9ca3af"
                  value={formData.confirmPassword}
                  onChangeText={(value) => handleInputChange('confirmPassword', value)}
                  secureTextEntry={!showConfirmPassword}
                />
                <TouchableOpacity
                  style={styles.eyeIcon}
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  <Ionicons
                    name={showConfirmPassword ? "eye-off-outline" : "eye-outline"}
                    size={20}
                    color="#667eea"
                  />
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={styles.registerButton}
                onPress={handleRegister}
              >
                <Text style={styles.registerButtonText}>S'inscrire</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.loginLink}
                onPress={() => navigation.navigate('Login')}
              >
                <Text style={styles.loginLinkText}>
                  Déjà un compte ? <Text style={styles.loginLinkTextBold}>Se connecter</Text>
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 40,
  },
  backButton: {
    marginRight: 16,
    padding: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  form: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 24,
    marginBottom: 32,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    marginBottom: 16,
    paddingLeft: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    minHeight: 50,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#2d3748',
  },
  eyeIcon: {
    padding: 8,
  },
  registerButton: {
    backgroundColor: '#667eea',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  registerButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  loginLink: {
    alignItems: 'center',
  },
  loginLinkText: {
    color: '#667eea',
    fontSize: 14,
  },
  loginLinkTextBold: {
    fontWeight: 'bold',
  },
  pickerWrapper: {
    flex: 1,
    marginLeft: 12,
  },
});
