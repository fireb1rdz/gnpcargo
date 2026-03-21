jQuery(document).ready(function () {

    function loadChart(days) {

        $.ajax({
            url: "/logistica/conferencia/amount_packages_by_day/",
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