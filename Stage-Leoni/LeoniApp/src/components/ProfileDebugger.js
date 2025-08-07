import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

const ProfileDebugger = ({ profile, formData, title = "Profile Debug" }) => {
  if (!profile && !formData) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.noData}>Aucune donnée de profil disponible</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      
      {profile && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Raw Profile Data:</Text>
          <Text style={styles.dataText}>{JSON.stringify(profile, null, 2)}</Text>
        </View>
      )}

      {formData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Form Data:</Text>
          <Text style={styles.dataText}>{JSON.stringify(formData, null, 2)}</Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Field Analysis:</Text>
        {[
          { key: 'firstName', label: 'Prénom' },
          { key: 'lastName', label: 'Nom' },
          { key: 'email', label: 'Adresse1' },
          { key: 'phoneNumber', label: 'Téléphone', altKey: 'phone' },
          { key: 'parentalEmail', label: 'Adresse2' },
          { key: 'parentalPhoneNumber', label: 'Téléphone parental' },
          { key: 'employeeId', label: 'ID employé' },
          { key: 'location', label: 'Localisation' },
          { key: 'department', label: 'Département' },
          { key: 'position', label: 'Poste' },
          { key: 'address', label: 'Adresse' }
        ].map((field) => {
          const profileValue = profile && (profile[field.key] || profile[field.altKey]);
          const formValue = formData && (formData[field.key] || formData[field.altKey]);
          
          return (
            <View key={field.key} style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>{field.label}:</Text>
              <Text style={styles.fieldValue}>
                Profile: {profileValue || 'null'} | Form: {formValue || 'null'}
              </Text>
            </View>
          );
        })}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    margin: 10,
    borderRadius: 5,
    maxHeight: 300,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  section: {
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#666',
  },
  dataText: {
    fontSize: 10,
    fontFamily: 'monospace',
    backgroundColor: '#fff',
    padding: 5,
    borderRadius: 3,
  },
  fieldRow: {
    flexDirection: 'row',
    marginBottom: 3,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    width: 120,
    color: '#333',
  },
  fieldValue: {
    fontSize: 12,
    flex: 1,
    color: '#666',
  },
  noData: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
  },
});

export default ProfileDebugger;
