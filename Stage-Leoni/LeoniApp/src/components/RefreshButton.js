import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const RefreshButton = ({ 
  onPress, 
  refreshing = false, 
  style = {}, 
  color = '#667eea',
  backgroundColor = 'rgba(102, 126, 234, 0.1)',
  text = 'Actualiser',
  showText = true,
  size = 20
}) => {
  return (
    <TouchableOpacity 
      style={[styles.refreshButton, { backgroundColor }, style]} 
      onPress={onPress}
      disabled={refreshing}
      activeOpacity={0.7}
    >
      <Ionicons 
        name={refreshing ? "refresh" : "refresh-outline"} 
        size={size} 
        color={color} 
      />
      {showText && (
        <Text style={[styles.refreshButtonText, { color }]}>
          {refreshing ? 'Actualisation...' : text}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  refreshButtonText: {
    marginLeft: 5,
    fontSize: 12,
    fontWeight: '600',
  },
});

export default RefreshButton;
