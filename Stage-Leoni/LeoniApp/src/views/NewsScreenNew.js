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

export default function NewsScreen({ navigation }) {
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

  const handleNewsPress = (newsItem) => {
    navigation.navigate('NewsDetail', { newsItem });
  };

  const renderNewsCard = ({ item, index }) => (
    <TouchableOpacity
      style={[styles.newsCard, { marginTop: index === 0 ? 0 : 20 }]}
      onPress={() => handleNewsPress(item)}
      activeOpacity={0.8}
    >
      <View style={styles.cardContent}>
        <View style={styles.cardHeader}>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{item.category || 'Info'}</Text>
          </View>
          <Text style={styles.dateText}>
            {new Date(item.createdAt).toLocaleDateString('fr-FR', {
              day: 'numeric',
              month: 'short'
            })}
          </Text>
        </View>

        <Text style={styles.newsTitle} numberOfLines={2}>
          {item.title}
        </Text>

        <Text style={styles.newsPreview} numberOfLines={3}>
          {item.content}
        </Text>

        <View style={styles.readMoreSection}>
          <Text style={styles.readMoreText}>Voir plus</Text>
          <Ionicons name="arrow-forward" size={18} color="#002857" />
        </View>
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
      {/* Bouton de debug temporaire */}
      <View style={styles.debugContainer}>
        <TouchableOpacity 
          style={styles.debugButton}
          onPress={async () => {
            try {
              const AsyncStorage = await import('@react-native-async-storage/async-storage');
              const token = await AsyncStorage.default.getItem('userToken');
              const userInfo = await AsyncStorage.default.getItem('userInfo');
              
              Alert.alert(
                'Debug Info',
                `Token: ${token ? 'Présent (' + token.substring(0, 20) + '...)' : 'Absent'}\n` +
                `UserInfo: ${userInfo ? 'Présent' : 'Absent'}`,
                [
                  { text: 'Test API', onPress: async () => {
                    try {
                      const response = await NewsService.getUserNews();
                      Alert.alert('Résultat API', JSON.stringify(response, null, 2));
                    } catch (error) {
                      Alert.alert('Erreur API', error.message);
                    }
                  }},
                  { text: 'OK' }
                ]
              );
            } catch (error) {
              Alert.alert('Erreur', error.message);
            }
          }}
        >
          <Ionicons name="bug" size={16} color="white" />
          <Text style={styles.debugButtonText}>Debug</Text>
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
    backgroundColor: '#f0f4f8',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 25,
    paddingBottom: 30,
  },
  newsCard: {
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    backgroundColor: '#ffffff',
  },
  cardContent: {
    padding: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  categoryBadge: {
    backgroundColor: '#6c5ce7',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
    textTransform: 'uppercase',
  },
  dateText: {
    fontSize: 12,
    color: '#718096',
    fontWeight: '500',
  },
  newsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 12,
    lineHeight: 26,
  },
  newsPreview: {
    fontSize: 16,
    color: '#4A5568',
    lineHeight: 24,
    marginBottom: 20,
  },
  readMoreSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  readMoreText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#002857',
    marginRight: 8,
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
  debugContainer: {
    padding: 10,
    backgroundColor: '#FFF3E0',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  debugButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF4444',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  debugButtonText: {
    color: 'white',
    fontWeight: 'bold',
    marginLeft: 8,
    fontSize: 12,
  },
});
