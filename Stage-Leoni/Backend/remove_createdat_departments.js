// Script MongoDB pour supprimer le champ createdAt de la collection departments
// À exécuter dans MongoDB Compass ou MongoDB Shell

// 1. Se connecter à la base de données LeoniApp
use('LeoniApp');

// 2. Vérifier combien de documents ont le champ createdAt
var countWithCreatedAt = db.departments.countDocuments({"createdAt": {"$exists": true}});
print("📊 Nombre de départements avec createdAt: " + countWithCreatedAt);

// 3. Afficher quelques exemples avant suppression
print("\n📋 Exemples de départements AVANT suppression:");
db.departments.find({}, {"name": 1, "location": 1, "createdAt": 1}).limit(3).forEach(doc => {
    print("  - " + JSON.stringify(doc));
});

// 4. Supprimer le champ createdAt de tous les documents
if (countWithCreatedAt > 0) {
    var result = db.departments.updateMany(
        {"createdAt": {"$exists": true}},  // Filtre: documents qui ont le champ createdAt
        {"$unset": {"createdAt": ""}}      // Opération: supprimer le champ createdAt
    );
    
    print("\n✅ Champ createdAt supprimé de " + result.modifiedCount + " département(s)");
} else {
    print("\nℹ️ Aucun document avec le champ createdAt trouvé");
}

// 5. Vérifier que la suppression a bien fonctionné
var remainingCount = db.departments.countDocuments({"createdAt": {"$exists": true}});
print("📊 Nombre de départements avec createdAt après suppression: " + remainingCount);

// 6. Afficher quelques exemples après suppression pour vérification
print("\n📋 Exemples de départements APRÈS suppression:");
db.departments.find({}, {"name": 1, "location": 1, "createdAt": 1}).limit(3).forEach(doc => {
    print("  - " + JSON.stringify(doc));
});

print("\n🎉 Script terminé!");

// Instructions pour exécuter ce script:
// 1. Ouvrir MongoDB Compass
// 2. Se connecter à votre cluster MongoDB Atlas
// 3. Ouvrir l'onglet "_MONGOSH" en bas
// 4. Copier-coller ce script et appuyer sur Entrée
