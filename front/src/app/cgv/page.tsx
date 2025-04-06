export default function CGV() {
  return (
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Conditions Générales de Vente (CGV)</h1>

        <p>Les présentes Conditions Générales de Vente régissent les inscriptions au
          tournoi national B de l'US Kremlin-Bicêtre.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Tarifs</h2>
        <p>Frais d'engagement : 10€ par tableau, maximum 2 tableaux par jour.
          Possibilité d’un 3e tableau en cas d’élimination dans au moins 1 tableau.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Inscriptions</h2>
        <p>Les inscriptions sont ouvertes jusqu’au vendredi 13 juin 2025 à 12h00 via le
          site <a className="text-blue-600 hover:underline"
                  href="https://tournoiuskb.fr">tournoiuskb.fr</a>.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Paiement</h2>
        <p>Le paiement est sécurisé via Stripe. Aucune inscription n'est validée sans
          paiement.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Remboursements</h2>
        <p>Remboursement de 50% en cas de présentation d’un certificat médical, jusqu’au
          lundi 9 juin 2025 à 12h00.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Litiges</h2>
        <p>En cas de litige, les tribunaux compétents seront ceux du siège social de
          l’association USKB.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Contact</h2>
        <p>Email : <a className="text-blue-600 hover:underline"
                      href="mailto:tournoiuskb@gmail.com">tournoiuskb@gmail.com</a></p>
      </main>
  );
}
