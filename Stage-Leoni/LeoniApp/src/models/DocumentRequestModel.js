class DocumentRequestModel {
  // Types de documents disponibles (synchronisés avec la base de données)
  static DOCUMENT_TYPES = [
    'Identity Card',
    'Employment Contract',
    'Medical Certificate', 
    'Educational Certificate',
    'Background Check',
    'Tax Documents'
  ];

  // Niveaux d'urgence disponibles
  static URGENCY_LEVELS = [
    'faible',
    'normale', 
    'élevée',
    'urgente'
  ];

  constructor() {
    this.document = {
      name: '',
      status: {
        current: ['en attente'],
        progress: [
          {step: ['en attente'], date: null, completed: false},
          {step: ['en cours'], date: null, completed: false}, 
          {step: ['accepté'], date: null, completed: false},
          {step: ['refusé'], date: null, completed: false},
          {step: ['livré'], date: null, completed: false}
        ]
      }
    };
  }

  getDocument() {
    // Return deep copy of document
    return JSON.parse(JSON.stringify(this.document));
  }

  updateStatus(newStatus) {
    const statusIndex = this.document.status.progress.findIndex(s => s.step.includes(newStatus[0]));
    if (statusIndex >= 0) {
      // Update all steps up to current one
      this.document.status.progress.forEach((step, index) => {
        this.document.status.progress[index].completed = index <= statusIndex;
        this.document.status.progress[index].date = new Date();
      });
      this.document.status.current = newStatus;
      this.notify();
    }
  }

  getCurrentStatus() {
    return this.document.status.current;
  }

  getStatusHistory() {
    return this.document.status.progress;
  }

  subscribe(callback) {
    this.onChange = callback;
  }

  notify() {
    if (this.onChange) {
      this.onChange(this.getDocument());
    }
  }

  /**
   * Valider les données de la demande
   */
  validate(data = {}) {
    const errors = [];
    console.log('🔍 DocumentRequestModel: Validation des données:', data);

    // Accepter soit 'type' soit 'documentType'
    const documentType = data.type || data.documentType;
    console.log('🔍 DocumentRequestModel: DocumentType extrait:', documentType);
    
    if (!documentType || !documentType.trim()) {
      errors.push('Le type de document est requis');
      console.log('❌ DocumentRequestModel: Type de document manquant');
    }

    // Vérifier si le type est valide
    if (documentType && !DocumentRequestModel.DOCUMENT_TYPES.includes(documentType)) {
      errors.push('Type de document invalide');
      console.log('❌ DocumentRequestModel: Type invalide:', documentType);
      console.log('📋 DocumentRequestModel: Types autorisés:', DocumentRequestModel.DOCUMENT_TYPES);
    }

    console.log('🔍 DocumentRequestModel: Résultat validation:', { isValid: errors.length === 0, errors });

    return {
      isValid: errors.length === 0,
      errors: errors
    };
  }

  /**
   * Convertir en objet pour l'API
   */
  toApiObject(data = {}) {
    return {
      documentType: data.type || data.documentType || '',
      description: data.description || '',
      urgency: data.urgency || 'normale'
    };
  }

  /**
   * Créer un modèle depuis la réponse de l'API
   */
  static fromApiResponse(apiData) {
    return {
      id: apiData._id || apiData.id,
      type: apiData.documentType || apiData.type, // Priorité à documentType
      documentType: apiData.documentType || apiData.type,
      description: apiData.description || '',
      status: apiData.status || 'en attente',
      createdAt: apiData.createdAt,
      updatedAt: apiData.updatedAt
    };
  }
}

export default DocumentRequestModel;
