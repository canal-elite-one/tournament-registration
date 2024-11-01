let playerObject;
let categoriesData;

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

function handleCheckbox(categoryId) {
    addExitConfirmation();
    let checkbox = document.getElementById('register-checkbox-' + categoryId);

    if (!(categoryId in sameColor)) {
        let absentCell = document.getElementById('absent-cell-' + categoryId);
        let absentCheckbox = document.getElementById('absent-checkbox-' + categoryId);
        if (checkbox.checked) {
            absentCheckbox.removeAttribute('disabled');
            absentCell.classList.remove('disabled-cell');
        } else {
            absentCheckbox.checked = false;
            absentCheckbox.setAttribute('disabled', '');
            absentCell.classList.add('disabled-cell');
        }
        if (initiallyRegistered(categoryId) && !checkbox.checked) {
            let label = document.getElementById(checkbox.id + '-label')
            label.firstChild.data = '\u26A0';
        } else if (initiallyRegistered(categoryId) && checkbox.checked) {
            let label = document.getElementById(checkbox.id + '-label')
            label.firstChild.data = ' ';
        }
        return;
    }

    let otherCheckbox = document.getElementById('register-checkbox-' + sameColor[categoryId]);
    if (checkbox.checked) {
        otherCheckbox.checked = false;
    }
    let absentCell = document.getElementById('absent-cell-' + categoryId);
    let absentCheckbox = document.getElementById('absent-checkbox-' + categoryId);
    if (checkbox.checked) {
        absentCheckbox.removeAttribute('disabled');
        absentCell.classList.remove('disabled-cell');
    } else {
        absentCheckbox.checked = false;
        absentCheckbox.setAttribute('disabled', '');
        absentCell.classList.add('disabled-cell');
    }
    let otherAbsentCell = document.getElementById('absent-cell-' + sameColor[categoryId]);
    let otherAbsentCheckbox = document.getElementById('absent-checkbox-' + sameColor[categoryId]);
    if (otherCheckbox.checked) {
        otherAbsentCheckbox.removeAttribute('disabled');
        otherAbsentCell.classList.remove('disabled-cell');
    } else {
        otherAbsentCheckbox.checked = false;
        otherAbsentCheckbox.setAttribute('disabled', '');
        otherAbsentCell.classList.add('disabled-cell');
    }
    if (initiallyRegistered(categoryId)) {
        let label = document.getElementById(checkbox.id + '-label')
        if (checkbox.checked) {
            label.firstChild.data = ' ';
        } else {
            label.firstChild.data = '\u26A0';
        }
    }
    if (initiallyRegistered(sameColor[categoryId])) {
        let label = document.getElementById(otherCheckbox.id + '-label')
        if (otherCheckbox.checked) {
            label.firstChild.data = ' ';
        } else {
            label.firstChild.data = '\u26A0';
        }
    }
}

