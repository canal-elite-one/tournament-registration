let playerObject;
let categoriesData;

function ifFfttApiError() {
    window.alert("Une erreur est survenue. Vous pouvez réessayer de vous réinscrire plus tard ou envoyer un courriel aux organisateurs du tournoi.");

    window.location.href = "/public";
}

function processPlayer() {
    document.getElementById("licence-no-cell").innerHTML = playerObject.licenceNo;
    document.getElementById("first-name-cell").innerHTML = playerObject.firstName;
    document.getElementById("last-name-cell").innerHTML = playerObject.lastName;
    document.getElementById("gender-cell").innerHTML = playerObject.gender;
    document.getElementById("club-cell").innerHTML = playerObject.club;
    document.getElementById("points-cell").innerHTML = playerObject.nbPoints;

    /*
    if (playerObject['gender'] == 'M') {
        document.getElementById('recap-message').innerHTML = 'Vous êtes inscrit aux tableaux suivants :';
    } else {
        document.getElementById('recap-message').innerHTML = 'Vous êtes inscrite aux tableaux suivants :';
    }
    */

    emailCell = document.getElementById("email-cell");
    if (playerObject.email) {
        emailCell.innerHTML = playerObject.email;
    } else {
        let emailField = document.createElement('input');
        emailField.setAttribute('type', 'email');
        emailField.setAttribute('id', 'email-field');
        emailField.setAttribute('required', '');
        emailCell.appendChild(emailField);
    }

    phoneCell = document.getElementById("phone-cell");
    if (playerObject.phone) {
        phoneCell.innerHTML = playerObject.phone;
    } else {
        let phoneField = document.createElement('input');
        phoneField.setAttribute('type', 'tel');
        phoneField.setAttribute('id', 'phone-field');
        phoneField.setAttribute('required', '');
        phoneCell.appendChild(phoneField);
    }

    for (let categoryId in playerObject['registeredEntries']) {
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        registerCheckbox.checked = true;
        if (registerCheckbox.getAttribute('data-day') == 'saturday') {
            nbEntriesSaturday += 1;
        } else {
            nbEntriesSunday += 1;
        }
        registerCheckbox.setAttribute('disabled', '');
        document.getElementById('register-cell-' + categoryId).style.backgroundColor = '#d3d3d3';
        if (categoryId in sameColor) {
            let otherCheckbox = document.getElementById('register-checkbox-' + sameColor[categoryId]);
            otherCheckbox.checked = false;
            otherCheckbox.setAttribute('disabled', '');
            document.getElementById('register-cell-' + sameColor[categoryId]).style.backgroundColor = '#d3d3d3';
        }
    };
}

const categoryIdByColor = {};
const sameColor = {};
let nbEntriesSaturday = 0;
let nbEntriesSunday = 0;

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

    if (registerCheckbox.getAttribute('data-day') == 'saturday') {
        nbEntriesSaturday += nbEntriesChange;
    } else {
        nbEntriesSunday += nbEntriesChange;
    }
    let submitButton = document.getElementById('submit-button');
    if (nbEntriesSaturday > maxEntriesPerDay || nbEntriesSunday > maxEntriesPerDay) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous ne pouvez pas vous inscrire à plus de ' + maxEntriesPerDay + ' tableaux par jour.');
    } else if (nbEntriesSaturday + nbEntriesSunday === 0) {
        submitButton.disabled = true;
        submitButton.style.cursor = 'not-allowed';
        submitButton.setAttribute('title', 'Vous devez vous inscrire à au moins un tableau.');
    } else {
        submitButton.disabled = false;
        submitButton.style.cursor = 'auto';
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
    registerCheckbox.setAttribute('data-checkbox-type', 'register')
    registerCheckbox.setAttribute('oninput', 'handleCheckbox("' + categoryId + '")');
    registerCell.appendChild(registerCheckbox);
    if (new Date(categoryObject['startTime']).getDate() == 6) {
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
    let maxOverbooked = Math.floor(categoryObject['maxPlayers'] * (1 + categoryObject['overbookingPercentage'] / 100.));
    let entryCountCell = document.createElement('td');

    if (entryCount < maxOverbooked || (categoryId in playerObject['registeredEntries'] && playerObject['registeredEntries'][categoryId]['rank'] < maxOverbooked)) {
        entryCountCell.appendChild(document.createTextNode('Places disponibles'));
        entryCountCell.style.backgroundColor = 'hsl(140, 100%, 80%)';
    } else {
        entryCountCell.appendChild(document.createTextNode('Liste d\'attente'));
        entryCountCell.style.backgroundColor = 'hsl(60, 100%, 80%)';
    }


    entryCountCell.setAttribute('id', 'entry-count-cell-' + categoryId);
    row.appendChild(entryCountCell);

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
        registerCell.style.backgroundColor = '#d3d3d3';
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
        registerCell.style.backgroundColor = '#d3d3d3';
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

function submitAll() {
    let nbSaturdayEntries = 0;
    let nbSundayEntries = 0;
    categoriesData.forEach(function (categoryObject) {
        let categoryId = categoryObject['categoryId'];
        let registerCheckbox = document.getElementById('register-checkbox-' + categoryId);
        if (registerCheckbox.checked) {
            if (new Date(categoryObject['startTime']).getDate() == 6) {
                nbSaturdayEntries += 1;
            } else {
                nbSundayEntries += 1;
            }
        }
    });

    console.log(maxEntriesPerDay);

    if (nbSaturdayEntries > maxEntriesPerDay || nbSundayEntries > maxEntriesPerDay) {
        window.alert("Vous ne pouvez pas vous inscrire à plus de " + maxEntriesPerDay + " tableaux par jour.");
        return;
    }

    if (!playerObject.email) {
        submitPlayer();
    } else {
        submitEntries();
    }
}

async function submitPlayer() {
    console.log("Submitting player");
    let emailField = document.getElementById("email-field");
    let phoneField = document.getElementById("phone-field");
    let isValid = emailField.reportValidity() && phoneField.reportValidity();
    if (isValid) {
        playerPayload = {
            'licenceNo': playerObject.licenceNo,
            'firstName': playerObject.firstName,
            'lastName': playerObject.lastName,
            'gender': playerObject.gender,
            'club': playerObject.club,
            'nbPoints': playerObject.nbPoints,
            'email': emailField.value,
            'phone': phoneField.value
        };
        try {
            let response = await fetch('/api/public/players', {
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
                submitEntries();
            } else {
                let responseData = await response.json();
                console.error("Error:", responseData);
                window.location.href = "/public/erreur";
            }

        } catch (error) {
            console.error("Error:", error);
            window.location.href = "/public/erreur";
        }
    }
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
        let responseData = await response.json();
        console.log(responseData);
        console.log("Entries successfully added");
        window.location.href = "/public/deja_inscrit/" + licenceNo;
    } else {
        publicHandleBadResponse(response);
    }
}

function closeRecap() {
    document.getElementById('recap-entries-div').style.display = 'none';
}

async function fetchCategoriesAndPlayer() {
    const categoriesPromise = fetch("/api/public/categories");
    const playerPromise = fetch("/api/public/players/" + licenceNo);
    const [categoriesResponse, playerResponse] = await Promise.all([categoriesPromise, playerPromise]);

    if (categoriesResponse.ok && playerResponse.ok) {
        categoriesData = await categoriesResponse.json();
        categoriesData = categoriesData['categories'];
        playerObject = await playerResponse.json();
        console.log(categoriesData);
        console.log(playerObject);
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
