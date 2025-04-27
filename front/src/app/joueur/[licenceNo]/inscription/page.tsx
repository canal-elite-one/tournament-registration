import {DefaultApi} from "@/backend_api/backend";
import EntriesSummary from "@/app/joueur/[licenceNo]/inscription/EntriesSummary";

export default async function Page({params}: {
  params: Promise<{ licenceNo: string }>;
}) {
  const { licenceNo } = await params;
  const api = new DefaultApi();
  const entries = await api.getEntries({licenceNo: licenceNo})

  const formattedEntries = entries.map(entry => {
    const maxOverbooked =  Math.floor(entry.maxPlayers * (1 + entry.overbookingPercentage/100.0));
    const rank = entry.rank;
    const waitingListPosition = rank - maxOverbooked;

    const isInWaitingList = rank > maxOverbooked;


    let entryString = "Tableau " + entry.categoryId;
    if (entry.alternateName !== null) {
      entryString += " (" + entry.alternateName + ")";
    }
    if (isInWaitingList) {
      entryString += " - " + waitingListPosition + "e sur liste d'attente";
    }
    const startTime = new Date(entry.startTime);
    entryString += ", le " + startTime.toLocaleDateString('fr-FR', {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
    entryString += " à " + startTime.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'});
    return {
      id: entry.categoryId,
      label: entryString,
      isInWaitingList: isInWaitingList,
      hasPaid: entry.markedAsPaid
    };
  });

  return <EntriesSummary licenceNo={licenceNo} entries={formattedEntries.filter(e => e.hasPaid || e.isInWaitingList)} emailContact={process.env.USKB_CONTACT_EMAIL}></EntriesSummary>
};
