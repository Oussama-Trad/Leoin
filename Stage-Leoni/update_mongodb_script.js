// Script complet pour modifier la collection document_request
try {
  // Remplacez "votre_base_de_donnees" par le nom réel de votre base
  db = db.getSiblingDB('votre_base_de_donnees');
  // 1. Convertir tous les status string en array
  db.document_request.find({}).forEach(doc => {
    db.document_request.updateOne(
      { _id: doc._id },
      { $set: { status: [doc.status] } }
    );
  });

  // 2. Ajouter la validation
  db.runCommand({
    collMod: "document_request",
    validator: {
      $jsonSchema: {
        bsonType: "object",
        properties: {
          status: {
            bsonType: "array",
            items: {
              enum: ["en attente", "en cours", "accepté", "refusé", "livré"],
              bsonType: "string"
            }
          }
        }
      }
    }
  });

  print("Mise à jour réussie ! Statuts convertis en tableau et validation ajoutée.");
} catch (e) {
  print("Erreur lors de la mise à jour : " + e);
}
