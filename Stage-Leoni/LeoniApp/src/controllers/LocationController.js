import LocationService from '../services/LocationService';
import { LocationModel } from '../models/LocationModel';

/**
 * Contrôleur pour gérer les locations/sites
 */
export class LocationController {
  constructor() {
    // LocationService utilise des méthodes statiques, pas besoin d'instanciation
  }

  /**
   * Récupérer toutes les locations
   * @returns {Promise<LocationModel[]>}
   */
  async getAllLocations() {
    try {
      console.log('🏢 LocationController: Récupération de toutes les locations');
      
      const response = await LocationService.getLocations();
      
      if (response.success && response.locations) {
        const locations = LocationModel.fromAPIArray(response.locations);
        console.log(`✅ LocationController: ${locations.length} locations récupérées`);
        return locations;
      } else {
        console.warn('⚠️ LocationController: Réponse API invalide', response);
        return [];
      }
    } catch (error) {
      console.error('❌ LocationController: Erreur lors de la récupération des locations:', error);
      throw new Error(`Erreur lors du chargement des sites: ${error.message}`);
    }
  }

  /**
   * Récupérer une location par son ID
   * @param {string} locationId 
   * @returns {Promise<LocationModel|null>}
   */
  async getLocationById(locationId) {
    try {
      if (!locationId) {
        console.warn('⚠️ LocationController: ID de location manquant');
        return null;
      }

      console.log(`🏢 LocationController: Récupération de la location ${locationId}`);
      
      const response = await LocationService.getLocationById(locationId);
      
      if (response.success && response.location) {
        const location = LocationModel.fromAPI(response.location);
        console.log(`✅ LocationController: Location ${location.name} récupérée`);
        return location;
      } else {
        console.warn('⚠️ LocationController: Location non trouvée', locationId);
        return null;
      }
    } catch (error) {
      console.error('❌ LocationController: Erreur lors de la récupération de la location:', error);
      throw new Error(`Erreur lors du chargement du site: ${error.message}`);
    }
  }

  /**
   * Récupérer les locations actives seulement
   * @returns {Promise<LocationModel[]>}
   */
  async getActiveLocations() {
    try {
      const allLocations = await this.getAllLocations();
      const activeLocations = allLocations.filter(location => location.isActive());
      
      console.log(`✅ LocationController: ${activeLocations.length} locations actives sur ${allLocations.length}`);
      return activeLocations;
    } catch (error) {
      console.error('❌ LocationController: Erreur lors de la récupération des locations actives:', error);
      throw error;
    }
  }

  /**
   * Formater les locations pour un picker/dropdown
   * @returns {Promise<Array>}
   */
  async getLocationsForPicker() {
    try {
      const locations = await this.getActiveLocations();
      
      const pickerData = locations.map(location => ({
        _id: location.id,
        name: location.getDisplayName(),
        code: location.code,
        departmentCount: location.getDepartmentCount()
      }));

      console.log(`✅ LocationController: ${pickerData.length} locations formatées pour picker`);
      return pickerData;
    } catch (error) {
      console.error('❌ LocationController: Erreur lors du formatage pour picker:', error);
      return [];
    }
  }

  /**
   * Rechercher des locations par nom
   * @param {string} searchTerm 
   * @returns {Promise<LocationModel[]>}
   */
  async searchLocations(searchTerm) {
    try {
      if (!searchTerm || searchTerm.trim().length === 0) {
        return await this.getAllLocations();
      }

      const allLocations = await this.getAllLocations();
      const filteredLocations = allLocations.filter(location =>
        location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        location.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        location.city.toLowerCase().includes(searchTerm.toLowerCase())
      );

      console.log(`🔍 LocationController: ${filteredLocations.length} locations trouvées pour "${searchTerm}"`);
      return filteredLocations;
    } catch (error) {
      console.error('❌ LocationController: Erreur lors de la recherche:', error);
      return [];
    }
  }

  /**
   * Valider les données d'une location
   * @param {Object} locationData 
   * @returns {Object} {isValid, errors}
   */
  validateLocationData(locationData) {
    const errors = [];

    if (!locationData.name || locationData.name.trim().length === 0) {
      errors.push('Le nom du site est obligatoire');
    }

    if (!locationData.code || locationData.code.trim().length === 0) {
      errors.push('Le code du site est obligatoire');
    }

    if (!locationData.city || locationData.city.trim().length === 0) {
      errors.push('La ville est obligatoire');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Nettoyer le cache des locations
   */
  clearCache() {
    console.log('🧹 LocationController: Cache des locations nettoyé');
    // Ici on pourrait implémenter un système de cache si nécessaire
  }
}

export default LocationController;
