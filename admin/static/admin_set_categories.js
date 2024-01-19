let nbRows = 0;

function removeFormRow() {
    if (nbRows == 0) {
        return null;
    }
    document.getElementById('categories-table-body').lastChild.remove();
    nbRows -= 1;
}

function addFormRow(rowData = null) {
    let fillValues = rowData !== null;

    let row = document.createElement('tr');

    let idField = document.createElement('input');
    idField.type = 'text';
    idField.maxLength = '1';
    idField.minLength = '1';
    idField.size = '1';
    idField.id = 'id-field-' + nbRows;
    idField.required = 'true';
    if (fillValues) { idField.value = rowData['categoryId']; }
    let idCell = document.createElement('td');
    idCell.appendChild(idField);
    row.appendChild(idCell);

    let alternateNameField = document.createElement('input');
    alternateNameField.type = 'text';
    alternateNameField.maxLength = '64';
    alternateNameField.minLength = '0';
    alternateNameField.size = '10';
    alternateNameField.id = 'alternate-name-field-' + nbRows;
    if (fillValues) { alternateNameField.value = rowData['alternateName']; }
    let alternateNameCell = document.createElement('td');
    alternateNameCell.appendChild(alternateNameField);
    row.appendChild(alternateNameCell);

    let colorField = document.createElement('input');
    colorField.type = 'color';
    colorField.size = '10';
    colorField.value = '#ffffff';
    colorField.id = 'color-field-' + nbRows;
    if (fillValues && !(rowData['color'] === null)) { colorField.value = rowData['color']; }
    let colorCell = document.createElement('td');
    colorCell.appendChild(colorField);
    row.appendChild(colorCell);

    let minPointsField = document.createElement('input');
    minPointsField.type = 'number';
    minPointsField.max = '4000';
    minPointsField.min = '0';
    minPointsField.style.width = '4em';
    minPointsField.id = 'min-points-field-' + nbRows;
    if (fillValues) { minPointsField.value = rowData['minPoints']; }
    let minPointsCell = document.createElement('td');
    minPointsCell.appendChild(minPointsField);
    row.appendChild(minPointsCell);

    let maxPointsField = document.createElement('input');
    maxPointsField.type = 'number';
    maxPointsField.max = '4000';
    maxPointsField.min = '0';
    maxPointsField.style.width = '4em';
    maxPointsField.id = 'max-points-field-' + nbRows;
    if (fillValues) { maxPointsField.value = rowData['maxPoints']; }
    let maxPointsCell = document.createElement('td');
    maxPointsCell.appendChild(maxPointsField);
    row.appendChild(maxPointsCell);

    let startTimeField = document.createElement('input');
    startTimeField.type = 'datetime-local';
    startTimeField.id = 'start-time-field-' + nbRows;
    if (nbRows > 0) {
        startTimeField.value = document.getElementById('start-time-field-' + (nbRows - 1)).value;
    }
    startTimeField.required = 'true';
    if (fillValues) { startTimeField.value = rowData['startTime']; }
    let startTimeCell = document.createElement('td');
    startTimeCell.appendChild(startTimeField);
    row.appendChild(startTimeCell);

    let womenOnlyField = document.createElement('input');
    womenOnlyField.type = 'checkbox';
    womenOnlyField.id = 'women-only-field-' + nbRows;
    if (fillValues) { womenOnlyField.checked = rowData['womenOnly']; }
    let womenOnlyCell = document.createElement('td');
    womenOnlyCell.appendChild(womenOnlyField);
    row.appendChild(womenOnlyCell);

    let baseCostField = document.createElement('input');
    baseCostField.type = 'number';
    baseCostField.min = '0';
    baseCostField.style.width = '5em';
    baseCostField.step = '0.1';
    baseCostField.id = 'base-cost-field-' + nbRows;
    baseCostField.required = 'true';
    if (fillValues) { baseCostField.value = rowData['baseRegistrationFee']; }
    let baseCostCell = document.createElement('td');
    baseCostCell.appendChild(baseCostField);
    row.appendChild(baseCostCell);

    let lateCostField = document.createElement('input');
    lateCostField.type = 'number';
    lateCostField.min = '0';
    lateCostField.style.width = '5em';
    lateCostField.step = '0.1';
    lateCostField.id = 'late-cost-field-' + nbRows;
    lateCostField.required = 'true';
    if (fillValues) { lateCostField.value = rowData['lateRegistrationFee']; }
    let lateCostCell = document.createElement('td');
    lateCostCell.appendChild(lateCostField);
    row.appendChild(lateCostCell);

    let rewardFirstField = document.createElement('input');
    rewardFirstField.type = 'number';
    rewardFirstField.min = '0';
    rewardFirstField.style.width = '4em';
    rewardFirstField.id = 'reward-first-field-' + nbRows;
    rewardFirstField.required = 'true';
    if (fillValues) { rewardFirstField.value = rowData['rewardFirst']; }
    let rewardFirstCell = document.createElement('td');
    rewardFirstCell.appendChild(rewardFirstField);
    row.appendChild(rewardFirstCell);

    let rewardSecondField = document.createElement('input');
    rewardSecondField.type = 'number';
    rewardSecondField.min = '0';
    rewardSecondField.style.width = '4em';
    rewardSecondField.id = 'reward-second-field-' + nbRows;
    rewardSecondField.required = 'true';
    if (fillValues) { rewardSecondField.value = rowData['rewardSecond']; }
    let rewardSecondCell = document.createElement('td');
    rewardSecondCell.appendChild(rewardSecondField);
    row.appendChild(rewardSecondCell);

    let rewardSemiField = document.createElement('input');
    rewardSemiField.type = 'number';
    rewardSemiField.min = '0';
    rewardSemiField.style.width = '4em';
    rewardSemiField.id = 'reward-semi-field-' + nbRows;
    rewardSemiField.required = 'true';
    if (fillValues) { rewardSemiField.value = rowData['rewardSemi']; }
    let rewardSemiCell = document.createElement('td');
    rewardSemiCell.appendChild(rewardSemiField);
    row.appendChild(rewardSemiCell);

    let rewardQuarterField = document.createElement('input');
    rewardQuarterField.type = 'number';
    rewardQuarterField.min = '0';
    rewardQuarterField.style.width = '4em';
    rewardQuarterField.id = 'reward-quarter-field-' + nbRows;
    if (fillValues) { rewardQuarterField.value = rowData['rewardQuarter']; }
    let rewardQuarterCell = document.createElement('td');
    rewardQuarterCell.appendChild(rewardQuarterField);
    row.appendChild(rewardQuarterCell);

    let maxPlayersField = document.createElement('input');
    maxPlayersField.type = 'number';
    maxPlayersField.min = '0';
    maxPlayersField.style.width = '3em';
    maxPlayersField.required = 'true';
    maxPlayersField.id = 'max-players-field-' + nbRows;
    if (fillValues) { maxPlayersField.value = rowData['maxPlayers']; }
    let maxPlayersCell = document.createElement('td');
    maxPlayersCell.appendChild(maxPlayersField);
    row.appendChild(maxPlayersCell);

    let overbookingPercentageField = document.createElement('input');
    overbookingPercentageField.type = 'number';
    overbookingPercentageField.min = '0';
    overbookingPercentageField.style = 'width:3em';
    overbookingPercentageField.id = 'overbooking-percentage-field-' + nbRows;
    if (fillValues) { overbookingPercentageField.value = rowData['overbookingPercentage']; }
    let overbookingPercentageCell = document.createElement('td');
    overbookingPercentageCell.appendChild(overbookingPercentageField);
    row.appendChild(overbookingPercentageCell);

    document.getElementById("categories-table-body").appendChild(row);
    nbRows += 1;
}

