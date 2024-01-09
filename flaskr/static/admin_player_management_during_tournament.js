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
let playerInDatabase;

const relevantPlayerFields = ['licenceNo', 'firstName', 'lastName', 'gender', 'club', 'nbPoints', 'email', 'phone'];
const relevantCategoriesFields = ['categoryId', 'color', 'entryCount', 'maxPlayers', 'overbookingPercentage', 'womenOnly', 'maxPoints', 'minPoints']

const categoryIdByColor = {};
const sameColor = {};

function initialChecked(checkbox) {
    let categoryId = checkbox.id.slice(-1);
    if (categoryId in playerObject['registeredEntries']) {
        if (checkbox.getAttribute('data-checkbox-type') == 'register') {
            return true;
        } else if (checkbox.getAttribute('data-checkbox-type') == 'present') {
            return playerObject['registeredEntries'][categoryId]['markedAsPresent'];
        } else if (checkbox.getAttribute('data-checkbox-type') == 'absent') {
            return playerObject['registeredEntries'][categoryId]['markedAsPresent'] === false;
        } else {
            return playerObject['registeredEntries'][categoryId]['markedAsPaid'];
        }
    } else {
        return false;
    }
}

function currentFee(categoryId) {
    if (categoryId in playerObject['registeredEntries']) {
        return playerObject['registeredEntries'][categoryId]['entryFee'];
    } else {
        let categoryObject = categoriesData.find(category => category['categoryId'] == categoryId);
        return categoryObject['currentFee'];
    }
}

function recomputePaymentStatus() {
    const paymentStatus = {
        'registerTotal': 0,
        'presentTotal': 0,
        'paidTotal': 0,
    };

    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register_checkbox_' + categoryId);
        let presentCheckbox = document.getElementById('present_checkbox_' + categoryId);
        let paidCheckbox = document.getElementById('paid_checkbox_' + categoryId);
        if (registerCheckbox.checked) {
            paymentStatus['registerTotal'] += currentFee(categoryId);
            if (presentCheckbox.checked) {
                paymentStatus['presentTotal'] += currentFee(categoryId);
            }
            if (paidCheckbox.checked) {
                paymentStatus['paidTotal'] += currentFee(categoryId);
            }
        }
        paymentStatus['currentActualTotal'] = paymentStatus['paidTotal'] - playerObject['paymentStatus']['totalActualPaid'];
    });

    document.getElementById('register_total').firstChild.nodeValue = paymentStatus['registerTotal'];
    document.getElementById('present_total').firstChild.nodeValue = paymentStatus['presentTotal'];
    document.getElementById('paid_total').firstChild.nodeValue = paymentStatus['paidTotal'];
    let due_total_value = paymentStatus['presentTotal'] - playerObject['paymentStatus']['totalActualPaid'];
    let due_total_cell = document.getElementById('due_total');
    due_total_cell.firstChild.nodeValue = due_total_value;
    due_total_cell.style.backgroundColor = due_total_value > 0 ? 'hsl(25, 100%, 80%)' : 'hsl(140, 100%, 80%)';

    document.getElementById('actual_total_field').value = paymentStatus['currentActualTotal'];
}


function ableCheckbox(checkbox, able) {
    if (checkbox == null) { return; }

    if (able) {
        if (!(checkbox.getAttribute('data-checkbox-type') == 'paid' && initialChecked(checkbox))) {
            checkbox.removeAttribute('disabled');
            checkbox.parentElement.style.backgroundColor = 'white';
        }
        checkbox.checked = initialChecked(checkbox);
        onCheckboxChange(checkbox);
    } else {
        checkbox.setAttribute('disabled', '');
        checkbox.checked = false;
        checkbox.parentElement.style.backgroundColor = '#d3d3d3';
        onCheckboxChange(checkbox);
    }
}

function onCheckboxChange(checkbox) {
    let checkboxType = checkbox.getAttribute('data-checkbox-type');
    let categoryId = checkbox.id.slice(-1);

    let checkboxLabel = document.getElementById(checkbox.id + '_label');
    if (!checkbox.checked && initialChecked(checkbox)) {
        checkboxLabel.firstChild.nodeValue = ' \u26A0';
    } else {
        checkboxLabel.firstChild.nodeValue = ' ';
    }

    let childCheckboxes = [];
    if (checkboxType == 'register') {
        childCheckboxes = [
            document.getElementById('present_checkbox_' + categoryId),
            document.getElementById('absent_checkbox_' + categoryId),
        ];
    } else if (checkboxType == 'present') {
        childCheckboxes = [document.getElementById('paid_checkbox_' + categoryId)];
    } else {
        return;
    }

    childCheckboxes.forEach(childCheckbox => ableCheckbox(childCheckbox, checkbox.checked));
}

