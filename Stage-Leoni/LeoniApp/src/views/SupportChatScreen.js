/**
 * SupportChatScreen - Écran de chat pour le support technique
 * Permet aux employés de contacter leur département IT ou autres départements
 */
import React, { useState, useEffect, useContext } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    TextInput,
    Alert,
    RefreshControl,
    Modal,
    ActivityIndicator
} from 'react-native';
import { AuthContext } from '../contexts/AuthContext';
import ChatService from '../services/ChatService';
import { TopBar } from '../components';

const SupportChatScreen = ({ navigation }) => {
    const { user } = useContext(AuthContext);
    const [conversations, setConversations] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newConversation, setNewConversation] = useState({
        title: '',
        description: '',
        targetDepartment: '',
        priority: 'normal'
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            await Promise.all([
                loadConversations(),
                loadDepartments()
            ]);
        } catch (error) {
            console.error('Erreur chargement données:', error);
            Alert.alert('Erreur', 'Impossible de charger les données');
        } finally {
            setLoading(false);
        }
    };

    const loadConversations = async () => {
        try {
            const result = await ChatService.getConversations();
            if (result.success) {
                const formattedConversations = result.conversations.map(conv => 
                    ChatService.formatConversation(conv)
                );
                setConversations(formattedConversations);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erreur chargement conversations:', error);
            Alert.alert('Erreur', 'Impossible de charger les conversations');
        }
    };

    const loadDepartments = async () => {
        try {
            const result = await ChatService.getAvailableDepartments();
            if (result.success) {
                setDepartments(result.departments);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erreur chargement départements:', error);
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadConversations();
        setRefreshing(false);
    };

    const handleCreateConversation = async () => {
        if (!newConversation.title.trim() || !newConversation.description.trim() || !newConversation.targetDepartment) {
            Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
            return;
        }

        try {
            const result = await ChatService.createConversation(newConversation);
            if (result.success) {
                Alert.alert('Succès', 'Conversation créée avec succès');
                setShowCreateModal(false);
                setNewConversation({
                    title: '',
                    description: '',
                    targetDepartment: '',
                    priority: 'normal'
                });
                await loadConversations();
                
                // Naviguer vers la conversation créée
                navigation.navigate('ChatDetail', { conversationId: result.conversationId });
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erreur création conversation:', error);
            Alert.alert('Erreur', error.message);
        }
    };

    const navigateToConversation = (conversation) => {
        navigation.navigate('ChatDetail', { 
            conversationId: conversation._id,
            conversationData: conversation
        });
    };

    const renderConversationItem = ({ item }) => (
        <TouchableOpacity 
            style={styles.conversationItem}
            onPress={() => navigateToConversation(item)}
        ><View style={styles.conversationHeader}><View style={styles.conversationInfo}><Text style={styles.conversationTitle} numberOfLines={1}>
                        {item.title}
                    </Text><View style={styles.conversationMeta}><Text style={styles.departmentText}>
                            {item.targetDepartment} • {item.targetLocation}
                        </Text><View style={[
                            styles.statusBadge, 
                            { backgroundColor: ChatService.getStatusColor(item.status) }
                        ]}><Text style={styles.statusText}>
                                {ChatService.getStatusText(item.status)}
                            </Text></View></View></View><View style={styles.conversationRight}><Text style={styles.timeText}>
                        {item.lastMessage?.timeAgo || item.createdTimeAgo}
                    </Text>
                    {item.priority !== 'normal' && (
                        <View style={[
                            styles.priorityBadge,
                            { backgroundColor: ChatService.getPriorityColor(item.priority) }
                        ]}><Text style={styles.priorityText}>
                                {ChatService.getPriorityText(item.priority)}
                            </Text></View>
                    )}</View></View>
            {item.lastMessage && (
                <View style={styles.lastMessage}><Text style={styles.lastMessageAuthor}>
                        {item.lastMessage.senderName}:
                    </Text><Text style={styles.lastMessageContent} numberOfLines={2}>
                        {item.lastMessage.content}
                    </Text></View>
            )}
            <Text style={styles.conversationDescription} numberOfLines={2}>
                {item.description}
            </Text></TouchableOpacity>
    );

    const renderDepartmentPicker = () => (
        <View style={styles.pickerContainer}><Text style={styles.label}>Département de destination *</Text><FlatList
                data={departments}
                keyExtractor={(item) => item._id}
                renderItem={({ item }) => (
                    <TouchableOpacity
                        style={[
                            styles.departmentOption,
                            newConversation.targetDepartment === item.name && styles.selectedDepartment
                        ]}
                        onPress={() => setNewConversation({
                            ...newConversation,
                            targetDepartment: item.name
                        })}
                    ><Text style={[
                            styles.departmentOptionText,
                            newConversation.targetDepartment === item.name && styles.selectedDepartmentText
                        ]}>
                            {item.name}
                        </Text>
                        {item.description && (
                            <Text style={styles.departmentDescription}>
                                {item.description}
                            </Text>
                        )}</TouchableOpacity>
                )}
                horizontal={false}
                showsVerticalScrollIndicator={false}
            /></View>
    );

    const renderPriorityPicker = () => {
        const priorities = [
            { value: 'low', label: 'Faible', color: '#28a745' },
            { value: 'normal', label: 'Normale', color: '#007bff' },
            { value: 'high', label: 'Élevée', color: '#ffc107' },
            { value: 'urgent', label: 'Urgente', color: '#dc3545' }
        ];

        return (
            <View style={styles.pickerContainer}><Text style={styles.label}>Priorité</Text><View style={styles.priorityContainer}>{priorities.map((priority) => (
                        <TouchableOpacity
                            key={priority.value}
                            style={[
                                styles.priorityOption,
                                { borderColor: priority.color },
                                newConversation.priority === priority.value && {
                                    backgroundColor: priority.color
                                }
                            ]}
                            onPress={() => setNewConversation({
                                ...newConversation,
                                priority: priority.value
                            })}
                        ><Text style={[
                                styles.priorityOptionText,
                                newConversation.priority === priority.value && styles.selectedPriorityText
                            ]}>
                                {priority.label}
                            </Text></TouchableOpacity>
                    ))}</View></View>
        );
    };

    if (loading) {
        return (
            <View style={styles.container}><TopBar title="Support Chat" /><View style={styles.loadingContainer}><ActivityIndicator size="large" color="#002857" /><Text style={styles.loadingText}>Chargement...</Text></View></View>
        );
    }

    return (
        <View style={styles.container}><TopBar title="Support Chat" /><View style={styles.header}><View style={styles.userInfo}><Text style={styles.welcomeText}>
                        Bonjour {user?.firstName} 👋
                    </Text><Text style={styles.locationText}>
                        {user?.department} • {user?.location}
                    </Text></View><TouchableOpacity 
                    style={styles.createButton}
                    onPress={() => setShowCreateModal(true)}
                ><Text style={styles.createButtonText}>+ Nouveau</Text></TouchableOpacity></View><FlatList
                data={conversations}
                keyExtractor={(item) => item._id}
                renderItem={renderConversationItem}
                style={styles.conversationsList}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        colors={['#002857']}
                    />
                }
                ListEmptyComponent={
                    <View style={styles.emptyContainer}><Text style={styles.emptyText}>
                            Aucune conversation pour le moment
                        </Text><Text style={styles.emptySubtext}>
                            Créez une nouvelle conversation pour contacter un département
                        </Text></View>
                }
            />

            {/* Modal de création de conversation */}
            <Modal
                visible={showCreateModal}
                animationType="slide"
                transparent={true}
                onRequestClose={() => setShowCreateModal(false)}
            ><View style={styles.modalOverlay}><View style={styles.modalContent}><View style={styles.modalHeader}><Text style={styles.modalTitle}>Nouvelle Conversation</Text><TouchableOpacity
                                onPress={() => setShowCreateModal(false)}
                                style={styles.closeButton}
                            ><Text style={styles.closeButtonText}>✕</Text></TouchableOpacity></View><TextInput
                            style={styles.input}
                            placeholder="Titre de la demande *"
                            value={newConversation.title}
                            onChangeText={(text) => setNewConversation({
                                ...newConversation,
                                title: text
                            })}
                        /><TextInput
                            style={[styles.input, styles.textArea]}
                            placeholder="Description détaillée du problème *"
                            value={newConversation.description}
                            onChangeText={(text) => setNewConversation({
                                ...newConversation,
                                description: text
                            })}
                            multiline
                            numberOfLines={4}
                        />

                        {renderDepartmentPicker()}
                        {renderPriorityPicker()}

                        <View style={styles.modalButtons}><TouchableOpacity
                                style={styles.cancelButton}
                                onPress={() => setShowCreateModal(false)}
                            ><Text style={styles.cancelButtonText}>Annuler</Text></TouchableOpacity><TouchableOpacity
                                style={styles.submitButton}
                                onPress={handleCreateConversation}
                            ><Text style={styles.submitButtonText}>Créer</Text></TouchableOpacity></View></View></View></Modal></View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5'
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center'
    },
    loadingText: {
        marginTop: 10,
        fontSize: 16,
        color: '#666'
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 15,
        backgroundColor: 'white',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0'
    },
    userInfo: {
        flex: 1
    },
    welcomeText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#002857'
    },
    locationText: {
        fontSize: 14,
        color: '#666',
        marginTop: 2
    },
    createButton: {
        backgroundColor: '#002857',
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 20
    },
    createButtonText: {
        color: 'white',
        fontWeight: 'bold',
        fontSize: 14
    },
    conversationsList: {
        flex: 1
    },
    conversationItem: {
        backgroundColor: 'white',
        margin: 8,
        padding: 15,
        borderRadius: 12,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4
    },
    conversationHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 8
    },
    conversationInfo: {
        flex: 1,
        marginRight: 10
    },
    conversationTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#002857',
        marginBottom: 4
    },
    conversationMeta: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8
    },
    departmentText: {
        fontSize: 12,
        color: '#666'
    },
    statusBadge: {
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 10
    },
    statusText: {
        color: 'white',
        fontSize: 10,
        fontWeight: 'bold'
    },
    conversationRight: {
        alignItems: 'flex-end',
        gap: 4
    },
    timeText: {
        fontSize: 12,
        color: '#999'
    },
    priorityBadge: {
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 8
    },
    priorityText: {
        color: 'white',
        fontSize: 10,
        fontWeight: 'bold'
    },
    lastMessage: {
        flexDirection: 'row',
        marginBottom: 8
    },
    lastMessageAuthor: {
        fontSize: 12,
        fontWeight: 'bold',
        color: '#002857',
        marginRight: 4
    },
    lastMessageContent: {
        fontSize: 12,
        color: '#666',
        flex: 1
    },
    conversationDescription: {
        fontSize: 14,
        color: '#444',
        lineHeight: 20
    },
    emptyContainer: {
        padding: 40,
        alignItems: 'center'
    },
    emptyText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#666',
        textAlign: 'center',
        marginBottom: 8
    },
    emptySubtext: {
        fontSize: 14,
        color: '#999',
        textAlign: 'center'
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        justifyContent: 'center',
        alignItems: 'center'
    },
    modalContent: {
        backgroundColor: 'white',
        margin: 20,
        borderRadius: 12,
        padding: 20,
        maxHeight: '80%',
        width: '90%'
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#002857'
    },
    closeButton: {
        padding: 5
    },
    closeButtonText: {
        fontSize: 20,
        color: '#666'
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: 12,
        marginBottom: 15,
        fontSize: 16
    },
    textArea: {
        height: 80,
        textAlignVertical: 'top'
    },
    label: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#002857',
        marginBottom: 10
    },
    pickerContainer: {
        marginBottom: 15
    },
    departmentOption: {
        padding: 12,
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        marginBottom: 8
    },
    selectedDepartment: {
        borderColor: '#002857',
        backgroundColor: '#002857'
    },
    departmentOptionText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#002857'
    },
    selectedDepartmentText: {
        color: 'white'
    },
    departmentDescription: {
        fontSize: 12,
        color: '#666',
        marginTop: 4
    },
    priorityContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8
    },
    priorityOption: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderWidth: 2,
        borderRadius: 16
    },
    priorityOptionText: {
        fontSize: 14,
        fontWeight: 'bold'
    },
    selectedPriorityText: {
        color: 'white'
    },
    modalButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 20,
        gap: 10
    },
    cancelButton: {
        flex: 1,
        padding: 12,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#ddd',
        alignItems: 'center'
    },
    cancelButtonText: {
        fontSize: 16,
        color: '#666'
    },
    submitButton: {
        flex: 1,
        padding: 12,
        borderRadius: 8,
        backgroundColor: '#002857',
        alignItems: 'center'
    },
    submitButtonText: {
        fontSize: 16,
        color: 'white',
        fontWeight: 'bold'
    }
});

export default SupportChatScreen;
