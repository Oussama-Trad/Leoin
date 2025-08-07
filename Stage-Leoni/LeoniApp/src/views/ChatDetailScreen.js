import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { apiService } from '../controllers/apiService';

const ChatDetailScreen = ({ route, navigation }) => {
  const { chatId, chatData } = route.params;
  
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chat, setChat] = useState(chatData || null);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  
  const flatListRef = useRef(null);
  const currentUserId = 'current_user_id'; // À récupérer du context d'authentification

  useEffect(() => {
    loadChatDetail();
    loadMessages();
    
    // Optionnel: Écouter les nouveaux messages en temps réel
    // setupWebSocket();
    
    // Nettoyer lors du démontage
    return () => {
      // closeWebSocket();
    };
  }, []);

  const loadChatDetail = async () => {
    if (chat) return; // On a déjà les données
    
    try {
      const response = await apiService.get(`/api/chats/${chatId}`);
      if (response.success) {
        setChat(response.data);
      } else {
        Alert.alert('Erreur', 'Impossible de charger cette conversation');
        navigation.goBack();
      }
    } catch (error) {
      console.error('Erreur chargement chat:', error);
      Alert.alert('Erreur', 'Problème de connexion');
      navigation.goBack();
    }
  };

  const loadMessages = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/api/chats/${chatId}/messages`);
      if (response.success) {
        setMessages(response.data);
        
        // Scroll vers le bas après chargement
        setTimeout(() => {
          flatListRef.current?.scrollToEnd({ animated: false });
        }, 100);
      } else {
        Alert.alert('Erreur', 'Impossible de charger les messages');
      }
    } catch (error) {
      console.error('Erreur chargement messages:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    const messageText = newMessage.trim();
    setNewMessage('');
    setSending(true);

    // Ajouter le message localement pour l'affichage immédiat
    const tempMessage = {
      _id: `temp_${Date.now()}`,
      message: { text: messageText, type: 'text' },
      senderId: currentUserId,
      senderName: 'Vous',
      senderRole: 'employee',
      createdAt: new Date().toISOString(),
      status: 'sending',
      isTemp: true
    };
    
    setMessages(prev => [...prev, tempMessage]);

    try {
      const response = await apiService.post(`/api/chats/${chatId}/messages`, {
        text: messageText
      });

      if (response.success) {
        // Remplacer le message temporaire par le vrai
        setMessages(prev => 
          prev.map(msg => 
            msg._id === tempMessage._id ? response.data : msg
          )
        );
        
        // Mettre à jour les infos du chat
        setChat(prev => ({
          ...prev,
          lastMessage: {
            text: messageText,
            senderId: currentUserId,
            senderName: 'Vous',
            sentAt: new Date().toISOString()
          },
          lastActivityAt: new Date().toISOString(),
          messageCount: prev.messageCount + 1
        }));
      } else {
        // Supprimer le message temporaire en cas d'erreur
        setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
        Alert.alert('Erreur', 'Impossible d\'envoyer le message');
      }
    } catch (error) {
      console.error('Erreur envoi message:', error);
      setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setSending(false);
    }
  };

  const closeChat = async () => {
    Alert.alert(
      'Fermer la conversation',
      'Êtes-vous sûr de vouloir fermer cette conversation ? Vous pourrez évaluer le service après.',
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Fermer', 
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await apiService.put(`/api/chats/${chatId}/close`);
              if (response.success) {
                setChat(prev => ({ ...prev, status: 'closed' }));
                setShowRatingModal(true);
              } else {
                Alert.alert('Erreur', 'Impossible de fermer la conversation');
              }
            } catch (error) {
              console.error('Erreur fermeture chat:', error);
              Alert.alert('Erreur', 'Problème de connexion');
            }
          }
        }
      ]
    );
  };

  const submitRating = async () => {
    if (rating === 0) {
      Alert.alert('Erreur', 'Veuillez donner une note');
      return;
    }

    try {
      setSubmittingRating(true);
      const response = await apiService.post(`/api/chats/${chatId}/rate`, {
        score: rating,
        feedback: feedback.trim()
      });

      if (response.success) {
        setShowRatingModal(false);
        setChat(prev => ({
          ...prev,
          rating: {
            score: rating,
            feedback: feedback.trim(),
            ratedAt: new Date().toISOString()
          }
        }));
        Alert.alert('Merci !', 'Votre évaluation a été enregistrée.');
      } else {
        Alert.alert('Erreur', 'Impossible d\'enregistrer votre évaluation');
      }
    } catch (error) {
      console.error('Erreur évaluation:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setSubmittingRating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#0066CC';
      case 'pending': return '#FF8800';
      case 'resolved': return '#00AA00';
      case 'closed': return '#888888';
      default: return '#888888';
    }
  };

  const formatMessageTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatMessageDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Aujourd'hui";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Hier';
    } else {
      return date.toLocaleDateString('fr-FR');
    }
  };

  const renderMessage = ({ item, index }) => {
    const isCurrentUser = item.senderId === currentUserId;
    const isSystemMessage = item.isSystemMessage;
    const prevMessage = index > 0 ? messages[index - 1] : null;
    const showDateSeparator = !prevMessage || 
      new Date(item.createdAt).toDateString() !== new Date(prevMessage.createdAt).toDateString();

    return (
      <View>
        {/* Séparateur de date */}
        {showDateSeparator && (
          <View style={styles.dateSeparator}>
            <Text style={styles.dateSeparatorText}>
              {formatMessageDate(item.createdAt)}
            </Text>
          </View>
        )}

        {/* Message système */}
        {isSystemMessage ? (
          <View style={styles.systemMessageContainer}>
            <Text style={styles.systemMessageText}>{item.message.text}</Text>
          </View>
        ) : (
          /* Message normal */
          <View style={[
            styles.messageContainer,
            isCurrentUser ? styles.currentUserMessage : styles.otherUserMessage
          ]}>
            {!isCurrentUser && (
              <Text style={styles.senderName}>{item.senderName}</Text>
            )}
            
            <View style={[
              styles.messageBubble,
              isCurrentUser ? styles.currentUserBubble : styles.otherUserBubble,
              item.isTemp && styles.tempMessage
            ]}>
              <Text style={[
                styles.messageText,
                isCurrentUser ? styles.currentUserText : styles.otherUserText
              ]}>
                {item.message.text}
              </Text>
              
              <View style={styles.messageFooter}>
                <Text style={[
                  styles.messageTime,
                  isCurrentUser ? styles.currentUserTime : styles.otherUserTime
                ]}>
                  {formatMessageTime(item.createdAt)}
                </Text>
                
                {isCurrentUser && (
                  <Ionicons
                    name={
                      item.isTemp ? 'time' :
                      item.status === 'read' ? 'checkmark-done' : 'checkmark'
                    }
                    size={14}
                    color={isCurrentUser ? '#FFFFFF' : '#666666'}
                    style={styles.messageStatus}
                  />
                )}
              </View>
            </View>
          </View>
        )}
      </View>
    );
  };

  const renderRatingModal = () => (
    <Modal
      visible={showRatingModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowRatingModal(false)}
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Évaluer le service</Text>
          <TouchableOpacity onPress={() => setShowRatingModal(false)}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>

        <View style={styles.ratingContent}>
          <Text style={styles.ratingQuestion}>
            Comment évaluez-vous ce service ?
          </Text>

          <View style={styles.starsContainer}>
            {[1, 2, 3, 4, 5].map((star) => (
              <TouchableOpacity
                key={star}
                onPress={() => setRating(star)}
                style={styles.starButton}
              >
                <Ionicons
                  name={star <= rating ? 'star' : 'star-outline'}
                  size={40}
                  color="#FFD700"
                />
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.ratingText}>
            {rating === 0 ? 'Touchez les étoiles pour noter' :
             rating === 1 ? 'Très insatisfait' :
             rating === 2 ? 'Insatisfait' :
             rating === 3 ? 'Neutre' :
             rating === 4 ? 'Satisfait' :
             rating === 5 ? 'Très satisfait' : ''}
          </Text>

          <TextInput
            style={styles.feedbackInput}
            placeholder="Commentaire optionnel..."
            value={feedback}
            onChangeText={setFeedback}
            multiline
            maxLength={500}
          />

          <TouchableOpacity
            style={[
              styles.submitRatingButton,
              (rating === 0 || submittingRating) && styles.submitRatingButtonDisabled
            ]}
            onPress={submitRating}
            disabled={rating === 0 || submittingRating}
          >
            {submittingRating ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.submitRatingButtonText}>Envoyer l'évaluation</Text>
            )}
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </Modal>
  );

  if (loading || !chat) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0066CC" />
          <Text style={styles.loadingText}>Chargement de la conversation...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const statusColor = getStatusColor(chat.status);
  const canSendMessage = chat.status === 'active' || chat.status === 'pending';

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* En-tête */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#0066CC" />
          </TouchableOpacity>
          
          <View style={styles.headerInfo}>
            <Text style={styles.headerTitle} numberOfLines={1}>
              {chat.participants.service.serviceName}
            </Text>
            <View style={styles.headerStatus}>
              <Ionicons name="person" size={12} color="#666" />
              <Text style={styles.headerSubtitle}>
                {chat.participants.service.currentRepresentative.name}
              </Text>
              <Text style={[styles.statusBadge, { color: statusColor }]}>
                • {chat.status === 'active' ? 'En ligne' : 
                   chat.status === 'pending' ? 'En attente' :
                   chat.status === 'resolved' ? 'Résolu' : 'Fermé'}
              </Text>
            </View>
          </View>

          {canSendMessage && (
            <TouchableOpacity onPress={closeChat}>
              <Ionicons name="close-circle-outline" size={24} color="#FF4444" />
            </TouchableOpacity>
          )}
        </View>

        {/* Sujet de la conversation */}
        <View style={styles.subjectContainer}>
          <Text style={styles.subjectLabel}>Sujet:</Text>
          <Text style={styles.subjectText}>{chat.subject}</Text>
        </View>

        {/* Liste des messages */}
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item._id}
          style={styles.messagesList}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() => {
            flatListRef.current?.scrollToEnd({ animated: true });
          }}
          ListEmptyComponent={
            <View style={styles.emptyMessagesContainer}>
              <Text style={styles.emptyMessagesText}>
                Conversation démarrée. Écrivez votre premier message !
              </Text>
            </View>
          }
        />

        {/* Zone de saisie */}
        {canSendMessage ? (
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              placeholder="Écrivez votre message..."
              value={newMessage}
              onChangeText={setNewMessage}
              multiline
              maxLength={1000}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                (!newMessage.trim() || sending) && styles.sendButtonDisabled
              ]}
              onPress={sendMessage}
              disabled={!newMessage.trim() || sending}
            >
              {sending ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Ionicons name="send" size={20} color="#FFFFFF" />
              )}
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.closedChatNotice}>
            <Ionicons name="lock-closed" size={16} color="#888" />
            <Text style={styles.closedChatText}>
              Cette conversation est {chat.status === 'resolved' ? 'résolue' : 'fermée'}
            </Text>
            {chat.status === 'closed' && !chat.rating && (
              <TouchableOpacity 
                style={styles.rateButton}
                onPress={() => setShowRatingModal(true)}
              >
                <Text style={styles.rateButtonText}>Évaluer</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Modal d'évaluation */}
        {renderRatingModal()}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerInfo: {
    flex: 1,
    marginLeft: 15,
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
  },
  headerStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  headerSubtitle: {
    marginLeft: 4,
    fontSize: 12,
    color: '#666666',
  },
  statusBadge: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: '500',
  },
  subjectContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  subjectLabel: {
    fontSize: 12,
    color: '#888888',
    marginBottom: 2,
  },
  subjectText: {
    fontSize: 14,
    color: '#333333',
    fontWeight: '500',
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: 10,
  },
  dateSeparator: {
    alignItems: 'center',
    marginVertical: 15,
  },
  dateSeparatorText: {
    fontSize: 12,
    color: '#888888',
    backgroundColor: '#F0F0F0',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  systemMessageContainer: {
    alignItems: 'center',
    marginVertical: 10,
  },
  systemMessageText: {
    fontSize: 12,
    color: '#888888',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  messageContainer: {
    paddingHorizontal: 20,
    marginVertical: 4,
  },
  currentUserMessage: {
    alignItems: 'flex-end',
  },
  otherUserMessage: {
    alignItems: 'flex-start',
  },
  senderName: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 4,
    marginLeft: 12,
  },
  messageBubble: {
    maxWidth: '80%',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 18,
  },
  currentUserBubble: {
    backgroundColor: '#0066CC',
    borderBottomRightRadius: 4,
  },
  otherUserBubble: {
    backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 1.41,
    elevation: 2,
  },
  tempMessage: {
    opacity: 0.7,
  },
  messageText: {
    fontSize: 14,
    lineHeight: 20,
  },
  currentUserText: {
    color: '#FFFFFF',
  },
  otherUserText: {
    color: '#333333',
  },
  messageFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    justifyContent: 'flex-end',
  },
  messageTime: {
    fontSize: 11,
  },
  currentUserTime: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  otherUserTime: {
    color: '#888888',
  },
  messageStatus: {
    marginLeft: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    maxHeight: 100,
    fontSize: 14,
    marginRight: 10,
  },
  sendButton: {
    backgroundColor: '#0066CC',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#CCCCCC',
  },
  closedChatNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    backgroundColor: '#F0F0F0',
  },
  closedChatText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#888888',
  },
  rateButton: {
    marginLeft: 15,
    backgroundColor: '#0066CC',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 15,
  },
  rateButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '500',
  },
  emptyMessagesContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyMessagesText: {
    fontSize: 14,
    color: '#888888',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666666',
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
  },
  ratingContent: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 30,
    alignItems: 'center',
  },
  ratingQuestion: {
    fontSize: 16,
    color: '#333333',
    textAlign: 'center',
    marginBottom: 30,
  },
  starsContainer: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  starButton: {
    padding: 5,
  },
  ratingText: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 30,
  },
  feedbackInput: {
    width: '100%',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 15,
    fontSize: 14,
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: 30,
  },
  submitRatingButton: {
    backgroundColor: '#0066CC',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
    width: '100%',
    alignItems: 'center',
  },
  submitRatingButtonDisabled: {
    backgroundColor: '#CCCCCC',
  },
  submitRatingButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ChatDetailScreen;
