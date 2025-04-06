let playerObject;
let categoriesData;


const categoryIdByColor = {};
const sameColor = {};
const womenOnlySaturday = [];
const womenOnlySunday = [];
let isValidMandatoryWomenOnlyRegistrationSaturday = true;
let isValidMandatoryWomenOnlyRegistrationSunday = true;
let nbEntriesSaturday = 0;
let nbEntriesSunday = 0;

function processPlayer() {
    document.getElementById("licence-no-cell").value = playerObject.licenceNo;
    document.getElementById("first-name-cell").value = playerObject.firstName;
    document.getElementById("last-name-cell").value = playerObject.lastName;
    document.getElementById("gender-cell").value = playerObject.gender;
    document.getElementById("club-cell").value = playerObject.club;
    document.getElementById("points-cell").value = playerObject.nbPoints;
}

function updateMandatoryWomenOnlyRegistration() {
    if (playerObject['gender'] === 'M') {return;}

    isValidMandatoryWomenOnlyRegistrationSaturday = (nbEntriesSaturday === 0) ||
        womenOnlySaturday.every(function (categoryId) {
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        return registerCheckbox.checked;
    });

    isValidMandatoryWomenOnlyRegistrationSunday = (nbEntriesSunday === 0) ||
        womenOnlySunday.every(function (categoryId) {
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        return registerCheckbox.checked;
    });
}

function handleCheckbox(categoryId) {
    let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
    let nbEntriesChange = registerCheckbox.checked ? 1 : -1;
    if (sameColor[categoryId] && registerCheckbox.checked) {
        let otherCheckbox = document.getElementById('register-checkbox-' + sameColor[categoryId]);
        if (otherCheckbox.checked) {
            nbEntriesChange -= 1;
        }
        otherCheckbox.checked = false;
    }

    if (registerCheckbox.getAttribute('data-day') === 'saturday') {
        nbEntriesSaturday += nbEntriesChange;
    } else {
        nbEntriesSunday += nbEntriesChange;
    }
    updateMandatoryWomenOnlyRegistration();

    let maxEntriesPerDaySaturday = maxEntriesPerDay + ((playerObject['gender'] == 'F' && womenOnlySaturday.length > 0) ? 1 : 0);
    let maxEntriesPerDaySunday = maxEntriesPerDay + ((playerObject['gender'] == 'F' && womenOnlySunday.length > 0) ? 1 : 0);

    let submitButton = document.getElementById('submit-button');
    if (nbEntriesSaturday > maxEntriesPerDaySaturday ) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous ne pouvez pas vous inscrire à plus de ' + maxEntriesPerDaySaturday + ' tableaux pour la journée de samedi.');
    } else if (nbEntriesSunday > maxEntriesPerDaySunday) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous ne pouvez pas vous inscrire à plus de ' + maxEntriesPerDaySunday + ' tableaux pour la journée de dimanche.');
    } else if (nbEntriesSaturday + nbEntriesSunday === 0) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous devez vous inscrire à au moins un tableau.');
    } else if (!isValidMandatoryWomenOnlyRegistrationSunday || !isValidMandatoryWomenOnlyRegistrationSaturday) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous devez vous inscrire à tous les tableaux féminins pour chaque jour où vous êtes inscrite à au moins un tableau.');
    } else {
        submitButton.disabled = false;
        submitButton.style.cursor = 'pointer';
        submitButton.setAttribute('title', '');
    }

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
    if (new Date(categoryObject['startTime']).getDay() === 6) {
        registerCheckbox.setAttribute('data-day', 'saturday');
    } else {
        registerCheckbox.setAttribute('data-day', 'sunday');
    }
    let registerLabel = document.createElement('label');
    registerLabel.id = registerCheckbox.id + '-label';
    registerLabel.setAttribute('for', registerCheckbox.id);
    registerLabel.appendChild(document.createTextNode(' '));
    registerCell.appendChild(registerLabel);

    let idCell = document.createElement('td');
    idCell.setAttribute('id', 'id-cell-' + categoryId);
    idCell.appendChild(document.createTextNode(categoryId));
    row.appendChild(idCell);

    let nameCell = document.createElement('td');
    nameCell.setAttribute('id', 'name-cell-' + categoryId);
    nameCell.appendChild(document.createTextNode(categoryObject['alternateName']));
    row.appendChild(nameCell);

    let color = categoryObject['color'];

    if (!(color === null)) {
        if (color in categoryIdByColor) {
            sameColor[categoryId] = categoryIdByColor[color];
            sameColor[categoryIdByColor[color]] = categoryId;
        } else { categoryIdByColor[color] = categoryId; }
        idCell.style.backgroundColor = color;
    }

    let entryCount = categoryObject['entryCount'];
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.0));
    let entryCountCell = document.createElement('td');

    if (entryCount <= maxOverbooked) {
        entryCountCell.appendChild(document.createTextNode('Oui'));
        entryCountCell.classList.add('non-waiting-list-cell');
        entryCountCell.classList.remove('waiting-list-cell');
        entryCountCell.classList.remove('full-cell');
    } else if (entryCount <= maxOverbooked + 40) {
        let waitingListString = 'Position ' + (entryCount - maxOverbooked + 1) + ' en liste d\'attente';
        entryCountCell.appendChild(document.createTextNode(waitingListString));
        entryCountCell.classList.add('waiting-list-cell');
        entryCountCell.classList.remove('non-waiting-list-cell');
        entryCountCell.classList.remove('full-cell');
    } else {
        entryCountCell.appendChild(document.createTextNode('Complet'));
        entryCountCell.classList.add('full-cell');
        entryCountCell.classList.remove('waiting-list-cell');
        entryCountCell.classList.remove('non-waiting-list-cell');
        registerCell.classList.add('disabled-cell');
        registerCheckbox.setAttribute('disabled', '');
    }


    entryCountCell.setAttribute('id', 'entry-count-cell-' + categoryId);
    row.appendChild(entryCountCell);

    let maxPoints = categoryObject['maxPoints'];
    let minPoints = categoryObject['minPoints'];
    if (playerObject['nbPoints'] < minPoints || playerObject['nbPoints'] > maxPoints) {
        registerCell.classList.add('disabled-cell');
        registerCheckbox.setAttribute('disabled', '');
    }

    if (categoryObject['womenOnly'] && playerObject['gender'] === 'M') {
        registerCell.classList.add('disabled-cell');
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
            if (categoryObject['womenOnly']) {
                womenOnlySaturday.push(categoryObject['categoryId']);
            }
            let row = createCategoryRow(categoryObject);
            saturdayBody.appendChild(row);
        });

    sundayCategories.forEach(
        function (categoryObject) {
            if (categoryObject['womenOnly']) {
                womenOnlySunday.push(categoryObject['categoryId']);
            }
            let row = createCategoryRow(categoryObject);
            sundayBody.appendChild(row);
        });
}

