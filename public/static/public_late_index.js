const licenceField = document.getElementById("licence-no-field");
licenceField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        findPlayer();
    }
});

licenceField.value = "";


function findPlayer() {
    let licenceNo = document.getElementById("licence-no-field").value;
    window.location.href = "/public/deja_inscrit/" + licenceNo;
}
