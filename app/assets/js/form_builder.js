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

    makeModal () {
        let wrapper = document.getElementById("modalWrapper");
        let newWrapper = wrapper.cloneNode(true);
        renameNodeTreeIDs(newWrapper, "_" + this.ccTitle);
        this.attachTo.appendChild(newWrapper);
        let tbody = this.gLE("modalTB");
        var tr, descCol, inpCol, inpName, inpEl;
        for (var i = 0; i < this.inputs.length; i++) {
            tr = document.createElement("TR");
            descCol = document.createElement("TD");
            inpCol = document.createElement("TD");
            inpEl = document.createElement("INPUT");
            inpCol.appendChild(inpEl);
            tr.appendChild(descCol);
            tr.appendChild(inpCol);
            tbody.appendChild(tr);
            inpEl.classList.add("input");
            inpName = this.inputs[i][0];
            descCol.innerHTML = inpName;
            inpEl.setAttribute("name", makeCamelCase(inpName));
            inpEl.setAttribute("type", "text");
            inpEl.setAttribute("form", this.gLN("modalForm"));
            inpEl.setAttribute("maxlength", this.inputs[i][1]);
            inpEl.setAttribute("required", this.inputs[i][2]);
        }
    }

    gLN (componentName) {
        return componentName + "_" + this.ccTitle;
    }

    gLE (componentName) {   // get Local Element
        return document.getElementById(this.gLN(componentName));
    }

    editComponents () {
        let form = this.gLE("modalForm");
        form.action = this.postUrl;
        form.method = "POST";
        let footer = this.gLE("modalFooter");
        for (var i = 0; i < footer.children.length; i++) {
            footer.children[i].setAttribute("form", form.id);
        }
        this.gLE("modalTitle").innerHTML = this.title;
        var self = this;
        this.gLE("modalClose").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
        this.gLE("modalBackground").onclick = function () { deactivateModal(self.gLN("modalWrapper")); };
    }

}