const fieldNames = {
    'id': 'categoryId',
    'alternate-name': 'alternateName',
    'color': 'color',
    'min-points': 'minPoints',
    'max-points': 'maxPoints',
    'start-time': 'startTime',
    'women-only': 'womenOnly',
    'base-cost': 'baseRegistrationFee',
    'late-cost': 'lateRegistrationFee',
    'reward-first': 'rewardFirst',
    'reward-second': 'rewardSecond',
    'reward-semi': 'rewardSemi',
    'reward-quarter': 'rewardQuarter',
    'max-players': 'maxPlayers',
    'overbooking-percentage': 'overbookingPercentage'
};

const nullables = ['alternate-name', 'color', 'min-points', 'max-points', 'reward-quarter'];

function isNotNull(fieldName, fieldValue) {
    if (fieldName == 'color' && fieldValue == '#ffffff') { return false; }
    if (fieldName == 'alternate-name' && fieldValue === '') { return false; }
    if (fieldName == 'min-points' && fieldValue === '') { return false; }
    if (fieldName == 'max-points' && fieldValue === '') { return false; }
    if (fieldName == 'reward-quarter' && fieldValue === '') {return false; }
    return true;
}


function submitForm() {
    let isValid = document.getElementById("categories-form").reportValidity();
    if (isValid) {
        let payloadObject = {'categories': []};
        for (let i = 0; i < nbRows; i++) {
            let categoryObject = {};
            for (const [formField, jsonField] of Object.entries(fieldNames)) {
                let field = document.getElementById(formField + '-field-' + i);
                if (isNotNull(formField, field.value)) {
                    categoryObject[jsonField] = field.value;
                }
            }
            payloadObject['categories'].push(categoryObject);
        }
        fetch('/api/admin/categories', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payloadObject),
        })
            .then(response => response.json())
            .then(data => {
              if ('error' in data) {
                console.error('Error setting categories:', data.error);
              } else {
                window.location.href = '/admin/inscrits';
              }
            })
            .catch(error => {
              console.error('Error fetching API data:', error);
            });

    }
}

function processExistingCategories(data) {
    if ('error' in data) {
        console.error('Error fetching categories data:', data.error)
    } else if (data['categories'].length == 0) {
        addFormRow();
    } else {
        data['categories'].forEach(categoryData => {
            addFormRow(categoryData);
            if (categoryData['entryCount'] > 0) {
                document.getElementById("submit-categories-button").disabled = 'true';
                document.getElementById("submit-categories-button").title = 'Les inscriptions ont déjà commencé.';
            }
        });
    }
}

document.getElementById('set-categories-navbar-link').setAttribute('class', 'navbar-link-current');

fetch('/api/admin/categories')
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        processExistingCategories(data);
    }).then(() => showContent());
