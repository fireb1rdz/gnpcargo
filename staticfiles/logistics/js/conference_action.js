document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("barcodeInput");
    const tableBody = document.querySelector("#packagesTable tbody");
    const totalRead = document.getElementById("totalRead");
    const blueCounter = document.getElementById("blueCounter");
    const resetCounter = document.getElementById("resetCounter");
    const conferenceId = CONFERENCE_ID;
    const conferenceItems = [];
    const conferenceMode = CONFERENCE_MODE;
    const OkSound = document.getElementById("OkSound");
    const ErrorSound = document.getElementById("ErrorSound");
    let scanQueue = [];
    let isProcessing = false;

    function playOk() {
        const audio = new Audio(OkSound.src);
        audio.play();
    }

    function playError() {
        const audio = new Audio(ErrorSound.src);
        audio.play();
    }

    function enqueueScan(package_code) {
        scanQueue.push(package_code);
        processQueue();
    }

    async function processQueue() {
        if (isProcessing) return;

        if (scanQueue.length === 0) return;

        isProcessing = true;

        const package_code = scanQueue.shift();

        try {
            if (CONFERENCE_MODE === "write") {
                await addPackage(package_code);
            } else if (CONFERENCE_MODE === "read") {
                await readPackage(package_code);
            }
        } catch (error) {
            console.error("Erro no processamento da fila:", error);
        }

        isProcessing = false;

        // processa próximo item automaticamente
        processQueue();
    }



    async function getConferenceItems() {
        try {
            const response = await fetch(`/logistica/conferencia/items/${conferenceId}/`);
            const data = await response.json();
            let playSound = false

            data.forEach(item => {
                addRow(item.package_code, item.status, playSound);

                // só incrementa contador se já estiver conferido
                if (conferenceMode === "read" && item.status === "ok") {
                    count++;
                } else if (conferenceMode === "write" && item.status === "pending") {
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

    function addRow(package_code, status, playSound) {
        const row = document.createElement("tr");

        if (status === "ok" && conferenceMode === "read" || status === "pending" && conferenceMode === "write") {
            row.classList.add("table-success");   // linha verde
            if (playSound) {
                playOk();
            }
        } else if (status === "error") {
            if (playSound) {
                playError();
            }
        }

        row.innerHTML = `
            <td>${package_code}</td>
            <td class="text-end">
                <button class="btn btn-danger btn-sm remove-btn">
                    X
                </button>
            </td>
        `;
        row.setAttribute("data-package-code", package_code);
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
        let playSound = true
        const response = await sendPost(ADD_ENDPOINT, {
            package_code: package_code
        });
        const data = await response.json();
        if (response.ok) {
            addRow(package_code, data.status, playSound);
            count++;
            blueCount++;
            updateCounters();
        } else {
            alert("Erro ao adicionar volume")
        }
    }

    async function updateRow(package_code, status) {
        const row = document.querySelector(`tr[data-package-code="${package_code}"]`);
        console.log(row)
        if (row) {
            row.classList.remove("table-success", "table-danger");
            if (status === "ok") {
                playOk();
                row.classList.add("table-success");
            } else if (status === "error") {
                playError();
                row.classList.add("table-danger");
            }
        }
    }

    async function readPackage(package_code) {
        const response = await sendPost(READ_ENDPOINT, {
            package_code: package_code
        });
        const data = await response.json();
        if (data.status === "ok") {
            updateRow(package_code, data.status);
            count++;
            blueCount++;
            updateCounters();
        } else if (data.status === "error") {
            updateRow(package_code, data.status);
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
                enqueueScan(value);
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
