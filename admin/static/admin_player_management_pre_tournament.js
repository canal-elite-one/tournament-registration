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

const categoryIdByColor = {};
const sameColor = {};

function exitConfirmation (e) {
    let confirmationMessage = 'Voulez-vous vraiment quitter la page? Les changements non sauvegardés seront perdus';
    (e).returnValue = confirmationMessage;
    return confirmationMessage;
}

function addExitConfirmation() {
    window.onbeforeunload = exitConfirmation;
}

function removeExitConfirmation() {
    window.onbeforeunload = null;
}

function handleCheckbox(categoryId) {
    addExitConfirmation();
    checkbox = document.getElementById('register-checkbox-' + categoryId);

    if (!(categoryId in sameColor)) {
        if (categoryId in playerObject['registeredEntries'] && !checkbox.checked) {
            let label = document.getElementById(checkbox.id + '-label')
            label.firstChild.data = '\u26A0';
        } else if (categoryId in playerObject['registeredEntries'] && checkbox.checked) {
            let label = document.getElementById(checkbox.id + '-label')
            label.firstChild.data = ' ';
        }
        return null;
    }

    otherCheckbox = document.getElementById('register-checkbox-' + sameColor[categoryId]);
    if (checkbox.checked) {
        otherCheckbox.checked = false;
    }
    if (categoryId in playerObject['registeredEntries']) {
        let label = document.getElementById(checkbox.id + '-label')
        if (checkbox.checked) {
            label.firstChild.data = ' ';
        } else {
            label.firstChild.data = '\u26A0';
        }
    }
    if (sameColor[categoryId] in playerObject['registeredEntries']) {
        let label = document.getElementById(otherCheckbox.id + '-label')
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
        fetch('/api/admin/players/' + licenceNo, {method: 'DELETE'}).then(() =>
        {
            console.log('Successfully deleted player' + licenceNo);
            window.location.href = "/admin/inscrits";
        });
    }
}

function processPlayerInfo() {
    let playerInfoTable = document.getElementById('player-info-table');

    relevantPlayerFields.forEach(
        function(fieldName) {
            let row = document.createElement('tr');
            let fieldNameCell = document.createElement('td');
            fieldNameCell.appendChild(document.createTextNode(enToFr[fieldName]));
            row.appendChild(fieldNameCell);
            let fieldValueCell = document.createElement('td');
            if (playerObject[fieldName] === null) {
                let fieldInput = document.createElement('input');
                fieldInput.type = (fieldName == 'email') ? 'email' : ((fieldName == 'phone') ? 'tel' : 'text');
                fieldInput.id = 'field-input-' + fieldName;
                fieldInput.value = '';
                fieldInput.setAttribute('required', '');
                fieldInput.setAttribute('onchange', 'addExitConfirmation()');
                fieldValueCell.appendChild(fieldInput);
            } else {
                fieldValueCell.appendChild(document.createTextNode(playerObject[fieldName]));
            }
            row.appendChild(fieldValueCell);
            playerInfoTable.appendChild(row);
        });
    let deleteButtonText;
    if (playerObject['gender'] == 'F') {
        deleteButtonText = document.createTextNode('Supprimer compétitrice \uD83D\uDDD1');
    } else {
        deleteButtonText = document.createTextNode('Supprimer compétiteur \uD83D\uDDD1');
    }
    document.getElementById('delete-player-button').appendChild(deleteButtonText);
}

function createEntryCountCell(categoryObject) {
    let categoryId = categoryObject['categoryId'];

    let entryCount = categoryObject['entryCount'];
    let maxPlayers = categoryObject['maxPlayers'];
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));

    let relevantEntryCount;
    let entryCountString;

    if (categoryId in playerObject['registeredEntries']) {
        rank = playerObject['registeredEntries'][categoryId]['rank'];
        relevantEntryCount = rank;
        entryCountString = rank + ' / ' + maxPlayers + ' (' + maxOverbooked + ') (' + entryCount + ')';
    } else {
        relevantEntryCount = entryCount;
        entryCountString =  ' - / ' + maxPlayers + ' (' + maxOverbooked + ') (' + entryCount + ')';
    }

    let entryCountColor;

    if (relevantEntryCount < maxPlayers) {
        entryCountColor = 'hsl(140, 100%, 80%)';
    } else if (relevantEntryCount > maxOverbooked) {
        entryCountColor = 'hsl(25, 100%, 80%)';
    } else {
        entryCountColor = 'hsl(60, 100%, 80%)';
    }

    let entryCountCell = document.createElement('td');
    entryCountCell.setAttribute('id', 'entry-count-cell-' + categoryId);
    entryCountCell.appendChild(document.createTextNode(entryCountString));

    entryCountCell.style.backgroundColor = entryCountColor;

    return entryCountCell;
}

