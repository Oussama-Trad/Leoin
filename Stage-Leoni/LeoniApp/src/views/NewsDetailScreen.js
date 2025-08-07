import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Share,
  Dimensions,
  SafeAreaView,
  ActivityIndicator,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  FlatList
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import NewsService from '../services/NewsService';

const { width, height } = Dimensions.get('window');

const NewsDetailScreen = ({ route, navigation }) => {
  const { newsId, newsItem: initialNewsItem } = route.params;
  
  const [newsItem, setNewsItem] = useState(initialNewsItem || null);
  const [loading, setLoading] = useState(!initialNewsItem);
  const [liked, setLiked] = useState(initialNewsItem?.liked || false);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [showComments, setShowComments] = useState(false);

  useEffect(() => {
    if (!initialNewsItem) {
      loadNewsDetail();
    }
    loadComments();
  }, []);

  const loadNewsDetail = async () => {
    try {
      setLoading(true);
      // Pour l'instant, on utilise les données passées en paramètre
      // TODO: Ajouter endpoint getNewsById si nécessaire
      if (newsId && !initialNewsItem) {
        Alert.alert('Erreur', 'Données d\'actualité manquantes');
        navigation.goBack();
      }
    } catch (error) {
      console.error('Erreur chargement actualité:', error);
      Alert.alert('Erreur', 'Impossible de charger cette actualité');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      // TODO: Implémenter loadComments avec le nouveau service
      // Pour l'instant, on laisse vide
      setComments([]);
    } catch (error) {
      console.error('Erreur chargement commentaires:', error);
    }
  };

  const toggleLike = async () => {
    try {
      // Pour l'instant, juste mise à jour locale
      // TODO: Ajouter endpoint toggleLike si nécessaire
      setLiked(!liked);
      setNewsItem(prev => ({
        ...prev,
        stats: {
          ...prev.stats,
          likes: liked ? (prev.stats?.likes || 0) - 1 : (prev.stats?.likes || 0) + 1
        }
      }));
    } catch (error) {
      console.error('Erreur like:', error);
      Alert.alert('Erreur', 'Impossible de liker cette actualité');
    }
  };
  };

  const submitComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      // TODO: Implémenter submitComment avec le nouveau service
      // Pour l'instant, commentaire local uniquement
      Alert.alert('Info', 'Fonctionnalité de commentaire en développement');
    } catch (error) {
      console.error('Erreur ajout commentaire:', error);
      Alert.alert('Erreur', 'Problème de connexion');
    } finally {
      setSubmittingComment(false);
    }
  };

  const shareNews = async () => {
    try {
      const result = await Share.share({
        message: `${newsItem.title}\n\n${newsItem.summary || newsItem.content.substring(0, 200)}...\n\n📱 Partagé depuis LEO-IN`,
        title: newsItem.title,
      });
    } catch (error) {
      console.error('Erreur partage:', error);
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
      case 'hr': return 'people';
      case 'it': return 'laptop';
      case 'safety': return 'shield';
      case 'events': return 'calendar';
      case 'general': return 'newspaper';
      default: return 'newspaper';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatContent = (content) => {
    // Simple formatage du contenu markdown-like
    return content
      .split('\n')
      .map((line, index) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return (
            <Text key={index} style={styles.boldText}>
              {line.slice(2, -2)}
            </Text>
          );
        } else if (line.startsWith('• ')) {
          return (
            <View key={index} style={styles.bulletPoint}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.bulletText}>{line.slice(2)}</Text>
            </View>
          );
        } else if (line.trim() === '') {
          return <View key={index} style={styles.spacer} />;
        } else {
          return (
            <Text key={index} style={styles.contentText}>
              {line}
            </Text>
          );
        }
      });
  };

  const renderComment = ({ item }) => (
    <View style={styles.commentItem}>
      <View style={styles.commentHeader}>
        <Ionicons name="person-circle" size={32} color="#0066CC" />
        <View style={styles.commentInfo}>
          <Text style={styles.commentAuthor}>{item.authorName}</Text>
          <Text style={styles.commentDate}>{formatDate(item.createdAt)}</Text>
        </View>
      </View>
      <Text style={styles.commentText}>{item.text}</Text>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0066CC" />
          <Text style={styles.loadingText}>Chargement de l'actualité...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!newsItem) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={80} color="#FF4444" />
          <Text style={styles.errorTitle}>Actualité introuvable</Text>
          <Text style={styles.errorText}>
            Cette actualité n'existe plus ou n'est plus disponible.
          </Text>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Text style={styles.backButtonText}>Retour</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const priorityColor = getPriorityColor(newsItem.priority);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* En-tête avec navigation */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#0066CC" />
          </TouchableOpacity>
          
          <View style={styles.headerActions}>
            <TouchableOpacity onPress={shareNews} style={styles.headerButton}>
              <Ionicons name="share-outline" size={24} color="#0066CC" />
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView 
          style={styles.scrollContainer}
          showsVerticalScrollIndicator={false}
        >
          {/* Métadonnées */}
          <View style={styles.metaContainer}>
            <View style={styles.categoryContainer}>
              <Ionicons 
                name={getCategoryIcon(newsItem.category)} 
                size={16} 
                color={priorityColor} 
              />
              <Text style={[styles.categoryText, { color: priorityColor }]}>
                {newsItem.category.toUpperCase()}
              </Text>
            </View>
            
            <View style={styles.priorityContainer}>
              <Ionicons 
                name={getPriorityIcon(newsItem.priority)} 
                size={16} 
                color={priorityColor} 
              />
              <Text style={[styles.priorityText, { color: priorityColor }]}>
                {newsItem.priority.toUpperCase()}
              </Text>
            </View>
          </View>

          {/* Titre */}
          <Text style={styles.title}>{newsItem.title}</Text>

          {/* Informations auteur et date */}
          <View style={styles.authorContainer}>
            <Ionicons name="person-circle" size={20} color="#666" />
            <Text style={styles.authorText}>Par {newsItem.authorName}</Text>
            <Text style={styles.dateText}>• {formatDate(newsItem.publishedAt)}</Text>
          </View>

          {/* Contenu */}
          <View style={styles.content}>
            {formatContent(newsItem.content)}
          </View>

          {/* Indicateur d'expiration */}
          {newsItem.expiryAt && new Date(newsItem.expiryAt) > new Date() && (
            <View style={styles.expiryWarning}>
              <Ionicons name="time" size={16} color="#FF8800" />
              <Text style={styles.expiryText}>
                Cette actualité expire le {new Date(newsItem.expiryAt).toLocaleDateString('fr-FR')}
              </Text>
            </View>
          )}

          {/* Actions et statistiques */}
          <View style={styles.actionsContainer}>
            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Ionicons name="eye" size={16} color="#888" />
                <Text style={styles.statText}>{newsItem.stats.views} vues</Text>
              </View>
              
              <View style={styles.statItem}>
                <Ionicons name="chatbubble" size={16} color="#888" />
                <Text style={styles.statText}>{newsItem.stats.comments} commentaires</Text>
              </View>
            </View>

            <TouchableOpacity 
              style={[styles.likeButton, liked && styles.likeButtonActive]}
              onPress={toggleLike}
            >
              <Ionicons 
                name={liked ? "heart" : "heart-outline"} 
                size={20} 
                color={liked ? "#FFFFFF" : "#0066CC"} 
              />
              <Text style={[styles.likeButtonText, liked && styles.likeButtonTextActive]}>
                {newsItem.stats.likes} J'aime
              </Text>
            </TouchableOpacity>
          </View>

          {/* Section commentaires */}
          <View style={styles.commentsSection}>
            <TouchableOpacity
              style={styles.commentsToggle}
              onPress={() => setShowComments(!showComments)}
            >
              <Text style={styles.commentsToggleText}>
                💬 Commentaires ({comments.length})
              </Text>
              <Ionicons 
                name={showComments ? "chevron-up" : "chevron-down"} 
                size={20} 
                color="#0066CC" 
              />
            </TouchableOpacity>

            {showComments && (
              <>
                {/* Zone de saisie commentaire */}
                <View style={styles.commentInputContainer}>
                  <TextInput
                    style={styles.commentInput}
                    placeholder="Ajouter un commentaire..."
                    value={newComment}
                    onChangeText={setNewComment}
                    multiline
                    maxLength={500}
                  />
                  <TouchableOpacity
                    style={[
                      styles.submitCommentButton,
                      !newComment.trim() && styles.submitCommentButtonDisabled
                    ]}
                    onPress={submitComment}
                    disabled={!newComment.trim() || submittingComment}
                  >
                    {submittingComment ? (
                      <ActivityIndicator size="small" color="#FFFFFF" />
                    ) : (
                      <Ionicons name="send" size={16} color="#FFFFFF" />
                    )}
                  </TouchableOpacity>
                </View>

                {/* Liste des commentaires */}
                <FlatList
                  data={comments}
                  renderItem={renderComment}
                  keyExtractor={(item) => item._id}
                  scrollEnabled={false}
                  ListEmptyComponent={
                    <View style={styles.noCommentsContainer}>
                      <Text style={styles.noCommentsText}>
                        Aucun commentaire pour le moment. Soyez le premier à commenter !
                      </Text>
                    </View>
                  }
                />
              </>
            )}
          </View>
        </ScrollView>
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
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    marginLeft: 15,
  },
  scrollContainer: {
    flex: 1,
  },
  metaContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
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
  priorityText: {
    marginLeft: 5,
    fontSize: 12,
    fontWeight: '600',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333333',
    paddingHorizontal: 20,
    marginBottom: 15,
    lineHeight: 32,
  },
  authorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  authorText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666666',
  },
  dateText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#888888',
  },
  content: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  contentText: {
    fontSize: 16,
    color: '#333333',
    lineHeight: 24,
    marginBottom: 8,
  },
  boldText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
    lineHeight: 24,
    marginBottom: 8,
  },
  bulletPoint: {
    flexDirection: 'row',
    marginBottom: 5,
    paddingLeft: 10,
  },
  bullet: {
    fontSize: 16,
    color: '#0066CC',
    marginRight: 10,
    marginTop: 2,
  },
  bulletText: {
    flex: 1,
    fontSize: 16,
    color: '#333333',
    lineHeight: 24,
  },
  spacer: {
    height: 10,
  },
  expiryWarning: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    paddingHorizontal: 20,
    paddingVertical: 12,
    marginHorizontal: 20,
    borderRadius: 8,
    marginBottom: 20,
  },
  expiryText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#FF8800',
    fontWeight: '500',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  statsContainer: {
    flexDirection: 'row',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
  },
  statText: {
    marginLeft: 5,
    fontSize: 14,
    color: '#888888',
  },
  likeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#0066CC',
    backgroundColor: '#FFFFFF',
  },
  likeButtonActive: {
    backgroundColor: '#0066CC',
  },
  likeButtonText: {
    marginLeft: 5,
    color: '#0066CC',
    fontWeight: '500',
  },
  likeButtonTextActive: {
    color: '#FFFFFF',
  },
  commentsSection: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  commentsToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  commentsToggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
  },
  commentInputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  commentInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    maxHeight: 80,
    fontSize: 14,
  },
  submitCommentButton: {
    backgroundColor: '#0066CC',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    marginLeft: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitCommentButtonDisabled: {
    backgroundColor: '#CCCCCC',
  },
  commentItem: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  commentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  commentInfo: {
    marginLeft: 10,
  },
  commentAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
  },
  commentDate: {
    fontSize: 12,
    color: '#888888',
  },
  commentText: {
    fontSize: 14,
    color: '#333333',
    lineHeight: 20,
    paddingLeft: 42,
  },
  noCommentsContainer: {
    paddingHorizontal: 20,
    paddingVertical: 30,
    alignItems: 'center',
  },
  noCommentsText: {
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF4444',
    marginTop: 20,
    marginBottom: 10,
  },
  errorText: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 30,
  },
  backButton: {
    backgroundColor: '#0066CC',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 16,
  },
});

export default NewsDetailScreen;
