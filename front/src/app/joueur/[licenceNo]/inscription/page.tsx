import {DefaultApi} from "@/backend_api/backend";

export default async function Page({
                                     params,
                                   }: {
  params: Promise<{ licenceNo: string }>;
}) {
  const {licenceNo} = await params;
  const api = new DefaultApi();
  const entries = await api.getEntries({licenceNo: licenceNo})

  const formattedEntries = entries.map(entry => {
    const maxOverbooked =  Math.floor(entry.maxPlayers * (1 + entry.overbookingPercentage/100.0));
    const rank = entry.rank;
    const waitingListPosition = rank - maxOverbooked;
    let entryString = "Tableau " + entry.categoryId;
    if (entry.alternateName !== null) {
      entryString += " (" + entry.alternateName + ")";
    }
    if (rank > maxOverbooked) {
      entryString += " - " + waitingListPosition + "e sur liste d'attente";
    }

    const startTime = new Date(entry.startTime);
    entryString += ", le " + startTime.toLocaleDateString('fr-FR', {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
    entryString += " à " + startTime.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'});
    return {
      id: entry.categoryId,
      label: entryString,
    };
  });

  const emailContact = process.env.USKB_CONTACT_EMAIL;
  return (
    <div>
      <h2>Vous êtes inscrit(s) aux tableaux suivants :</h2>
      <ul>
        {formattedEntries.map((entry) => (
            <li key={entry.id}>
              {entry.label}
            </li>
        ))}
      </ul>
      <p className="mb-4">Si vous souhaitez modifier vos informations ou vos
        inscriptions,
        veuillez <a href={`mailto:${emailContact}`}
                    className="font-bold text-blue-500 hover:underline">envoyer un
          mail</a> aux organisateurs :
        <a href={`mailto:${emailContact}`}
           className="font-bold text-blue-500 hover:underline"> {emailContact}</a>.
      </p>
    </div>
  );
};