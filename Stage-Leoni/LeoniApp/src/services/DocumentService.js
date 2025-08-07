import { BASE_URL } from '../config';
import DocumentRequestModel from '../models/DocumentRequestModel';

/**
 * Service pour la gestion des documents
 */
class DocumentService {
  
  /**
   * Créer une nouvelle demande de document
   */
  static async createDocumentRequest(documentData, token) {
    try {
      console.log('🔄 DocumentService: Création demande -', documentData);

      const response = await fetch(`${BASE_URL}/document-request`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(documentData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ DocumentService: Erreur HTTP', response.status, errorData);
        return {
          success: false,
          message: errorData.message || `Erreur HTTP ${response.status}`
        };
      }

      const data = await response.json();
      console.log('🔍 DocumentService: Réponse JSON brute du serveur:', data);
      
      if (data.success && data.document) {
        data.document = DocumentRequestModel.fromApiResponse(data.document);
      }

      console.log('🔍 DocumentService: Résultat final à retourner:', data);
      return data;
    } catch (error) {
      console.error('Erreur création demande document:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }

  /**
   * Obtenir toutes les demandes de documents de l'utilisateur
   */
  static async getUserDocuments(token) {
    try {
      console.log('🔄 DocumentService: getUserDocuments appelé');
      console.log('🔄 DocumentService: Token fourni:', token ? `${token.substring(0, 20)}...` : 'null');
      
      const response = await fetch(`${BASE_URL}/document-requests`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      console.log('📡 DocumentService: Status response:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ DocumentService: Erreur récupération HTTP', response.status, errorData);
        return {
          success: false,
          message: errorData.message || `Erreur HTTP ${response.status}`,
          documents: []
        };
      }

      const data = await response.json();
      console.log('📋 DocumentService: Données brutes reçues du serveur:', data);
      
      if (data.success && data.documents) {
        console.log('✅ DocumentService: Transformation des documents...');
        data.documents = data.documents.map((doc, index) => {
          console.log(`📄 DocumentService: Document ${index + 1}:`, doc);
          const transformed = DocumentRequestModel.fromApiResponse(doc);
          console.log(`🔄 DocumentService: Transformé ${index + 1}:`, transformed);
          return transformed;
        });
        console.log('✅ DocumentService: Tous les documents transformés:', data.documents.length, 'docs');
      } else if (data.success) {
        // Si pas de documents, on initialise avec un array vide
        console.log('📋 DocumentService: Aucun document trouvé, initialisation array vide');
        data.documents = [];
      }

      console.log('📤 DocumentService: Retour final:', {
        success: data.success,
        documentsCount: data.documents ? data.documents.length : 0
      });

      return data;
    } catch (error) {
      console.error('❌ DocumentService: Erreur réseau:', error);
      return {
        success: false,
        message: 'Erreur de connexion',
        documents: []
      };
    }
  }

  /**
   * Mettre à jour le statut d'une demande (pour admin)
   */
  static async updateDocumentStatus(token, documentId, newStatus) {
    try {
      const response = await fetch(`${BASE_URL}/document-request/${documentId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });

      const data = await response.json();
      
      if (data.success && data.document) {
        data.document = DocumentRequestModel.fromApiResponse(data.document);
      }

      return data;
    } catch (error) {
      console.error('Erreur mise à jour statut document:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }

  /**
   * Obtenir les types de documents disponibles
   */
  static getAvailableDocumentTypes() {
    return DocumentRequestModel.getAvailableTypes();
  }

  /**
   * Obtenir les statuts possibles
   */
  static getAvailableStatuses() {
    return DocumentRequestModel.getAvailableStatuses();
  }

  /**
   * Récupérer les types de documents disponibles
   */
  static async getDocumentTypes(token = null) {
    try {
      console.log('🔄 DocumentService: Récupération types de documents');

      const headers = {
        'Content-Type': 'application/json',
      };

      // Ajouter l'authentification si token fourni
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${BASE_URL}/document-types`, {
        method: 'GET',
        headers: headers
      });

      if (!response.ok) {
        console.error('❌ DocumentService: Erreur HTTP', response.status);
        return {
          success: false,
          message: `Erreur HTTP ${response.status}`
        };
      }

      const data = await response.json();
      console.log('✅ DocumentService: Types récupérés:', data);

      return data;
    } catch (error) {
      console.error('❌ DocumentService: Erreur récupération types:', error);
      return {
        success: false,
        message: 'Erreur de connexion'
      };
    }
  }
}

export default DocumentService;
