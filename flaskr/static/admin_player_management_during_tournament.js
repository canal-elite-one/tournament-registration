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
let paymentStatus = {
    'register_total': 0,
    'present_total': 0,
    'paid_total': 0,
};

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

function processFeeChange(checkbox, futureChecked, oppositeFactor=1) {
    let categoryId = checkbox.id.slice(-1);
    let checkboxType = checkbox.getAttribute('data-checkbox-type');
    if (futureChecked == checkbox.checked) { return; }
    else if (futureChecked) {
        paymentStatus[checkboxType + '_total'] += currentFee(categoryId) * oppositeFactor;
    } else {
        paymentStatus[checkboxType + '_total'] -= currentFee(categoryId) * oppositeFactor;
    }
    document.getElementById(checkboxType + '_total').firstChild.nodeValue = paymentStatus[checkboxType + '_total'];
    if (checkboxType == 'paid') {
        currentPaymentField.value = paymentStatus['paid_total'] - playerObject['paymentStatus']['totalActualPaid'];
    } else if (checkboxType == 'present') {
        currentPaymentField.setAttribute('max', paymentStatus['present_total'] - playerObject['paymentStatus']['totalActualPaid']);
    }
}

function disableCheckbox(checkbox) {
    if (checkbox == null) { return; }
    checkbox.setAttribute('disabled', '');
    processFeeChange(checkbox, false);
    checkbox.checked = false;
    checkbox.parentElement.style.backgroundColor = '#d3d3d3';
    onCheckboxChange(checkbox);
}

function enableCheckbox(checkbox) {
    if (checkbox == null) { return; }
    if (!(checkbox.getAttribute('data-checkbox-type') == 'paid' && initialChecked(checkbox))) {
        checkbox.removeAttribute('disabled');
        checkbox.parentElement.style.backgroundColor = 'white';
    }
    processFeeChange(checkbox, initialChecked(checkbox));
    checkbox.checked = initialChecked(checkbox);
    onCheckboxChange(checkbox);
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

    let childCheckbox = null;
    if (checkboxType == 'register') {
        childCheckbox = document.getElementById('present_checkbox_' + categoryId);
    } else if (checkboxType == 'present') {
        childCheckbox = document.getElementById('paid_checkbox_' + categoryId);
    } else {
        return;
    }
    if (checkbox.checked) {
        enableCheckbox(childCheckbox);
    } else {
        disableCheckbox(childCheckbox);
    }
}

function handleColor(checkbox) {
    let categoryId = checkbox.id.slice(-1);
    onCheckboxChange(checkbox);

    if (categoryId in sameColor) {
        let otherCheckbox = document.getElementById('register_checkbox_' + sameColor[categoryId]);
        if (checkbox.checked) {
            processFeeChange(otherCheckbox, false);
            otherCheckbox.checked = false;
            onCheckboxChange(otherCheckbox);
        }
    }
}

function onclickCheckboxWrapper(checkboxType, categoryId) {
    let checkbox = document.getElementById(checkboxType + '_checkbox_' + categoryId);
    processFeeChange(checkbox, !checkbox.checked, -1);
    if (checkboxType == 'register') {
        handleColor(checkbox);
    } else {
        onCheckboxChange(checkbox);
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
    console.log(playerObject);
    let playerInfoTable = document.getElementById('player_info_table');

    document.getElementById('register_total').firstChild.nodeValue = playerObject['paymentStatus']['totalRegistered'];
    document.getElementById('present_total').firstChild.nodeValue = playerObject['paymentStatus']['totalPresent'];
    document.getElementById('paid_total').firstChild.nodeValue = playerObject['paymentStatus']['totalPaid'];
    document.getElementById('previous_actual_total').firstChild.nodeValue = playerObject['paymentStatus']['totalActualPaid'];
    currentPaymentField = document.getElementById('actual_total_field');
    currentPaymentField.value = playerObject['paymentStatus']['totalPaid'] - playerObject['paymentStatus']['totalActualPaid'];
    currentPaymentField.setAttribute('max', playerObject['paymentStatus']['totalPresent'] - playerObject['paymentStatus']['totalActualPaid']);

    for (const categoryId in playerObject['registeredEntries']) {
        let registerCheckbox = document.getElementById('register_checkbox_' + categoryId);
        registerCheckbox.checked = true;
        onclickCheckboxWrapper('register', categoryId);
    }

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
    registerCheckbox.setAttribute('data-checkbox-type', 'register')
    registerCheckbox.setAttribute('oninput', 'onclickCheckboxWrapper("register", "' + categoryId + '")');
    registerCell.appendChild(registerCheckbox);
    let registerLabel = document.createElement('label');
    registerLabel.id = registerCheckbox.id + '_label';
    registerLabel.setAttribute('for', registerCheckbox.id);
    registerLabel.appendChild(document.createTextNode(' '));
    registerCell.appendChild(registerLabel);

    let presentCell = document.createElement('td');
    presentCell.setAttribute('id', 'present_cell_' + categoryId);
    let presentCheckbox = document.createElement('input');
    presentCheckbox.type = 'checkbox';
    presentCheckbox.id = 'present_checkbox_' + categoryId;
    presentCheckbox.setAttribute('data-checkbox-type', 'present')
    presentCheckbox.setAttribute('oninput', 'onclickCheckboxWrapper("present", "' + categoryId + '")');
    presentCell.appendChild(presentCheckbox);
    let presentLabel = document.createElement('label');
    presentLabel.id = presentCheckbox.id + '_label';
    presentLabel.setAttribute('for', presentCheckbox.id);
    presentLabel.appendChild(document.createTextNode(' '));
    presentCell.appendChild(presentLabel);

    let paidCell = document.createElement('td');
    paidCell.setAttribute('id', 'paid_cell_' + categoryId);
    let paidCheckbox = document.createElement('input');
    paidCheckbox.type = 'checkbox';
    paidCheckbox.id = 'paid_checkbox_' + categoryId;
    paidCheckbox.setAttribute('data-checkbox-type', 'paid')
    paidCheckbox.setAttribute('oninput', 'onclickCheckboxWrapper("paid", "' + categoryId + '")');
    paidCell.appendChild(paidCheckbox);
    let paidLabel = document.createElement('label');
    paidLabel.id = paidCheckbox.id + '_label';
    paidLabel.setAttribute('for', paidCheckbox.id);
    paidLabel.appendChild(document.createTextNode(' '));
    paidCell.appendChild(paidLabel);

    presentCell.style.backgroundColor = '#d3d3d3';
    presentCheckbox.setAttribute('disabled', '');
    paidCell.style.backgroundColor = '#d3d3d3';
    paidCheckbox.setAttribute('disabled', '');

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
        registerCell.style.backgroundColor = '#d3d3d3';
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
        registerCell.style.backgroundColor = '#d3d3d3';
        registerCheckbox.setAttribute('disabled', '');
    }

    row.appendChild(registerCell);
    row.appendChild(presentCell);
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
        setUpCategoriesTable();
        processPlayerInfo();
    });
