import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import DocumentController from '../controllers/DocumentController';
import DocumentRequestModel from '../models/DocumentRequestModel';
import { useNavigation } from '@react-navigation/native';

const DocumentRequestScreen = () => {
  const navigation = useNavigation();
  const [documentType, setDocumentType] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingTypes, setLoadingTypes] = useState(true);
  const [documentTypes, setDocumentTypes] = useState([]);
  const [selectedDocumentTypeId, setSelectedDocumentTypeId] = useState('');

  const [showDropdown, setShowDropdown] = useState(false);

  // Charger les types de documents au démarrage
  useEffect(() => {
    loadDocumentTypes();
  }, []);

  const loadDocumentTypes = async () => {
    try {
      setLoadingTypes(true);
      const result = await DocumentController.getDocumentTypes();
      
      if (result.success && result.documentTypes) {
        setDocumentTypes(result.documentTypes);
        console.log('✅ Types de documents chargés:', result.documentTypes.length);
      } else {
        console.warn('⚠️ Échec du chargement des types, utilisation des types par défaut');
        // Fallback vers les types par défaut
        const defaultTypes = DocumentRequestModel.DOCUMENT_TYPES || [
          'Attestation de travail',
          'Certificat de salaire', 
          'Congé',
          'Formation',
          'Autre'
        ];
        // Convertir en format compatible
        setDocumentTypes(defaultTypes.map((name, index) => ({
          _id: `default_${index}`,
          name: name,
          description: `Type de document: ${name}`,
          active: true
        })));
      }
    } catch (error) {
      console.error('❌ Erreur lors du chargement des types:', error);
      // Fallback vers les types par défaut
      const defaultTypes = DocumentRequestModel.DOCUMENT_TYPES || [
        'Attestation de travail',
        'Certificat de salaire', 
        'Congé',
        'Formation',
        'Autre'
      ];
      setDocumentTypes(defaultTypes.map((name, index) => ({
        _id: `default_${index}`,
        name: name,
        description: `Type de document: ${name}`,
        active: true
      })));
    } finally {
      setLoadingTypes(false);
    }
  };

  const handleSubmit = async () => {
    if (!documentType.trim()) {
      Alert.alert('Erreur', 'Veuillez sélectionner un type de document');
      return;
    }

    try {
      setIsLoading(true);

      const requestData = {
        documentType: documentType.trim(),
        description: description.trim(),
        urgency: 'normale' // valeur par défaut
      };

      console.log('📄 Création demande de document:', requestData);

      const result = await DocumentController.createDocumentRequest(requestData);

      console.log('🔍 DocumentRequestScreen: Résultat reçu du controller:', result);
      console.log('🔍 DocumentRequestScreen: result.success =', result.success);
      console.log('🔍 DocumentRequestScreen: result.errors =', result.errors);

      if (result.success) {
        // 🎉 MESSAGE DE SUCCÈS AMÉLIORÉ
        Alert.alert(
          '✅ Demande Envoyée !', 
          `Votre demande de "${documentType}" a été créée avec succès.\n\nElle apparaîtra dans votre liste de demandes.`,
          [
            {
              text: 'Voir mes documents',
              onPress: () => {
                // Réinitialiser le formulaire
                setDocumentType('');
                setDescription('');
                setSelectedDocumentTypeId('');
                console.log('✅ Formulaire réinitialisé après succès');
                // Navigation vers l'onglet Documents
                navigation.navigate('Documents');
              }
            },
            {
              text: 'OK',
              onPress: () => {
                // Réinitialiser le formulaire
                setDocumentType('');
                setDescription('');
                setSelectedDocumentTypeId('');
                console.log('✅ Formulaire réinitialisé après succès');
              }
            }
          ]
        );
      } else {
        Alert.alert(
          'Erreur', 
          result.message || 'Erreur lors de l\'envoi de la demande',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('❌ Erreur création demande:', error);
      Alert.alert(
        'Erreur', 
        'Impossible de créer la demande de document. Vérifiez votre connexion.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const selectDocumentType = (documentTypeObj) => {
    setDocumentType(documentTypeObj.name);
    setSelectedDocumentTypeId(documentTypeObj._id);
    setShowDropdown(false);
  };

  return (
    <View style={{ flex: 1 }}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
      >
      <ScrollView 
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Ionicons name="document-text" size={60} color="#fff" />
          <Text style={styles.headerTitle}>Demande de Document</Text>
          <Text style={styles.headerSubtitle}>
            Remplissez le formulaire ci-dessous pour faire votre demande
          </Text>
        </View>

        <View style={styles.formContainer}>
          <Text style={styles.sectionTitle}>Informations de la demande</Text>
          
          {/* Type de document */}
          <View style={styles.inputContainer}>
            <Ionicons name="folder-outline" size={20} color="#6c5ce7" style={styles.inputIcon} />
            <TouchableOpacity 
              style={styles.dropdownButton}
              onPress={() => setShowDropdown(!showDropdown)}
              disabled={loadingTypes}
            >
              <Text style={[
                styles.dropdownText, 
                !documentType && styles.placeholderText,
                loadingTypes && styles.dropdownDisabled
              ]}>
                {loadingTypes ? 'Chargement des types...' : documentType || 'Sélectionner un type de document *'}
              </Text>
              {loadingTypes ? (
                <ActivityIndicator size="small" color="#666" />
              ) : (
                <Ionicons 
                  name={showDropdown ? "chevron-up" : "chevron-down"} 
                  size={20} 
                  color="#666" 
                />
              )}
            </TouchableOpacity>
          </View>

          {/* Dropdown des types de documents */}
          {showDropdown && documentTypes && documentTypes.length > 0 && (
            <View style={styles.dropdown}>
              {documentTypes.map((typeObj, index) => (
                <TouchableOpacity
                  key={typeObj._id || index}
                  style={styles.dropdownItem}
                  onPress={() => selectDocumentType(typeObj)}
                >
                  <View>
                    <Text style={styles.dropdownItemText}>{typeObj.name}</Text>
                    {typeObj.description && (
                      <Text style={styles.dropdownItemDescription}>{typeObj.description}</Text>
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}

          {/* Description */}
          <View style={styles.inputContainer}>
            <Ionicons name="create-outline" size={20} color="#6c5ce7" style={styles.inputIcon} />
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description (facultatif)"
              placeholderTextColor="#999"
              value={description}
              onChangeText={setDescription}
              multiline={true}
              numberOfLines={4}
              textAlignVertical="top"
            />
          </View>

          {/* Bouton d'envoi */}
          <TouchableOpacity 
            style={[styles.submitButton, isLoading && styles.disabledButton]} 
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="send" size={20} color="#fff" style={styles.buttonIcon} />
                <Text style={styles.submitButtonText}>Envoyer la demande</Text>
              </>
            )}
          </TouchableOpacity>

          <Text style={styles.requiredText}>* Champs obligatoires</Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002857',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 30,
  },
  header: {
    padding: 20,
    paddingTop: 30,
    alignItems: 'center',
    backgroundColor: 'rgba(0, 40, 87, 0.8)',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 15,
    marginBottom: 10,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 20,
  },
  formContainer: {
    paddingHorizontal: 20,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 15,
    marginTop: 10,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: 15,
    marginBottom: 15,
    paddingHorizontal: 15,
    minHeight: 55,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputIcon: {
    marginRight: 10,
    marginTop: 17,
  },
  input: {
    flex: 1,
    height: 55,
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  textArea: {
    height: 100,
    paddingTop: 15,
    paddingBottom: 15,
  },
  dropdownButton: {
    flex: 1,
    height: 55,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  dropdownText: {
    color: '#333',
    fontSize: 15,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  placeholderText: {
    color: '#999',
  },
  dropdown: {
    backgroundColor: '#fff',
    borderRadius: 15,
    marginBottom: 15,
    marginTop: -10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dropdownItem: {
    paddingHorizontal: 15,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  dropdownItemText: {
    color: '#333',
    fontSize: 15,
    fontWeight: '500',
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  dropdownItemDescription: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
    fontStyle: 'italic',
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  dropdownDisabled: {
    color: '#999',
  },
  submitButton: {
    height: 55,
    backgroundColor: '#6c5ce7',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  disabledButton: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  buttonIcon: {
    marginRight: 10,
  },
  requiredText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 15,
  },
});

export default DocumentRequestScreen;
