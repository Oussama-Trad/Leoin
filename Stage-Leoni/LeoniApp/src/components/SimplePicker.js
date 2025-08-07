import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SimplePicker = ({ 
  data = [], 
  selectedValue, 
  onValueChange, 
  placeholder = "Sélectionner...", 
  disabled = false,
  style 
}) => {
  const [modalVisible, setModalVisible] = React.useState(false);

  const selectedItem = data.find(item => item.value === selectedValue);
  const displayText = selectedItem ? selectedItem.label : placeholder;

  const handleSelect = (value) => {
    onValueChange(value);
    setModalVisible(false);
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.modalItem,
        selectedValue === item.value && styles.selectedItem
      ]}
      onPress={() => handleSelect(item.value)}
    >
      <Text style={[
        styles.modalItemText,
        selectedValue === item.value && styles.selectedItemText
      ]}>
        {item.label}
      </Text>
      {selectedValue === item.value && (
        <Ionicons name="checkmark" size={20} color="#667eea" />
      )}
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, style]}>
      <TouchableOpacity
        style={[styles.picker, disabled && styles.disabledPicker]}
        onPress={() => !disabled && setModalVisible(true)}
        disabled={disabled}
      >
        <Text style={[
          styles.pickerText,
          !selectedItem && styles.placeholderText,
          disabled && styles.disabledText
        ]}>
          {displayText}
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
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Sélectionner</Text>
              <TouchableOpacity
                onPress={() => setModalVisible(false)}
                style={styles.closeButton}
              >
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            <FlatList
              data={data}
              renderItem={renderItem}
              keyExtractor={(item) => item.value.toString()}
              style={styles.modalList}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  picker: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 50,
    paddingHorizontal: 12,
    paddingRight: 16,
    backgroundColor: 'transparent',
  },
  disabledPicker: {
    backgroundColor: '#f3f4f6',
    opacity: 0.6,
  },
  pickerText: {
    fontSize: 16,
    color: '#2d3748',
    flex: 1,
  },
  placeholderText: {
    color: '#9ca3af',
  },
  disabledText: {
    color: '#9ca3af',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d3748',
  },
  closeButton: {
    padding: 5,
  },
  modalList: {
    flex: 1,
  },
  modalItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  selectedItem: {
    backgroundColor: '#f0f4ff',
  },
  modalItemText: {
    fontSize: 16,
    color: '#2d3748',
    flex: 1,
  },
  selectedItemText: {
    color: '#667eea',
    fontWeight: '500',
  },
});

export default SimplePicker;
