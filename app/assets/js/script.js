function confirmPasswordsMatch () {
    var pass1 = document.getElementById("pass1");
    var pass2 = document.getElementById("pass2");
    var match = pass1.value == pass2.value;
    if (!match) {
        alert("Passwords don't match.");
    }
    return match;
}

function addToDataList (dlID, text) {
    var optionEl = document.createElement("OPTION");
    optionEl.value = text;
    document.getElementById(dlID).appendChild(optionEl);
}

function confirmDelConn () {
    var res = confirm("Delete this video?");
    return res;
}

function delConn (connID) {
    if (confirmDelConn()) {
        document.getElementById("delConnID").value = connID;
        document.getElementById("delConnBtn").click();
    }
}