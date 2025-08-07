import DocumentService from '../services/DocumentService';
import DocumentRequestModel from '../models/DocumentRequestModel';
import AuthController from './AuthController';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Contrôleur pour la gestion des demandes de documents
 */
class DocumentController {

  /**
   * Créer une nouvelle demande de document
   */
  static async createDocumentRequest(documentData) {
    try {
      console.log('📄 DocumentController: Création demande de document');

      // Validation des données avec le modèle
      const documentModel = new DocumentRequestModel();
      const validation = documentModel.validate(documentData);

      if (!validation.isValid) {
        return {
          success: false,
          message: 'Données invalides',
          errors: validation.errors
        };
      }

      // Récupérer le token d'authentification
      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      // Créer la demande via le service
      const result = await DocumentService.createDocumentRequest(
        documentModel.toApiObject(documentData),
        token
      );

      if (result.success) {
        console.log('✅ DocumentController: Demande créée avec succès');
        console.log('🔍 DocumentController: Résultat détaillé:', result);
      } else {
        console.log('❌ DocumentController: Échec création -', result.message);
        console.log('🔍 DocumentController: Résultat d\'échec détaillé:', result);
      }

      console.log('🔍 DocumentController: Résultat final à retourner:', result);
      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur création demande:', error);
      return {
        success: false,
        message: 'Erreur lors de la création de la demande'
      };
    }
  }

  /**
   * Récupérer toutes les demandes de l'utilisateur
   */
  static async getUserDocuments() {
    try {
      console.log('📄 DocumentController: Récupération des documents');

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      // Vérifier si le token a le bon format
      const hasValidFormat = await AuthController.hasValidTokenFormat();
      if (!hasValidFormat) {
        console.warn('⚠️ DocumentController: Token ancien format détecté - Déconnexion nécessaire');
        return {
          success: false,
          message: 'Session expirée - Reconnectez-vous',
          requiresReconnection: true
        };
      }

      const result = await DocumentService.getUserDocuments(token);

      if (result.success && result.documents && Array.isArray(result.documents)) {
        console.log(`✅ DocumentController: ${result.documents.length} documents récupérés`);
        
        // Transformer les données avec le modèle
        const transformedDocuments = result.documents.map(doc => 
          DocumentRequestModel.fromApiResponse(doc)
        );

        return {
          ...result,
          documents: transformedDocuments
        };
      } else {
        // Vérifier si c'est une erreur de token invalide
        if (result.message && result.message.includes('user_id manquant')) {
          console.warn('⚠️ DocumentController: Token invalide - Déconnexion nécessaire');
          return {
            success: false,
            message: 'Session expirée - Reconnectez-vous',
            requiresReconnection: true
          };
        }
        
        console.log('❌ DocumentController: Échec récupération -', result.message || 'Aucun document trouvé');
        return {
          success: true,
          documents: [],
          message: 'Aucun document trouvé'
        };
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur récupération documents:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération des documents'
      };
    }
  }

  /**
   * Récupérer une demande spécifique par ID
   */
  static async getDocumentById(documentId) {
    try {
      console.log('📄 DocumentController: Récupération document ID:', documentId);

      if (!documentId) {
        return {
          success: false,
          message: 'ID document requis'
        };
      }

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      const result = await DocumentService.getDocumentById(documentId, token);

      if (result.success) {
        console.log('✅ DocumentController: Document récupéré avec succès');
        
        // Transformer avec le modèle
        const transformedDocument = DocumentRequestModel.fromApiResponse(result.document);

        return {
          ...result,
          document: transformedDocument
        };
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur récupération document:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération du document'
      };
    }
  }

