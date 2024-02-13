var jsondata = null;

function debounce(func, delay, ...args) {
    let debounceTimer;
    return function () {
        const context = this;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
}

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
        jsondata = await httpGetJson("http://192.168.178.56:5000/data");
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
        if (element_total_dc_power != null) {
            element_total_dc_power.innerHTML = total_dc_power;
        }

        self_consumption_rate = jsondata["Daily Self-consumption Rate"];
        element_self_consumption_rate = document.getElementById(
            "entry-eigenverbrauch"
        );
        if (element_self_consumption_rate != null) {
            element_self_consumption_rate.innerHTML = self_consumption_rate;
        }

        purchased_power = jsondata["Purchased Power"];
        element_purchased_power = document.getElementById("entry-netzbezug");
        if (element_purchased_power != null) {
            element_purchased_power.innerHTML = purchased_power;
        }

        total_exported_active_power = jsondata["Total Export Active Power"];
        element_total_exported_active_power = document.getElementById(
            "entry-netzeinspeisung"
        );
        if (element_total_exported_active_power != null) {
            element_total_exported_active_power.innerHTML =
                total_exported_active_power;
        }

        await sleep(1000);
    }
}

let isMouseOver = false;

async function handleMouseOver(caller_id, parameter) {
    if (!isMouseOver) {
        element_caller = document.getElementById(caller_id);
        element_caller.innerHTML = "";
        element_caller.className = "main-overview-full";
        element_caller.innerHTML = "<canvas id='current-graph'></canvas>";

        document
            .getElementById(caller_id)
            .removeEventListener("mouseover", debounce(handleMouseOver, 100));

        document
            .getElementById(caller_id)
            .addEventListener("mouseout", debounce(handleMouseOut, 100));

        console.log("handlemouseover");

        isMouseOver = true;

        await drawCurrentGraph(parameter);
    }
}

function handleMouseOut(caller_id) {
    if (isMouseOver) {
        element_caller = document.getElementById(caller_id);
        element_caller.innerHTML = "";
        element_caller.className = "main-overview";
        element_caller.innerHTML = `<li>${caller_id
            .replace(/-/g, " ")
            .replace(/\b\w/g, (c) =>
                c.toUpperCase()
            )}:</li><li id="entry-${caller_id}" class="entry"></li>`;

        document
            .getElementById(caller_id)
            .removeEventListener("mouseout", debounce(handleMouseOut, 100));

        document
            .getElementById(caller_id)
            .addEventListener("mouseover", debounce(handleMouseOver, 100));

        console.log("handleMouseOut");

        isMouseOver = false;
    }
}

async function drawCurrentGraph(parameter) {
    if (document.getElementById("current-graph")) {
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
                        pointStyle: "none",
                        pointRadius: 0,
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

        let all_data = await httpGetJson("http://192.168.178.56:5000/all_data");

        for (let i = 0; i < all_data.length; i++) {
            myChart.data.labels.push(all_data[i]["Timestamp"]); // Use the current time as the label
            myChart.data.datasets[0].data.push(all_data[i][parameter]); // Add the new data to the dataset
        }
        myChart.update(); // Update the chart
    }
}

//aktueller-verbrauch
document
    .getElementById("aktueller-verbrauch")
    .addEventListener(
        "mouseover",
        debounce(
            handleMouseOver,
            100,
            "aktueller-verbrauch",
            "Total Load Active Power"
        )
    );

document
    .getElementById("aktueller-verbrauch")
    .addEventListener(
        "mouseout",
        debounce(handleMouseOut, 100, "aktueller-verbrauch")
    );

//aktuelle-produktion
document
    .getElementById("aktuelle-produktion")
    .addEventListener(
        "mouseover",
        debounce(handleMouseOver, 100, "aktuelle-produktion", "Total DC Power")
    );

document
    .getElementById("aktuelle-produktion")
    .addEventListener(
        "mouseout",
        debounce(handleMouseOut, 100, "aktuelle-produktion")
    );

//aktuelle-produktion
document
    .getElementById("netzbezug")
    .addEventListener(
        "mouseover",
        debounce(handleMouseOver, 100, "netzbezug", "Purchased Power")
    );

document
    .getElementById("netzbezug")
    .addEventListener("mouseout", debounce(handleMouseOut, 100, "netzbezug"));

//netzeinspeisung
document
    .getElementById("netzeinspeisung")
    .addEventListener(
        "mouseover",
        debounce(
            handleMouseOver,
            100,
            "netzeinspeisung",
            "Total Export Active Power"
        )
    );

document
    .getElementById("netzeinspeisung")
    .addEventListener(
        "mouseout",
        debounce(handleMouseOut, 100, "netzeinspeisung")
    );

refreshData();
