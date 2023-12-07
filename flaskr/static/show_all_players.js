const enToFr = {
    'bibNo':'N° dossard',
    'club':'Club',
    'email': 'Adresse Mail',
    'firstName':'Prénom',
    'gender': 'Genre',
    'lastName':'Nom de Famille',
    'licenceNo': 'N° licence',
    'nbPoints': 'Classement',
    'paymentDiff': 'Surplus de paiement',
    'phone': 'N° téléphone',
    'registeredEntries': 'Tableaux'
}
const FrToEn = {
    'N° licence':'licenceNo',
    'Prénom':'firstName',
    'Nom de Famille':'lastName',
    'N° de Dossard': 'bibNo',
    'Club':'club',
    'Adresse Mail':'email',
    'Genre':'gender',
    'Classement':'nbPoints',
    'Surplus de paiement':'paymentDiff',
    'N° téléphone':'phone',
    'Tableaux':'registeredEntries'
}


function putDataInTable(data, elementId) {
    const playerArray = data;
    const columns = Object.getOwnPropertyNames(FrToEn);
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    const head = document.createElement('thead');
    console.log(columns);

    columns.forEach(function(colName) {
        if (colName != 'Surplus de paiement') {
            let colCell = document.createElement('th');
            colCell.appendChild(document.createTextNode(colName));
            head.appendChild(colCell);
        }
    });
    table.appendChild(head);

    playerArray.forEach(function(playerObject) {
        let row = document.createElement('tr');
        columns.forEach(function(colName) {
            if (colName != 'Surplus de paiement') {
                let dataCell = document.createElement('td');
                if (colName == 'Tableaux') {
                    let entriesString = "";
                    playerObject["registeredEntries"].forEach(function(entryObject) {
                        entriesString += entryObject["categoryId"] + " ";
                    });
                    dataCell.appendChild(document.createTextNode(entriesString));
                } else {
                    dataCell.appendChild(document.createTextNode(playerObject[FrToEn[colName]]));
                }
                row.appendChild(dataCell);
            }
        });
        row.setAttribute('onclick', "goToPlayerPage(" + playerObject['licenceNo'] + ")");

        body.appendChild(row);
    });
    table.appendChild(body);
    document.getElementById(elementId).appendChild(table);
};

function goToPlayerPage(licenceNo) {
    console.log("pouet");
    window.location.href = "/admin/inscrits/" + licenceNo;
};

fetch("http://localhost:5000/api/all_players")
        .then(response => { return response.json(); })
            .then(data => { putDataInTable(data['players'], "tableaux_des_inscrits"); });
