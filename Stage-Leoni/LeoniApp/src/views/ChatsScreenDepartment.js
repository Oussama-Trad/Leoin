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
import AsyncStorage from '@react-native-async-storage/async-storage';

const ChatsScreenDepartment = ({ navigation }) => {
  const [chats, setChats] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'active', 'resolved'
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [chatSubject, setChatSubject] = useState('');
  const [creatingChat, setCreatingChat] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadUserProfile();
      loadChats();
      loadDepartments();
    }, [])
  );

  const loadUserProfile = async () => {
    try {
      const userDataStr = await AsyncStorage.getItem('userData');
      if (userDataStr) {
        const userData = JSON.parse(userDataStr);
        setUserProfile(userData);
        console.log('📱 Profil utilisateur:', userData);
      }
    } catch (error) {
      console.error('Erreur chargement profil:', error);
    }
  };

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

  const loadDepartments = async () => {
    try {
      console.log('📋 Chargement des départements depuis l\'API...');
      const response = await chatAPI.getDepartments();
      console.log('📋 Réponse API départements complète:', JSON.stringify(response, null, 2));
      
      if (response.success && response.data && Array.isArray(response.data) && response.data.length > 0) {
        console.log('✅ Départements chargés depuis l\'API:', response.data.length, 'départements');
        setDepartments(response.data);
      } else {
        console.log('⚠️ API départements invalide ou vide, utilisation du fallback');
        console.log('Réponse reçue:', response);
        // Fallback avec les vrais départements de manufacture
        const fallbackDepartments = [
          { _id: '1', name: 'Production', location: 'Messadine', description: 'Département Production - Fabrication et assemblage' },
          { _id: '2', name: 'Production', location: 'Mateur', description: 'Département Production - Fabrication et assemblage' },
          { _id: '3', name: 'Production', location: 'Manzel Hayet', description: 'Département Production - Fabrication et assemblage' },
          { _id: '4', name: 'Qualité', location: 'Messadine', description: 'Département Qualité - Contrôle et conformité' },
          { _id: '5', name: 'Qualité', location: 'Mateur', description: 'Département Qualité - Contrôle et conformité' },
          { _id: '6', name: 'Qualité', location: 'Manzel Hayet', description: 'Département Qualité - Contrôle et conformité' },
          { _id: '7', name: 'Maintenance', location: 'Messadine', description: 'Département Maintenance - Entretien équipements' },
          { _id: '8', name: 'Maintenance', location: 'Mateur', description: 'Département Maintenance - Entretien équipements' },
          { _id: '9', name: 'Maintenance', location: 'Manzel Hayet', description: 'Département Maintenance - Entretien équipements' },
          { _id: '10', name: 'Logistique', location: 'Messadine', description: 'Département Logistique - Gestion stocks et expéditions' },
          { _id: '11', name: 'Logistique', location: 'Mateur', description: 'Département Logistique - Gestion stocks et expéditions' },
          { _id: '12', name: 'Logistique', location: 'Manzel Hayet', description: 'Département Logistique - Gestion stocks et expéditions' },
          { _id: '13', name: 'Ingénierie', location: 'Messadine', description: 'Département Ingénierie - Conception et amélioration' },
          { _id: '14', name: 'Planification', location: 'Messadine', description: 'Département Planification - Organisation production' },
          { _id: '15', name: 'Achat', location: 'Messadine', description: 'Département Achat - Approvisionnement matières' },
          { _id: '16', name: 'Ressources Humaines', location: 'Messadine', description: 'Département RH - Gestion du personnel' },
          { _id: '17', name: 'Finance', location: 'Messadine', description: 'Département Finance - Gestion financière' },
          { _id: '18', name: 'Support Technique', location: 'Messadine', description: 'Support Technique - Assistance générale' },
        ];
        setDepartments(fallbackDepartments);
        console.log('✅ Départements fallback définis:', fallbackDepartments.length, 'départements');
      }
    } catch (error) {
      console.error('❌ Erreur chargement départements depuis API:', error);
      // Fallback en cas d'erreur réseau
      const fallbackDepartments = [
        { _id: '1', name: 'Production', location: 'Messadine', description: 'Département Production - Fabrication et assemblage' },
        { _id: '2', name: 'Production', location: 'Mateur', description: 'Département Production - Fabrication et assemblage' },
        { _id: '3', name: 'Production', location: 'Manzel Hayet', description: 'Département Production - Fabrication et assemblage' },
        { _id: '4', name: 'Qualité', location: 'Messadine', description: 'Département Qualité - Contrôle et conformité' },
        { _id: '5', name: 'Qualité', location: 'Mateur', description: 'Département Qualité - Contrôle et conformité' },
        { _id: '6', name: 'Qualité', location: 'Manzel Hayet', description: 'Département Qualité - Contrôle et conformité' },
        { _id: '7', name: 'Maintenance', location: 'Messadine', description: 'Département Maintenance - Entretien équipements' },
        { _id: '8', name: 'Maintenance', location: 'Mateur', description: 'Département Maintenance - Entretien équipements' },
        { _id: '9', name: 'Maintenance', location: 'Manzel Hayet', description: 'Département Maintenance - Entretien équipements' },
        { _id: '10', name: 'Logistique', location: 'Messadine', description: 'Département Logistique - Gestion stocks et expéditions' },
        { _id: '11', name: 'Logistique', location: 'Mateur', description: 'Département Logistique - Gestion stocks et expéditions' },
        { _id: '12', name: 'Logistique', location: 'Manzel Hayet', description: 'Département Logistique - Gestion stocks et expéditions' },
        { _id: '13', name: 'Ingénierie', location: 'Messadine', description: 'Département Ingénierie - Conception et amélioration' },
        { _id: '14', name: 'Planification', location: 'Messadine', description: 'Département Planification - Organisation production' },
        { _id: '15', name: 'Achat', location: 'Messadine', description: 'Département Achat - Approvisionnement matières' },
        { _id: '16', name: 'Ressources Humaines', location: 'Messadine', description: 'Département RH - Gestion du personnel' },
        { _id: '17', name: 'Finance', location: 'Messadine', description: 'Département Finance - Gestion financière' },
        { _id: '18', name: 'Support Technique', location: 'Messadine', description: 'Support Technique - Assistance générale' },
      ];
      setDepartments(fallbackDepartments);
      console.log('✅ Départements fallback d\'erreur définis:', fallbackDepartments.length, 'départements');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadChats();
    setRefreshing(false);
  };

  const createNewChat = async () => {
    if (!selectedDepartment || !chatSubject.trim()) {
      Alert.alert('Erreur', 'Veuillez sélectionner un département et saisir un sujet');
      return;
    }

    if (!userProfile || !userProfile.location) {
      Alert.alert('Erreur', 'Profil utilisateur incomplet. Veuillez vous reconnecter.');
      return;
    }

    try {
      setCreatingChat(true);
      
      console.log('🚀 Création chat département:', {
        targetDepartment: selectedDepartment.name,
        targetLocation: selectedDepartment.location || userProfile.location,
        subject: chatSubject.trim(),
        userLocation: userProfile.location,
        baseURL: 'http://192.168.1.15:5000'
      });

      // Test de connectivité avec localhost uniquement
      let serverFound = false;
      const testUrls = [
        'http://localhost:5000',
        'http://127.0.0.1:5000'
      ];

      for (const testUrl of testUrls) {
        try {
          console.log(`🔍 Test connectivité serveur: ${testUrl}/health`);
          const testResponse = await fetch(`${testUrl}/health`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            timeout: 3000,
          });
          
          if (testResponse.ok) {
            const healthData = await testResponse.json();
            console.log(`✅ Serveur trouvé sur ${testUrl}:`, healthData);
            serverFound = true;
            break;
          }
        } catch (testError) {
          console.log(`❌ ${testUrl} non accessible:`, testError.message);
        }
      }

      if (!serverFound) {
        console.error('❌ Aucun serveur accessible sur localhost');
        Alert.alert(
          'Erreur de connexion', 
          'Impossible de joindre le serveur backend sur localhost.\n\nVérifiez que:\n- Le serveur Python est démarré sur localhost:5000\n- Votre connexion réseau fonctionne\n- Aucun firewall ne bloque le port 5000',
          [
            { text: 'Réessayer', onPress: () => createNewChat() },
            { text: 'Annuler', style: 'cancel' }
          ]
        );
        return;
      }

      console.log('🚀 Création du chat avec le département:', selectedDepartment.name);
      // Création de la conversation avec les bons paramètres
      const response = await chatAPI.createChatWithDepartment(
        selectedDepartment.name,  // Le nom du département sera passé comme "department"
        selectedDepartment.location || userProfile.location,
        chatSubject.trim(),
        'normal'
      );

      if (response.success) {
        Alert.alert(
          'Succès', 
          `Votre message a été envoyé au département ${selectedDepartment.name} (${selectedDepartment.location || userProfile.location}).\nUn admin va vous répondre.`
        );
        
        setShowNewChatModal(false);
        setSelectedDepartment(null);
        setChatSubject('');
        await loadChats();
        
        // Naviguer vers le nouveau chat si possible
        if (response.data && response.data._id) {
          navigation.navigate('ChatDetail', { 
            chatId: response.data._id,
            chatData: response.data 
          });
        }
      } else {
        Alert.alert('Erreur', response.message || 'Impossible de créer la conversation');
      }
    } catch (error) {
      console.error('Erreur création chat:', error);
      Alert.alert(
        'Erreur de connexion', 
        `Problème de communication avec le serveur.\nDétails: ${error.message}\nVérifiez que le serveur Python est démarré.`
      );
    } finally {
      setCreatingChat(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#0066CC';
      case 'pending': return '#FF8800';
      case 'in_progress': return '#0066CC';
      case 'resolved': return '#00AA00';
      case 'closed': return '#888888';
      default: return '#888888';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return 'chatbubble-ellipses';
      case 'pending': return 'time';
      case 'in_progress': return 'chatbubble-ellipses';
      case 'resolved': return 'checkmark-circle';
      case 'closed': return 'close-circle';
      default: return 'help-circle';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Actif';
      case 'pending': return 'En attente';
      case 'in_progress': return 'En cours';
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
    if (filter === 'active') return chat.status === 'active' || chat.status === 'pending' || chat.status === 'in_progress';
    return chat.status === filter;
  });

  const renderChatItem = ({ item }) => {
    const statusColor = getStatusColor(item.status);
    const priorityColor = getPriorityColor(item.priority);
    const hasUnreadMessage = item.unreadCount > 0;

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
          <View style={styles.departmentInfo}>
            <Text style={styles.departmentName}>
              🏢 {item.targetDepartment || 'Département inconnu'}
            </Text>
            <Text style={styles.locationText}>
              📍 {item.targetLocation || 'Location inconnue'}
            </Text>
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
            <Text style={styles.chatDate}>{formatDate(item.lastActivityAt || item.createdAt)}</Text>
            {item.priority !== 'normal' && (
              <View style={[styles.priorityBadge, { backgroundColor: priorityColor }]}>
                <Text style={styles.priorityBadgeText}>
                  {item.priority === 'urgent' ? 'URGENT' : 'IMPORTANT'}
                </Text>
              </View>
            )}
            {hasUnreadMessage && (
              <View style={styles.unreadBadge}>
                <Text style={styles.unreadBadgeText}>{item.unreadCount}</Text>
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
              {item.lastMessage.senderName || 'Admin'}:
            </Text>
            <Text style={styles.lastMessageText} numberOfLines={2}>
              {item.lastMessage.content || item.lastMessage.message || 'Message...'}
            </Text>
          </View>
        )}

        {/* Nombre de messages */}
        <View style={styles.messageCountContainer}>
          <Ionicons name="chatbubble" size={14} color="#666" />
          <Text style={styles.messageCountText}>
            {item.messageCount || 0} message{(item.messageCount || 0) > 1 ? 's' : ''}
          </Text>
        </View>
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
          ? "Vous n'avez pas encore de conversations. Contactez un département !" 
          : `Aucune conversation ${filter === 'active' ? 'active' : 'résolue'} pour le moment.`
        }
      </Text>
      {filter === 'all' && (
        <TouchableOpacity 
          style={styles.startChatButton} 
          onPress={() => setShowNewChatModal(true)}
        >
          <Text style={styles.startChatButtonText}>Contacter un département</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderDepartmentItem = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.departmentItem,
        selectedDepartment?._id === item._id && styles.departmentItemSelected
      ]}
      onPress={() => setSelectedDepartment(item)}
    >
      <View style={styles.departmentInfo}>
        <Text style={styles.departmentItemName}>🏢 {item.name}</Text>
        {item.location && (
          <Text style={styles.departmentItemLocation}>📍 {item.location}</Text>
        )}
        <Text style={styles.departmentItemDescription}>{item.description}</Text>
      </View>
      <Ionicons 
        name={selectedDepartment?._id === item._id ? 'radio-button-on' : 'radio-button-off'} 
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
          <Text style={styles.modalTitle}>Contacter un département</Text>
          <TouchableOpacity onPress={() => setShowNewChatModal(false)}>
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
        </View>

        <View style={styles.modalContent}>
          {userProfile && (
            <View style={styles.userLocationInfo}>
              <Ionicons name="location" size={16} color="#0066CC" />
              <Text style={styles.userLocationText}>
                Votre location: {userProfile.location}
              </Text>
            </View>
          )}

          <Text style={styles.modalSectionTitle}>Choisir un département</Text>
          <FlatList
            data={departments}
            renderItem={renderDepartmentItem}
            keyExtractor={(item) => item._id}
            style={styles.departmentsList}
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
              (!selectedDepartment || !chatSubject.trim() || creatingChat) && styles.createChatButtonDisabled
            ]}
            onPress={createNewChat}
            disabled={!selectedDepartment || !chatSubject.trim() || creatingChat}
          >
            {creatingChat ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <>
                <Ionicons name="send" size={20} color="#FFFFFF" />
                <Text style={styles.createChatButtonText}>Envoyer au département</Text>
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

      {/* Info utilisateur */}
      {userProfile && (
        <View style={styles.userInfoBanner}>
          <Ionicons name="person" size={16} color="#0066CC" />
          <Text style={styles.userInfoText}>
            {userProfile.firstName} {userProfile.lastName} - {userProfile.location}
          </Text>
        </View>
      )}

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
  userInfoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#F0F8FF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  userInfoText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#0066CC',
    fontWeight: '500',
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
  departmentInfo: {
    flex: 1,
  },
  departmentName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 2,
  },
  locationText: {
    fontSize: 12,
    color: '#666666',
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
    marginBottom: 4,
  },
  priorityBadgeText: {
    fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  unreadBadge: {
    backgroundColor: '#FF4444',
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    minWidth: 20,
    alignItems: 'center',
  },
  unreadBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
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
  messageCountContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  messageCountText: {
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
  userLocationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F8FF',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  userLocationText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#0066CC',
    fontWeight: '500',
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 15,
  },
  departmentsList: {
    maxHeight: 200,
    marginBottom: 20,
  },
  departmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 10,
  },
  departmentItemSelected: {
    borderWidth: 2,
    borderColor: '#0066CC',
  },
  departmentItemName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333333',
    marginBottom: 4,
  },
  departmentItemLocation: {
    fontSize: 12,
    color: '#0066CC',
    marginBottom: 4,
    fontWeight: '500',
  },
  departmentItemDescription: {
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

export default ChatsScreenDepartment;
