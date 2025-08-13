import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  Dimensions 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ChatController from '../controllers/ChatController';

const { width } = Dimensions.get('window');

export default function ChatDetailScreen({ route, navigation }) {
  const params = route.params || {};
  // Support multiple parameter names for chat data
  const chat = params.chat || params.chatData || params.conversationData || null;
  const chatId = params.chatId || params.conversationId || (chat && chat._id) || null;
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [chatData, setChatData] = useState(chat);

  // Add null check for chat object and provide default values
  if (!chat) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Conversation non trouvée</Text>
      </View>
    );
  }

  // Default values for missing chat properties
  const chatColor = (chatData && chatData.color) || '#002857';
  const chatIcon = (chatData && chatData.icon) || 'chatbubble-outline';
  const chatName = (chatData && (chatData.name || chatData.subject || chatData.targetDepartment)) || 'Conversation';

  useEffect(() => {
    loadMessages();
    
    // Auto-refresh des messages toutes les 10 secondes
    const interval = setInterval(loadMessages, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadMessages = async () => {
    try {
      const response = await ChatController.getConversationMessages(chatId);
      
      if (response.success) {
        setMessages(response.messages || []);
        
        // Marquer la conversation comme lue
        ChatController.markConversationAsRead(chatId);
      } else {
        console.error('Erreur chargement messages:', response.message);
        if (!loading) {
          Alert.alert('Erreur', response.message || 'Impossible de charger les messages');
        }
      }
    } catch (error) {
      console.error('Erreur chargement messages:', error);
      if (!loading) {
        Alert.alert('Erreur', 'Problème de connexion');
      }
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = () => {
    if (!newMessage.trim() || sending) return;

    const messageText = newMessage.trim();
    setSending(true);
    setNewMessage('');

    // Ajouter le message localement pour l'affichage immédiat
    const tempMessage = {
      _id: `temp_${Date.now()}`,
      content: messageText,
      message: messageText,
      senderName: 'Vous',
      senderType: 'user',
      isCurrentUser: true,
      createdAt: new Date().toISOString(),
      isTemp: true
    };
    
    setMessages(prev => [...prev, tempMessage]);

    // Envoyer le message
    ChatController.sendMessage(chatId, messageText)
      .then(response => {
        if (response.success) {
          // Remplacer le message temporaire par le vrai
          setMessages(prev => 
            prev.map(msg => 
              msg._id === tempMessage._id ? {
                ...tempMessage,
                _id: response.messageId,
                isTemp: false
              } : msg
            )
          );
        } else {
          // Supprimer le message temporaire en cas d'erreur
          setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
          Alert.alert('Erreur', response.message || 'Impossible d\'envoyer le message');
        }
      })
      .catch(error => {
        console.error('Erreur envoi message:', error);
        setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
        Alert.alert('Erreur', 'Problème de connexion');
      })
      .finally(() => {
        setSending(false);
      });
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <ActivityIndicator size="large" color={chatColor} />
        <Text style={styles.loadingText}>Chargement de la conversation...</Text>
      </View>
    );
  }
      setNewMessage('');
    }
  };

  const renderMessage = ({ item }) => {
    const isUser = item.isCurrentUser || item.senderType === 'user';
    
    return (
      <View style={[styles.messageContainer, isUser ? styles.userMessage : styles.serviceMessage]}>
        <View style={[
          styles.messageBubble, 
          { 
            backgroundColor: isUser ? chatColor : '#ffffff',
            opacity: item.isTemp ? 0.7 : 1
          }
        ]}>
          <Text style={[styles.messageText, { color: isUser ? '#ffffff' : '#2D3748' }]}>
            {item.content || item.message}
          </Text>
        </View>
        <Text style={styles.timestamp}>
          {new Date(item.createdAt).toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={[styles.header, { backgroundColor: chatColor }]}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        
        <View style={styles.headerInfo}>
          <View style={styles.serviceIcon}>
            <Ionicons name={chatIcon} size={24} color="#ffffff" />
          </View>
          <View>
            <Text style={styles.headerTitle}>{chatName}</Text>
            <Text style={styles.headerSubtitle}>
              {chatData && chatData.status ? getStatusText(chatData.status) : 'En ligne'}
            </Text>
          </View>
        </View>
      </View>

      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item._id || item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() => {
          // Auto-scroll vers le bas
        }}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>
              Conversation démarrée. Écrivez votre premier message !
            </Text>
          </View>
        }
      />

      <View style={styles.inputContainer}>
        <View style={styles.inputWrapper}>
          <TextInput
            style={styles.textInput}
            value={newMessage}
            onChangeText={setNewMessage}
            placeholder="Tapez votre message..."
            placeholderTextColor="#718096"
            multiline
            maxLength={1000}
          />
          <TouchableOpacity 
            style={[styles.sendButton, { backgroundColor: chatColor }]}
            onPress={sendMessage}
            disabled={!newMessage.trim() || sending}
          >
            {sending ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Ionicons name="send" size={20} color="#ffffff" />
            )}
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

// Fonction utilitaire pour le statut
function getStatusText(status) {
  const statusTexts = {
    'open': 'Ouvert',
    'in_progress': 'En cours',
    'closed': 'Fermé'
  };
  return statusTexts[status] || 'En ligne';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f4f8',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  headerInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  serviceIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.8,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  messageContainer: {
    marginBottom: 15,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  serviceMessage: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  timestamp: {
    fontSize: 12,
    color: '#718096',
    marginTop: 4,
    textAlign: 'center',
  },
  inputContainer: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#f7fafc',
    borderRadius: 25,
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: '#2D3748',
    maxHeight: 100,
    paddingVertical: 8,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 10,
  },
  errorText: {
    fontSize: 16,
    color: '#e53e3e',
    textAlign: 'center',
    marginTop: 50,
  },
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyText: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