function submitAll() {
    let nbSaturdayEntries = 0;
    let nbSundayEntries = 0;
    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        if (registerCheckbox.checked) {
            if (new Date(categoryObject['startTime']).getDay() === 6) {
                nbSaturdayEntries += 1;
            } else {
                nbSundayEntries += 1;
            }
        }
    });

    let maxEntriesPerDaySaturday = maxEntriesPerDay + ((playerObject['gender'] === 'F' && womenOnlySaturday.length > 0) ? 1 : 0);
    let maxEntriesPerDaySunday = maxEntriesPerDay + ((playerObject['gender'] === 'F' && womenOnlySunday.length > 0) ? 1 : 0);


    if (nbSaturdayEntries > maxEntriesPerDaySaturday) {
        window.alert("Vous ne pouvez pas vous inscrire à plus de " + maxEntriesPerDaySaturday + " tableaux pour la journée de samedi.");
        return;
    } else if (nbSundayEntries > maxEntriesPerDaySunday) {
        window.alert("Vous ne pouvez pas vous inscrire à plus de " + maxEntriesPerDaySunday + " tableaux pour la journée de dimanche.");
        return;
    }

    submitPlayer().then(() => console.log("Player submitted"));
}

async function submitPlayer() {
    let emailField = document.getElementById("email-cell");
    let phoneField = document.getElementById("phone-cell");
    changeRequiredMessage(emailField, "Veuillez entrer votre adresse email.");
    changeRequiredMessage(phoneField, "Veuillez entrer votre numéro de téléphone.");
    let isValid = emailField.reportValidity() && phoneField.reportValidity();
    if (isValid) {
        let contactPayload = {
            'email': emailField.value,
            'phone': phoneField.value
        };
        let response = await fetch(`/api/public/players/${licenceNo}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contactPayload)
        })
        if (response.ok) {
            console.log("Player successfully added");
            await submitEntries();
        } else {
            await publicHandleBadResponse(response);
        }
    }
}

function changeRequiredMessage(field, message) {
    field.addEventListener('invalid', function() {
    if(field.validity.valueMissing) {
      field.setCustomValidity(message);
    } else {
      field.setCustomValidity('');
    }
    });
}

async function submitEntries() {
    let payload = {
        'categoryIds': [],
    };
    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        if (registerCheckbox.checked) {
            payload['categoryIds'].push(categoryId);
        }
    });
    let response = await fetch('/api/public/entries/' + licenceNo, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    if (response.ok) {
        window.location.href = "/public/deja_inscrit/" + licenceNo;
    } else {
        await publicHandleBadResponse(response);
    }
}


async function fetchCategoriesAndPlayer() {
    const categoriesPromise = fetch("/api/public/categories");
    const playerPromise = fetch("/api/public/players/" + licenceNo);
    const [categoriesResponse, playerResponse] = await Promise.all([categoriesPromise, playerPromise]);

    if (categoriesResponse.ok && playerResponse.ok) {
        categoriesData = await categoriesResponse.json();
        categoriesData = categoriesData['categories'];
        playerObject = await playerResponse.json();
        setUpCategoriesTable();
        processPlayer();
        return true;
    } else if (!categoriesResponse.ok) {
        return publicHandleBadResponse(categoriesResponse);
    } else {
        return publicHandleBadResponse(playerResponse);
    }
}

fetchCategoriesAndPlayer().then((flag) => {
    if (flag) { showContent(); }
});
