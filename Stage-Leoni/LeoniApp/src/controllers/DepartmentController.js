import LocationService from '../services/LocationService';
import { DepartmentModel } from '../models/DepartmentModel';

/**
 * Contrôleur pour gérer les départements
 */
export class DepartmentController {
  constructor() {
    // LocationService utilise des méthodes statiques, pas besoin d'instanciation
  }

  /**
   * Récupérer tous les départements
   * @returns {Promise<DepartmentModel[]>}
   */
  async getAllDepartments() {
    try {
      console.log('🏢 DepartmentController: Récupération de tous les départements');
      
      const response = await LocationService.getAllDepartments();
      
      if (response.success && response.departments) {
        const departments = DepartmentModel.fromAPIArray(response.departments);
        console.log(`✅ DepartmentController: ${departments.length} départements récupérés`);
        return departments;
      } else {
        console.warn('⚠️ DepartmentController: Réponse API invalide', response);
        return [];
      }
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors de la récupération des départements:', error);
      throw new Error(`Erreur lors du chargement des départements: ${error.message}`);
    }
  }

  /**
   * Récupérer les départements d'une location spécifique
   * @param {string} locationId 
   * @returns {Promise<DepartmentModel[]>}
   */
  async getDepartmentsByLocation(locationId) {
    try {
      if (!locationId) {
        console.warn('⚠️ DepartmentController: ID de location manquant');
        return [];
      }

      console.log(`🏢 DepartmentController: Récupération des départements pour la location ${locationId}`);
      
      const response = await LocationService.getDepartmentsByLocation(locationId);
      
      if (response.success && response.departments) {
        console.log(`🔍 DepartmentController: Données brutes reçues:`, response.departments);
        const departments = DepartmentModel.fromAPIArray(response.departments);
        console.log(`✅ DepartmentController: ${departments.length} départements récupérés pour la location`);
        console.log(`🔍 DepartmentController: Premier département transformé:`, departments[0]);
        return departments;
      } else {
        console.warn('⚠️ DepartmentController: Aucun département trouvé pour cette location', locationId);
        return [];
      }
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors de la récupération des départements:', error);
      throw new Error(`Erreur lors du chargement des départements: ${error.message}`);
    }
  }

  /**
   * Récupérer un département par son ID
   * @param {string} departmentId 
   * @returns {Promise<DepartmentModel|null>}
   */
  async getDepartmentById(departmentId) {
    try {
      if (!departmentId) {
        console.warn('⚠️ DepartmentController: ID de département manquant');
        return null;
      }

      console.log(`🏢 DepartmentController: Récupération du département ${departmentId}`);
      
      // Pour l'instant, on récupère tous les départements et on filtre
      // On pourrait améliorer cela avec un endpoint spécifique
      const allDepartments = await this.getAllDepartments();
      const department = allDepartments.find(dept => dept.id === departmentId);
      
      if (department) {
        console.log(`✅ DepartmentController: Département ${department.name} récupéré`);
        return department;
      } else {
        console.warn('⚠️ DepartmentController: Département non trouvé', departmentId);
        return null;
      }
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors de la récupération du département:', error);
      throw new Error(`Erreur lors du chargement du département: ${error.message}`);
    }
  }

  /**
   * Récupérer les départements actifs seulement
   * @param {string|null} locationId - Optionnel: filtrer par location
   * @returns {Promise<DepartmentModel[]>}
   */
  async getActiveDepartments(locationId = null) {
    try {
      let departments;
      
      if (locationId) {
        departments = await this.getDepartmentsByLocation(locationId);
      } else {
        departments = await this.getAllDepartments();
      }
      
      const activeDepartments = DepartmentModel.filterActive(departments);
      
      console.log(`✅ DepartmentController: ${activeDepartments.length} départements actifs sur ${departments.length}`);
      return activeDepartments;
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors de la récupération des départements actifs:', error);
      throw error;
    }
  }

  /**
   * Formater les départements pour un picker/dropdown
   * @param {string|null} locationId - Optionnel: filtrer par location
   * @returns {Promise<Array>}
   */
  async getDepartmentsForPicker(locationId = null) {
    try {
      const departments = await this.getActiveDepartments(locationId);
      const sortedDepartments = DepartmentModel.sortByName(departments);
      
      const pickerData = sortedDepartments.map(department => ({
        _id: department.id,
        name: department.getDisplayName(),
        code: department.code,
        locationId: department.locationRef || department.locationId,
        locationName: department.getLocationName()
      }));

      console.log(`✅ DepartmentController: ${pickerData.length} départements formatés pour picker`);
      return pickerData;
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors du formatage pour picker:', error);
      return [];
    }
  }

  /**
   * Rechercher des départements par nom
   * @param {string} searchTerm 
   * @param {string|null} locationId - Optionnel: filtrer par location
   * @returns {Promise<DepartmentModel[]>}
   */
  async searchDepartments(searchTerm, locationId = null) {
    try {
      if (!searchTerm || searchTerm.trim().length === 0) {
        return locationId ? 
          await this.getDepartmentsByLocation(locationId) : 
          await this.getAllDepartments();
      }

      const departments = locationId ? 
        await this.getDepartmentsByLocation(locationId) : 
        await this.getAllDepartments();
        
      const filteredDepartments = departments.filter(department =>
        department.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        department.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (department.description && department.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );

      console.log(`🔍 DepartmentController: ${filteredDepartments.length} départements trouvés pour "${searchTerm}"`);
      return filteredDepartments;
    } catch (error) {
      console.error('❌ DepartmentController: Erreur lors de la recherche:', error);
      return [];
    }
  }

  /**
   * Valider les données d'un département
   * @param {Object} departmentData 
   * @returns {Object} {isValid, errors}
   */
  validateDepartmentData(departmentData) {
    const errors = [];

    if (!departmentData.name || departmentData.name.trim().length === 0) {
      errors.push('Le nom du département est obligatoire');
    }

    if (!departmentData.locationRef && !departmentData.locationId) {
      errors.push('Le site du département est obligatoire');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Grouper les départements par location
   * @param {DepartmentModel[]} departments 
   * @returns {Object} Départements groupés par location
   */
  groupDepartmentsByLocation(departments) {
    if (!Array.isArray(departments)) return {};

    const grouped = {};
    
    departments.forEach(department => {
      const locationKey = department.locationRef || department.locationId || 'unknown';
      const locationName = department.getLocationName();
      
      if (!grouped[locationKey]) {
        grouped[locationKey] = {
          locationId: locationKey,
          locationName: locationName,
          departments: []
        };
      }
      
      grouped[locationKey].departments.push(department);
    });

    // Trier les départements dans chaque groupe
    Object.values(grouped).forEach(group => {
      group.departments = DepartmentModel.sortByName(group.departments);
    });

    console.log(`📊 DepartmentController: Départements groupés en ${Object.keys(grouped).length} locations`);
    return grouped;
  }

  /**
   * Nettoyer le cache des départements
   */
  clearCache() {
    console.log('🧹 DepartmentController: Cache des départements nettoyé');
    // Ici on pourrait implémenter un système de cache si nécessaire
  }
}

export default DepartmentController;
