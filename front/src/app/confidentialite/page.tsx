export default function Confidentialite() {
  return (
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Politique de confidentialité</h1>

        <p>Cette politique de confidentialité décrit comment nous collectons et
          utilisons vos données lors de votre inscription au tournoi.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Responsable du traitement</h2>
        <p>Union Sportive du Kremlin-Bicêtre (USKB)</p>
        <p>Email : <a className="text-blue-600 hover:underline"
                      href="mailto:tournoiuskb@gmail.com">tournoiuskb@gmail.com</a></p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Données collectées</h2>
        <p>Nous collectons uniquement les données nécessaires à l’inscription : nom,
          prénom, email, téléphone, licence FFTT.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Utilisation des données</h2>
        <p>Vos données servent exclusivement à la gestion du tournoi et ne sont pas
          partagées avec des tiers.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Hébergement des données</h2>
        <p>Vos données sont hébergées par Amazon Web Services (AWS), dans la région
          "eu-west-3" (Paris, France). AWS garantit un haut niveau de sécurité et de
          conformité avec le RGPD.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Paiement sécurisé</h2>
        <p>Les paiements sont traités via Stripe. Aucune donnée bancaire n’est stockée
          par l’USKB.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Durée de conservation</h2>
        <p>Vos données sont conservées jusqu'à la fin du tournoi et archivées pour une
          durée maximale de 12 mois.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Vos droits</h2>
        <p>Conformément au RGPD, vous pouvez accéder, rectifier ou supprimer vos données
          en nous contactant par email.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Contact</h2>
        <p>Email : <a className="text-blue-600 hover:underline"
                      href="mailto:tournoiuskb@gmail.com">tournoiuskb@gmail.com</a></p>
      </main>
  );
}
