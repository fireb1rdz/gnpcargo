jQuery(document).ready(function () {

    const charts = {};

    function fmtDuration(seconds) {
        seconds = parseInt(seconds || 0);
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h}h ${m}m ${s}s`;
    }

    function destroyChart(id) {
        if (charts[id]) {
            charts[id].destroy();
        }
    }

    function makeBarChart(canvasId, labels, data, labelText) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        destroyChart(canvasId);
        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: data,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    function makeLineChart(canvasId, labels, data, labelText) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        destroyChart(canvasId);
        charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: data,
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    function makePieChart(canvasId, labels, data, labelText) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        destroyChart(canvasId);
        charts[canvasId] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: labelText,
                    data: data,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    function loadConferencesInProgress() {
        $.getJSON("/api/conferences-in-progress/", function (response) {
            const tbody = $("#table-conferences-in-progress tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.started_by}</td>
                        <td>${row.start_date}</td>
                        <td>${fmtDuration(row.elapsed_seconds)}</td>
                        <td>${row.read_items}/${row.total_items}</td>
                    </tr>
                `);
            });
        });
    }

    function loadAverageConferenceTime() {
        $.getJSON("/api/average-conference-time/", function (response) {
            makeBarChart(
                "chart-average-time-user",
                response.by_user.map(x => x.label),
                response.by_user.map(x => x.avg_seconds),
                "Tempo médio por usuário (segundos)"
            );
            makeBarChart(
                "chart-average-time-type",
                response.by_event_type.map(x => x.label),
                response.by_event_type.map(x => x.avg_seconds),
                "Tempo médio por tipo (segundos)"
            );
        });
    }

    function loadConferencesWithProblem() {
        $.getJSON("/api/conferences-with-problem/", function (response) {
            const tbody = $("#table-conferences-with-problem tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.problem_type}</td>
                        <td>${row.faulty_items}</td>
                        <td>${row.pending_items}</td>
                        <td>${row.total_items}</td>
                        <td>${row.error_rate}%</td>
                    </tr>
                `);
            });
        });
    }

    function loadPendingItems() {
        $.getJSON("/api/pending-items-by-conference/", function (response) {
            const tbody = $("#table-pending-items tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.status}</td>
                        <td>${row.pending_items}</td>
                        <td>${row.total_items}</td>
                        <td>${row.last_read_at}</td>
                    </tr>
                `);
            });
        });
    }

    function loadFaultyGrouped() {
        $.getJSON("/api/faulty-items-grouped/", function (response) {
            makeBarChart(
                "chart-faulty-packages",
                response.by_package.map(x => x.label),
                response.by_package.map(x => x.total),
                "Falhas por pacote"
            );
        });
    }

    function loadErrorRateRankings() {
        $.getJSON("/api/error-rate-rankings/", function (response) {
            makeBarChart(
                "chart-error-rate-origin",
                response.by_origin.map(x => x.label),
                response.by_origin.map(x => x.error_rate),
                "% erro por fornecedor"
            );
        });
    }

    function loadOperatorPerformance() {
        $.getJSON("/api/operator-performance/", function (response) {
            const tbody = $("#table-operator-performance tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.operator}</td>
                        <td>${row.conferences}</td>
                        <td>${fmtDuration(row.avg_seconds)}</td>
                        <td>${row.error_rate}%</td>
                    </tr>
                `);
            });
        });
    }

    function loadVolumeByType() {
        $.getJSON("/api/volume-by-operation-type/?days=30", function (response) {
            makePieChart(
                "chart-volume-operation-type",
                response.labels,
                response.data,
                "Volume por tipo"
            );
        });
    }

    function loadConferencesByPeriod() {
        $.getJSON("/api/conferences-by-period/?days=90&period=day", function (response) {
            makeLineChart(
                "chart-conferences-period",
                response.labels,
                response.data,
                "Conferências por dia"
            );
        });
    }

    function loadDerivedConferences() {
        $.getJSON("/api/derived-conferences/", function (response) {
            const tbody = $("#table-derived-conferences tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.parent_id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.event_type}</td>
                        <td>${row.status}</td>
                        <td>${row.total_items}</td>
                    </tr>
                `);
            });
        });
    }

    function loadProblematicSuppliers() {
        $.getJSON("/api/problematic-suppliers/", function (response) {
            makeBarChart(
                "chart-problematic-suppliers",
                response.results.map(x => x.supplier),
                response.results.map(x => x.faulty_rate),
                "% falha por fornecedor"
            );
        });
    }

    function loadProductsWithDivergence() {
        $.getJSON("/api/products-with-divergence/", function (response) {
            makeBarChart(
                "chart-products-divergence",
                response.results.map(x => x.package),
                response.results.map(x => x.total_faulty),
                "Falhas por pacote"
            );
        });
    }

    function loadIdleTime() {
        $.getJSON("/api/idle-time-conferences/", function (response) {
            const tbody = $("#table-idle-time tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.started_by}</td>
                        <td>${row.unread_items}</td>
                        <td>${row.total_items}</td>
                        <td>${row.last_read_at}</td>
                        <td>${fmtDuration(row.idle_seconds)}</td>
                    </tr>
                `);
            });
        });
    }

    function loadFullFlow() {
        $.getJSON("/api/full-flow-load-unload/", function (response) {
            const tbody = $("#table-full-flow tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.parent_id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.parent_event_type}</td>
                        <td>${row.loads}</td>
                        <td>${row.unloads}</td>
                        <td>${row.derived_total}</td>
                    </tr>
                `);
            });
        });
    }

    function loadCancelled() {
        $.getJSON("/api/cancelled-conferences/", function (response) {
            const tbody = $("#table-cancelled tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.id}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                        <td>${row.created_by}</td>
                        <td>${row.created_at}</td>
                        <td>${row.updated_at}</td>
                    </tr>
                `);
            });
        });
    }

    function loadSla() {
        $.getJSON("/api/conference-sla/", function (response) {
            const within = response.results.filter(x => x.within_sla).length;
            const out = response.results.filter(x => !x.within_sla).length;
            makePieChart(
                "chart-sla",
                ["Dentro do SLA", "Fora do SLA"],
                [within, out],
                "SLA"
            );
        });
    }

    function loadAudit() {
        $.getJSON("/api/full-audit/", function (response) {
            const tbody = $("#table-audit tbody");
            tbody.empty();
            response.results.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row.conference_id}</td>
                        <td>${row.package_id}</td>
                        <td>${row.read_by}</td>
                        <td>${row.read_at}</td>
                        <td>${row.status}</td>
                        <td>${row.origin}</td>
                        <td>${row.destination}</td>
                    </tr>
                `);
            });
        });
    }

    function loadHeatmap() {
        $.getJSON("/api/errors-heatmap/", function (response) {
            const labels = response.results.map(x => `${x.hour}h - ${x.operator}`);
            const data = response.results.map(x => x.total);
            makeBarChart(
                "chart-errors-heatmap",
                labels,
                data,
                "Erros por hora/operador"
            );
        });
    }

    loadConferencesInProgress();
    loadAverageConferenceTime();
    loadConferencesWithProblem();
    loadPendingItems();
    loadFaultyGrouped();
    loadErrorRateRankings();
    loadOperatorPerformance();
    loadVolumeByType();
    loadConferencesByPeriod();
    loadDerivedConferences();
    loadProblematicSuppliers();
    loadProductsWithDivergence();
    loadIdleTime();
    loadFullFlow();
    loadCancelled();
    loadSla();
    loadAudit();
    loadHeatmap();

    setInterval(loadConferencesInProgress, 60000);
    setInterval(loadIdleTime, 60000);
    setInterval(loadFullFlow, 60000);
    setInterval(loadCancelled, 60000);
    setInterval(loadSla, 60000);
    setInterval(loadAudit, 60000);
    setInterval(loadHeatmap, 60000);
    function loadChart(days) {

        $.ajax({
            url: "/api/conferencia/amount_packages_by_day/",
            method: "GET",
            data: {
                days: days
            },
            success: function (response) {

                const ctx = document.getElementById('volumes-by-day');

                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: response.labels,
                        datasets: [{
                            label: `Volumes (últimos ${response.days} dias)`,
                            data: response.data,
                            borderWidth: 2,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });

            },
            error: function (error) {
                console.error("Erro ao carregar dados:", error);
            }
        });
    }

    // exemplo: últimos 30 dias
    const days = 30;
    loadChart(days);

});