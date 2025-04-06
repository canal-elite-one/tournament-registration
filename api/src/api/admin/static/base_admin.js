// these functions are used in all the admin .js files

function showContent() {
    console.log("showContent");
    document.getElementById("content-div").style.display = "block";
}

function hideContent() {
    document.getElementById("content-div").style.display = "none";
}

async function adminHandleBadResponse(response) {
    try {
        if (response.headers.get("Content-Type") != "application/json") {
            alert("Une erreur non gérée par le serveur est survenue..." + response.status + response.statusText)
            window.location.href = "/admin";
            return false;
        }
        const error = await response.json();
        if (error["errorType"] == "PLAYER_NOT_FOUND") {
            alert(`Aucun licencié avec le numéro de licence ${error["payload"]["licenceNo"]} n'a été trouvé.`);
            window.location.href = "/admin";
            return false;
        } else {
            alert(error.toString());
            window.location.href = "/admin";
            return false;
        }
    } catch (e) {
        alert("Une erreur est survenue lors de la gestion d'une réponse invalide du serveur...");
        window.location.href = "/admin";
        return false;
    }
}

// functions/objects below are used in only some of the .js files


// used in admin_player_management pre/during tournament
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


function deletePlayer() {
    let confirmMessage = `Voulez-vous vraiment supprimer ${playerObject['gender'] == 'M' ? "ce compétiteur" : "cette compétitrice"} de la base ` +
    `de données ? Toutes les informations sur les inscriptions seront perdues.`;

    if (confirm(confirmMessage)) {
        fetch('/api/admin/players/' + licenceNo, {method: 'DELETE'}).then(() =>
        {
            console.log('Successfully deleted player with licence n°:' + licenceNo);
            window.location.href = "../inscrits";
        });
    }
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

function takeCheckboxStateSnapshot () {
    let checkboxes = document.querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < checkboxes.length; i++) {
        let checkbox = checkboxes[i];
        checkbox.setAttribute("data-initial-checked", checkbox.checked ? "true" : "false");
        checkbox.setAttribute("data-initial-enabled", !(checkbox.disabled) ? "true" : "false");
    }
}

// used in admin_show_all_players && admin_players_by_category

async function downloadCsv(by_category) {
    let filename = by_category ? 'competiteurs_par_tableau.zip' : 'competiteurs_samedi_dimanche.zip';
    let downloadLink = document.createElement('a');
    downloadLink.setAttribute('href', `/api/admin/csv?by_category=${by_category}`);
    downloadLink.setAttribute('download', filename);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}
