var jsondata = null;

async function httpGetJson(url) {
    return fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch((e) => {
            console.log(
                "There was a problem with your fetch operation: " + e.message
            );
        });
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function refreshData() {
    while (true) {
        jsondata = await httpGetJson("http://127.0.0.1:5000/data");
        console.log(jsondata);

        total_load_active_power = jsondata["Total Load Active Power"];
        element_total_load_active_power = document.getElementById(
            "entry-aktueller-verbrauch"
        );
        if (element_total_load_active_power != null)
            element_total_load_active_power.innerHTML = total_load_active_power;

        total_dc_power = jsondata["Total DC Power"];
        element_total_dc_power = document.getElementById(
            "entry-aktuelle-produktion"
        );
        element_total_dc_power.innerHTML = total_dc_power;

        purchased_power = jsondata["Purchased Power"];
        element_purchased_power = document.getElementById("entry-netzbezug");
        element_purchased_power.innerHTML = purchased_power;

        total_exported_active_power = jsondata["Total Export Active Power"];
        element_total_exported_active_power = document.getElementById(
            "entry-netzeinspeisung"
        );
        element_total_exported_active_power.innerHTML =
            total_exported_active_power;

        await sleep(1000);
    }
}

async function handleMouseOver() {
    element_aktueller_verbrauch = document.getElementById(
        "aktueller-verbrauch"
    );
    element_aktueller_verbrauch.innerHTML = "";
    element_aktueller_verbrauch.className = "main-overview-full";
    element_aktueller_verbrauch.innerHTML =
        "<canvas id='current-graph'></canvas>";

    await document
        .getElementById("aktueller-verbrauch")
        .removeEventListener("mouseover", handleMouseOver);

    await drawCurrentGraph("Total Load Active Power");
}

function handleMouseOut() {
    element_aktueller_verbrauch = document.getElementById(
        "aktueller-verbrauch"
    );
    element_aktueller_verbrauch.innerHTML = "";
    element_aktueller_verbrauch.className = "main-overview";
    element_aktueller_verbrauch.innerHTML =
        '<li>Aktueller Verbrauch:</li><li id="entry-aktueller-verbrauch" class="entry"></li>';

    document
        .getElementById("aktueller-verbrauch")
        .removeEventListener("mouseout", handleMouseOut);

    document.addEventListener("mouseover", handleMouseOver);
}

async function drawCurrentGraph(parameter) {
    var ctx = document.getElementById("current-graph").getContext("2d");
    var myChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Data",
                    data: [],
                    backgroundColor: "rgba(0, 123, 255, 0.5)",
                    borderColor: "rgba(0, 123, 255, 1)",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            scales: {
                yAxes: [
                    {
                        ticks: {
                            beginAtZero: true,
                        },
                    },
                ],
            },
        },
    });

    all_data = await httpGetJson("http://127.0.0.1:5000/all_data");

    for (let i = 0; i < all_data.length; i++) {
        myChart.data.labels.push(new Date().toLocaleTimeString()); // Use the current time as the label
        myChart.data.datasets[0].data.push(
            all_data[i]["Total Load Active Power"].replace(" kW", "")
        ); // Add the new data to the dataset
    }
    myChart.update(); // Update the chart
}

document
    .getElementById("aktueller-verbrauch")
    .addEventListener("mouseover", handleMouseOver);

/*document
    .getElementById("aktueller-verbrauch")
    .addEventListener("mouseout", handleMouseOut);*/

refreshData();
