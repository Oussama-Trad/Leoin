import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, FlatList, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const CustomPicker = ({ 
    data = [], 
    selectedValue, 
    onValueChange, 
    placeholder = "Sélectionnez...", 
    renderItem,
    style,
    disabled = false 
}) => {
    const [modalVisible, setModalVisible] = useState(false);

    const getSelectedText = () => {
        if (!selectedValue) return placeholder;
        
        const selectedItem = data.find(item => item._id === selectedValue);
        return selectedItem ? selectedItem.name : placeholder;
    };

    const handleSelect = (item) => {
        onValueChange(item._id, item);
        setModalVisible(false);
    };

    const defaultRenderItem = ({ item }) => (
        <TouchableOpacity
            style={styles.modalItem}
            onPress={() => handleSelect(item)}
        >
            <Text style={styles.modalItemText}>{item.name}</Text>
            <Text style={styles.modalItemCode}>{item.code}</Text>
        </TouchableOpacity>
    );

    return (
        <View style={style}>
            <TouchableOpacity
                style={[styles.picker, disabled && styles.pickerDisabled]}
                onPress={() => !disabled && setModalVisible(true)}
            >
                <Text style={[styles.pickerText, !selectedValue && styles.placeholderText]}>
                    {getSelectedText()}
                </Text>
                <Ionicons 
                    name="chevron-down" 
                    size={20} 
                    color={disabled ? "#9ca3af" : "#667eea"} 
                />
            </TouchableOpacity>

            <Modal
                animationType="slide"
                transparent={true}
                visible={modalVisible}
                onRequestClose={() => setModalVisible(false)}
            >
                <View style={styles.modalContainer}>
                    <View style={styles.modalContent}>
                        <View style={styles.modalHeader}>
                            <Text style={styles.modalTitle}>
                                {placeholder}
                            </Text>
                            <TouchableOpacity
                                onPress={() => setModalVisible(false)}
                                style={styles.closeButton}
                            >
                                <Ionicons name="close" size={24} color="#002857" />
                            </TouchableOpacity>
                        </View>
                        
                        <FlatList
                            data={data}
                            keyExtractor={(item) => item._id}
                            renderItem={renderItem || defaultRenderItem}
                            style={styles.modalList}
                        />
                    </View>
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    picker: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#ffffff',
        borderRadius: 12,
        paddingHorizontal: 16,
        paddingVertical: 14,
        borderWidth: 1,
        borderColor: '#e5e7eb',
    },
    pickerDisabled: {
        backgroundColor: '#f3f4f6',
        borderColor: '#d1d5db',
    },
    pickerText: {
        fontSize: 16,
        color: '#1f2937',
        flex: 1,
    },
    placeholderText: {
        color: '#9ca3af',
    },
    modalContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    modalContent: {
        backgroundColor: 'white',
        borderRadius: 20,
        width: '90%',
        maxHeight: '70%',
        padding: 0,
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#e5e7eb',
    },
    modalTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#002857',
    },
    closeButton: {
        padding: 5,
    },
    modalList: {
        maxHeight: 400,
    },
    modalItem: {
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#f3f4f6',
    },
    modalItemText: {
        fontSize: 16,
        fontWeight: '500',
        color: '#1f2937',
        marginBottom: 4,
    },
    modalItemCode: {
        fontSize: 14,
        color: '#6b7280',
    },
});

export default CustomPicker;
