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
    try {
        const response = await fetch('/api/public/entries/' + licenceNo);
        if (!response.ok) {
            const data = await response.json();
            if ('PLAYER_NOT_FOUND_ERROR' in data) {
                window.alert('Aucun joueur avec ce numéro de licence n\'a été trouvé.');
                window.location.href = '/public';
            } else {
                console.log(data);
                // window.location.href = '/public/erreur';
            }
        } else {
            const entries = await response.json();
            console.log(entries);
            fillEntries(entries);
        }
    } catch (error) {
        console.log(error);
        // window.location.href = 'public/erreur';
    }
}

fetchEntries().then(() => showContent());
