/**
 * Modèle pour les départements Leoni
 */
export class DepartmentModel {
  constructor(data = {}) {
    this.id = data.id || data._id || null;
    this.name = data.name || '';
    this.code = data.code || '';
    this.description = data.description || '';
    this.locationRef = data.locationRef || null;
    this.locationId = data.locationId || data.locationRef || null;
    this.location = data.location || null; // Nom de la location si populé
    this.active = data.active !== undefined ? data.active : true;
    this._isActive = data.isActive !== undefined ? data.isActive : data.active;
    this.manager = data.manager || null;
    this.employees = data.employees || [];
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
  }

  // Méthodes d'instance
  isActive() {
    // Vérifier les deux propriétés pour compatibilité
    return this.active === true || this._isActive === true;
  }

  hasLocation() {
    return !!(this.locationRef || this.locationId);
  }

  hasManager() {
    return !!(this.manager && this.manager.trim().length > 0);
  }

  getEmployeeCount() {
    return this.employees ? this.employees.length : 0;
  }

  getDisplayName() {
    return this.name || this.code || 'Département non défini';
  }

  getLocationName() {
    return this.location || 'Site non défini';
  }

  // Méthodes de validation
  isValid() {
    return !!(this.name && this.name.trim().length > 0);
  }

  // Méthodes de transformation
  toJSON() {
    return {
      id: this.id,
      name: this.name,
      code: this.code,
      description: this.description,
      locationRef: this.locationRef,
      locationId: this.locationId,
      location: this.location,
      active: this.active,
      isActive: this.isActive,
      manager: this.manager,
      employees: this.employees,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }

  // Pour l'envoi vers l'API
  toAPIFormat() {
    return {
      name: this.name,
      code: this.code,
      description: this.description,
      locationRef: this.locationRef || this.locationId,
      active: this.active,
      manager: this.manager
    };
  }

  // Méthodes statiques
  static fromAPI(apiData) {
    return new DepartmentModel(apiData);
  }

  static fromAPIArray(apiArray) {
    if (!Array.isArray(apiArray)) return [];
    return apiArray.map(item => DepartmentModel.fromAPI(item));
  }

  static getEmpty() {
    return new DepartmentModel({
      id: null,
      name: '',
      code: '',
      description: '',
      locationRef: null,
      location: null,
      active: true,
      isActive: true,
      manager: null,
      employees: []
    });
  }

  // Méthodes de comparaison
  equals(other) {
    if (!(other instanceof DepartmentModel)) return false;
    return this.id === other.id;
  }

  // Méthode pour créer une copie
  clone() {
    return new DepartmentModel(this.toJSON());
  }

  // Méthodes utilitaires pour les listes
  static filterByLocation(departments, locationId) {
    if (!Array.isArray(departments)) return [];
    return departments.filter(dept => 
      dept.locationRef === locationId || dept.locationId === locationId
    );
  }

  static filterActive(departments) {
    if (!Array.isArray(departments)) return [];
    return departments.filter(dept => {
      // Si c'est une instance de DepartmentModel, utiliser la méthode
      if (dept instanceof DepartmentModel) {
        return dept.isActive();
      }
      // Sinon, vérifier directement le champ isActive (fallback)
      return dept.isActive !== false && dept.isActive !== null;
    });
  }

  static sortByName(departments) {
    if (!Array.isArray(departments)) return [];
    return [...departments].sort((a, b) => {
      // Si c'est une instance de DepartmentModel, utiliser la méthode
      const nameA = (a instanceof DepartmentModel) ? a.getDisplayName() : (a.name || '');
      const nameB = (b instanceof DepartmentModel) ? b.getDisplayName() : (b.name || '');
      return nameA.localeCompare(nameB);
    });
  }
}

export default DepartmentModel;