function handlePresentAbsent(checkbox) {
    let categoryId = checkbox.id.slice(-1);
    let checkboxType = checkbox.getAttribute('data-checkbox-type');
    onCheckboxChange(checkbox);

    if (checkbox.checked) {
        let otherCheckbox = document.getElementById((checkboxType == 'absent' ? 'present' : 'absent') +'_checkbox_' + categoryId);
        otherCheckbox.checked = false;
        onCheckboxChange(otherCheckbox);
    }
}


function handleColor(checkbox) {
    let categoryId = checkbox.id.slice(-1);
    onCheckboxChange(checkbox);

    if (categoryId in sameColor) {
        let otherCheckbox = document.getElementById('register_checkbox_' + sameColor[categoryId]);
        if (checkbox.checked) {
            otherCheckbox.checked = false;
            onCheckboxChange(otherCheckbox);
        }
    }
}

function onclickCheckboxWrapper(checkboxType, categoryId) {
    let checkbox = document.getElementById(checkboxType + '_checkbox_' + categoryId);
    if (checkboxType == 'register') {
        handleColor(checkbox);
    } else if (checkboxType == 'present' || checkboxType == 'absent') {
        handlePresentAbsent(checkbox);
    } else {
        onCheckboxChange(checkbox);
    }
    recomputePaymentStatus();
    addExitConfirmation();
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
            console.log('Successfully deleted player with licence n°:' + licenceNo);
            window.location.href = "/admin/inscrits";
        });
    }
}

async function generateBibNo() {
    if (!playerInDatabase) {
        let success = await submitPlayer();
        if (!success) { return; }
        else { playerInDatabase = true; }
    }

    response = await fetch('/api/admin/bibs/' + licenceNo, {method: 'PUT'});
    if (response.ok) {
        let data = await response.json();
        console.log('Successfully generated bib number');
        let bibNoCell = document.getElementById('bib_no_cell');
        bibNoCell.innerHTML = data['bibNo'];
        bibNoCell.style.backgroundColor = 'white';
    } else {
        let data = await response.json();
        window.alert('An unexpected error occured while trying to generate bib number:' + response.status + ' ' + JSON.stringify(data));
    }
}

function processPlayerInfo() {
    let playerInfoTable = document.getElementById('player_info_table');

    for (const categoryId in playerObject['registeredEntries']) {
        let registerCheckbox = document.getElementById('register_checkbox_' + categoryId);
        registerCheckbox.checked = true;
        onclickCheckboxWrapper('register', categoryId);
    }

    recomputePaymentStatus();

    if (showBib) {
        let row = document.createElement('tr');
        row.appendChild(document.createElement('td').appendChild(document.createTextNode('N° dossard')));
        let bibNoCell = document.createElement('td');
        bibNoCell.setAttribute('id', 'bib_no_cell');

        if (playerObject['bibNo'] === null) {
            let generateBibNoButton = document.createElement('button');
            generateBibNoButton.setAttribute('onclick', 'generateBibNo()');
            generateBibNoButton.appendChild(document.createTextNode('Générer N° dossard'));
            bibNoCell.appendChild(generateBibNoButton);
            bibNoCell.style.backgroundColor = 'red';
        } else {
            bibNoCell.appendChild(document.createTextNode(playerObject['bibNo']));
        }
        row.appendChild(bibNoCell);
        playerInfoTable.appendChild(row);
    }

    relevantPlayerFields.forEach(
        function(fieldName) {
            let row = document.createElement('tr');
            let fieldNameCell = document.createElement('td');
            fieldNameCell.appendChild(document.createTextNode(enToFr[fieldName]));
            row.appendChild(fieldNameCell);
            let fieldValueCell = document.createElement('td');
            let fieldString = playerObject[fieldName] || (fieldName == 'email' ? `${playerObject['firstName'].toLowerCase()}@samplehost.com` : '+33000000000');
            fieldValueCell.appendChild(document.createTextNode(fieldString));
            row.appendChild(fieldValueCell);
            playerInfoTable.appendChild(row);
        });
    let deleteButtonText;
    if (playerObject['gender'] == 'F') {
        deleteButtonText = document.createTextNode('Supprimer compétitrice \uD83D\uDDD1');
    } else {
        deleteButtonText = document.createTextNode('Supprimer compétiteur \uD83D\uDDD1');
    }

    document.getElementById('previous_actual_total').firstChild.nodeValue = playerObject['paymentStatus']['totalActualPaid'];

    document.getElementById('delete_player_button').appendChild(deleteButtonText);
}

