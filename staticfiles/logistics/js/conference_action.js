document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("barcodeInput");
    const tableBody = document.querySelector("#packagesTable tbody");
    const totalRead = document.getElementById("totalRead");
    const blueCounter = document.getElementById("blueCounter");
    const resetCounter = document.getElementById("resetCounter");
    const readingHistory = document.getElementById("readingHistory");
    const session_id = document.getElementById("session_id").textContent;
    const conferenceMode = CONFERENCE_MODE;
    const okSound = document.getElementById("OkSound");
    const errorSound = document.getElementById("ErrorSound");

    const pauseButton = document.getElementById("btn-pausar");
    const resumeButton = document.getElementById("btn-retomar");
    const counterDisplay = document.getElementById("contador");
    const timerStatusBadge = document.getElementById("timer-status-badge");

    let scanQueue = [];
    let isProcessing = false;

    let count = 0;
    let blueCount = 0;

    let isPaused = false;
    let elapsedSeconds = 0;
    let timerInterval = null;

    function playOk() {
        const audio = new Audio(okSound.src);
        audio.play();
    }

    function playError() {
        const audio = new Audio(errorSound.src);
        audio.play();
    }

    function formatTime(totalSeconds) {
        const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
        const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");
        return `${hours}:${minutes}:${seconds}`;
    }

    function updateCounterDisplay() {
        if (counterDisplay) {
            counterDisplay.textContent = formatTime(elapsedSeconds);
        }
    }

    function startTimer() {
        if (timerInterval) clearInterval(timerInterval);

        timerInterval = setInterval(() => {
            if (!isPaused) {
                elapsedSeconds++;
                updateCounterDisplay();
            }
        }, 1000);
    }

    function applyPausedState() {
        if (pauseButton) pauseButton.style.display = "none";
        if (resumeButton) resumeButton.style.display = "inline-flex";

        if (timerStatusBadge) {
            timerStatusBadge.textContent = "Pausado";
            timerStatusBadge.classList.remove("timer-running");
            timerStatusBadge.classList.add("timer-paused");
        }
    }

    function applyRunningState() {
        if (pauseButton) pauseButton.style.display = "inline-flex";
        if (resumeButton) resumeButton.style.display = "none";

        if (timerStatusBadge) {
            timerStatusBadge.textContent = "Em andamento";
            timerStatusBadge.classList.remove("timer-paused");
            timerStatusBadge.classList.add("timer-running");
        }
    }

    async function sendSessionEvent(eventType) {
        try {
            const response = await fetch(`/api/conference/session/${session_id}/event/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": CSRF_TOKEN
                },
                body: JSON.stringify({ event_type: eventType })
            });

            if (!response.ok) {
                console.error("Server error while sending session event:", eventType);
                return null;
            }

            const data = await response.json();

            if (data.total_seconds !== undefined) {
                elapsedSeconds = data.total_seconds;
                updateCounterDisplay();
            }

            return data;
        } catch (error) {
            console.error(`Error sending session event (${eventType}):`, error);
            return null;
        }
    }

    function enqueueScan(packageCode) {
        scanQueue.push(packageCode);
        processQueue();
    }

    async function processQueue() {
        if (isProcessing) return;
        if (scanQueue.length === 0) return;
        if (isPaused) return;

        isProcessing = true;
        const packageCode = scanQueue.shift();

        try {
            if (conferenceMode === "write") {
                await addPackage(packageCode);
            } else if (conferenceMode === "read") {
                await readPackage(packageCode);
            }
        } catch (error) {
            console.error("Queue processing error:", error);
        }

        isProcessing = false;
        processQueue();
    }

    async function getConferenceItems() {
        try {
            const response = await fetch(`/api/conference/items/${session_id}/`);
            const data = await response.json();

            data.forEach(item => {
                addRow(item.package_code, item.status);

                if (conferenceMode === "read" && item.status === "ok") {
                    count++;
                } else if (conferenceMode === "write" && item.status === "pending") {
                    count++;
                }
            });

            updateCounters();
        } catch (error) {
            console.error("Error loading conference items:", error);
        }
    }

    function updateCounters() {
        totalRead.textContent = count;
        blueCounter.textContent = blueCount;
    }

    function addToHistory(packageCode, status) {
        const entry = document.createElement("div");
        let message = "";

        if (status === "ok") {
            message = `${packageCode}: Lido com sucesso`;
            entry.style.color = "green";
        } else if (status === "not_found") {
            message = `${packageCode}: Não localizado`;
            entry.style.color = "red";
        } else if (status === "already_read") {
            message = `${packageCode}: Já lido`;
            entry.style.color = "orange";
        } else if (status === "pending") {
            message = `${packageCode}: Cadastrado com sucesso`;
            entry.style.color = "blue";
        } else {
            message = `${packageCode}: ${status}`;
        }

        entry.textContent = message;
        readingHistory.prepend(entry);
    }

    function addRow(packageCode, status) {
        const row = document.createElement("tr");

        if (
            (status === "ok" && conferenceMode === "read") ||
            (status === "pending" && conferenceMode === "write")
        ) {
            row.classList.add("table-success");
        }

        row.innerHTML = `
            <td>${packageCode}</td>
            <td class="text-end">
                <button class="btn btn-danger btn-sm remove-btn">
                    X
                </button>
            </td>
        `;

        row.setAttribute("data-package-code", packageCode);
        row.querySelector(".remove-btn").addEventListener("click", function () {
            removePackage(packageCode, row);
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

    async function addPackage(packageCode) {
        const response = await sendPost(ADD_ENDPOINT, {
            package_code: packageCode
        });

        const data = await response.json();
        addToHistory(packageCode, data.status);

        if (response.ok) {
            playOk();
            addRow(packageCode, data.status);
            count++;
            blueCount++;
            updateCounters();
        } else {
            playError();
            alert("Erro ao adicionar volume");
        }
    }

    async function updateRow(packageCode, status) {
        const row = document.querySelector(`tr[data-package-code="${packageCode}"]`);

        if (row) {
            row.classList.remove("table-success", "table-danger");

            if (status === "ok") {
                playOk();
                row.classList.add("table-success");
            } else {
                playError();
                row.classList.add("table-danger");
            }
        }
    }

    async function readPackage(packageCode) {
        const response = await sendPost(READ_ENDPOINT, {
            package_code: packageCode
        });

        const data = await response.json();
        addToHistory(packageCode, data.status);

        if (data.status === "ok") {
            playOk();
            updateRow(packageCode, data.status);
            count++;
            blueCount++;
            updateCounters();
        } else {
            playError();
        }
    }

    async function removePackage(packageCode, rowElement) {
        const response = await sendPost(REMOVE_ENDPOINT, {
            package_code: packageCode
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

    input.addEventListener("keydown", async function (e) {
        if (e.key === "Enter") {
            e.preventDefault();

            const value = input.value.trim();
            if (!value) return;

            if (isPaused) {
                isPaused = false;
                applyRunningState();
                await sendSessionEvent("resume");
            }

            enqueueScan(value);
            input.value = "";
        }
    });

    resetCounter.addEventListener("click", function () {
        blueCount = 0;
        updateCounters();
    });

    if (pauseButton) {
        pauseButton.addEventListener("click", async function () {
            isPaused = true;
            applyPausedState();
            input.blur();
            await sendSessionEvent("pause");
        });
    }

    if (resumeButton) {
        resumeButton.addEventListener("click", async function () {
            isPaused = false;
            applyRunningState();
            input.focus();
            await sendSessionEvent("resume");
            processQueue();
        });
    }

    document.addEventListener("visibilitychange", async function () {
        if (document.hidden) {
            if (!isPaused) {
                isPaused = true;
                applyPausedState();
                await sendSessionEvent("pause");
            }
        }
    });

    window.addEventListener("beforeunload", function () {
        try {
            navigator.sendBeacon(
                `/api/conference/session/${session_id}/event/`,
                new Blob(
                    [JSON.stringify({ event_type: "finish" })],
                    { type: "application/json" }
                )
            );
        } catch (error) {
            console.error("Error sending finish beacon:", error);
        }
    });

    setInterval(() => {
        if (!isPaused && !document.hidden) {
            try {
                navigator.sendBeacon(
                    `/api/conference/session/${session_id}/event/`,
                    new Blob(
                        [JSON.stringify({ event_type: "heartbeat" })],
                        { type: "application/json" }
                    )
                );
            } catch (error) {
                console.error("Heartbeat error:", error);
            }
        }
    }, 30000);

    setTimeout(() => {
        input.focus();
    }, 300);

    input.focus();
    updateCounterDisplay();
    startTimer();
    applyRunningState();
    updateCounters();
    getConferenceItems();
    sendSessionEvent("resume");
});