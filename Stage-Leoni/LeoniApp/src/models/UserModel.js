/**
 * Modèle User - Définit la structure et les validations pour un utilisateur
 */
class UserModel {
  constructor(userData = {}) {
    this.id = userData.id || null;
    this.firstName = userData.firstName || '';
    this.lastName = userData.lastName || '';
    this.adresse1 = userData.adresse1 || '';
    this.phoneNumber = userData.phoneNumber || '';
    this.adresse2 = userData.adresse2 || '';
    this.parentalPhoneNumber = userData.parentalPhoneNumber || '';
    this.employeeId = userData.employeeId || '';
    // CORRECTION: Utiliser les données du backend au lieu de valeurs par défaut
    this.department = userData.department || (userData.departmentName || 'IT');
    this.location = userData.location || (userData.locationName || 'Sousse');  // Nom de la location
    this.position = userData.position || 'Non spécifié';
    this.address = userData.address || '';
    this.profilePicture = userData.profilePicture || null;
    this.createdAt = userData.createdAt || null;
    this.updatedAt = userData.updatedAt || null;
  }

  /**
   * Valider les données de l'utilisateur
   */
  static validate(userData) {
    const errors = [];

    // Validation prénom
    if (!userData.firstName || userData.firstName.trim().length < 2) {
      errors.push('Le prénom doit contenir au moins 2 caractères');
    }

    // Validation nom
    if (!userData.lastName || userData.lastName.trim().length < 2) {
      errors.push('Le nom doit contenir au moins 2 caractères');
    }

    // Validation adresse1
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!userData.adresse1 || !emailRegex.test(userData.adresse1)) {
      errors.push('Format adresse1 invalide');
    }

    // Validation téléphone
    if (!userData.phoneNumber || userData.phoneNumber.length < 8) {
      errors.push('Numéro de téléphone invalide');
    }

    // Validation adresse2 (obligatoire)
    if (!userData.adresse2 || !userData.adresse2.trim()) {
      errors.push('Adresse2 est obligatoire');
    } else if (!emailRegex.test(userData.adresse2)) {
      errors.push('Format adresse2 invalide');
    }

    // Validation employeeId (optionnel mais doit être à 8 chiffres si fourni)
    if (userData.employeeId && userData.employeeId.trim()) {
      const employeeIdRegex = /^\d{8}$/;
      if (!employeeIdRegex.test(userData.employeeId.trim())) {
        errors.push('L\'ID employé doit être un nombre à 8 chiffres');
      }
    }

    // Validation location et département (obligatoires)
    if (!userData.location || !userData.location.trim()) {
      errors.push('Veuillez sélectionner votre site de travail');
    }

    if (!userData.department || !userData.department.trim()) {
      errors.push('Veuillez sélectionner votre département');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Convertir en objet pour l'API
   */
  toApiObject() {
    return {
      firstName: this.firstName,
      lastName: this.lastName,
      adresse1: this.adresse1.toLowerCase().trim(),
      phoneNumber: this.phoneNumber,
      adresse2: this.adresse2 ? this.adresse2.toLowerCase().trim() : '',
      parentalPhoneNumber: this.parentalPhoneNumber,
      employeeId: this.employeeId,
      department: this.department,
      location: this.location,
      position: this.position,
      address: this.address,
      profilePicture: this.profilePicture
    };
  }

  /**
   * Obtenir le nom complet
   */
  getFullName() {
    const firstName = this.firstName || '';
    const lastName = this.lastName || '';
    return `${firstName} ${lastName}`.trim();
  }

  /**
   * Vérifier si le profil est complet
   */
  isProfileComplete() {
    return !!(
      this.firstName &&
      this.lastName &&
      this.adresse1 &&
      this.phoneNumber &&
      this.department !== 'Non spécifié' &&
      this.position !== 'Non spécifié'
    );
  }

  /**
   * Créer une instance depuis les données de l'API
   */
  static fromApiResponse(apiData) {
    return new UserModel({
      id: apiData.id || apiData._id,
      firstName: apiData.firstName,
      lastName: apiData.lastName,
      adresse1: apiData.adresse1,
      phoneNumber: apiData.phoneNumber,
      adresse2: apiData.adresse2,
      parentalPhoneNumber: apiData.parentalPhoneNumber,
      employeeId: apiData.employeeId,
      department: apiData.department || 'Non spécifié',
      position: apiData.position,
      address: apiData.address,
      profilePicture: apiData.profilePicture,
      locationId: apiData.locationRef || apiData.locationId,  // Récupérer depuis locationRef
      departmentId: apiData.departmentRef || apiData.departmentId,  // Récupérer depuis departmentRef
      location: apiData.location,  // Nom de la location
      createdAt: apiData.createdAt,
      updatedAt: apiData.updatedAt
    });
  }
}

export default UserModel;