function createCategoryRow(categoryObject) {
    let row = document.createElement('tr');
    let categoryId = categoryObject['categoryId'];

    let registerCell = document.createElement('td');
    registerCell.setAttribute('id', 'register-cell-' + categoryId);
    let registerCheckbox = document.createElement('input');
    registerCheckbox.type = 'checkbox';
    registerCheckbox.id = 'register-checkbox-' + categoryId;
    registerCheckbox.setAttribute('oninput', 'handleCheckbox("' + categoryId + '")');
    if (categoryId in playerObject['registeredEntries']) {
        registerCheckbox.checked = true;
    }
    registerCell.appendChild(registerCheckbox);
    let registerLabel = document.createElement('label');
    registerLabel.id = registerCheckbox.id + '-label';
    registerLabel.setAttribute('for', registerCheckbox.id);
    registerLabel.appendChild(document.createTextNode(' '));
    registerCell.appendChild(registerLabel);

    let idCell = document.createElement('td');
    idCell.setAttribute('id', 'id-cell-' + categoryId);
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

    row.appendChild(createEntryCountCell(categoryObject));

    let pointsCell = document.createElement('td');
    pointsCell.setAttribute('id', 'points-cell-' + categoryId);
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
    womenOnlyCell.setAttribute('id', 'women-only-cell-' + categoryId);
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

    let saturdayBody = document.getElementById('saturday-table-body');

    let sundayBody = document.getElementById('sunday-table-body');

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

async function submitPlayer() {

    let emailInput = document.getElementById('field-input-email');
    let phoneInput = document.getElementById('field-input-phone');
    let isValid = emailInput.reportValidity() && phoneInput.reportValidity();
    if (!isValid) {
        return;
    }
    console.log("Submitting player");
    let playerPayload = {
        'licenceNo': playerObject.licenceNo,
        'firstName': playerObject.firstName,
        'lastName': playerObject.lastName,
        'gender': playerObject.gender,
        'club': playerObject.club,
        'nbPoints': playerObject.nbPoints,
        'email': emailInput.value,
        'phone': phoneInput.value
    };
    try {
        let response = await fetch('/api/admin/players', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(playerPayload)
        })
        if (response.ok) {
            let responseData = await response.json();
            console.log(responseData);
            console.log("Player successfully added");
            return true;
        } else {
            let responseData = await response.json();
            console.error("Error:", responseData);
            window.alert('An unexpected error occured while trying to submit player:' + response.status + ' ' + JSON.stringify(responseData));
            return false;
        }

    } catch (error) {
        console.error("Error:", error);
        window.alert('An unexpected error occured while trying to submit player:' + error);
        return false;
    }
}

async function submitEntries() {
    let categoryIdsToRegister = [];
    let categoryIdsToDelete = [];

    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let checkbox = document.getElementById('register-checkbox-' + categoryId);
        if (checkbox.checked) {
            categoryIdsToRegister.push(categoryId);
        } else if (categoryId in playerObject['registeredEntries']) {
            categoryIdsToDelete.push(categoryId);
        }
    });

    let registerData = {
        'categoryIds': categoryIdsToRegister,
    };

    let deleteData = {
        'categoryIds': categoryIdsToDelete,
    };

    let registerResponse = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
    });

    if (!registerResponse.ok) {
        let data = await registerResponse.json();
        console.alert('An unexpected error occured while trying to register entries:' + registerResponse.status + ' ' + JSON.stringify(data));
        return false;
    }
    console.log('Successfully registered new entries');
    let data = await registerResponse.json();
    console.log(data);

    let deleteResponse = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deleteData),
    });

    if (!deleteResponse.ok) {
        let data = await deleteResponse.json();
        console.alert('An unexpected error occured while trying to delete entries:' + deleteResponse.status + ' ' + JSON.stringify(data));
        return false;
    }
    console.log('Successfully deleted entries');
    data = await deleteResponse.json();
    console.log(data);
    return true;
}

async function submitAll() {
    removeExitConfirmation();
    let playerSubmitted;
    if (playerObject['email'] === null) {
        playerSubmitted = await submitPlayer();
    } else {
        playerSubmitted = true;
    }
    if (playerSubmitted) {
        let entriesSubmitted = await submitEntries();
        if (entriesSubmitted) {
            console.log('Successfully submitted player and entries')
            window.location.href = "/admin/inscrits";
        }
    }
}

async function fetchAll() {
    let categoriesResponse = await fetch("/api/admin/categories");
    let playerResponse = await fetch("/api/admin/players/" + licenceNo);

    if (categoriesResponse.ok && playerResponse.ok) {
        categoriesData = await categoriesResponse.json();
        categoriesData = categoriesData["categories"];
        playerObject = await playerResponse.json();
        console.log(categoriesData);
        console.log(playerObject);
        setUpCategoriesTable();
        processPlayerInfo();
    } else if (!categoriesResponse.ok) {
        if (categoriesResponse.status == 400) {
            let data = await categoriesResponse.json();
            console.error("400 Bad Request: " + data);
        } else {
            console.error("Could not fetch categories: " + categoriesResponse.status);
        }
    } else {
        if (playerResponse.status == 400) {
            let data = await playerResponse.json();
            console.error("400 Bad Request: " + data);
        } else {
            console.error("Could not fetch player: " + playerResponse.status);
        }
    }
}

fetchAll().then(() => showContent());
