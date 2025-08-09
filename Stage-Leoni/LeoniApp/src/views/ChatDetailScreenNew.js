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
  Dimensions 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function ChatDetailScreen({ route, navigation }) {
  const { chat } = route.params || {};
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  // Add null check for chat object and provide default values
  if (!chat) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Chat not found</Text>
      </View>
    );
  }

  // Default values for missing chat properties
  const chatColor = chat.color || '#002857'; // Default blue color
  const chatIcon = chat.icon || 'chatbubble-outline'; // Default chat icon
  const chatName = chat.name || chat.subject || chat.targetDepartment || 'Conversation';

  useEffect(() => {
    // Simuler des messages
    const mockMessages = [
      {
        id: '1',
        text: 'Bonjour ! Comment puis-je vous aider aujourd\'hui ?',
        sender: 'service',
        timestamp: new Date(Date.now() - 3600000),
      },
      {
        id: '2',
        text: 'Bonjour, j\'ai une question concernant ma demande de congé',
        sender: 'user',
        timestamp: new Date(Date.now() - 3500000),
      },
      {
        id: '3',
        text: 'Je vais vérifier le statut de votre demande. Un moment s\'il vous plaît.',
        sender: 'service',
        timestamp: new Date(Date.now() - 3400000),
      },
    ];
    setMessages(mockMessages);
  }, []);

  const sendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now().toString(),
        text: newMessage,
        sender: 'user',
        timestamp: new Date(),
      };
      setMessages([...messages, message]);
      setNewMessage('');
    }
  };

  const renderMessage = ({ item }) => {
    const isUser = item.sender === 'user';
    
    return (
      <View style={[styles.messageContainer, isUser ? styles.userMessage : styles.serviceMessage]}>
        <View style={[
          styles.messageBubble, 
          { backgroundColor: isUser ? '#002857' : '#ffffff' }
        ]}>
          <Text style={[styles.messageText, { color: isUser ? '#ffffff' : '#2D3748' }]}>
            {item.text}
          </Text>
        </View>
        <Text style={styles.timestamp}>
          {item.timestamp.toLocaleTimeString('fr-FR', { 
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
            <Text style={styles.headerSubtitle}>En ligne</Text>
          </View>
        </View>
      </View>

      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
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
          />
          <TouchableOpacity 
            style={[styles.sendButton, { backgroundColor: chatColor }]}
            onPress={sendMessage}
            disabled={!newMessage.trim()}
          >
            <Ionicons name="send" size={20} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
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
});
