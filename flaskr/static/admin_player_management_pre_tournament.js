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
    checkbox = document.getElementById('register_checkbox_' + categoryId);

    if (!(categoryId in sameColor)) {
        if (initialRegisteredCategoryIds.includes(categoryId) && !checkbox.checked) {
            let label = document.getElementById(checkbox.id + '_label')
            label.firstChild.data = '\u26A0';
        } else if (initialRegisteredCategoryIds.includes(categoryId) && checkbox.checked) {
            let label = document.getElementById(checkbox.id + '_label')
            label.firstChild.data = ' ';
        }
        return null;
    }

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
    let playerInfoTable = document.getElementById('player_info_table');
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
            playerInfoTable.appendChild(row);
        });
    let deleteButtonText;
    if (playerObject['gender'] == 'F') {
        deleteButtonText = document.createTextNode('Supprimer compétitrice \uD83D\uDDD1');
    } else {
        deleteButtonText = document.createTextNode('Supprimer compétiteur \uD83D\uDDD1');
    }
    document.getElementById('delete_player_button').appendChild(deleteButtonText);
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

    let saturdayBody = document.getElementById('saturday_table_body');

    let sundayBody = document.getElementById('sunday_table_body');

    saturdayCategories.forEach(
        function (categoryObject) {
            row = createCategoryRow(categoryObject);
            saturdayBody.appendChild(row);
        });

    sundayCategories.forEach(
        function (categoryObject) {
            row = createCategoryRow(categoryObject);
            sundayBody.appendChild(row);
        });
}

function submitEntries() {
    let categoryIdsToRegister = [];
    let categoryIdsToDelete = [];

    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let checkbox = document.getElementById('register_checkbox_' + categoryId);
        if (checkbox.checked) {
            categoryIdsToRegister.push(categoryId);
        } else if (initialRegisteredCategoryIds.includes(categoryId)) {
            categoryIdsToDelete.push(categoryId);
        }
    });

    let registerData = {
        'categoryIds': categoryIdsToRegister,
    };

    let deleteData = {
        'categoryIds': categoryIdsToDelete,
    };

    fetch('/api/entries/' + licence_no, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
    }).then((response) => response.json())
    .then((data) => {
        if ('error' in data) {
            console.error('Could not register new entries: ' + data.error);
        } else {
            console.log('Successfully registered new entries');
            console.log(data);
            fetch('/api/entries/' + licence_no, {
                method: 'DELETE',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(deleteData),
            }).then((response) => response.json())
            .then((data) => {
                if ('error' in data) {
                    console.error('Could not delete entries: ' + data.error);
                } else {
                    console.log('Successfully deleted entries');
                    window.location.href = "/admin/inscrits";
                }
            });
        }
    });
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
