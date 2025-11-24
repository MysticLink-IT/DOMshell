function toggleInfoPopover(popID, content) {
    let d = document.getElementById(popID);
    d.innerHTML = content;
    d.togglePopover();
}
