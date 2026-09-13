let charts = {};

function money(x) {
    return "₹" + Number(x).toLocaleString("en-IN", {
        maximumFractionDigits: 0
    });
}

function destroy(name) {
    if (charts[name]) {
        charts[name].destroy();
        delete charts[name];
    }
}

/* =========================
   ANALYTICS CHARTS
========================= */

async function loadAnalytics() {
    try {
        const a = await fetch("/api/analytics").then(r => r.json());

        /* Location Chart */
        const locationCanvas = document.getElementById("locationChart");

        if (locationCanvas) {
            destroy("location");

            charts.location = new Chart(locationCanvas, {
                type: "bar",
                data: {
                    labels: a.locations,
                    datasets: [{
                        label: "Average Price",
                        data: a.location_prices
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return money(value);
                                }
                            }
                        }
                    }
                }
            });
        }

        /* Distribution Chart */
        const distributionCanvas =
            document.getElementById("distributionChart");

        if (distributionCanvas) {
            destroy("distribution");

            charts.distribution = new Chart(distributionCanvas, {
                type: "line",
                data: {
                    labels: a.distribution_labels,
                    datasets: [{
                        label: "Number of Properties",
                        data: a.distribution_values,
                        fill: true
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }

        /* Bedroom Chart */
        const bedroomCanvas =
            document.getElementById("bedroomChart");

        if (bedroomCanvas) {
            destroy("bedroom");

            charts.bedroom = new Chart(bedroomCanvas, {
                type: "bar",
                data: {
                    labels: a.bedrooms,
                    datasets: [{
                        label: "Average Price",
                        data: a.bedroom_prices
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            ticks: {
                                callback: function(value) {
                                    return money(value);
                                }
                            }
                        }
                    }
                }
            });
        }

        /* Actual vs Predicted */
        const e = await fetch("/api/evaluation").then(r => r.json());

        const actualCanvas =
            document.getElementById("actualChart");

        if (actualCanvas && e.actual && e.predicted) {
            destroy("actual");

            charts.actual = new Chart(actualCanvas, {
                type: "scatter",
                data: {
                    datasets: [{
                        label: "Actual vs Predicted",
                        data: e.actual.map((x, i) => ({
                            x: x,
                            y: e.predicted[i]
                        }))
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: "Actual Price"
                            },
                            ticks: {
                                callback: function(value) {
                                    return money(value);
                                }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: "Predicted Price"
                            },
                            ticks: {
                                callback: function(value) {
                                    return money(value);
                                }
                            }
                        }
                    }
                }
            });
        }

    } catch (error) {
        console.error("Analytics error:", error);
    }
}


/* =========================
   PREDICTION RESULT CHARTS
========================= */

function updatePredictionCharts(area, price, marketAverage) {

    const compareCanvas =
        document.getElementById("compareChart");

    const areaCanvas =
        document.getElementById("areaChart");

    if (!compareCanvas || !areaCanvas) {
        return;
    }

    /* -------------------------
       YOUR PROPERTY VS MARKET
    ------------------------- */

    destroy("compare");

    charts.compare = new Chart(compareCanvas, {
        type: "bar",

        data: {
            labels: [
                "Your Property",
                "Market Average"
            ],

            datasets: [{
                label: "Price",
                data: [
                    Number(price),
                    Number(marketAverage)
                ]
            }]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return money(context.raw);
                        }
                    }
                }
            },

            scales: {
                y: {
                    beginAtZero: true,

                    ticks: {
                        callback: function(value) {
                            return money(value);
                        }
                    }
                }
            }
        }
    });


    /* -------------------------
       AREA VS PRICE
    ------------------------- */

    fetch("/api/analytics")
        .then(response => response.json())
        .then(a => {

            destroy("area");

            let propertyData = [];

            if (a.area && a.price) {
                propertyData = a.area.map((x, i) => ({
                    x: Number(x),
                    y: Number(a.price[i])
                }));
            }

            charts.area = new Chart(areaCanvas, {

                type: "scatter",

                data: {

                    datasets: [

                        {
                            label: "Properties",

                            data: propertyData,

                            pointRadius: 4
                        },

                        {
                            label: "Your Property",

                            data: [{
                                x: Number(area),
                                y: Number(price)
                            }],

                            pointRadius: 9,
                            pointHoverRadius: 12
                        }

                    ]
                },

                options: {

                    responsive: true,

                    plugins: {

                        tooltip: {

                            callbacks: {

                                label: function(context) {

                                    return (
                                        "Area: " +
                                        context.parsed.x +
                                        " sq.ft | Price: " +
                                        money(context.parsed.y)
                                    );
                                }
                            }
                        }
                    },

                    scales: {

                        x: {

                            title: {
                                display: true,
                                text: "Area (sq.ft.)"
                            }

                        },

                        y: {

                            title: {
                                display: true,
                                text: "Price"
                            },

                            ticks: {

                                callback: function(value) {
                                    return money(value);
                                }
                            }
                        }
                    }
                }
            });

        })

        .catch(error => {
            console.error("Area chart error:", error);
        });
}


/* =========================
   MODEL PERFORMANCE
========================= */

async function loadModel() {

    try {

        const m =
            await fetch("/api/model-performance")
                .then(r => r.json());

        console.log("Model Performance:", m);

    } catch (error) {

        console.error(
            "Model performance error:",
            error
        );
    }
}


/* =========================
   HISTORY
========================= */

async function loadHistory() {

    try {

        const h =
            await fetch("/api/history")
                .then(r => r.json());

        const body =
            document.getElementById("historyBody");

        if (!body) {
            return;
        }

        body.innerHTML = h.map(x => `

            <tr>

                <td>${x.created_at}</td>

                <td>${x.location}</td>

                <td>${x.area}</td>

                <td>${x.bedrooms}</td>

                <td>${x.bathrooms}</td>

                <td>${money(x.predicted_price)}</td>

            </tr>

        `).join("");

    } catch (error) {

        console.error(
            "History error:",
            error
        );
    }
}


/* =========================
   CLEAR HISTORY
========================= */

async function clearHistory() {

    try {

        await fetch(
            "/api/history/clear",
            {
                method: "DELETE"
            }
        );

        loadHistory();

    } catch (error) {

        console.error(
            "Clear history error:",
            error
        );
    }
}


/* =========================
   PAGE LOAD
========================= */

loadAnalytics();
loadModel();
loadHistory();