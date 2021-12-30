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

class FormType {
    constructor (attachTo, title, postUrl, inputs) {
        this.title = title;
        //this.camelCaseTitle();
        this.ccTitle = makeCamelCase(this.title);
        this.postUrl = postUrl;
        this.attachTo = attachTo;
        this.inputs = inputs;
        this.makeModal();
        this.editComponents();
    }

    addTextInput (tbody, inputDets) {
        var tr, descCol, inpCol, inpName, inpEl;
        tr = document.createElement("TR");
        descCol = document.createElement("TD");
        inpCol = document.createElement("TD");
        inpEl = document.createElement("INPUT");
        inpCol.appendChild(inpEl);
        tr.appendChild(descCol);
        tr.appendChild(inpCol);
        tbody.appendChild(tr);
        inpEl.classList.add("input");
        inpName = inputDets[1];
        descCol.innerHTML = inpName;
        inpEl.setAttribute("name", makeCamelCase(inpName));
        inpEl.setAttribute("type", "text");
        inpEl.setAttribute("form", this.gLN("modalForm"));
        inpEl.setAttribute("maxlength", inputDets[2]);
        if (inputDets[3]) { // swtich to objs!!
            inpEl.setAttribute("required", "required");
        }
    }

    addHiddenInput (section, inputDets) {
        var inpEl = document.createElement("INPUT");
        section.appendChild(inpEl);
        inpEl.setAttribute("type", "hidden");
        inpEl.setAttribute("name", makeCamelCase(inputDets[1]));
        inpEl.setAttribute("form", this.gLN("modalForm"));
        inpEl.setAttribute("value", inputDets[2]);
    }

    makeModal () {
        let wrapper = document.getElementById("modalWrapper");
        let newWrapper = wrapper.cloneNode(true);
        renameNodeTreeIDs(newWrapper, "_" + this.ccTitle);
        this.attachTo.appendChild(newWrapper);
        let section = this.gLE("modalSection");
        let tbody = this.gLE("modalTB");
        for (var i = 0; i < this.inputs.length; i++) {
            if (this.inputs[i][0] == "text") {
                this.addTextInput(tbody, this.inputs[i]);
            } else if (this.inputs[i][0] == "hidden") {
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
        let form = this.gLE("modalForm");
        form.action = this.postUrl;
        form.method = "POST";
        let footer = this.gLE("modalFooter");
        for (var i = 0; i < footer.children.length; i++) {
            footer.children[i].setAttribute("form", form.id);
        }
        this.setDisplayTitle(this.title);
        var self = this;
        this.gLE("modalClose").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
        this.gLE("modalBackground").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
    }
}