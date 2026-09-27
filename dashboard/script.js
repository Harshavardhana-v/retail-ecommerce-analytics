const API_URL =
    "http://localhost:5000/api/top-products";

let salesChart = null;
let previousEventCount = null;


// ============================================================
// FETCH DATA
// ============================================================

async function fetchDashboardData() {

    try {

        const response =
            await fetch(API_URL);

        if (!response.ok) {

            throw new Error(
                "API request failed"
            );
        }

        const data =
            await response.json();


        // Update status

        document.getElementById(
            "status"
        ).textContent = "LIVE";


        // Update summary

        document.getElementById(
            "window"
        ).textContent =
            `${data.window_minutes} Minutes`;


        document.getElementById(
            "events"
        ).textContent =
            data.total_events_in_window;

        document.getElementById(
            "totalEvents"
        ).textContent =
            data.total_events_received;



        // ============================================================
// EVENT NOTIFICATION
// ============================================================

const notification =
    document.getElementById(
        "eventNotification"
    );

if (previousEventCount === null) {

    notification.textContent =
        `✓ Stream connected — ${data.total_events_received} events received so far.`;

} else {

    const difference =
        data.total_events_received -
        previousEventCount;

    if (difference > 0) {

        notification.textContent =
            `✓ ${difference} new event(s) received — Event time: ${data.window_end}`;

    } else {

        notification.textContent =
            `✓ Stream active — Event time: ${data.window_end}`;

    }

}

previousEventCount =
    data.total_events_received;


        document.getElementById(
            "updated"
        ).textContent =
            data.generated_at;


        // Update chart

        updateChart(
            data.top_products
        );


        // Update table

        updateTable(
            data.top_products
        );


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        document.getElementById(
            "status"
        ).textContent = "OFFLINE";

    }

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


    // Destroy previous chart

    if (salesChart) {

        salesChart.destroy();

    }


    // Create new chart

    salesChart =
        new Chart(ctx, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [

                    {

                        label:
                            "Units Sold",

                        data: values,

                        borderWidth: 1

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                indexAxis: "y",

                plugins: {

                    legend: {

                        display: true

                    }

                },

                scales: {

                    x: {

                        beginAtZero: true

                    }

                }

            }

        });

}


// ============================================================
// UPDATE TABLE
// ============================================================

function updateTable(products) {

    const table =
        document.getElementById(
            "productTable"
        );


    table.innerHTML = "";


    products.forEach(
        (product, index) => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${index + 1}
                </td>

                <td>
                    ${product.product_name}
                </td>

                <td>
                    ${product.product_id}
                </td>

                <td>
                    <strong>
                        ${product.units_sold}
                    </strong>
                </td>

            `;


            table.appendChild(row);

        }
    );

}


// ============================================================
// INITIAL LOAD
// ============================================================

fetchDashboardData();


// ============================================================
// REFRESH EVERY 5 MINUTES
// ============================================================

setInterval(

    fetchDashboardData,

    5 * 1000

);