document.addEventListener('DOMContentLoaded', function() {
    // Initialize Booking Trends Line Chart
    function initializeBookingTrendChart() {
        const ctx = document.getElementById('bookingTrendsChart');
        if (!ctx) return;

        const months = JSON.parse(ctx.dataset.months);
        const counts = JSON.parse(ctx.dataset.counts);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Bookings per Month',
                    data: counts,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Initialize Payment Methods Pie Chart
    function initializePaymentMethodsChart() {
        const ctx = document.getElementById('paymentMethodsChart');
        if (!ctx) return;

        const labels = JSON.parse(ctx.dataset.labels);
        const data = JSON.parse(ctx.dataset.data);

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
                        '#e74a3b', '#858796', '#5a5c69'
                    ],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: $${context.raw.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize Spending Breakdown Doughnut Chart
    function initializeSpendingCategoryChart() {
        const ctx = document.getElementById('spendingCategoryChart');
        if (!ctx) return;

        const labels = JSON.parse(ctx.dataset.labels);
        const data = JSON.parse(ctx.dataset.data);

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#4e73df', '#1cc88a', '#f6c23e', '#36b9cc',
                        '#e74a3b', '#858796', '#5a5c69'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: $${context.raw.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize all charts
    initializeBookingTrendChart();
    initializePaymentMethodsChart();
    initializeSpendingCategoryChart();

    // Responsive chart resizing
    window.addEventListener('resize', function() {
        Chart.getRegisteredComponents().forEach(chart => {
            chart.resize();
        });
    });
}); 