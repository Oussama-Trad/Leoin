import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  TextInput,
  Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { chatAPI } from '../controllers/apiService';

const ChatsScreen = ({ navigation }) => {
  const [chats, setChats] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'active', 'resolved'
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [selectedService, setSelectedService] = useState(null);
  const [chatSubject, setChatSubject] = useState('');
  const [creatingChat, setCreatingChat] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadChats();
      loadServices();
    }, [])
  );

  const loadChats = async () => {
    try {
      setLoading(true);
      const response = await chatAPI.getChats();
      if (response.success) {
        setChats(response.data || []);
      } else {
        Alert.alert('Erreur', response.message || 'Impossible de charger vos conversations');
      }
    } catch (error) {
      console.error('Erreur chargement chats:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setLoading(false);
    }
  };

  const loadServices = async () => {
    try {
      const response = await chatAPI.getServices();
      if (response.success) {
        setServices(response.data || []);
      }
    } catch (error) {
      console.error('Erreur chargement services:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadChats();
    setRefreshing(false);
  };

  const createNewChat = async () => {
    if (!selectedService || !chatSubject.trim()) {
      Alert.alert('Erreur', 'Veuillez sélectionner un service et saisir un sujet');
      return;
    }

    try {
      setCreatingChat(true);
      const response = await chatAPI.createChat(
        selectedService._id,
        chatSubject.trim(),
        'normal'
      );

      if (response.success) {
        setShowNewChatModal(false);
        setSelectedService(null);
        setChatSubject('');
        await loadChats();
        
        // Naviguer vers le nouveau chat
        navigation.navigate('ChatDetail', { 
          chatId: response.data._id,
          chatData: response.data 
        });
      } else {
        Alert.alert('Erreur', response.message || 'Impossible de créer la conversation');
      }
    } catch (error) {
      console.error('Erreur création chat:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setCreatingChat(false);
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return 'chatbubble-ellipses';
      case 'pending': return 'time';
      case 'resolved': return 'checkmark-circle';
      case 'closed': return 'close-circle';
      default: return 'help-circle';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Actif';
      case 'pending': return 'En attente';
      case 'resolved': return 'Résolu';
      case 'closed': return 'Fermé';
      default: return 'Inconnu';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return '#FF4444';
      case 'high': return '#FF8800';
      case 'normal': return '#0066CC';
      case 'low': return '#888888';
      default: return '#0066CC';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `Il y a ${diffInMinutes} min`;
    } else if (diffInMinutes < 1440) {
      return `Il y a ${Math.floor(diffInMinutes / 60)}h`;
    } else if (diffInMinutes < 10080) {
      return `Il y a ${Math.floor(diffInMinutes / 1440)} jour${Math.floor(diffInMinutes / 1440) > 1 ? 's' : ''}`;
    } else {
      return date.toLocaleDateString('fr-FR');
    }
  };

  const filteredChats = chats.filter(chat => {
    if (filter === 'all') return true;
    if (filter === 'active') return chat.status === 'active' || chat.status === 'pending';
    return chat.status === filter;
  });

  const renderChatItem = ({ item }) => {
    const statusColor = getStatusColor(item.status);
    const priorityColor = getPriorityColor(item.priority);
    const hasUnreadMessage = item.status === 'active' && item.lastMessage?.senderId !== 'current_user_id'; // À adapter

    return (
      <TouchableOpacity
        style={[styles.chatCard, hasUnreadMessage && styles.unreadChatCard]}
        onPress={() => navigation.navigate('ChatDetail', { 
          chatId: item._id,
          chatData: item 
        })}
        activeOpacity={0.7}
      >
        {/* En-tête de la carte */}
        <View style={styles.chatHeader}>
          <View style={styles.serviceInfo}>
            <Text style={styles.serviceName}>{item.participants.service.serviceName}</Text>
            <View style={styles.statusContainer}>
              <Ionicons 
                name={getStatusIcon(item.status)} 
                size={12} 
                color={statusColor} 
              />
              <Text style={[styles.statusText, { color: statusColor }]}>
                {getStatusText(item.status)}
              </Text>
            </View>
          </View>
          
          <View style={styles.chatMeta}>
            <Text style={styles.chatDate}>{formatDate(item.lastActivityAt)}</Text>
            {item.priority !== 'normal' && (
              <View style={[styles.priorityBadge, { backgroundColor: priorityColor }]}>
                <Text style={styles.priorityBadgeText}>
                  {item.priority === 'urgent' ? 'URGENT' : 'IMPORTANT'}
                </Text>
              </View>
            )}
          </View>
        </View>

        {/* Sujet */}
        <Text style={styles.chatSubject} numberOfLines={1}>
          {item.subject}
        </Text>

        {/* Dernier message */}
        {item.lastMessage && (
          <View style={styles.lastMessageContainer}>
            <Text style={styles.lastMessageSender}>
              {item.lastMessage.senderName}:
            </Text>
            <Text style={styles.lastMessageText} numberOfLines={2}>
              {item.lastMessage.text}
            </Text>
          </View>
        )}

        {/* Représentant du service */}
        <View style={styles.representativeContainer}>
          <Ionicons name="person" size={14} color="#666" />
          <Text style={styles.representativeText}>
            {item.participants.service.currentRepresentative.name}
          </Text>
          
          {hasUnreadMessage && <View style={styles.unreadIndicator} />}
        </View>

        {/* Évaluation si fermé */}
        {item.status === 'closed' && item.rating && (
          <View style={styles.ratingContainer}>
            <View style={styles.starsContainer}>
              {[1, 2, 3, 4, 5].map((star) => (
                <Ionicons
                  key={star}
                  name={star <= item.rating.score ? 'star' : 'star-outline'}
                  size={12}
                  color="#FFD700"
                />
              ))}
            </View>
            <Text style={styles.ratingText}>({item.rating.score}/5)</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const renderFilterButtons = () => (
    <View style={styles.filterContainer}>
      {[
        { key: 'all', label: 'Toutes', icon: 'list' },
        { key: 'active', label: 'Actives', icon: 'chatbubble-ellipses' },
        { key: 'resolved', label: 'Résolues', icon: 'checkmark-circle' },
      ].map((filterOption) => (
        <TouchableOpacity
          key={filterOption.key}
          style={[
            styles.filterButton,
            filter === filterOption.key && styles.filterButtonActive
          ]}
          onPress={() => setFilter(filterOption.key)}
        >
          <Ionicons 
            name={filterOption.icon} 
            size={16} 
            color={filter === filterOption.key ? '#FFFFFF' : '#0066CC'} 
          />
          <Text style={[
            styles.filterButtonText,
            filter === filterOption.key && styles.filterButtonTextActive
          ]}>
            {filterOption.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="chatbubbles-outline" size={80} color="#CCCCCC" />
      <Text style={styles.emptyTitle}>
        {filter === 'all' ? 'Aucune conversation' : `Aucune conversation ${filter === 'active' ? 'active' : 'résolue'}`}
      </Text>
      <Text style={styles.emptyText}>
        {filter === 'all' 
          ? "Vous n'avez pas encore de conversations. Commencez par contacter un service !" 
          : `Aucune conversation ${filter === 'active' ? 'active' : 'résolue'} pour le moment.`
        }
      </Text>
      {filter === 'all' && (
        <TouchableOpacity 
          style={styles.startChatButton} 
          onPress={() => setShowNewChatModal(true)}
        >
          <Text style={styles.startChatButtonText}>Démarrer une conversation</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderServiceItem = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.serviceItem,
        selectedService?._id === item._id && styles.serviceItemSelected
      ]}
      onPress={() => setSelectedService(item)}
    >
      <View style={styles.serviceInfo}>
        <Text style={styles.serviceItemName}>{item.name}</Text>
        <Text style={styles.serviceItemDescription}>{item.description}</Text>
      </View>
      <Ionicons 
        name={selectedService?._id === item._id ? 'radio-button-on' : 'radio-button-off'} 
        size={20} 
        color="#0066CC" 
      />
    </TouchableOpacity>
  );

  const renderNewChatModal = () => (
    <Modal
      visible={showNewChatModal}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Nouvelle conversation</Text>
          <TouchableOpacity onPress={() => setShowNewChatModal(false)}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>

        <View style={styles.modalContent}>
          <Text style={styles.modalSectionTitle}>Choisir un service</Text>
          <FlatList
            data={services}
            renderItem={renderServiceItem}
            keyExtractor={(item) => item._id}
            style={styles.servicesList}
            showsVerticalScrollIndicator={false}
          />

          <Text style={styles.modalSectionTitle}>Sujet de votre demande</Text>
          <TextInput
            style={styles.subjectInput}
            placeholder="Décrivez brièvement votre demande..."
            value={chatSubject}
            onChangeText={setChatSubject}
            multiline
            maxLength={200}
          />

          <TouchableOpacity
            style={[
              styles.createChatButton,
              (!selectedService || !chatSubject.trim() || creatingChat) && styles.createChatButtonDisabled
            ]}
            onPress={createNewChat}
            disabled={!selectedService || !chatSubject.trim() || creatingChat}
          >
            {creatingChat ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <>
                <Ionicons name="add" size={20} color="#FFFFFF" />
                <Text style={styles.createChatButtonText}>Créer la conversation</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </Modal>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0066CC" />
          <Text style={styles.loadingText}>Chargement de vos conversations...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* En-tête */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>💬 Mes conversations</Text>
        <TouchableOpacity onPress={() => setShowNewChatModal(true)}>
          <Ionicons name="add-circle" size={28} color="#0066CC" />
        </TouchableOpacity>
      </View>

      {/* Filtres */}
      {renderFilterButtons()}

      {/* Liste des conversations */}
      <FlatList
        data={filteredChats}
        renderItem={renderChatItem}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
      />

      {/* Modal nouvelle conversation */}
      {renderNewChatModal()}
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
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    marginRight: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#0066CC',
    backgroundColor: '#FFFFFF',
  },
  filterButtonActive: {
    backgroundColor: '#0066CC',
  },
  filterButtonText: {
    marginLeft: 5,
    color: '#0066CC',
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#FFFFFF',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 15,
  },
  chatCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  unreadChatCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#0066CC',
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  serviceInfo: {
    flex: 1,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 4,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: '500',
  },
  chatMeta: {
    alignItems: 'flex-end',
  },
  chatDate: {
    fontSize: 12,
    color: '#888888',
    marginBottom: 4,
  },
  priorityBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
  },
  priorityBadgeText: {
    fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  chatSubject: {
    fontSize: 15,
    fontWeight: '500',
    color: '#333333',
    marginBottom: 8,
  },
  lastMessageContainer: {
    marginBottom: 10,
  },
  lastMessageSender: {
    fontSize: 12,
    color: '#0066CC',
    fontWeight: '500',
  },
  lastMessageText: {
    fontSize: 14,
    color: '#666666',
    marginTop: 2,
    lineHeight: 18,
  },
  representativeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  representativeText: {
    marginLeft: 5,
    fontSize: 12,
    color: '#666666',
    flex: 1,
  },
  unreadIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#0066CC',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
  },
  starsContainer: {
    flexDirection: 'row',
  },
  ratingText: {
    marginLeft: 5,
    fontSize: 12,
    color: '#666666',
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 14,
    color: '#666666',
    textAlign: 'center',
    paddingHorizontal: 40,
    lineHeight: 20,
    marginBottom: 20,
  },
  startChatButton: {
    backgroundColor: '#0066CC',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  startChatButtonText: {
    color: '#FFFFFF',
    fontWeight: '500',
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
  modalContent: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 15,
  },
  servicesList: {
    maxHeight: 200,
    marginBottom: 20,
  },
  serviceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 10,
  },
  serviceItemSelected: {
    borderWidth: 2,
    borderColor: '#0066CC',
  },
  serviceItemName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333333',
    marginBottom: 4,
  },
  serviceItemDescription: {
    fontSize: 12,
    color: '#666666',
  },
  subjectInput: {
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
  createChatButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0066CC',
    paddingVertical: 15,
    borderRadius: 8,
  },
  createChatButtonDisabled: {
    backgroundColor: '#CCCCCC',
  },
  createChatButtonText: {
    marginLeft: 8,
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ChatsScreen;
