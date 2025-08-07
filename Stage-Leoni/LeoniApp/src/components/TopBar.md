# TopBar Component

## Description
Composant de barre de navigation supérieure qui affiche la photo de profil, le nom complet de l'utilisateur, son département et un bouton de déconnexion.

## Fonctionnalités
- ✅ Photo de profil avec image par défaut
- ✅ Nom complet récupéré via UserModel.getFullName()
- ✅ Département de l'utilisateur 
- ✅ Bouton de déconnexion avec confirmation
- ✅ Masquage automatique sur la page "Mon profil"
- ✅ Support AuthContext pour la gestion d'état global
- ✅ Style cohérent avec votre charte graphique Leoni

## Utilisation

### Dans MainTabNavigator.js
```javascript
import TopBar from '../components/TopBar';

const MainTabNavigator = ({ route }) => {
  const { userData } = route.params || {};
  
  return (
    <View style={styles.container}>
      <TopBar
        userData={userData}
        navigation={navigation}
        hideOnProfile={true}
        currentRoute={currentRoute}
      />
      <Tab.Navigator>
        {/* ... vos onglets */}
      </Tab.Navigator>
    </View>
  );
};
```

## Props

| Prop | Type | Description | Requis |
|------|------|-------------|---------|
| `userData` | Object | Données utilisateur (peut être null si utilise AuthContext) | Non |
| `navigation` | Object | Objet navigation React Navigation | Oui |
| `hideOnProfile` | Boolean | Masquer sur la page profil (défaut: false) | Non |
| `currentRoute` | String | Route actuelle pour déterminer le masquage | Non |

## Dépendances
- UserModel (pour la gestion des données utilisateur)
- AuthController (pour la déconnexion)
- AuthContext (pour l'état global d'authentification)
- @expo/vector-icons (pour les icônes)

## Gestion d'état
Le composant peut fonctionner avec :
1. **Props directes** : `userData` passé en prop
2. **AuthContext** : Utilise `currentUser` depuis le contexte si pas de props

## Style
- Couleur de fond : `#002857` (bleu Leoni)
- Photo de profil circulaire 40x40px
- Bouton de déconnexion avec effet de transparence
- Ombrage pour l'élévation
