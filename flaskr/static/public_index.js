const licenceField = document.getElementById("licence_no_field");
licenceField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        findPlayer();
    }
});

licenceField.value = "";


function findPlayer() {
    let licenceNo = document.getElementById("licence_no_field").value;
    window.location.href = "/public/joueur/" + licenceNo;
}
