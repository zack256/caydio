function confirmPasswordsMatch () {
    var pass1 = document.getElementById("pass1");
    var pass2 = document.getElementById("pass2");
    var match = pass1.value == pass2.value;
    if (!match) {
        alert("Passwords don't match.");
    }
    return match;
}