function showContent() {
    console.log("showContent");
    document.getElementById("content_div").style.display = "block";
    // document.getElementById("loading_div").style.display = "none";
}

function hideContent() {
    document.getElementById("loading_div").style.display = "block";
    // document.getElementById("content_div").style.display = "none";
}

function showLoading() {
    document.getElementById("loading_div").style.display = "block";
}

function hideLoading() {
    document.getElementById("loading_div").style.display = "none";
}
