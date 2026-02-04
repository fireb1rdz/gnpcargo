document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("barcodeInput");
    const tableBody = document.querySelector("#packagesTable tbody");
    const totalRead = document.getElementById("totalRead");
    const blueCounter = document.getElementById("blueCounter");
    const resetCounter = document.getElementById("resetCounter");
    const conferenceId = CONFERENCE_ID;
    const conferenceItems = [];

    async function getConferenceItems() {
        try {
            const response = await fetch(`/logistica/conferencia/items/${conferenceId}/`);
            const data = await response.json();

            data.forEach(item => {
                addRow(item.package_code, item.status);

                // só incrementa contador se já estiver conferido
                if (item.status === "CHECKED") {
                    count++;
                }

            });
            updateCounters();

        } catch (error) {
            console.error("Erro ao carregar itens da conferência:", error);
        }
    }


    setTimeout(() => {
        input.focus();
    }, 300);

    let count = 0;
    let blueCount = 0;

    input.focus();

    function updateCounters() {
        totalRead.textContent = count;
        blueCounter.textContent = blueCount;
    }

    function addRow(package_code, status) {
        const row = document.createElement("tr");

        if (status === "ok") {
            row.classList.add("table-success");   // linha verde
        }

        row.innerHTML = `
            <td>${package_code}</td>
            <td class="text-end">
                <button class="btn btn-danger btn-sm remove-btn">
                    X
                </button>
            </td>
        `;

        row.querySelector(".remove-btn").addEventListener("click", function () {
            removePackage(package_code, row);
        });

        tableBody.prepend(row);
    }

    async function sendPost(url, data) {
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN
            },
            body: JSON.stringify(data)
        });
    }

    async function addPackage(package_code) {

        const response = await sendPost(ADD_ENDPOINT, {
            package_code: package_code
        });
        const data = await response.json();
        if (response.ok) {
            addRow(package_code, data.status);
            count++;
            blueCount++;
            updateCounters();
        } else {
            alert("Erro ao adicionar volume")
        }
    }

    async function removePackage(package_code, rowElement) {
        const response = await sendPost(REMOVE_ENDPOINT, {
            package_code: package_code
        });

        if (response.ok) {
            rowElement.remove();
            if (count > 0) {
                count--;
            }
            updateCounters();
        } else {
            alert("Erro ao remover volume");
        }
    }

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            const value = input.value.trim();
            console.log(value)

            if (value) {
                addPackage(value);
                input.value = "";
            }
        }
    });

    resetCounter.addEventListener("click", function () {
        blueCount = 0;
        updateCounters();
    });

    getConferenceItems();
});
