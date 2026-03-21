jQuery(function () {
    // Inicializa Select2 em todos os selects marcados
    $('.select2').select2({
        width: '100%',
        theme: 'bootstrap-5',
        placeholder: 'Selecione uma opção',
        allowClear: true
    });

    const cteSection = document.getElementById("cte-section");
    const nfeSection = document.getElementById("nfe-section");
    const accessKeySection = document.getElementById("access-key-section");

    const radios = document.querySelectorAll("input[name='creation_mode']");
    const cteInput = document.getElementById("{{ form.cte_files.id_for_label }}");
    const nfeInput = document.getElementById("{{ form.nfe_files.id_for_label }}");
    const keyInput = document.getElementById("access-key-input");
    const container = document.getElementById("access-key-container");
    const hiddenInput = document.getElementById("access-keys-hidden");

    let accessKeys = [];

    function syncHiddenField() {
        hiddenInput.value = JSON.stringify(accessKeys);
    }

    function isValidAccessKey(value) {
        return /^\d{44}$/.test(value); // chave NF-e tem 44 dígitos
    }

    function addAccessKey(value) {
        if (!isValidAccessKey(value)) return;
        if (accessKeys.includes(value)) return;

        accessKeys.push(value);
        syncHiddenField();

        const chip = document.createElement("div");
        chip.className = "access-key-chip";
        chip.innerHTML = `
            <span>${value}</span>
            <button type="button">×</button>
        `;

        chip.querySelector("button").addEventListener("click", () => {
            accessKeys = accessKeys.filter(k => k !== value);
            syncHiddenField();
            chip.remove();
        });

        container.insertBefore(chip, keyInput);
    }

    keyInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            const value = keyInput.value.trim();
            addAccessKey(value);
            keyInput.value = "";
        }
    });

    container.addEventListener("click", () => keyInput.focus());

    function toggleSections() {
        const mode = document.querySelector("input[name='creation_mode']:checked").value;

        if (mode === "cte") {
            cteSection.style.display = "block";
            nfeSection.style.display = "none";
            accessKeySection.style.display = "none";

            cteInput.required = true;
            nfeInput.required = false;
            accessKeyInput.required = false;
        } else if (mode === "nfe") {
            cteSection.style.display = "none";
            nfeSection.style.display = "block";
            accessKeySection.style.display = "none";

            cteInput.required = false;
            nfeInput.required = true;
            accessKeyInput.required = false;
        } else if (mode === "access_key") {
            cteSection.style.display = "none";
            nfeSection.style.display = "none";
            accessKeySection.style.display = "block";

            cteInput.required = false;
            nfeInput.required = false;
            accessKeyInput.required = true;
        }
    }

    radios.forEach(radio => radio.addEventListener("change", toggleSections));
    toggleSections();
});