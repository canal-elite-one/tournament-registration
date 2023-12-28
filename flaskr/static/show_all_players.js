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
const frToEn = {
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

const numericCols = ["bibNo", "licenceNo", "nbPoints"];
const dontSort = ["registeredEntries", "phone"];

const searchCols = ["licenceNo", "firstName", "lastName", "club"];

let sortedArray;
let filteredArray;

function putDataInTable(data, elementId) {
    const columns = Object.getOwnPropertyNames(frToEn);
    const table = document.createElement('table');
    table.id = "players_table";
    const body = document.createElement('tbody');
    const head = document.createElement('thead');

    columns.forEach(function(colName) {
        if (colName != 'Surplus de paiement') {
            let colCell = document.createElement('th');
            colCell.setAttribute("onclick", "sortByColumn('" + frToEn[colName] + "')");
            colCell.appendChild(document.createTextNode(colName));
            head.appendChild(colCell);
        }
    });
    table.appendChild(head);

    data.forEach(function(playerObject) {
        let row = document.createElement('tr');
        row.setAttribute("class", "players_table_row")
        columns.forEach(function(colName) {
            if (colName != 'Surplus de paiement') {
                let dataCell = document.createElement('td');
                if (colName == 'Tableaux') {
                    dataCell.appendChild(document.createTextNode(playerObject["registeredEntries"].map((x) => x['categoryId']).join(", ")));
                } else {
                    dataCell.appendChild(document.createTextNode(playerObject[frToEn[colName]]));
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

    currentSort["ascending"] = (colName == currentSort["colName"]) ? (!(currentSort["ascending"])) : true;
    currentSort["colName"] = colName;
    if (numericCols.includes(colName)) {
        sortedArray.sort(function(a, b){return a[colName] - b[colName]});
        filteredArray.sort(function(a, b){return a[colName] - b[colName]});
    } else {
        function strCompare(a, b){
            let x = a[colName].toLowerCase();
            let y = b[colName].toLowerCase();
            if (x > y) { return 1; }
            if (x < y) { return -1; }
            return 0;
        }
        sortedArray.sort(strCompare);
        filteredArray.sort(strCompare);
    }
    if (!(currentSort["ascending"])) {
        sortedArray.reverse();
        filteredArray.reverse();
    }
    document.getElementById("players_table").remove();
    putDataInTable(filteredArray, "players_table_div");
}

function filterData() {
    searchString = document.getElementById("players_table_search").value.toLowerCase();
    filteredArray = [];
    let cellValue;
    sortedArray.forEach(function(playerObject) {
        for (let x in searchCols) {
            colName = searchCols[x];
            cellValue = (numericCols.includes(colName) ? playerObject[colName].toString() : playerObject[colName]).toLowerCase();
            if (cellValue.startsWith(searchString)) {
                filteredArray.push(playerObject);
                break;
            }
        };
    })
    document.getElementById("players_table").remove();
    putDataInTable(filteredArray, "players_table_div");
}


fetch("/api/all_players")
        .then(response => { return response.json(); })
            .then(dataJson => {
                sortedArray=dataJson["players"];
                filteredArray = [...sortedArray];
                putDataInTable(dataJson["players"], "players_table_div");
            });

document.getElementById("players_table_search").value = "";
