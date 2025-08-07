import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Image,
  Alert,
  ActivityIndicator,
  Dimensions,
  SafeAreaView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import NewsService from '../services/NewsService';

const { width } = Dimensions.get('window');

const NewsScreen = ({ navigation }) => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'high', 'urgent'

  useFocusEffect(
    useCallback(() => {
      loadNews();
    }, [])
  );

  const loadNews = async () => {
    try {
      setLoading(true);
      const response = await NewsService.getUserNews();
      if (response.success) {
        setNews(response.news || []);
      } else {
        Alert.alert('Erreur', response.message || 'Impossible de charger les actualités');
      }
    } catch (error) {
      console.error('Erreur chargement news:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNews();
    setRefreshing(false);
  };

  const markAsViewed = async (newsId) => {
    try {
      // Pour l'instant, juste mise à jour locale
      // TODO: Ajouter endpoint markAsViewed au backend si nécessaire
      setNews(prevNews => 
        prevNews.map(item => 
          item._id === newsId 
            ? { ...item, viewed: true }
            : item
        )
      );
    } catch (error) {
      console.error('Erreur marquage vue:', error);
    }
  };

  const toggleLike = async (newsId, currentLiked) => {
    try {
      // Pour l'instant, juste mise à jour locale
      // TODO: Ajouter endpoint toggleLike au backend si nécessaire
      setNews(prevNews =>
        prevNews.map(item =>
          item._id === newsId
            ? {
                ...item,
                liked: !currentLiked,
                stats: {
                  ...item.stats,
                  likes: !currentLiked ? (item.stats?.likes || 0) + 1 : Math.max(0, (item.stats?.likes || 0) - 1)
                }
              }
            : item
        )
      );
    } catch (error) {
      console.error('Erreur like:', error);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#FF4444';
      case 'normal': return '#0066CC';
      case 'low': return '#888888';
      default: return '#0066CC';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'urgent': return 'warning';
      case 'high': return 'alert-circle';
      case 'normal': return 'information-circle';
      case 'low': return 'checkmark-circle';
      default: return 'information-circle';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'safety': return 'shield-checkmark';
      case 'announcement': return 'megaphone';
      case 'training': return 'school';
      case 'general': return 'newspaper';
      case 'hr': return 'people';
      case 'it': return 'laptop';
      case 'events': return 'calendar';
      default: return 'newspaper';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date inconnue';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Date invalide';
    
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `Il y a ${diffInMinutes} min`;
    } else if (diffInMinutes < 1440) {
      return `Il y a ${Math.floor(diffInMinutes / 60)}h`;
    } else {
      return `Il y a ${Math.floor(diffInMinutes / 1440)} jour${Math.floor(diffInMinutes / 1440) > 1 ? 's' : ''}`;
    }
  };

  const filteredNews = news.filter(item => {
    if (filter === 'all') return true;
    return item.priority === filter;
  });

  const renderNewsItem = ({ item }) => {
    const priorityColor = getPriorityColor(item.priority);
    const isUnread = !item.viewed;

    return (
      <TouchableOpacity
        style={[styles.newsCard, isUnread && styles.unreadCard]}
        onPress={() => {
          markAsViewed(item._id);
          navigation.navigate('NewsDetail', { newsId: item._id, newsItem: item });
        }}
        activeOpacity={0.7}
      >
        {/* En-tête de la carte */}
        <View style={styles.cardHeader}>
          <View style={styles.categoryContainer}>
            <Ionicons 
              name={getCategoryIcon(item.category)} 
              size={16} 
              color={priorityColor} 
            />
            <Text style={[styles.categoryText, { color: priorityColor }]}>
              {item.category.toUpperCase()}
            </Text>
          </View>
          
          <View style={styles.priorityContainer}>
            <Ionicons 
              name={getPriorityIcon(item.priority)} 
              size={16} 
              color={priorityColor} 
            />
            {isUnread && <View style={styles.unreadDot} />}
          </View>
        </View>

        {/* Titre */}
        <Text style={[styles.newsTitle, isUnread && styles.unreadTitle]} numberOfLines={2}>
          {item.title}
        </Text>

        {/* Résumé */}
        {item.description && (
          <Text style={styles.newsSummary} numberOfLines={3}>
            {item.description}
          </Text>
        )}

        {/* Pied de carte */}
        <View style={styles.cardFooter}>
          <View style={styles.authorContainer}>
            <Ionicons name="person-circle" size={16} color="#666" />
            <Text style={styles.authorText}>{item.authorName}</Text>
            <Text style={styles.dateText}>• {formatDate(item.createdAt)}</Text>
          </View>

          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Ionicons name="eye" size={14} color="#888" />
              <Text style={styles.statText}>{item.stats?.views || 0}</Text>
            </View>
            
            <TouchableOpacity 
              style={styles.statItem}
              onPress={() => toggleLike(item._id, item.liked)}
            >
              <Ionicons 
                name={item.liked ? "heart" : "heart-outline"} 
                size={14} 
                color={item.liked ? "#FF4444" : "#888"} 
              />
              <Text style={[styles.statText, item.liked && styles.likedText]}>
                {item.stats?.likes || 0}
              </Text>
            </TouchableOpacity>

            <View style={styles.statItem}>
              <Ionicons name="chatbubble" size={14} color="#888" />
              <Text style={styles.statText}>{item.stats?.comments || 0}</Text>
            </View>
          </View>
        </View>

        {/* Indicateur d'expiration - retiré car pas dans notre structure simplifiée */}
      </TouchableOpacity>
    );
  };

  const renderFilterButtons = () => (
    <View style={styles.filterContainer}>
      {[
        { key: 'all', label: 'Toutes', icon: 'list' },
        { key: 'urgent', label: 'Urgent', icon: 'warning' },
        { key: 'high', label: 'Important', icon: 'alert-circle' },
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
      <Ionicons name="newspaper-outline" size={80} color="#CCCCCC" />
      <Text style={styles.emptyTitle}>Aucune actualité</Text>
      <Text style={styles.emptyText}>
        {filter === 'all' 
          ? "Aucune actualité disponible pour le moment" 
          : `Aucune actualité ${filter === 'urgent' ? 'urgente' : 'importante'} pour le moment`
        }
      </Text>
      <TouchableOpacity style={styles.refreshButton} onPress={loadNews}>
        <Text style={styles.refreshButtonText}>Actualiser</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0066CC" />
          <Text style={styles.loadingText}>Chargement des actualités...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* En-tête */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📰 Actualités</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity onPress={() => navigation.navigate('Debug')} style={styles.debugButton}>
            <Ionicons name="bug" size={20} color="#FF4444" />
          </TouchableOpacity>
          <TouchableOpacity onPress={loadNews}>
            <Ionicons name="refresh" size={24} color="#0066CC" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Filtres */}
      {renderFilterButtons()}

      {/* Liste des actualités */}
      <FlatList
        data={filteredNews}
        renderItem={renderNewsItem}
        keyExtractor={(item) => item._id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
      />
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
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  debugButton: {
    marginRight: 15,
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
  newsCard: {
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
  unreadCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#0066CC',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  categoryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  categoryText: {
    marginLeft: 5,
    fontSize: 12,
    fontWeight: '600',
  },
  priorityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#0066CC',
    marginLeft: 5,
  },
  newsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
    lineHeight: 22,
  },
  unreadTitle: {
    fontWeight: 'bold',
  },
  newsSummary: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  authorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  authorText: {
    marginLeft: 5,
    fontSize: 12,
    color: '#666666',
  },
  dateText: {
    marginLeft: 5,
    fontSize: 12,
    color: '#888888',
  },
  statsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 15,
  },
  statText: {
    marginLeft: 3,
    fontSize: 12,
    color: '#888888',
  },
  likedText: {
    color: '#FF4444',
  },
  expiryIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
  },
  expiryText: {
    marginLeft: 5,
    fontSize: 11,
    color: '#FF8800',
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
  refreshButton: {
    backgroundColor: '#0066CC',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  refreshButtonText: {
    color: '#FFFFFF',
    fontWeight: '500',
  },
});

export default NewsScreen;
