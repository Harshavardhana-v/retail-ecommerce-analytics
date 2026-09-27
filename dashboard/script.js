const API_URL =
    "http://localhost:5000/api/top-products";

let salesChart = null;

let previousEventCount = null;

let eventHistory = [];

let recentEvents = [];


// ============================================================
// SYSTEM CLOCK
// ============================================================

function updateClock() {

    const now = new Date();

    const time =
        now.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

    document.getElementById("systemTime").textContent =
        time;
}

updateClock();

setInterval(updateClock, 1000);


// ============================================================
// FETCH DASHBOARD DATA
// ============================================================

async function fetchDashboardData() {

    try {

        const response =
            await fetch(API_URL);

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const data =
            await response.json();


        // ----------------------------------------------------
        // STATUS
        // ----------------------------------------------------

        document.getElementById("status").textContent =
            "LIVE";


        // ----------------------------------------------------
        // KPI CARDS
        // ----------------------------------------------------

        document.getElementById("window").textContent =
            `${data.window_minutes} Min`;

        document.getElementById("events").textContent =
            data.total_events_in_window;

        document.getElementById("totalEvents").textContent =
            data.total_events_received;

        document.getElementById("updated").textContent =
            formatTime(data.generated_at);


        // ----------------------------------------------------
        // EVENT NOTIFICATION
        // ----------------------------------------------------

        const notification =
            document.getElementById(
                "eventNotification"
            );

        if (previousEventCount === null) {

            notification.innerHTML =
                `<span class="notification-icon">✓</span>
                 <span>Stream connected — ${data.total_events_received} events received.</span>`;

        } else {

            const difference =
                data.total_events_received -
                previousEventCount;


            if (difference > 0) {

                notification.innerHTML =
                    `<span class="notification-icon">✓</span>
                     <span>${difference} new event(s) received — Stream is active</span>`;

            } else {

                notification.innerHTML =
                    `<span class="notification-icon">✓</span>
                     <span>Stream active — Waiting for new events...</span>`;
            }
        }

        


        // ----------------------------------------------------
        // TOP PRODUCTS
        // ----------------------------------------------------

        const products =
            data.top_products || [];

        updateChart(products);

        updateTable(products);


        // ----------------------------------------------------
        // LATEST EVENT
        // ----------------------------------------------------

        if (data.latest_event) {

            updateLatestEvent(
                data.latest_event
            );

            addEventToStream(
                data.latest_event
            );
        }


        // ----------------------------------------------------
        // ACTIVITY
        // ----------------------------------------------------

        updateActivity(
            data.total_events_received
        );

        previousEventCount =
         data.total_events_received;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        document.getElementById(
            "status"
        ).textContent = "OFFLINE";

        document.getElementById(
            "eventNotification"
        ).innerHTML =
            `<span class="notification-icon">!</span>
             <span>Unable to connect to analytics API</span>`;
    }
}


// ============================================================
// FORMAT TIME
// ============================================================

function formatTime(value) {

    if (!value) {
        return "-";
    }

    const date =
        new Date(value);

    if (isNaN(date)) {
        return value;
    }

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}


// ============================================================
// UPDATE CHART
// ============================================================

function updateChart(products) {

    const labels =
        products.map(
            product =>
                product.product_name
        );

    const values =
        products.map(
            product =>
                product.units_sold
        );


    const ctx =
        document
            .getElementById(
                "salesChart"
            )
            .getContext("2d");


    // --------------------------------------------------------
    // CREATE CHART FIRST TIME
    // --------------------------------------------------------

    if (!salesChart) {

        salesChart =
            new Chart(ctx, {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label: "Units Sold",

                            data: values,

                            borderWidth: 0,

                            borderRadius: 7,

                            backgroundColor:
                                "rgba(56, 189, 248, 0.72)",

                            hoverBackgroundColor:
                                "rgba(56, 189, 248, 1)"
                        }

                    ]
                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    indexAxis: "y",


                    animation: {
                        duration: 600
                    },


                    plugins: {

                        legend: {
                            display: false
                        },

                        tooltip: {

                            backgroundColor:
                                "rgba(7, 11, 20, 0.95)",

                            titleColor: "#f8fafc",

                            bodyColor: "#cbd5e1",

                            borderColor:
                                "rgba(255,255,255,0.1)",

                            borderWidth: 1,

                            padding: 12,

                            displayColors: false
                        }
                    },


                    scales: {

                        x: {

                            beginAtZero: true,

                            grid: {
                                color:
                                    "rgba(255,255,255,0.05)"
                            },

                            ticks: {
                                color: "#64748b",

                                font: {
                                    size: 10
                                }
                            }
                        },


                        y: {

                            grid: {
                                display: false
                            },

                            ticks: {

                                color: "#cbd5e1",

                                font: {
                                    size: 10
                                }
                            }
                        }
                    }
                }
            });

        return;
    }


    // --------------------------------------------------------
    // UPDATE EXISTING CHART
    // --------------------------------------------------------

    salesChart.data.labels =
        labels;

    salesChart.data.datasets[0].data =
        values;

    salesChart.update();
}