function createCheckboxCell(categoryId, checkboxType) {
    let cell = document.createElement('td');
    cell.setAttribute('id', checkboxType + '_cell_' + categoryId);
    let checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = checkboxType + '_checkbox_' + categoryId;
    checkbox.setAttribute('data-checkbox-type', checkboxType)
    checkbox.setAttribute('oninput', 'onclickCheckboxWrapper("' + checkboxType + '", "' + categoryId + '")');
    cell.appendChild(checkbox);
    let label = document.createElement('label');
    label.id = checkbox.id + '_label';
    label.setAttribute('for', checkbox.id);
    label.appendChild(document.createTextNode(' '));
    cell.appendChild(label);

    if (checkboxType != 'register') {
        cell.style.backgroundColor = '#d3d3d3';
        checkbox.setAttribute('disabled', '');
    }

    return cell;
}

function updateEntryCountCell(categoryObject, entryCountCell=null) {
    let categoryId = categoryObject['categoryId'];

    let entryCount = categoryObject['entryCount'];
    let maxPlayers = categoryObject['maxPlayers'];
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));

    let rankOrCount = categoryId in playerObject['registeredEntries']
    let relevantEntryCount = rankOrCount ? playerObject['registeredEntries'][categoryId]['rank'] + 1 : entryCount;

    let cellString = rankOrCount ? `${relevantEntryCount + 1}e` : `${relevantEntryCount} inscrits`;

    let entryCountColor;

    if (relevantEntryCount < maxPlayers) {
        entryCountColor = 'hsl(140, 100%, 80%)';
    } else if (relevantEntryCount > maxOverbooked) {
        entryCountColor = 'hsl(25, 100%, 80%)';
    } else {
        entryCountColor = 'hsl(60, 100%, 80%)';
    }

    if (entryCountCell === null) {
        entryCountCell = document.getElementById('entry_count_cell_' + categoryId);
    }
    entryCountCell.innerHTML = cellString;

    entryCountCell.style.backgroundColor = entryCountColor;
}

function createCategoryRow(categoryObject) {
    let row = document.createElement('tr');
    let categoryId = categoryObject['categoryId'];

    let registerCell = createCheckboxCell(categoryId, 'register');
    let presentCell = createCheckboxCell(categoryId, 'present');
    let absentCell = createCheckboxCell(categoryId, 'absent');
    let paidCell = createCheckboxCell(categoryId, 'paid');

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

    let entryCountCell = document.createElement('td');
    entryCountCell.setAttribute('id', 'entry_count_cell_' + categoryId);
    row.appendChild(entryCountCell);

    updateEntryCountCell(categoryObject, entryCountCell);

    let maxPlayersCell = document.createElement('td');
    maxPlayersCell.setAttribute('id', 'max_players_cell_' + categoryId);
    maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));
    maxPlayersCell.appendChild(document.createTextNode(categoryObject['maxPlayers'] + ' (' + maxOverbooked + ')'));
    row.appendChild(maxPlayersCell);

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
        registerCell.style.backgroundColor = '#d3d3d3';
        registerCell.firstChild.setAttribute('disabled', '');
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
        registerCell.style.backgroundColor = '#d3d3d3';
        registerCell.firstChild.setAttribute('disabled', '');
    }

    row.appendChild(registerCell);
    row.appendChild(presentCell);
    row.appendChild(absentCell);
    row.appendChild(paidCell);

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

