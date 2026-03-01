var ctxDoughnut = document.getElementById('surveyDoughnut').getContext('2d');

var ctxBar = document.getElementById('surveyBar').getContext('2d');

var doughnutChart = new Chart(ctxDoughnut, {
    type: 'doughnut',
    options: {
        plugins: {
            legend: {
                display: true,
                position: 'bottom',
                onClick: function(event, legendItem) {}
            }, layout: {
                padding: 20
            }
        }
    },
    data: {
        labels: [
            'Food',
            'Home',
            'Stuff',
            'Travel',
        ], font: {
            size: 20
        },
        datasets: [{
            label: 'Survey Results',
            data: [30, 10, 20, 40],
            backgroundColor: [
                '#EC6B56',
                '#FFC154',
                '#118AB2',
                '#47B39C'
            ],
            hoverOffset: 4,
        }]
    }
});

var barChart = new Chart(ctxBar, {
    type: 'bar',
    options: {
        aspectRatio: 1,
        plugins: {
            legend: {
                display: false,
                position: 'bottom'
            }, layout: {
                padding: 20
            }, scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    },
    data: {
        labels: [
            'World average',
            'Country average',
            'Your carbon footprint',
        ], font: {
            size: 20
        },
        datasets: [{
            label: '',
            data: [32, 50, 55],
            backgroundColor: [
                '#EC6B56',
                '#FFC154',
                '#118AB2',
            ],
            hoverOffset: 4,
        }]
    }
});