  /**
   * Mettre à jour une demande de document
   */
  static async updateDocumentRequest(documentId, updateData) {
    try {
      console.log('📄 DocumentController: Mise à jour document ID:', documentId);

      if (!documentId) {
        return {
          success: false,
          message: 'ID document requis'
        };
      }

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      // Validation partielle des données
      if (updateData.type && !DocumentRequestModel.DOCUMENT_TYPES.includes(updateData.type)) {
        return {
          success: false,
          message: 'Type de document invalide'
        };
      }

      if (updateData.urgency && !DocumentRequestModel.URGENCY_LEVELS.includes(updateData.urgency)) {
        return {
          success: false,
          message: 'Niveau d\'urgence invalide'
        };
      }

      const result = await DocumentService.updateDocumentRequest(
        documentId,
        updateData,
        token
      );

      if (result.success) {
        console.log('✅ DocumentController: Document mis à jour avec succès');
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur mise à jour document:', error);
      return {
        success: false,
        message: 'Erreur lors de la mise à jour du document'
      };
    }
  }

  /**
   * Filtrer les documents par statut
   */
  static async getDocumentsByStatus(status) {
    try {
      console.log('📄 DocumentController: Filtrage par statut:', status);

      if (!DocumentRequestModel.STATUSES.includes(status)) {
        return {
          success: false,
          message: 'Statut invalide'
        };
      }

      const result = await this.getUserDocuments();

      if (result.success) {
        const filteredDocuments = result.documents.filter(doc => doc.status === status);
        
        return {
          success: true,
          documents: filteredDocuments,
          message: `${filteredDocuments.length} documents trouvés avec le statut ${status}`
        };
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur filtrage par statut:', error);
      return {
        success: false,
        message: 'Erreur lors du filtrage des documents'
      };
    }
  }

  /**
   * Obtenir les statistiques des demandes
   */
  static async getDocumentStatistics() {
    try {
      console.log('📄 DocumentController: Récupération statistiques');

      const result = await this.getUserDocuments();

      if (result.success) {
        const documents = result.documents;
        const stats = {
          total: documents.length,
          pending: documents.filter(doc => doc.status === 'en_attente').length,
          approved: documents.filter(doc => doc.status === 'approuve').length,
          rejected: documents.filter(doc => doc.status === 'rejete').length,
          processing: documents.filter(doc => doc.status === 'en_cours').length,
          byType: {}
        };

        // Statistiques par type
        DocumentRequestModel.DOCUMENT_TYPES.forEach(type => {
          stats.byType[type] = documents.filter(doc => doc.type === type).length;
        });

        console.log('✅ DocumentController: Statistiques générées');
        return {
          success: true,
          statistics: stats
        };
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur génération statistiques:', error);
      return {
        success: false,
        message: 'Erreur lors du calcul des statistiques'
      };
    }
  }

  /**
   * Alias pour getUserDocuments - pour compatibilité
   */
  static async getDocumentRequests() {
    console.log('📄 DocumentController: getDocumentRequests appelé (alias getUserDocuments)');
    console.log('📄 DocumentController: Forçage du rafraîchissement...');
    
    const result = await this.getUserDocuments();
    
    console.log('📄 DocumentController: Résultat getUserDocuments:', {
      success: result.success,
      documentsCount: result.documents ? result.documents.length : 0,
      message: result.message
    });
    
    // Adapter le format de retour pour compatibilité
    if (result.success && result.documents) {
      console.log('✅ DocumentController: Format de retour adapté avec', result.documents.length, 'documents');
      return {
        success: true,
        data: result.documents,
        message: result.message
      };
    }
    
    console.log('❌ DocumentController: Retour d\'erreur ou pas de documents');
    return result;
  }

  /**
   * Récupérer les types de documents disponibles
   */
  static async getDocumentTypes() {
    try {
      console.log('📋 DocumentController: Récupération des types de documents');

      // Optionnel: récupérer le token pour l'authentification si nécessaire
      const token = await AsyncStorage.getItem('userToken');

      const result = await DocumentService.getDocumentTypes(token);

      if (result.success) {
        console.log(`✅ DocumentController: ${result.count || 0} types de documents récupérés`);
      } else {
        console.log('❌ DocumentController: Échec récupération types -', result.message);
      }

      return result;
    } catch (error) {
      console.error('❌ DocumentController: Erreur récupération types:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération des types de documents'
      };
    }
  }
}

export default DocumentController;
