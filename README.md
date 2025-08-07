# 🚀 Leoni - Système de Gestion d'Employés

Ce repository contient le système complet de gestion d'employés Leoni avec filtrage par département et localisation.

## 📋 Structure du Projet

```
Leoni/
├── Stage-Leoni/          # 📱 Application Mobile (React Native + Flask Backend)
│   ├── Backend/          # 🔧 Flask API avec filtrage par département/location
│   ├── LeoniApp/         # 📱 Application React Native (Expo)
│   └── Diagramme/        # 📊 Diagrammes et documentation
│
└── StageLeoni/           # 🖥️ Panel Admin (Spring Boot)
    ├── admin-service/    # 🏢 Service d'administration Spring Boot
    ├── src/             # 📁 Code source Java
    └── target/          # 🎯 Fichiers compilés
```

## 🎯 Fonctionnalités Principales

### 🔐 Système d'Authentification
- Connexion sécurisée avec JWT
- Gestion des rôles (EMPLOYEE, ADMIN, SUPERADMIN)
- Filtrage basé sur département et localisation

### 📱 Application Mobile (React Native)
- Interface utilisateur intuitive
- Gestion des demandes de documents
- Actualités filtrées par département
- Profil utilisateur avec photo

### 🖥️ Panel d'Administration (Spring Boot)
- Interface web pour les administrateurs
- Gestion filtrée des employés
- Traitement des demandes de documents
- Système de notifications

### 🔧 Backend Flask
- API RESTful complète
- Filtrage intelligent par département/location
- Base de données MongoDB Atlas
- Système de notifications

## 🏢 Départements et Localisations

### 📍 Localisations
- **Messadine** - Site principal
- **Mateur** - Site secondaire  
- **Manzel Hayet** - Site tertiaire

### 🏬 Départements par Localisation
- **IT** (Information Technology)
- **Production** (Ligne de production)
- **Sales** (Équipe commerciale)

## 🚀 Démarrage Rapide

### Backend Flask (Port 5000)
```bash
cd Stage-Leoni/Backend
python app.py
```

### Application Mobile
```bash
cd Stage-Leoni/LeoniApp
expo start
```

### Panel Admin Spring Boot (Port 8085)
```bash
cd StageLeoni
mvn spring-boot:run
```

## 🔧 Configuration

### Base de Données
- **MongoDB Atlas** (Production)
- **MongoDB Local** (Développement - fallback)

### Variables d'Environnement
```env
MONGODB_URI=mongodb+srv://...
JWT_SECRET_KEY=your_secret_key
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your_email@gmail.com
```

## 👥 Architecture Multi-Projets

Ce repository unifie deux projets indépendants qui partagent la même base de données MongoDB :

1. **Stage-Leoni** : Application mobile complète avec backend Flask
2. **StageLeoni** : Panel d'administration Spring Boot

## 🛡️ Sécurité

- Authentification JWT sécurisée
- Filtrage automatique par département/location
- Validation des données côté serveur
- CORS configuré pour la sécurité

## 📊 Système de Filtrage

Les administrateurs ne peuvent gérer que les employés de leur :
- **Département** (pour les ADMIN)
- **Tous les départements** (pour les SUPERADMIN)
- **Localisation** (obligatoire pour tous)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changes (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est développé pour Leoni - Tous droits réservés.

---

**Développé avec ❤️ par l'équipe Leoni**
