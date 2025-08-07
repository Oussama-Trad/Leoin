import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  Alert, 
  RefreshControl,
  Dimensions,
  ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import NewsModel from '../models/NewsModel';
import NewsService from '../services/NewsService';

const { width } = Dimensions.get('window');

export default function NewsScreenNew({ navigation }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    try {
      setLoading(true);
      console.log('🔍 Chargement des news avec NewsService...');
      
      const response = await NewsService.getUserNews();
      console.log('📡 Réponse NewsService:', response);
      
      if (response && response.success) {
        const newsData = response.news || [];
        setNews(newsData);
        console.log(`✅ ${newsData.length} actualités chargées`);
        
        if (newsData.length === 0) {
          console.log('⚠️ Aucune actualité trouvée pour cet utilisateur');
        }
      } else {
        console.log('⚠️ Échec du chargement:', response?.message || 'Erreur inconnue');
        setNews([]);
        Alert.alert('Erreur', response?.message || 'Impossible de charger les actualités');
      }
    } catch (error) {
      console.error('❌ Erreur lors du chargement des actualités:', error);
      Alert.alert('Erreur', error.message || 'Problème de connexion');
      setNews([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNews();
  };

  const renderNewsCard = ({ item }) => (
    <TouchableOpacity style={styles.newsCard}>
      <View style={styles.cardHeader}>
        <View style={styles.categoryContainer}>
          <Ionicons name="newspaper" size={16} color="#0066CC" />
          <Text style={styles.categoryText}>{item.category || 'GÉNÉRAL'}</Text>
        </View>
        <View style={styles.priorityContainer}>
          <Ionicons name="alert-circle" size={16} color="#FF4444" />
          <Text style={styles.priorityText}>{item.priority || 'NORMAL'}</Text>
        </View>
      </View>

      <Text style={styles.newsTitle} numberOfLines={2}>
        {item.title}
      </Text>

      {item.description && (
        <Text style={styles.newsDescription} numberOfLines={3}>
          {item.description}
        </Text>
      )}

      <View style={styles.cardFooter}>
        <View style={styles.authorContainer}>
          <Ionicons name="person-circle" size={16} color="#666" />
          <Text style={styles.authorText}>{item.authorName || 'Administrateur'}</Text>
        </View>
        <Text style={styles.dateText}>
          {item.createdAt ? new Date(item.createdAt).toLocaleDateString() : 'Date inconnue'}
        </Text>
      </View>

      <View style={styles.targetInfo}>
        <Ionicons name="location" size={12} color="#999" />
        <Text style={styles.targetText}>
          {item.targetLocation === 'All' ? 'Tous les sites' : item.targetLocation} • {' '}
          {item.targetDepartment === 'All' ? 'Tous les départements' : item.targetDepartment}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <View style={styles.loadingCard}>
            <Ionicons name="newspaper-outline" size={48} color="#002857" />
            <Text style={styles.loadingText}>Chargement des actualités...</Text>
          </View>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Boutons de debug temporaires */}
      <View style={styles.debugContainer}>
        <TouchableOpacity 
          style={styles.debugButton}
          onPress={() => navigation.navigate('LoginTest')}
        >
          <Ionicons name="log-in" size={16} color="white" />
          <Text style={styles.debugButtonText}>🔐 Test Login</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.debugButton, styles.refreshButton]}
          onPress={loadNews}
        >
          <Ionicons name="refresh" size={16} color="white" />
          <Text style={styles.debugButtonText}>🔄 Refresh News</Text>
        </TouchableOpacity>
      </View>

      {news.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="newspaper-outline" size={64} color="#CBD5E0" />
          <Text style={styles.emptyTitle}>Aucune actualité</Text>
          <Text style={styles.emptyText}>Les nouvelles apparaîtront ici</Text>
        </View>
      ) : (
        <FlatList
          data={news}
          renderItem={renderNewsCard}
          keyExtractor={(item) => item._id || item.id || Math.random().toString()}
          refreshControl={
            <RefreshControl 
              refreshing={refreshing} 
              onRefresh={onRefresh}
              colors={['#002857']}
              tintColor="#002857"
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
    backgroundColor: '#F8F9FA',
  },
  debugContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#FFF3CD',
    borderBottomWidth: 1,
    borderBottomColor: '#FFEAA7',
  },
  debugButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0066CC',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 10,
  },
  refreshButton: {
    backgroundColor: '#28A745',
  },
  debugButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 5,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingCard: {
    backgroundColor: 'white',
    padding: 30,
    borderRadius: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#002857',
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 15,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 15,
  },
  newsCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
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
    color: '#0066CC',
  },
  priorityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priorityText: {
    marginLeft: 5,
    fontSize: 12,
    fontWeight: '600',
    color: '#FF4444',
  },
  newsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    lineHeight: 22,
  },
  newsDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  authorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  authorText: {
    marginLeft: 5,
    fontSize: 12,
    color: '#666',
  },
  dateText: {
    fontSize: 12,
    color: '#999',
  },
  targetInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  targetText: {
    fontSize: 10,
    color: '#999',
    marginLeft: 4,
  },
});
