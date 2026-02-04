document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("barcodeInput");
    const tableBody = document.querySelector("#packagesTable tbody");
    const totalRead = document.getElementById("totalRead");
    const blueCounter = document.getElementById("blueCounter");
    const resetCounter = document.getElementById("resetCounter");
    const conferenceId = CONFERENCE_ID;


    let count = 0;
    let blueCount = 0;

    input.focus();

    function updateCounters() {
        totalRead.textContent = count;
        blueCounter.textContent = blueCount;
    }

    function addRow(package_code) {
        const row = document.createElement("tr");

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
        if (response.ok) {
            addRow(package_code);
            count++;
            blueCount++;
            updateCounters();
        } else {
            alert("Erro ao adicionar volume")
        }
    }

    async function removePackage(identity, rowElement) {

        const response = await sendPost(REMOVE_ENDPOINT, {
            identity: identity
        });

        if (response.ok) {
            rowElement.remove();
            count--;
            updateCounters();
        } else {
            alert("Erro ao remover volume");
        }
    }

    input.addEventListener("keypress", function (e) {
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

});
