import AsyncStorage from '@react-native-async-storage/async-storage';
import NetworkService from '../services/NetworkService';

/**
 * Contrôleur unifié pour la gestion des conversations avec synchronisation admin
 */
class ChatController {

  /**
   * Créer une nouvelle conversation avec un département spécifique
   */
  static async createConversationWithDepartment(targetDepartment, targetLocation, subject, initialMessage = null) {
    try {
      console.log('🔄 ChatController: Création conversation avec département');
      console.log('Département:', targetDepartment, 'Location:', targetLocation);

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      const response = await NetworkService.fetch('/api/chats/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          targetDepartment: targetDepartment,
          targetLocation: targetLocation,
          subject: subject,
          initialMessage: initialMessage
        })
      });

      const data = await response.json();
      
      if (data.success) {
        console.log('✅ ChatController: Conversation créée avec succès');
        return {
          success: true,
          conversationId: data.conversationId,
          message: data.message
        };
      } else {
        console.log('❌ ChatController: Échec création -', data.message);
        return data;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur création conversation:', error);
      return {
        success: false,
        message: 'Erreur lors de la création de la conversation'
      };
    }
  }

  /**
   * Récupérer toutes les conversations de l'utilisateur
   */
  static async getUserConversations() {
    try {
      console.log('🔄 ChatController: Récupération des conversations utilisateur');

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      const response = await NetworkService.fetch('/api/chats', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ ChatController: ${data.count} conversations récupérées`);
        
        // Transformer les données pour l'affichage mobile
        const transformedConversations = data.data.map(conv => ({
          _id: conv._id,
          id: conv._id,
          chatId: conv._id,
          subject: conv.subject,
          title: conv.subject,
          targetDepartment: conv.targetDepartment,
          targetLocation: conv.targetLocation,
          status: conv.status,
          priority: conv.priority,
          messageCount: conv.messageCount || 0,
          unreadCount: conv.unreadCount || 0,
          hasUnreadMessages: conv.hasUnreadMessages || false,
          lastMessage: conv.lastMessage,
          createdAt: conv.createdAt,
          lastActivityAt: conv.lastActivityAt,
          // Propriétés pour l'affichage mobile
          name: `Chat - ${conv.targetDepartment}`,
          color: '#002857',
          icon: 'chatbubble-outline'
        }));

        return {
          success: true,
          data: transformedConversations,
          count: transformedConversations.length
        };
      } else {
        console.log('❌ ChatController: Échec récupération -', data.message);
        return data;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur récupération conversations:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération des conversations'
      };
    }
  }

  /**
   * Récupérer les messages d'une conversation
   */
  static async getConversationMessages(conversationId) {
    try {
      console.log('🔄 ChatController: Récupération messages conversation', conversationId);

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      const response = await NetworkService.fetch(`/api/chat/conversation/${conversationId}/messages`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ ChatController: ${data.count} messages récupérés`);
        
        // Transformer les messages pour l'affichage mobile
        const transformedMessages = data.messages.map(msg => ({
          _id: msg._id,
          id: msg._id,
          content: msg.message || msg.content,
          message: msg.message || msg.content,
          senderId: msg.senderId,
          senderName: msg.senderName,
          senderRole: msg.senderRole || msg.senderType,
          senderType: msg.senderType,
          createdAt: msg.createdAt,
          isRead: msg.isRead,
          isCurrentUser: msg.senderType === 'user'
        }));

        return {
          success: true,
          messages: transformedMessages,
          count: transformedMessages.length
        };
      } else {
        console.log('❌ ChatController: Échec récupération messages -', data.message);
        return data;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur récupération messages:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération des messages'
      };
    }
  }

  /**
   * Envoyer un message dans une conversation
   */
  static async sendMessage(conversationId, content) {
    try {
      console.log('🔄 ChatController: Envoi message dans conversation', conversationId);

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      if (!content || !content.trim()) {
        return {
          success: false,
          message: 'Le message ne peut pas être vide'
        };
      }

      const response = await NetworkService.fetch(`/api/chat/conversation/${conversationId}/message`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content.trim()
        })
      });

      const data = await response.json();
      
      if (data.success) {
        console.log('✅ ChatController: Message envoyé avec succès');
        return {
          success: true,
          messageId: data.messageId,
          message: data.message
        };
      } else {
        console.log('❌ ChatController: Échec envoi message -', data.message);
        return data;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur envoi message:', error);
      return {
        success: false,
        message: 'Erreur lors de l\'envoi du message'
      };
    }
  }

  /**
   * Récupérer les départements disponibles pour créer une conversation
   */
  static async getAvailableDepartments() {
    try {
      console.log('🔄 ChatController: Récupération départements disponibles');

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      const response = await NetworkService.fetch('/api/departments', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ ChatController: ${data.count} départements récupérés`);
        return {
          success: true,
          departments: data.data,
          count: data.count
        };
      } else {
        console.log('❌ ChatController: Échec récupération départements -', data.message);
        return data;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur récupération départements:', error);
      return {
        success: false,
        message: 'Erreur lors de la récupération des départements'
      };
    }
  }

  /**
   * Marquer une conversation comme lue
   */
  static async markConversationAsRead(conversationId) {
    try {
      console.log('🔄 ChatController: Marquage conversation comme lue', conversationId);

      const token = await AsyncStorage.getItem('userToken');
      if (!token) {
        return {
          success: false,
          message: 'Non connecté'
        };
      }

      // Pour l'instant, on marque comme lue côté client
      // L'API pourrait être étendue pour supporter cette fonctionnalité
      
      return {
        success: true,
        message: 'Conversation marquée comme lue'
      };

    } catch (error) {
      console.error('❌ ChatController: Erreur marquage lecture:', error);
      return {
        success: false,
        message: 'Erreur lors du marquage'
      };
    }
  }

  /**
   * Rechercher dans les conversations
   */
  static async searchConversations(keyword) {
    try {
      console.log('🔄 ChatController: Recherche conversations avec mot-clé:', keyword);

      const conversations = await this.getUserConversations();
      
      if (conversations.success) {
        // Filtrer côté client pour l'instant
        const filteredConversations = conversations.data.filter(conv => 
          conv.subject.toLowerCase().includes(keyword.toLowerCase()) ||
          conv.targetDepartment.toLowerCase().includes(keyword.toLowerCase())
        );

        return {
          success: true,
          data: filteredConversations,
          count: filteredConversations.length,
          keyword: keyword
        };
      } else {
        return conversations;
      }

    } catch (error) {
      console.error('❌ ChatController: Erreur recherche conversations:', error);
      return {
        success: false,
        message: 'Erreur lors de la recherche'
      };
    }
  }
}

export default ChatController;