async function submitPlayer() {
    console.log("Submitting player");
    let playerPayload = {
        'licenceNo': playerObject.licenceNo,
        'firstName': playerObject.firstName,
        'lastName': playerObject.lastName,
        'gender': playerObject.gender,
        'club': playerObject.club,
        'nbPoints': playerObject.nbPoints,
        'email': `${playerObject['firstName'].toLowerCase()}@samplehost.com`,
        'phone': '+33000000000'
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

async function deleteEntries(categoryIds) {
    let response = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({"categoryIds": categoryIds}),
    });

    if (response.ok) {
        let data = await response.json();
        console.log('Successfully deleted entries', data);
        return true;
    } else {
        let data = await response.json();
        window.alert('An unexpected error occured while trying to delete entries:' + response.status + ' ' + JSON.stringify(data));
        return false;
    }
}

async function registerEntries(categoryIds) {
    let response = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({"categoryIds": categoryIds}),
    });

    if (response.ok) {
        let data = await response.json();
        console.log('Successfully registered new entries', data);
        return true;
    } else {
        let data = await response.json();
        window.alert('An unexpected error occured while trying to registered entries:' + response.status + ' ' + JSON.stringify(data));
        return false;
    }
}

async function markAsPresent(categoryIdsPresence) {
    let response = await fetch('/api/admin/present/' + licenceNo, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "categoryIdsPresence": categoryIdsPresence,
        }),
    });

    if (response.ok) {
        let data = await response.json();
        console.log('Successfully marked/unmarked entries as present', data);
        return true;
    } else {
        let data = await response.json();
        window.alert('An unexpected error occured while trying to mark/unmark entries as present:' + response.status + ' ' + JSON.stringify(data));
        return false;
    }
}

async function processPayments(categoryIds, totalActualPaid) {
    let response = await fetch('/api/admin/pay/' + licenceNo, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "categoryIds": categoryIds,
            "totalActualPaid": totalActualPaid,
        }),
    });

    if (response.ok) {
        let data = await response.json();
        console.log('Successfully processed payments', data);
        return true;
    } else {
        let data = await response.json();
        window.alert('An unexpected error occured while trying to process payments:' + response.status + ' ' + JSON.stringify(data));
        return false;
    }
}

async function submitChanges() {
    removeExitConfirmation();
    const categoryIdsToRegister = [];
    const categoryIdsToDelete = [];
    const categoryIdsPresence = {};
    const categoryIdsToMarkAsPaid = [];

    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register_checkbox_' + categoryId);
        let presentCheckbox = document.getElementById('present_checkbox_' + categoryId);
        let absentCheckbox = document.getElementById('absent_checkbox_' + categoryId);
        let paidCheckbox = document.getElementById('paid_checkbox_' + categoryId);
        if (registerCheckbox.checked) {
            categoryIdsPresence[categoryId] = presentCheckbox.checked ? true : (absentCheckbox.checked ? false : null);
            if (paidCheckbox.checked) {
                categoryIdsToMarkAsPaid.push(categoryId);
            }
            categoryIdsToRegister.push(categoryId);
        } else if (initialChecked(registerCheckbox)) {
            categoryIdsToDelete.push(categoryId);
        }
    });

    let totalActualPaid = parseInt(document.getElementById('actual_total_field').value) + playerObject['paymentStatus']['totalActualPaid'];

    try {
        if (!playerInDatabase) {
            let success = await submitPlayer();
            if (!success) { return; }
        }
        console.log('Submitting changes');
        let success = await deleteEntries(categoryIdsToDelete);
        if (!success) { return; }
        success = await registerEntries(categoryIdsToRegister);
        if (!success) { return; }
        success = await markAsPresent(categoryIdsPresence);
        if (!success) { return; }
        success = await processPayments(categoryIdsToMarkAsPaid, totalActualPaid);
        if (success) {
            console.log('Successfully submitted changes');
            window.location.reload();
        }
    } catch (error) {
        window.alert('An unexpected error occured while trying to submit changes:' + error);
        return;
    }
}

async function fetchAll() {
    let categoriesResponse = await fetch("/api/public/categories");
    let playerResponse = await fetch("/api/admin/players/" + licenceNo);

    if (categoriesResponse.ok && playerResponse.ok) {
        categoriesData = await categoriesResponse.json();
        categoriesData = categoriesData["categories"];
        playerObject = await playerResponse.json();
        console.log(categoriesData);
        console.log(playerObject);
        playerInDatabase = !(playerObject['email'] === null);
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

fetchAll().then(() => {
    showContent();
});
