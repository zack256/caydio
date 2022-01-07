function renameNodeTreeIDs (el, IDSuffix) {
    if (el.hasAttribute("id")) {
        el.id += IDSuffix;
    }
    for (var i = 0; i < el.children.length; i++) {
        renameNodeTreeIDs(el.children[i], IDSuffix);
    }
}

function makeCamelCase (s) {
    var newS = "";
    var doUpper = false;
    for (var i = 0; i < s.length; i++) {
        if (s[i] == ' ') {
            doUpper = true;
        } else {
            if (doUpper) {
                newS += s[i].toUpperCase();
                doUpper = false;
            } else {
                newS += s[i].toLowerCase();
            }
        }
    }
    return newS;
}

let defaultTextInp = {
    required : false,
    maxlength : 255,
    value : null,
    list : null,
}

let defaultHiddenInp = {
    value : "",
}

let necessaryForTextInp = new Set(["name"]);
let necessaryForHiddenInp = new Set(["name"]);

function checkIfProvidedAttrsGood (providedObj, nescSet) {
    for (const e of nescSet) {
        if (!providedObj.hasOwnProperty(e)) {
            return false;
        }
    }
    return true;
}

function setFTInputAttrs (providedObj, defaultObj) {
    for (let key in defaultObj) {
        if (!providedObj.hasOwnProperty(key)) {
            providedObj[key] = defaultObj[key];
        }
    }
}

class FormType {
    constructor (attachTo, title, inputs, formDataObj) {
        this.title = title;
        //this.camelCaseTitle();
        this.ccTitle = makeCamelCase(this.title);
        this.formDataObj = formDataObj;
        this.attachTo = attachTo;
        this.inputs = inputs;
        this.makeModal();
        this.editComponents();
    }

    addTextInput (tbody, inputObj) {

        if (!checkIfProvidedAttrsGood(inputObj, necessaryForTextInp)) {
            return; // error!
        }

        var tr, descCol, inpCol, inpEl;
        tr = document.createElement("TR");
        descCol = document.createElement("TD");
        inpCol = document.createElement("TD");
        inpEl = document.createElement("INPUT");
        inpCol.appendChild(inpEl);
        tr.appendChild(descCol);
        tr.appendChild(inpCol);
        tbody.appendChild(tr);
        inpEl.classList.add("input");

        setFTInputAttrs(inputObj, defaultTextInp);

        descCol.innerHTML = inputObj.name;
        inpEl.setAttribute("name", makeCamelCase(inputObj.name));
        inpEl.setAttribute("type", "text");
        inpEl.setAttribute("form", this.gLN("modalForm"));
        inpEl.setAttribute("maxlength", inputObj.maxlength);
        if (inputObj.required) {
            inpEl.setAttribute("required", "required");
        }
        if (inputObj.value) {
            inpEl.setAttribute("value", inputObj.value);
        }
        if (inputObj.list) {
            inpEl.setAttribute("list", inputObj.list);
        }
    }

    addHiddenInput (section, inputObj) {

        if (!checkIfProvidedAttrsGood(inputObj, necessaryForHiddenInp)) {
            return; // error!
        }
        setFTInputAttrs(inputObj, defaultHiddenInp);
        var inpEl = document.createElement("INPUT");
        section.appendChild(inpEl);
        inpEl.setAttribute("type", "hidden");
        inpEl.setAttribute("name", makeCamelCase(inputObj.name));
        inpEl.setAttribute("form", this.gLN("modalForm"));
        inpEl.setAttribute("value", inputObj.value);
    }

    makeModal () {
        let wrapper = document.getElementById("modalWrapper");
        let newWrapper = wrapper.cloneNode(true);
        renameNodeTreeIDs(newWrapper, "_" + this.ccTitle);
        this.attachTo.appendChild(newWrapper);
        let section = this.gLE("modalSection");
        let tbody = this.gLE("modalTB");
        for (var i = 0; i < this.inputs.length; i++) {
            if (!this.inputs[i].hasOwnProperty("type")) {
                continue;   // error!!
            }
            if (this.inputs[i].type == "text") {
                this.addTextInput(tbody, this.inputs[i]);
            } else if (this.inputs[i].type == "hidden") {
                this.addHiddenInput(section, this.inputs[i]);
            }
        }
    }

    gLN (componentName) {
        return componentName + "_" + this.ccTitle;
    }

    gLE (componentName) {   // get Local Element
        return document.getElementById(this.gLN(componentName));
    }

    setDisplayTitle (newTitle) {
        this.gLE("modalTitle").innerHTML = newTitle;
    }

    editComponents () {
        var self = this;
        let form = this.gLE("modalForm");
        form.action = this.formDataObj.postUrl;
        form.method = "POST";
        if (this.formDataObj.hasOwnProperty("confirmMsg")) {
            form.onsubmit = function () { return confirm(self.formDataObj.confirmMsg); };
        }
        let footer = this.gLE("modalFooter");
        for (var i = 0; i < footer.children.length; i++) {
            footer.children[i].setAttribute("form", form.id);
        }
        this.setDisplayTitle(this.title);
        this.gLE("modalClose").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
        this.gLE("modalBackground").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
    }
}