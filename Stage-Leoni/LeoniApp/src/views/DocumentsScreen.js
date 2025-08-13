// Version complète et corrigée du fichier
import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  Alert,
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import DocumentController from '../controllers/DocumentController';

const DocumentsScreen = ({ navigation }) => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState(null);



  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      console.log('🔍 FRONTEND: Chargement des documents...');

      const result = await DocumentController.getDocumentRequests();
      console.log('📊 FRONTEND: Résultat complet getDocumentRequests:', result);

      if (result.success && result.data) {
        console.log('✅ Documents reçus:', result.data.length, 'documents');
        if (result.data.length > 0) {
          console.log('📋 Premier document (structure complète):', JSON.stringify(result.data[0], null, 2));
          console.log('📋 Liste des IDs:', result.data.map(d => {
            const id = d.id || d._id;
            return {
              original_id: d.id,
              original__id: d._id,
              selected_id: id,
              type: typeof id,
              length: id ? id.length : 'null'
            };
          }));
        }
        setDocuments(result.data);
      } else {
        console.error('❌ FRONTEND: Erreur:', result.message);
        setDocuments([]);
        
        // Ne pas afficher d'alerte si c'est juste qu'il n'y a pas de documents
        if (result.message && !result.message.includes('Aucun document')) {
          Alert.alert('Erreur', result.message || 'Impossible de charger les documents');
        }
      }
    } catch (error) {
      console.error('❌ FRONTEND: Erreur lors du chargement des documents:', error);
      setDocuments([]);
      Alert.alert(
        'Erreur',
        'Impossible de charger les documents. Veuillez réessayer.',
        [{ text: 'Réessayer', onPress: loadDocuments }]
      );
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const handleDeleteDocument = async (documentId, documentType) => {
    Alert.alert(
      'Supprimer le document',
      `Êtes-vous sûr de vouloir supprimer cette demande de "${documentType}" ?`,
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Supprimer', 
          style: 'destructive', 
          onPress: async () => {
            try {
              setDeletingId(documentId);
              console.log('🗑️ Suppression document:', documentId);
              
              const result = await DocumentController.deleteDocumentRequest(documentId);
              
              if (result.success) {
                Alert.alert('Succès', 'Document supprimé avec succès');
                // Recharger la liste
                loadDocuments();
              } else {
                Alert.alert('Erreur', result.message || 'Impossible de supprimer le document');
              }
            } catch (error) {
              console.error('Erreur suppression document:', error);
              Alert.alert('Erreur', 'Erreur lors de la suppression');
            } finally {
              setDeletingId(null);
            }
          }
        }
      ]
    );
  };
  const onRefresh = () => {
    setRefreshing(true);
    loadDocuments();
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // Rafraîchir quand la page devient visible
  useFocusEffect(
    React.useCallback(() => {
      console.log('📱 DocumentsScreen: Page visible, rafraîchissement...');
      loadDocuments();
    }, [])
  );

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#fff']}
            tintColor="#fff"
          />
        }
      >
        {isLoading && !refreshing ? (
          <ActivityIndicator size="large" color="#fff" />
        ) : documents.map((doc, index) => (
          <View key={index} style={styles.documentCard}>
            <View style={styles.documentHeader}>
              <Text style={styles.documentType}>{doc.type || doc.documentType || 'Document'}</Text>
              <View style={styles.headerActions}>
                <View style={[
                  styles.statusBadge,
                  {
                    backgroundColor: '#fff',
                    borderColor: '#ddd'
                  },
                  doc.status?.current === 'en cours' ? styles.inProgressStatus : null,
                  doc.status?.current === 'accepté' ? styles.acceptedStatus : null,
                  doc.status?.current === 'refusé' ? styles.rejectedStatus : null
                ]}>
                  <Text style={[styles.statusText, {color: '#000'}]}>{(doc.status?.current || 'en attente').toUpperCase()}</Text>
                </View>
                
                {/* Bouton supprimer - seulement si pas accepté */}
                {doc.status?.current !== 'accepté' && (
                  <TouchableOpacity
                    style={[
                      styles.deleteButton,
                      deletingId === (doc.id || doc._id) && styles.deleteButtonDisabled
                    ]}
                    onPress={() => handleDeleteDocument(doc.id || doc._id, doc.type || doc.documentType)}
                    disabled={deletingId === (doc.id || doc._id)}
                  >
                    {deletingId === (doc.id || doc._id) ? (
                      <ActivityIndicator size="small" color="#dc3545" />
                    ) : (
                      <Ionicons name="trash-outline" size={20} color="#dc3545" />
                    )}
                  </TouchableOpacity>
                )}
              </View>
            </View>

            {doc.description && doc.description.trim() ? (
              <Text style={styles.documentDescription}>
                Description: {doc.description}
              </Text>
            ) : null}

            <Text style={styles.documentDate}>
              Envoyé le: {doc.createdAt ? new Date(doc.createdAt).toLocaleDateString() : '---'}
            </Text>
            
            {doc.updatedAt && doc.updatedAt !== doc.createdAt && (
              <Text style={styles.documentDate}>
                Mis à jour le: {new Date(doc.updatedAt).toLocaleDateString()}
              </Text>
            )}
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#002857',
  },
  scrollContainer: {
    paddingBottom: 20,
  },
  header: {
    padding: 20,
    paddingTop: 40,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(0, 40, 87, 0.8)',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    marginBottom: 20,
  },
  headerContent: {
    alignItems: 'center',
    flex: 1,
  },
  headerIcon: {
    fontSize: 60,
    color: '#fff',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 15,
    marginBottom: 10,
  },
  refreshButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 8,
    borderRadius: 20,
  },
  refreshText: {
    fontSize: 20,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  documentCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 15,
    marginHorizontal: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  documentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  documentType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    borderWidth: 1,
    backgroundColor: '#fff',
  },
  deleteButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'transparent',
  },
  deleteButtonDisabled: {
    opacity: 0.5,
  },
  inProgressStatus: {
    backgroundColor: '#FFC107',
    borderColor: '#FFA000',
  },
  acceptedStatus: {
    backgroundColor: '#4CAF50',
    borderColor: '#388E3C',
  },
  rejectedStatus: {
    backgroundColor: '#F44336',
    borderColor: '#D32F2F',
  },
  statusText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  documentDescription: {
    fontSize: 14,
    color: '#444',
    marginVertical: 8,
  },
  documentDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 10,
    fontStyle: 'italic',
  }
}); 

export default DocumentsScreen;
