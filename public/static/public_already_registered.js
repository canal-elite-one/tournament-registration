function fillEntries(entries) {
    let registeredList = document.getElementById('already-registered-list');
    entries.forEach(entryObject => {
        let entry = document.createElement('li');
        let entryString = "Tableau " + entryObject['categoryId']
        if (entryObject['alternateName'] !== null) {
            entryString += " (" + entryObject['alternateName'] + ") ";
        }
        let startTime = new Date(entryObject['startTime']);
        entryString += ", le " + startTime.toLocaleDateString('fr-FR', {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
        entryString += " à " + startTime.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'});
        entry.appendChild(document.createTextNode(entryString));
        registeredList.appendChild(entry);
    });
}

async function fetchEntries() {
    const response = await fetch('/api/public/entries/' + licenceNo);
    if (!response.ok) {
        publicHandleBadResponse(response);
    } else {
        const entries = await response.json();
        console.log(entries);
        fillEntries(entries);
    }
}

fetchEntries().then(() => showContent());
