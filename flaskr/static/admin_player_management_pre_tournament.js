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
};

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

let playerObject;
let categoriesData;

const relevantPlayerFields = ['licenceNo', 'firstName', 'lastName', 'gender', 'club', 'nbPoints', 'email', 'phone'];
const relevantCategoriesFields = ['categoryId', 'color', 'entryCount', 'maxPlayers', 'overbookingPercentage', 'womenOnly', 'maxPoints', 'minPoints']

const initialRegisteredCategoryIds = [];

const categoryIdByColor = {};
const sameColor = {};

function handleCheckbox(categoryId) {
    if (!(categoryId in sameColor)) { return null; }
    checkbox = document.getElementById('register_checkbox_' + categoryId);
    otherCheckbox = document.getElementById('register_checkbox_' + sameColor[categoryId]);
    if (checkbox.checked) {
        otherCheckbox.checked = false;
    }
    if (initialRegisteredCategoryIds.includes(categoryId)) {
        let label = document.getElementById(checkbox.id + '_label')
        if (checkbox.checked) {
            label.firstChild.data = ' ';
        } else {
            label.firstChild.data = '\u26A0';
        }
    }
    if (initialRegisteredCategoryIds.includes(sameColor[categoryId])) {
        let label = document.getElementById(otherCheckbox.id + '_label')
        if (otherCheckbox.checked) {
            label.firstChild.data = ' ';
        } else {
            label.firstChild.data = '\u26A0';
        }
    }
}

function deletePlayer() {
    let confirmMessage
    if (playerObject['gender'] == 'M') {
        confirmMessage = "Voulez-vous vraiment supprimer ce compétiteur de la base de données ? Toutes les informations sur les inscriptions seront perdues";
    } else {
        confirmMessage = "Voulez-vous vraiment supprimer cette compétitrice de la base de données ? Toutes les informations sur les inscriptions seront perdues";
    }
    if (confirm(confirmMessage)) {
        fetch('/api/players/' + licence_no, {method: 'DELETE'}).then(() =>
        {
            console.log('Successfully deleted player' + licence_no);
            window.location.href = "/admin/inscrits";
        });
    }
}

function processPlayerInfo() {
    let playerInfo = document.createElement('table');
    playerInfo.setAttribute('id', 'player_info_table');
    playerObject['registeredEntries'].forEach( (entryObject) =>
    {
        let categoryId = entryObject['categoryId'];
        initialRegisteredCategoryIds.push(categoryId);
        document.getElementById('register_checkbox_' + categoryId).checked = true;
    });
    relevantPlayerFields.forEach(
        function(fieldName) {
            let row = document.createElement('tr');
            let fieldNameCell = document.createElement('td');
            fieldNameCell.appendChild(document.createTextNode(enToFr[fieldName]));
            row.appendChild(fieldNameCell);
            let fieldValueCell = document.createElement('td');
            fieldValueCell.appendChild(document.createTextNode(playerObject[fieldName]));
            row.appendChild(fieldValueCell);
            playerInfo.appendChild(row);
        });
    document.getElementById('player_info').appendChild(playerInfo);
    let deleteButton = document.createElement('input');
    deleteButton.type = 'button';
    deleteButton.setAttribute('onclick', 'deletePlayer()');
    deleteButton.id = 'delete_player_button';
    if (playerObject['gender'] == 'F') {
        deleteButton.setAttribute('value', 'Supprimer compétitrice \uD83D\uDDD1');
    } else {
        deleteButton.setAttribute('value', 'Supprimer compétiteur \uD83D\uDDD1');
    }

    document.getElementById('player_info').appendChild(deleteButton);
}

