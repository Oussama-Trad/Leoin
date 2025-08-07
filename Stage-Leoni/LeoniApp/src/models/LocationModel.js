/**
 * Modèle pour les locations/sites Leoni
 */
export class LocationModel {
  constructor(data = {}) {
    this.id = data.id || data._id || null;
    this.name = data.name || '';
    this.code = data.code || '';
    this.address = data.address || '';
    this.city = data.city || '';
    this.country = data.country || 'Tunisia';
    this.active = data.active !== undefined ? data.active : true;
    this.departments = data.departments || [];
    this.createdAt = data.createdAt || null;
    this.updatedAt = data.updatedAt || null;
  }

  // Méthodes d'instance
  isActive() {
    return this.active === true;
  }

  hasDepartments() {
    return this.departments && this.departments.length > 0;
  }

  getDepartmentCount() {
    return this.departments ? this.departments.length : 0;
  }

  getDisplayName() {
    return this.name || this.code || 'Site non défini';
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
      address: this.address,
      city: this.city,
      country: this.country,
      active: this.active,
      departments: this.departments,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }

  // Méthodes statiques
  static fromAPI(apiData) {
    return new LocationModel(apiData);
  }

  static fromAPIArray(apiArray) {
    if (!Array.isArray(apiArray)) return [];
    return apiArray.map(item => LocationModel.fromAPI(item));
  }

  static getEmpty() {
    return new LocationModel({
      id: null,
      name: '',
      code: '',
      address: '',
      city: '',
      country: 'Tunisia',
      active: true,
      departments: []
    });
  }

  // Méthodes de comparaison
  equals(other) {
    if (!(other instanceof LocationModel)) return false;
    return this.id === other.id;
  }

  // Méthode pour créer une copie
  clone() {
    return new LocationModel(this.toJSON());
  }
}

export default LocationModel;