// ============================================================
// UPDATE PRODUCT TABLE
// ============================================================

function updateTable(products) {

    const table =
        document.getElementById(
            "productTable"
        );


    table.innerHTML = "";


    if (!products.length) {

        table.innerHTML =
            `<tr>
                <td colspan="5">
                    No product data available
                </td>
             </tr>`;

        return;
    }


    const totalUnits =
        products.reduce(
            (sum, product) =>
                sum + Number(product.units_sold || 0),
            0
        );


    products.forEach(
        (product, index) => {

            const row =
                document.createElement("tr");


            const rank =
                index + 1;


            let rankDisplay =
                rank;


            if (rank === 1) {
                rankDisplay = "🥇";
            } else if (rank === 2) {
                rankDisplay = "🥈";
            } else if (rank === 3) {
                rankDisplay = "🥉";
            }


            const share =
                totalUnits > 0
                    ? (
                        Number(product.units_sold)
                        / totalUnits
                        * 100
                    ).toFixed(1)
                    : "0.0";


            row.innerHTML = `

                <td class="rank ${rank <= 3 ? "top" : ""}">
                    ${rankDisplay}
                </td>

                <td class="product-name">
                    ${escapeHtml(product.product_name)}
                </td>

                <td class="product-id">
                    #${product.product_id}
                </td>

                <td class="units">
                    ${product.units_sold}
                </td>

                <td class="share">
                    ${share}%
                </td>
            `;


            table.appendChild(row);
        }
    );
}


// ============================================================
// LATEST EVENT
// ============================================================

function updateLatestEvent(event) {

    const product =
        event.product_name ||
        "Unknown Product";


    document.getElementById(
        "latestProduct"
    ).textContent =
        product;


    document.getElementById(
        "latestProductId"
    ).textContent =
        event.product_id ?? "-";


    document.getElementById(
        "latestQuantity"
    ).textContent =
        event.quantity ?? 1;


    document.getElementById(
        "latestTime"
    ).textContent =
        formatTime(event.event_time);
}


// ============================================================
// LIVE EVENT STREAM
// ============================================================

function addEventToStream(event) {

    if (!event) {
        return;
    }


    const eventKey =
        `${event.product_id}-${event.event_time}`;


    // Prevent duplicate events

    if (
        recentEvents.some(
            item =>
                item.key === eventKey
        )
    ) {
        return;
    }


    recentEvents.unshift({

        key: eventKey,

        product_name:
            event.product_name,

        event_time:
            event.event_time
    });


    // Keep only latest 8 events

    recentEvents =
        recentEvents.slice(0, 8);


    renderEventStream();
}


function renderEventStream() {

    const container =
        document.getElementById(
            "eventList"
        );


    const count =
        document.getElementById(
            "streamCount"
        );


    count.textContent =
        `${recentEvents.length} recent`;


    if (!recentEvents.length) {

        container.innerHTML =
            `<div class="empty-stream">
                Waiting for events...
             </div>`;

        return;
    }


    container.innerHTML =
        recentEvents
            .map(
                event => `

                <div class="event-item">

                    <span class="event-dot"></span>

                    <span class="event-name">
                        ${escapeHtml(event.product_name)}
                    </span>

                    <span class="event-time">
                        ${formatTime(event.event_time)}
                    </span>

                </div>
            `
            )
            .join("");
}


// ============================================================
// ACTIVITY BARS
// ============================================================

function updateActivity(totalEventsReceived) {

    const currentCount =
        Number(totalEventsReceived) || 0;

    let newEvents = 0;

    // First API request
    if (previousEventCount === null) {

        newEvents = 0;

    } else {

        // Calculate how many NEW events arrived
        // since the previous dashboard refresh
        newEvents =
            Math.max(
                0,
                currentCount - previousEventCount
            );
    }

    // Store this refresh interval
    eventHistory.push(newEvents);

    // Keep only latest 30 intervals
    if (eventHistory.length > 30) {

        eventHistory =
            eventHistory.slice(-30);
    }

    const container =
        document.getElementById(
            "activityBars"
        );

    if (!eventHistory.length) {
        return;
    }

    const max =
        Math.max(
            ...eventHistory,
            1
        );

    container.innerHTML =
        eventHistory
            .map(
                value => {

                    const height =
                        Math.max(
                            5,
                            (value / max) * 100
                        );

                    return `
                        <div
                            class="activity-bar"
                            style="height: ${height}%"
                            title="${value} new events"
                        ></div>
                    `;
                }
            )
            .join("");
}


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// INITIAL LOAD
// ============================================================

fetchDashboardData();


// ============================================================
// REFRESH
// ============================================================

// 5 seconds for demonstration.
// Project requirement can remain 5 minutes.

setInterval(
    fetchDashboardData,
    5 * 1000
);