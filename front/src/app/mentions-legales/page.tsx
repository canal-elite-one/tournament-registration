export default function MentionsLegales() {
  return (
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Mentions légales</h1>
        <p><strong>Éditeur du site :</strong> Union Sportive du Kremlin-Bicêtre (USKB)
        </p>
        <p>SIREN : 319 625 208</p>
        <p>Adresse : 12 Boulevard Chastenet de Géry, 94270 Le Kremlin-Bicêtre</p>
        <p>Email : <a className="text-blue-600 hover:underline"
                      href="mailto:tournoiuskb@gmail.com">tournoiuskb@gmail.com</a></p>
        <p>Téléphone : 06 89 06 10 57</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Hébergement du site</h2>
        <p>Le site est hébergé par Amazon Web Services (AWS).</p>
        <p>Amazon Web Services EMEA SARL</p>
        <p>38 Avenue John F. Kennedy, L-1855, Luxembourg</p>
        <p>Site web : <a className="text-blue-600 hover:underline"
                         href="https://aws.amazon.com/fr/">aws.amazon.com/fr/</a></p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Propriété intellectuelle</h2>
        <p>Tout le contenu de ce site est la propriété exclusive de l’USKB. Toute
          reproduction est interdite sans autorisation préalable.</p>

        <h2 className="text-xl font-semibold mt-6 mb-2">Contact</h2>
        <p>Pour toute question, vous pouvez nous contacter à : <a
            className="text-blue-600 hover:underline"
            href="mailto:tournoiuskb@gmail.com">tournoiuskb@gmail.com</a></p>
      </main>
  );
}
