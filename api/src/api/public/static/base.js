function showContent() {
    document.getElementById("content-div").style.display = "block";
}

function hideContent() {
    document.getElementById("content-div").style.display = "none";
}

async function publicHandleBadResponse(response) {
    try {
        if (response.status === 500) {
            window.location.href = "../erreur";
            return false;
        }
        const error = await response.json();
        if (error["errorType"] == "PLAYER_NOT_FOUND") {
            alert(`Aucun licencié avec le numéro de licence ${error["payload"]["licenceNo"]} n'a été trouvé.`);
            window.location.href = "/public";
            return false;
        } else if (error["errorType"] == "PLAYER_ALREADY_REGISTERED") {
            window.location.href = "/public/deja_inscrit/" + error["payload"]["licenceNo"];
            return false;
        } else {
            window.location.href = "../erreur";
            return false;
        }
    } catch (e) {
        window.location.href = "../erreur";
        return false;
    }
}
