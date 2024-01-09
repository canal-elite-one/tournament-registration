/*
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
*/

const frToEn = {
    'N° dossard': 'bibNo',
    'N° licence':'licenceNo',
    'Nom':'lastName',
    'Prénom':'firstName',
    'Club':'club',
    'Adresse Mail':'email',
    'Genre':'gender',
    'Classement':'nbPoints',
    'N° téléphone':'phone',
    'Montant dû (€)': 'leftToPay',
    'Tableaux':'registeredEntries'
}


const numericCols = ["licenceNo", "nbPoints"];
const dontSort = ["registeredEntries", "phone"];

const searchCols = ["licenceNo", "firstName", "lastName", "club"];

if (!hasRegistrationEnded) {
    delete frToEn['N° dossard'];
    delete frToEn['Montant dû (€)'];
} else {
    searchCols.push("bibNo");
    numericCols.push("bibNo");
    numericCols.push("leftToPay");
}

let sortedArray;
let filteredArray;
let bibsSet;

function setAllBibs() {
    fetch('/api/admin/bibs', {
        method: 'POST',
    }).then((response) => response.json())
    .then((data) => {
        if ('error' in data) {
            console.error('Could not set bibs: ' + data.error);
        } else {
            console.log(data);
            window.location.reload();
        }
    });
}

function resetAllBibs() {
    let confirmationMessage = window.prompt('Etes vous sûr de vouloir supprimer les n° de dossards existants ? Avez-vous appelé Céline avant de cliquer sur ce bouton ? Si oui, ou si vous êtes Céline, tapez "Je suis sur! J\'ai appelé Céline!" et validez.')
    if (confirmationMessage == "Je suis sur! J'ai appelé Céline!") {
        fetch('/api/admin/bibs', {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({'confirmation': confirmationMessage}),
        }).then((response) => [response.json(), response.status])
        .then((data) => {
            if (data[1] != 204) {
                console.error('Could not reset bibs: ' + data[0].error);
            } else {
                console.log('Successfully reset bibs');
                window.location.reload();
            }
        })
    } else {
        window.alert('Vous n\'êtes pas sûr et/ou vous n\'avez pas appelé Céline.');
    }
}

function putDataInTable(data, elementId) {
    const columns = Object.getOwnPropertyNames(frToEn);
    const table = document.createElement('table');
    table.id = "players_table";
    const body = document.createElement('tbody');
    const head = document.createElement('thead');

    columns.forEach(function(colName) {
        let colCell = document.createElement('th');
        colCell.setAttribute("onclick", "sortByColumn('" + frToEn[colName] + "')");
        colCell.appendChild(document.createTextNode(colName));
        head.appendChild(colCell);
    });

    table.appendChild(head);

    data.forEach(function(playerObject) {
        let row = document.createElement('tr');
        row.setAttribute("class", "players_table_row")
        columns.forEach(function(colName) {
            let dataCell = document.createElement('td');
            if (colName == 'Tableaux') {;
                dataCell.appendChild(document.createTextNode(playerObject["registeredEntries"]));
            } else {
                let cellString = playerObject[frToEn[colName]] === null ? '-' : playerObject[frToEn[colName]].toString();
                dataCell.appendChild(document.createTextNode(cellString));
                if (colName == 'Montant dû (€)' && playerObject['leftToPay'] > 0) {
                    dataCell.style.color = "red";
                }
            }
            row.appendChild(dataCell);
        });

        row.setAttribute('onclick', "goToPlayerPage(" + playerObject['licenceNo'] + ")");

        body.appendChild(row);
    });
    table.appendChild(body);
    document.getElementById(elementId).appendChild(table);
};

function goToPlayerPage(licenceNo) {
    let targetUrl = "/admin/inscrits/" + licenceNo;
    if (hasRegistrationEnded) {
        if (!bibsSet) {
            targetUrl += "?bib=false";
        } else {
            targetUrl += "?bib=true";
        }
    }
    window.location.href = targetUrl;
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

    let searchFfttButton = document.getElementById("search_fftt_button");
    if (!isNaN(searchString)) {
        searchFfttButton.removeAttribute("disabled");
    } else {
        searchFfttButton.setAttribute("disabled", "");
    }

    document.getElementById("players_table").remove();
    putDataInTable(filteredArray, "players_table_div");
}

function onEnterSearch() {
    let searchString = document.getElementById("players_table_search").value;
    if (filteredArray.length == 1) {
        goToPlayerPage(filteredArray[0]["licenceNo"]);
    } else if (searchString.length > 0 && !isNaN(searchString)) {
        goToPlayerPage(searchString);
    }
}

const searchField = document.getElementById("players_table_search");
searchField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        onEnterSearch();
    }
});

searchField.value = "";

document.getElementById('all_players_navbar_link').setAttribute('class', 'navbar-link-current');
if (!hasRegistrationEnded) {
    document.getElementById("csv_export_button").style.display = "none";
}

async function downloadCsv() {
    let downloadLink = document.createElement('a');
    downloadLink.setAttribute('href', '/api/admin/csv?by_category=false');
    downloadLink.setAttribute('download', 'competiteurs_samedi_dimanche.zip');
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

function areBibsSet() {
    let result = false;
    filteredArray.forEach(function(playerObject) {
        if (!(playerObject["bibNo"] === null)) {
            result = true;
        }
    });
    return result;
}

async function fetchPlayers() {
    let response = await fetch("/api/admin/all_players");
    if (!response.ok) {
        if (response.status == 400) {
            data = await response.json();
            console.error("Bad request: " + data);
        } else {
            console.error("Unable to fetch players: " + response.status);
        }
    } else {
        let dataJson = await response.json();
        console.log(dataJson);
        sortedArray = dataJson["players"];
        sortedArray.sort(function(a, b){return a['licenceNo'] - b['licenceNo']});
        filteredArray = [...sortedArray];
        bibsSet = areBibsSet();
        putDataInTable(dataJson["players"], "players_table_div");
    }
}

fetchPlayers().then(() => showContent());
