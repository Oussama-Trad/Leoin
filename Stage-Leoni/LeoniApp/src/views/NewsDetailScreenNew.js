import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity,
  Dimensions 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function NewsDetailScreen({ route, navigation }) {
  const { newsItem } = route.params;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        
        <Text style={styles.headerTitle}>Actualité</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.articleContainer}>
          <View style={styles.articleHeader}>
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryText}>{newsItem.category || 'Info'}</Text>
            </View>
            <Text style={styles.dateText}>
              {new Date(newsItem.createdAt).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })}
            </Text>
          </View>

          <Text style={styles.title}>{newsItem.title}</Text>

          <View style={styles.contentWrapper}>
            <Text style={styles.articleContent}>{newsItem.content}</Text>
          </View>

          {newsItem.author && (
            <View style={styles.authorSection}>
              <View style={styles.authorIcon}>
                <Ionicons name="person" size={20} color="#4A90E2" />
              </View>
              <Text style={styles.authorText}>Par {newsItem.author}</Text>
            </View>
          )}
        </View>
      </ScrollView>
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
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#002857',
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
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  content: {
    flex: 1,
  },
  articleContainer: {
    backgroundColor: '#ffffff',
    margin: 20,
    borderRadius: 20,
    padding: 25,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  articleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  categoryBadge: {
    backgroundColor: '#6c5ce7',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    textTransform: 'uppercase',
  },
  dateText: {
    fontSize: 14,
    color: '#718096',
    fontWeight: '500',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 25,
    lineHeight: 36,
  },
  contentWrapper: {
    marginBottom: 25,
  },
  articleContent: {
    fontSize: 18,
    color: '#4A5568',
    lineHeight: 28,
    textAlign: 'justify',
  },
  authorSection: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  authorIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#002857',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  authorText: {
    fontSize: 16,
    color: '#4A5568',
    fontWeight: '500',
  },
});