function processPlayerInfo() {
    document.getElementById("licence-no-cell").value = playerObject.licenceNo;
    document.getElementById("first-name-cell").value = playerObject.firstName;
    document.getElementById("last-name-cell").value = playerObject.lastName;
    document.getElementById("gender-cell").value = playerObject.gender;
    document.getElementById("club-cell").value = playerObject.club;
    document.getElementById("points-cell").value = playerObject.nbPoints;
    let emailInput = document.getElementById("email-cell")
    emailInput.value = playerObject.email;
    emailInput.setAttribute('onchange', 'addExitConfirmation()');
    let phoneInput = document.getElementById("phone-cell")
    phoneInput.value = playerObject.phone;
    phoneInput.setAttribute('onchange', 'addExitConfirmation()');

    let deleteButtonText;
    if (playerObject['gender'] === 'F') {
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

    if (initiallyRegistered(categoryId)) {
        rank = playerObject['registeredEntries'][categoryId]['rank'] + 1;
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

    registerCell.appendChild(registerCheckbox);
    let registerLabel = document.createElement('label');
    registerLabel.id = registerCheckbox.id + '-label';
    registerLabel.setAttribute('for', registerCheckbox.id);
    registerLabel.appendChild(document.createTextNode(' '));
    registerCell.appendChild(registerLabel);

    let absentCell = document.createElement('td');
    absentCell.setAttribute('id', 'absent-cell-' + categoryId);
    let absentCheckbox = document.createElement('input');
    absentCheckbox.type = 'checkbox';
    absentCheckbox.id = 'absent-checkbox-' + categoryId;
    absentCheckbox.setAttribute('oninput', 'addExitConfirmation()');
    absentCell.appendChild(absentCheckbox);

    if (initiallyRegistered(categoryId)) {
        registerCheckbox.checked = true;
        if (playerObject['registeredEntries'][categoryId]['markedAsPresent'] === false) {
            absentCheckbox.checked = true;
        }
    } else {
        absentCheckbox.setAttribute('disabled', '');
        absentCell.classList.add('disabled-cell');
    }

    let idCell = document.createElement('td');
    idCell.setAttribute('id', 'id-cell-' + categoryId);
    idCell.appendChild(document.createTextNode(categoryId));
    row.appendChild(idCell);

    let color = categoryObject['color'];

    if (color !== null) {
        if (color in categoryIdByColor) {
            sameColor[categoryId] = categoryIdByColor[color];
            sameColor[categoryIdByColor[color]] = categoryId;
        } else { categoryIdByColor[color] = categoryId; }
        idCell.style.backgroundColor = color;
    }

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
    } else { pointsString = '-'}

    if (playerObject['nbPoints'] < minPoints || playerObject['nbPoints'] > maxPoints) {
        pointsCell.style.backgroundColor = 'red';
        registerCell.classList.add('disabled-cell');
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
    if (categoryObject['womenOnly'] && playerObject['gender'] === 'M') {
        womenOnlyCell.style.backgroundColor = 'red';
        registerCell.classList.add('disabled-cell');
        registerCheckbox.setAttribute('disabled', '');
    }
    row.appendChild(registerCell);
    row.appendChild(absentCell);

    return row;
}

function setUpCategoriesTable() {
    const saturdayCategories = [];
    const sundayCategories = [];
    categoriesData.forEach(function (categoryObject)
    {
        let categoryDay = new Date(categoryObject['startTime']);
        if (categoryDay.getDay() === 6) {
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

    let emailInput = document.getElementById('email-cell');
    let phoneInput = document.getElementById('phone-cell');
    let isValid = emailInput.reportValidity() && phoneInput.reportValidity();
    if (!isValid) {
        return;
    }
    console.log("Submitting player");
    let contactPayload = {
        'email': emailInput.value,
        'phone': phoneInput.value
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

async function submitEntries() {
    let registerData = {
        'totalActualPaid': 0,
        'entries': []
    };

    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        let absentCheckbox = document.getElementById('absent-checkbox-' + categoryId);
        if (registerCheckbox.checked) {
            let entry = {
                'categoryId': categoryId,
                'markedAsPresent': absentCheckbox.checked ? false : null,
                'markedAsPaid': false,
            };
            registerData['entries'].push(entry);
        }
    });

    let registerResponse = await fetch('/api/admin/entries/' + licenceNo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
    });

    if (!registerResponse.ok) {
        adminHandleBadResponse(registerResponse);
        return false;
    }
    return true;
}

async function submitAll() {
    removeExitConfirmation();

    let emailInput = document.getElementById('email-cell');
    let phoneInput = document.getElementById('phone-cell');

    console.log(emailInput.value, playerObject['email'], phoneInput.value, playerObject['phone'])
    let playerSubmitted = (playerObject['email'] !== emailInput.value || playerObject['phone'] !== phoneInput.value) ? await submitPlayer() : true;

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
        adminHandleBadResponse(categoriesResponse)
    } else {
        adminHandleBadResponse(playerResponse)
    }
}

fetchAll().then(() => showContent());
