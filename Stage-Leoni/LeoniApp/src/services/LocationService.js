// Service pour gérer les locations et départements
import NetworkService from './NetworkService';

class LocationService {
    /**
     * Récupérer toutes les locations (sites)
     */
    static async getLocations() {
        try {
            console.log('🔍 LocationService: Appel API GET locations...');
            
            const response = await NetworkService.fetch('/api/locations');
            console.log('🔍 LocationService: Status =', response.status);
            
            const data = await response.json();
            console.log('🔍 LocationService: Réponse =', data);
            
            if (data.success) {
                console.log('✅ LocationService: Succès, locations =', data.locations);
                return {
                    success: true,
                    locations: data.locations  // L'API retourne "locations", pas "data"
                };
            } else {
                console.log('❌ LocationService: Échec =', data.message);
                return {
                    success: false,
                    message: data.message || 'Erreur lors de la récupération des sites'
                };
            }
        } catch (error) {
            console.error('❌ LocationService: Erreur fetch:', error);
            return {
                success: false,
                message: 'Erreur de connexion'
            };
        }
    }

    /**
     * Récupérer les départements d'une location spécifique par nom
     */
    static async getDepartmentsByLocationName(locationName) {
        try {
            console.log('🔍 LocationService: Récupération départements pour location =', locationName);
            
            const response = await NetworkService.fetch('/api/departments');
            console.log('🔍 LocationService: Status =', response.status);
            
            const data = await response.json();
            console.log('🔍 LocationService: Réponse départements =', data);
            
            if (data.departments) {
                // Filtrer les départements par nom de location
                const filteredDepartments = data.departments.filter(dept => dept.location === locationName);
                console.log('✅ LocationService: Départements filtrés =', filteredDepartments);
                return {
                    success: true,
                    departments: filteredDepartments
                };
            } else {
                console.log('❌ LocationService: Aucun département trouvé');
                return {
                    success: false,
                    message: 'Aucun département trouvé'
                };
            }
        } catch (error) {
            console.error('❌ LocationService: Exception départements:', error);
            return {
                success: false,
                message: 'Erreur de connexion'
            };
        }
    }

    /**
     * Récupérer les départements d'une location spécifique
     */
    static async getDepartmentsByLocation(locationId) {
        try {
            console.log('🔍 LocationService: Récupération départements pour locationId =', locationId);
            
            const response = await NetworkService.fetch(`/api/locations/${locationId}/departments`);
            console.log('🔍 LocationService: Status =', response.status);
            
            const data = await response.json();
            console.log('🔍 LocationService: Réponse départements =', data);
            
            if (data.success) {
                console.log('✅ LocationService: Succès, départements =', data.departments);
                return {
                    success: true,
                    departments: data.departments  // L'API retourne "departments"
                };
            } else {
                console.log('❌ LocationService: Échec =', data.message);
                return {
                    success: false,
                    message: data.message || 'Erreur lors de la récupération des départements'
                };
            }
        } catch (error) {
            console.error('❌ LocationService: Exception départements:', error);
            return {
                success: false,
                message: 'Erreur de connexion'
            };
        }
    }

    /**
     * Récupérer tous les départements (pour usage général)
     */
    static async getAllDepartments() {
        try {
            const response = await NetworkService.fetch('/api/departments');
            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    departments: data.data
                };
            } else {
                return {
                    success: false,
                    message: data.message || 'Erreur lors de la récupération des départements'
                };
            }
        } catch (error) {
            console.error('Error fetching all departments:', error);
            return {
                success: false,
                message: 'Erreur de connexion'
            };
        }
    }

    /**
     * Récupérer une location spécifique par son ID
     */
    static async getLocationById(locationId) {
        try {
            console.log(`🔍 LocationService: Récupération location ${locationId}`);
            
            const response = await NetworkService.fetch(`/api/locations/${locationId}`);
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ LocationService: Location récupérée:', data.location);
                return {
                    success: true,
                    location: data.location
                };
            } else {
                console.log('❌ LocationService: Location non trouvée:', data.message);
                return {
                    success: false,
                    message: data.message || 'Location non trouvée'
                };
            }
        } catch (error) {
            console.error('❌ LocationService: Erreur fetch location:', error);
            return {
                success: false,
                message: 'Erreur de connexion'
            };
        }
    }
}

export default LocationService;
