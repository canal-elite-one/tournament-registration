let playerObject;
let categoriesData;
let playerInDatabase;

const relevantPlayerFields = ['licenceNo', 'firstName', 'lastName', 'gender', 'club', 'nbPoints', 'email', 'phone'];
const relevantCategoriesFields = ['categoryId', 'color', 'entryCount', 'maxPlayers', 'overbookingPercentage', 'womenOnly', 'maxPoints', 'minPoints']

const categoryIdByColor = {};
const sameColor = {};

function initiallyRegistered(categoryId) {
    if (!('registeredEntries' in playerObject)) {
        return false;
    }
    return categoryId in playerObject['registeredEntries'];
}

/*
checkboxLinks contains behavioral links between checkboxes.
format: checkboxLinks = {parentcheckboxId: [{'parentState': bool, 'checkboxId': str, 'checked': bool, 'enabled': bool}...]}
'parentState' is the state of the parent checkbox that triggers the change, e.g.
    for color links, the disabling of same-color checkboxes is triggered only when the parent checkbox is checked, i.e. 'parentState' = true
'checkboxId' is the id of the child checkbox
'checked' is the target checked state of the child checkbox
'enabled' is the target enabled state of the child checkbox
for 'checked' and 'enabled', null means to revert to the initial state after processing player data.
*/
const checkboxLinks = {};

function addLink(parentcheckboxId, link) {
    if (!(parentcheckboxId in checkboxLinks)) {
        checkboxLinks[parentcheckboxId] = [];
    }
    checkboxLinks[parentcheckboxId].push(link);
}

function handleCheckbox(checkboxId, fromClick=false, targetChecked=null, targetEnabled=null) {
    let checkbox = document.getElementById(checkboxId);
    let stateChangeFlag = false;
    if (fromClick) {
        addExitConfirmation();
        stateChangeFlag = true;
    } else {
        targetChecked = (targetChecked === null) ? (initialChecked(checkbox)) : targetChecked;
        targetEnabled = (targetEnabled === null) ? !checkbox.disabled : targetEnabled;
        if (checkbox.checked != targetChecked) {
            checkbox.checked = targetChecked;
            stateChangeFlag = true;
        }
        console.log('checkbox.disabled: ' + checkbox.disabled);
        if (checkbox.disabled == targetEnabled) {
            if (targetEnabled) {
                checkbox.removeAttribute('disabled');
                checkbox.parentElement.classList.remove('disabled-cell');
            } else {
                checkbox.setAttribute('disabled', '');
                checkbox.parentElement.classList.add('disabled-cell');
            }
            stateChangeFlag = true;
        }
    }
    console.log('stateChangeFlag: ' + stateChangeFlag);
    // only process links if the state of the checkbox has changed
    if (stateChangeFlag) {
        for (const i in checkboxLinks[checkboxId]) {
            let checkboxLink = checkboxLinks[checkboxId][i];
            if (checkboxLink['parentState'] == checkbox.checked) {
                handleCheckbox(checkboxLink['checkboxId'], false, checkboxLink['checked'], checkboxLink['enabled']);
            }
        }
    }
    if (fromClick) { recomputePaymentStatus(); }
}

