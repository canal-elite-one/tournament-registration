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
    'N° dossard': 'bibNo',
    'Club':'club',
    'Adresse Mail':'email',
    'Genre':'gender',
    'Classement':'nbPoints',
    'Surplus de paiement':'paymentDiff',
    'N° téléphone':'phone',
    'Tableaux':'registeredEntries'
}

const numericCols = ["bibNo", "licenceNo", "nbPoints"]
const dontSort = ["registeredEntries", "phone"]

let playerArray;

function putDataInTable(data, elementId) {
    const columns = Object.getOwnPropertyNames(FrToEn);
    const table = document.createElement('table');
    table.id = "players_table";
    const body = document.createElement('tbody');
    const head = document.createElement('thead');

    columns.forEach(function(colName) {
        if (colName != 'Surplus de paiement') {
            let colCell = document.createElement('th');
            colCell.setAttribute("onclick", "sortByColumn('" + FrToEn[colName] + "')");
            colCell.appendChild(document.createTextNode(colName));
            head.appendChild(colCell);
        }
    });
    table.appendChild(head);

    data.forEach(function(playerObject) {
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
    window.location.href = "/admin/inscrits/" + licenceNo;
};


let currentSort = {"colName": null, "ascending": true};

function sortByColumn(colName) {
    if (dontSort.includes(colName)) {
        return null;
    }
    currentSort["ascending"] = (colName == currentSort["colName"]) ? (!(currentSort["ascending"])):true;
    currentSort["colName"] = colName;
    if (numericCols.includes(colName)) {
        playerArray.sort(function(a, b){return a[colName] - b[colName]});
    } else {
        playerArray.sort(function(a, b){
            let x = a[colName].toLowerCase();
            let y = b[colName].toLowerCase();
            if (x > y) { return 1; }
            if (x < y) { return -1; }
            return 0;
        });
    }
    if (!(currentSort["ascending"])) {
        playerArray.reverse();
    }
    let oldTable = document.getElementById("players_table");
    oldTable.remove();
    putDataInTable(playerArray, "players_table_div");
}

fetch("http://localhost:5000/api/all_players")
        .then(response => { return response.json(); })
            .then(dataJson => { playerArray=dataJson["players"]; putDataInTable(dataJson["players"], "players_table_div"); });
