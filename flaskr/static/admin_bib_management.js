function setAllBibs() {
    fetch('/api/admin/bibs', {
        method: 'POST',
    }).then((response) => response.json())
    .then((data) => {
        if ('error' in data) {
            console.error('Could not set bibs: ' + data.error);
        } else {
            console.log(data);
            window.location.href = "/admin/inscrits";
        }
    });
}

function resetAllBibs() {
    let confirmationMessage = window.prompt('Etes vous sûr de vouloir supprimer les n° de dossards existants ? Avez-vous appelé Céline avant de cliquer sur ce bouton ? Si oui, ou si vous êtes Céline, tapez "Je suis sur! J\'ai appelé Céline!" et validez.')
    if (confirmationMessage == "Je suis sur! J'ai appelé Céline!") {
        fetch('/api/admin/bibs', {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({'confirmation': confirmationMessage}),
        }).then((response) => [response.json(), response.status])
        .then((data) => {
            if (data[1] != 204) {
                console.error('Could not reset bibs: ' + data[0].error);
            } else {
                console.log('Successfully reset bibs');
                window.location.href = '/admin/inscrits';
            }
        })
    } else {
        window.alert('Vous n\'êtes pas sûr et/ou vous n\'avez pas appelé Céline.');
    }
}

document.getElementById('bibs_navbar_link').setAttribute('class', 'navbar-link-current');

showContent();