function initialChecked(checkbox) {
    let categoryId = checkbox.id.slice(-1);
    if (initiallyRegistered(categoryId)) {
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
    if (initiallyRegistered(categoryId)) {
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
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        let presentCheckbox = document.getElementById('present-checkbox-' + categoryId);
        let paidCheckbox = document.getElementById('paid-checkbox-' + categoryId);
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

    document.getElementById('register-total').firstChild.nodeValue = paymentStatus['registerTotal'];
    document.getElementById('present-total').firstChild.nodeValue = paymentStatus['presentTotal'];
    document.getElementById('paid-total').firstChild.nodeValue = paymentStatus['paidTotal'];
    let dueTotalValue = paymentStatus['presentTotal'] - playerObject['paymentStatus']['totalActualPaid'];
    let dueTotalCell = document.getElementById('due-total');
    dueTotalCell.firstChild.nodeValue = dueTotalValue;
    dueTotalCell.style.backgroundColor = dueTotalValue > 0 ? 'hsl(25, 100%, 80%)' : 'hsl(140, 100%, 80%)';

    document.getElementById('actual-total-field').value = paymentStatus['currentActualTotal'];
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
        let bibNoCell = document.getElementById('bib-no-cell');
        bibNoCell.innerHTML = data['bibNo'];
        bibNoCell.style.backgroundColor = 'white';
    } else {
        adminHandleBadResponse(response);
    }
}

function processPlayerInfo() {
    let playerInfoTable = document.getElementById('player-info-table');

    takeCheckboxStateSnapshot();

    if ('registeredEntries' in playerObject) {
        for (const categoryId in playerObject['registeredEntries']) {
            handleCheckbox(checkboxId='register-checkbox-' + categoryId, fromClick=false, targetChecked=true, targetEnabled=true);
        }
    }

    removeExitConfirmation();
    recomputePaymentStatus();

    if (showBib) {
        let row = document.createElement('tr');
        row.appendChild(document.createElement('td').appendChild(document.createTextNode('N° dossard')));
        let bibNoCell = document.createElement('td');
        bibNoCell.setAttribute('id', 'bib-no-cell');

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

    document.getElementById('previous-actual-total').firstChild.nodeValue = playerObject['paymentStatus']['totalActualPaid'];

    document.getElementById('delete-player-button').appendChild(deleteButtonText);
}

function createCheckboxCell(categoryId, checkboxType) {
    let cell = document.createElement('td');
    cell.setAttribute('id', checkboxType + '-cell-' + categoryId);
    let checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = checkboxType + '-checkbox-' + categoryId;
    checkbox.setAttribute('data-checkbox-type', checkboxType)
    checkbox.setAttribute('oninput', `handleCheckbox('${checkbox.id}', true)`);
    cell.appendChild(checkbox);
    let label = document.createElement('label');
    label.id = checkbox.id + '-label';
    label.setAttribute('for', checkbox.id);
    label.appendChild(document.createTextNode(' '));
    cell.appendChild(label);

    if (checkboxType != 'register') {
        cell.classList.add('disabled-cell');
        checkbox.setAttribute('disabled', '');
    }

    if (checkboxType == 'register') {
        const shortLinkArray = [['present', true], ['present', false], ['absent', true], ['absent', false]];
        shortLinkArray.forEach(function (shortLink) {
            let [childCheckboxType, flag] = shortLink;
            addLink(
                checkbox.id,
                {'parentState': flag, 'checkboxId': childCheckboxType + '-checkbox-' + categoryId, 'checked': flag ? null : false, 'enabled': flag}
            );
        });
    } else if (checkboxType == 'present') {
        addLink(
            checkbox.id,
            {'parentState': true, 'checkboxId': 'paid-checkbox-' + categoryId, 'checked': null, 'enabled': true}
        );
        addLink(
            checkbox.id,
            {'parentState': false, 'checkboxId': 'paid-checkbox-' + categoryId, 'checked': false, 'enabled': false}
        );
        addLink(
            checkbox.id,
            {'parentState': true, 'checkboxId': 'absent-checkbox-' + categoryId, 'checked': false, 'enabled': true}
        );
    } else if (checkboxType == 'absent') {
        addLink(
            checkbox.id,
            {'parentState': true, 'checkboxId': 'present-checkbox-' + categoryId, 'checked': false, 'enabled': true}
        );
    }
    return cell;
}

function updateEntryCountCell(categoryObject, entryCountCell=null) {
    let categoryId = categoryObject['categoryId'];

    let entryCount = categoryObject['entryCount'];
    let maxPlayers = categoryObject['maxPlayers'];
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));

    let isRegistered = initiallyRegistered(categoryId)
    let relevantEntryCount = isRegistered ? playerObject['registeredEntries'][categoryId]['rank'] : entryCount;

    let cellString = isRegistered ? `${relevantEntryCount + 1}e` : `${relevantEntryCount} inscrits`;

    let entryCountColor;

    if (relevantEntryCount < maxPlayers) {
        entryCountColor = 'hsl(140, 100%, 80%)';
    } else if (relevantEntryCount > maxOverbooked) {
        entryCountColor = 'hsl(25, 100%, 80%)';
    } else {
        entryCountColor = 'hsl(60, 100%, 80%)';
    }

    if (entryCountCell === null) {
        entryCountCell = document.getElementById('entry-count-cell-' + categoryId);
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
    idCell.setAttribute('id', 'id-cell-' + categoryId);
    idCell.appendChild(document.createTextNode(categoryId));
    row.appendChild(idCell);

    let color = categoryObject['color'];

    if (color !== null) {
        if (color in categoryIdByColor) {
            addLink(
                'register-checkbox-' + categoryIdByColor[color],
                {'parentState': true, 'checkboxId': 'register-checkbox-' + categoryId, 'checked': false, 'enabled': null}
            );
            addLink(
                'register-checkbox-' + categoryId,
                {'parentState': true, 'checkboxId': 'register-checkbox-' + categoryIdByColor[color], 'checked': false, 'enabled': null}
            );
            sameColor[categoryId] = categoryIdByColor[color];
            sameColor[categoryIdByColor[color]] = categoryId;
        } else { categoryIdByColor[color] = categoryId; }
        idCell.style.backgroundColor = color;
    };

    let entryCountCell = document.createElement('td');
    entryCountCell.setAttribute('id', 'entry-count-cell-' + categoryId);
    row.appendChild(entryCountCell);

    updateEntryCountCell(categoryObject, entryCountCell);

    let maxPlayersCell = document.createElement('td');
    maxPlayersCell.setAttribute('id', 'max-players-cell-' + categoryId);
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));
    maxPlayersCell.appendChild(document.createTextNode(categoryObject['maxPlayers'] + ' (' + maxOverbooked + ')'));
    row.appendChild(maxPlayersCell);

    let pointsCell = document.createElement('td');
    pointsCell.setAttribute('id', 'points-cell-' + categoryId);
    let maxPoints = categoryObject['maxPoints'];
    let minPoints = categoryObject['minPoints'];
    let pointsString;
    if (maxPoints < 4000) {
        pointsString = '< ' + maxPoints;
    } else if (minPoints > 0) {
        pointsString = '> ' + minPoints;
    } else { pointsString = '-'}

    if (playerObject['nbPoints'] < minPoints || playerObject['nbPoints'] > maxPoints) {
        pointsCell.style.backgroundColor = 'red';
        registerCell.classList.add('disabled-cell');
        registerCell.firstChild.setAttribute('disabled', '');
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
        registerCell.classList.add('disabled-cell');
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
    console.log("Submitting player");
    let contactPayload = {
        'email': `${playerObject['firstName'].toLowerCase()}@samplehost.com`,
        'phone': '+33000000000'
    };
    let response = await fetch(`/api/admin/players/${licenceNo}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(contactPayload)
    })
    if (response.ok) {
        return true;
    } else {
        adminHandleBadResponse(response);
        return false;
    }
}

async function registerEntries(registerPayload) {
    let response = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerPayload),
    });

    if (response.ok) {
        return true;
    } else {
        adminHandleBadResponse(response);
        return false;
    }
}

async function submitChanges() {
    removeExitConfirmation();
    let totalActualPaid = parseInt(document.getElementById('actual-total-field').value) + playerObject['paymentStatus']['totalActualPaid'];
    let registerPayload = {'entries': [], 'totalActualPaid': totalActualPaid};
    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        if (registerCheckbox.checked) {
            let presentCheckbox = document.getElementById('present-checkbox-' + categoryId);
            let absentCheckbox = document.getElementById('absent-checkbox-' + categoryId);
            let paidCheckbox = document.getElementById('paid-checkbox-' + categoryId);
            registerPayload['entries'].push({
                'categoryId': categoryId,
                'markedAsPresent': presentCheckbox.checked ? true : (absentCheckbox.checked ? false : null),
                'markedAsPaid': paidCheckbox.checked,
            });
        }
    });

    if (!playerInDatabase) {
        let success = await submitPlayer();
        if (!success) { return; }
    }
    console.log('Submitting changes');
    let success = await registerEntries(registerPayload);
    if (success) {
        console.log('Successfully submitted changes');
        window.location.reload();
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
        playerInDatabase = (playerObject['email'] !== null);
        setUpCategoriesTable();
        processPlayerInfo();
        takeCheckboxStateSnapshot();
    } else if (!categoriesResponse.ok) {
        adminHandleBadResponse(categoriesResponse);
    } else {
        adminHandleBadResponse(playerResponse);
    }
}

fetchAll().then(() => {
    showContent();
});
