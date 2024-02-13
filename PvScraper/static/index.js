var ctx = document.getElementById("myChart").getContext("2d");
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

setInterval(function () {
    $.get("http://192.168.178.56:5000/data", function (data) {
        // Find the array that contains "Total Load Active Power"
        var totalLoadActivePowerArray = data.find(function (item) {
            return item[0] === "Total Load Active Power";
        });

        // Extract the power value and convert it to a number
        var totalLoadActivePower = Number(
            totalLoadActivePowerArray[1].split(" ")[0]
        );

        myChart.data.labels.push(new Date().toLocaleTimeString()); // Use the current time as the label
        myChart.data.datasets[0].data.push(totalLoadActivePower); // Add the new data to the dataset
        if (myChart.data.labels.length > 1000) {
            // Limit to 10 points
            myChart.data.labels.shift(); // Remove first label
            myChart.data.datasets[0].data.shift(); // Remove first data point
        }
        myChart.update(); // Update the chart
    });
}, 1000);
