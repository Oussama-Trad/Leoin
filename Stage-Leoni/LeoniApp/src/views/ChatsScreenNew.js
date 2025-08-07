import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  Alert, 
  RefreshControl,
  Dimensions 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ChatModel from '../models/ChatModel';
import AuthController from '../controllers/AuthController';

const { width } = Dimensions.get('window');

export default function ChatsScreen({ navigation }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      setLoading(true);
      // Simuler des chats avec les services principaux
      const mockChats = [
        {
          id: '1',
          name: 'Support Technique',
          lastMessage: 'Votre demande a été prise en compte',
          lastMessageTime: new Date(),
          icon: 'construct-outline',
          color: '#4A90E2',
          unreadCount: 2,
          type: 'support'
        },
        {
          id: '2', 
          name: 'Ressources Humaines',
          lastMessage: 'Documents reçus, merci !',
          lastMessageTime: new Date(Date.now() - 3600000),
          icon: 'people-outline',
          color: '#48BB78',
          unreadCount: 0,
          type: 'hr'
        },
        {
          id: '3',
          name: 'Administration',
          lastMessage: 'Nouvelle procédure disponible',
          lastMessageTime: new Date(Date.now() - 7200000),
          icon: 'business-outline',
          color: '#ED8936',
          unreadCount: 1,
          type: 'admin'
        },
        {
          id: '4',
          name: 'Formation',
          lastMessage: 'Session programmée pour demain',
          lastMessageTime: new Date(Date.now() - 86400000),
          icon: 'school-outline',
          color: '#9F7AEA',
          unreadCount: 0,
          type: 'training'
        }
      ];
      setChats(mockChats);
    } catch (error) {
      console.error('Erreur lors du chargement des chats:', error);
      Alert.alert('Erreur', 'Impossible de charger les conversations');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadChats();
    setRefreshing(false);
  };

  const handleChatPress = (chat) => {
    navigation.navigate('ChatDetail', { chat });
  };

  const formatTime = (date) => {
    const now = new Date();
    const diff = now - date;
    
    if (diff < 3600000) { // moins d'1h
      return `${Math.floor(diff / 60000)}min`;
    } else if (diff < 86400000) { // moins d'1j
      return `${Math.floor(diff / 3600000)}h`;
    } else {
      return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
    }
  };

  const renderChatCard = ({ item, index }) => (
    <TouchableOpacity
      style={[styles.chatCard, { marginTop: index === 0 ? 0 : 15 }]}
      onPress={() => handleChatPress(item)}
      activeOpacity={0.8}
    >
      <View style={styles.cardContent}>
        <View style={styles.chatInfo}>
          <View style={[styles.iconContainer, { backgroundColor: `${item.color}15` }]}>
            <Ionicons name={item.icon} size={28} color={item.color} />
          </View>
          
          <View style={styles.chatDetails}>
            <View style={styles.chatHeader}>
              <Text style={styles.chatName}>{item.name}</Text>
              <View style={styles.timeContainer}>
                <Text style={styles.timeText}>{formatTime(item.lastMessageTime)}</Text>
                {item.unreadCount > 0 && (
                  <View style={styles.unreadBadge}>
                    <Text style={styles.unreadText}>{item.unreadCount}</Text>
                  </View>
                )}
              </View>
            </View>
            
            <Text style={styles.lastMessage} numberOfLines={1}>
              {item.lastMessage}
            </Text>
          </View>
        </View>

        <View style={styles.chatActions}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="chatbubble-outline" size={20} color={item.color} />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <View style={styles.loadingCard}>
            <Ionicons name="chatbubbles-outline" size={48} color="#002857" />
            <Text style={styles.loadingText}>Chargement des conversations...</Text>
          </View>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>💬 Messages</Text>
          <Text style={styles.headerSubtitle}>Communiquez avec les services</Text>
        </View>
      </View>

      {chats.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="chatbubbles-outline" size={64} color="#CBD5E0" />
          <Text style={styles.emptyTitle}>Aucune conversation</Text>
          <Text style={styles.emptyText}>Vos messages apparaîtront ici</Text>
        </View>
      ) : (
        <FlatList
          data={chats}
          renderItem={renderChatCard}
          keyExtractor={(item) => item.id}
          refreshControl={
            <RefreshControl 
              refreshing={refreshing} 
              onRefresh={onRefresh}
              colors={['#48BB78']}
              tintColor="#48BB78"
            />
          }
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContainer}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f4f8',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
    backgroundColor: '#002857',
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.9,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 25,
    paddingBottom: 30,
  },
  chatCard: {
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    backgroundColor: '#ffffff',
  },
  cardContent: {
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  chatInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  chatDetails: {
    flex: 1,
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  chatName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2D3748',
  },
  timeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeText: {
    fontSize: 12,
    color: '#718096',
    marginRight: 8,
  },
  unreadBadge: {
    backgroundColor: '#E53E3E',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  unreadText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  lastMessage: {
    fontSize: 14,
    color: '#718096',
    lineHeight: 20,
  },
  chatActions: {
    marginLeft: 15,
  },
  actionButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f4f8',
  },
  loadingCard: {
    backgroundColor: '#ffffff',
    padding: 40,
    borderRadius: 20,
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  loadingText: {
    fontSize: 18,
    color: '#4A5568',
    marginTop: 16,
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A5568',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#718096',
    textAlign: 'center',
    lineHeight: 24,
  },
});