function createCategoryRow(categoryObject) {
    let row = document.createElement('tr');
            let categoryId = categoryObject['categoryId'];

            let registerCell = document.createElement('td');
            registerCell.setAttribute('id', 'register_cell_' + categoryId);
            let registerCheckbox = document.createElement('input');
            registerCheckbox.type = 'checkbox';
            registerCheckbox.id = 'register_checkbox_' + categoryId;
            registerCheckbox.setAttribute('oninput', 'handleCheckbox("' + categoryId + '")');
            registerCell.appendChild(registerCheckbox);
            let registerLabel = document.createElement('label');
            registerLabel.id = registerCheckbox.id + '_label';
            registerLabel.setAttribute('for', registerCheckbox.id);
            registerLabel.appendChild(document.createTextNode(' '));
            registerCell.appendChild(registerLabel);

            let idCell = document.createElement('td');
            idCell.setAttribute('id', 'id_cell_' + categoryId);
            idCell.appendChild(document.createTextNode(categoryId));
            row.appendChild(idCell);

            let color = categoryObject['color'];

            if (!(color === null)) {
                if (color in categoryIdByColor) {
                    sameColor[categoryId] = categoryIdByColor[color];
                    sameColor[categoryIdByColor[color]] = categoryId;
                } else { categoryIdByColor[color] = categoryId; }
                // registerCell.style.backgroundColor = categoryObject['color'];
                idCell.style.backgroundColor = color;
            };

            let entryCount = categoryObject['entryCount'];
            let maxPlayers = categoryObject['maxPlayers'];
            let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));

            let entryCountColor;

            if (entryCount < maxPlayers) {
                entryCountColor = 'hsl(140, 100%, 80%)';
            } else if (entryCount > maxOverbooked) {
                entryCountColor = 'hsl(25, 100%, 80%)';
            } else {
                entryCountColor = 'hsl(60, 100%, 80%)';
            }

            let entryCountCell = document.createElement('td');
            entryCountCell.setAttribute('id', 'entry_count_cell_' + categoryId);
            entryCountCell.appendChild(document.createTextNode(entryCount + ' / ' + maxPlayers + ' (' + maxOverbooked + ')'));
            row.appendChild(entryCountCell);

            entryCountCell.style.backgroundColor = entryCountColor;

            let pointsCell = document.createElement('td');
            pointsCell.setAttribute('id', 'points_cell_' + categoryId);
            let maxPoints = categoryObject['maxPoints'];
            let minPoints = categoryObject['minPoints'];
            let pointsString;
            if (maxPoints < 4000) {
                pointsString = '< ' + maxPoints;
            } else if (minPoints > 0) {
                pointsString = '> ' + minPoints;
            } else { pointsString = ' -'}

            if (playerObject['nbPoints'] < minPoints || playerObject['nbPoints'] > maxPoints) {
                pointsCell.style.backgroundColor = 'red';
                registerCell.style.backgroundColor = 'grey';
                registerCheckbox.setAttribute('disabled', '');
                pointsString = pointsString + ' \u2717';
            } else {
                pointsString = pointsString + ' \u2713';
            }
            pointsCell.appendChild(document.createTextNode(pointsString));
            row.appendChild(pointsCell);

            let womenOnlyCell = document.createElement('td');
            womenOnlyCell.setAttribute('id', 'women_only_cell_' + categoryId);
            womenOnlyCell.appendChild(document.createTextNode(categoryObject['womenOnly'] ? 'Oui' : 'Non'));
            row.appendChild(womenOnlyCell);
            if (categoryObject['womenOnly'] && playerObject['gender'] == 'M') {
                womenOnlyCell.style.backgroundColor = 'red';
                registerCell.style.backgroundColor = 'red';
                registerCheckbox.setAttribute('disabled', '');
            }
            row.appendChild(registerCell);

            return row;
}

function fillHead(head, tempColumns) {
    tempColumns.forEach(function (colName){
        let colCell = document.createElement('th');
        colCell.id = 'col_' + colName.toLowerCase().replace(' ', '_');
        colCell.appendChild(document.createTextNode(colName));
        head.appendChild(colCell);
    });
}

function setUpCategoriesTable() {
    const saturdayCategories = [];
    const sundayCategories = [];
    categoriesData.forEach(function (categoryObject)
    {
        let categoryDay = new Date(categoryObject['startTime']);
        if (categoryDay.getDate() == 6) {
            saturdayCategories.push(categoryObject);
        } else {
            sundayCategories.push(categoryObject);
        }
    });

    let saturdayTable = document.createElement('table');
    let saturdayHead = document.createElement('thead');
    let saturdayBody = document.createElement('tbody');

    let sundayTable = document.createElement('table');
    let sundayHead = document.createElement('thead');
    let sundayBody = document.createElement('tbody');

    let columns = ['Tableaux', "Nombre d'inscrits", 'Limite de points', 'Féminin ?', 'Inscription'];

    fillHead(saturdayHead, columns);
    saturdayTable.appendChild(saturdayHead);
    fillHead(sundayHead, columns);
    sundayTable.appendChild(sundayHead);

    saturdayCategories.forEach(
        function (categoryObject) {
            row = createCategoryRow(categoryObject);
            saturdayBody.appendChild(row);
        });
    saturdayTable.appendChild(saturdayBody);
    document.getElementById('admin_entry_management').appendChild(saturdayTable);
    sundayCategories.forEach(
        function (categoryObject) {
            row = createCategoryRow(categoryObject);
            sundayBody.appendChild(row);
        });
    sundayTable.appendChild(sundayBody);
    document.getElementById('admin_entry_management').appendChild(sundayTable);
}

const categoriesPromise = fetch("/api/categories");
const playerPromise = fetch("/api/players/" + licence_no);

Promise.all([categoriesPromise, playerPromise]).then(
    async(responses) =>
    {
        categoriesData = await responses[0].json();
        playerObject = await responses[1].json();
        categoriesData = categoriesData["categories"];
    }).then(() =>
    {
        setUpCategoriesTable()
        processPlayerInfo();
    });
