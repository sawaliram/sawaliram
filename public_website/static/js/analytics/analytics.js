bar_color = "#FEB740";

var ctx = document.getElementById('nos_qestions_graph');

var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels_lang,
        datasets: [{
            label: '# Questions',
            data: data_lang,
            backgroundColor: bar_color,
            borderWidth: 0.5,
            minHeight: 5,
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    steps: 10,
                }
            }]
        },
   
    }
});

var current_clicked = "#g_lang";

$('#param-choice input:radio').click(function() {
   current_click = $(this).val();

    if (current_click == "g_lang"){
        //$(current_clicked).css("background-color", "white");
        current_clicked = "#g_lang";
        //$(current_clicked).css("background-color", "lightblue");
        myChart.data.datasets[0].data = data_lang;
        myChart.data.labels = labels_lang;
        myChart.update();
    }

    else if (current_click == "g_gender"){
        //$(current_clicked).css("background-color", "white");
        current_clicked = "#g_gender";
        //$(current_clicked).css("background-color", "lightblue");
        myChart.data.datasets[0].data = data_gender;
        myChart.data.labels = labels_gender;

        myChart.update();
    }
    else if (current_click == "g_class"){
        //$(current_clicked).css("background-color", "white");
        current_clicked = "#g_class";
        //$(current_clicked).css("background-color", "lightblue");
        myChart.data.datasets[0].data = data_class;
        myChart.data.labels = labels_class;

        myChart.update();
    }

    else if (current_click == "g_medium"){
        //$(current_clicked).css("background-color", "white");
        current_clicked = "#g_medium";
        //$(current_clicked).css("background-color", "lightblue");
        myChart.data.datasets[0].data = data_medium;
        myChart.data.labels = labels_medium;

        myChart.update();
    }

    else if (current_click == "g_year"){
        //$(current_clicked).css("background-color", "white");
        current_clicked = "#g_year";
        //$(current_clicked).css("background-color", "lightblue");
        myChart.data.datasets[0].data = data_year;
        myChart.data.labels = labels_year;
        myChart.update();
    }
});

var ctx_fomat  = document.getElementById("doughnut-fomat");
var ctx_curriculum  = document.getElementById("doughnut-curriculum");
var ctx_context  = document.getElementById("doughnut-context");
var bg_colors = ["orange", "lightgreen", "blue", "pink", "lightgoldenrodyellow", "yellow"]; //Some arbitrary list of colors for all doughnut charts.

var fomatDoughnutChart = new Chart(ctx_fomat, {
    type: 'doughnut',
    data: {
    datasets: [{
        data: data_format,
        backgroundColor: bg_colors,
    }],
    labels: labels_format
},
   options: {
        legend: {
            position: "bottom",
        },

        title : {
            display: true,
            text: "How was the question originally asked?"
        }
    }
});

var curriculumDoughnutChart = new Chart(ctx_curriculum, {
    type: 'doughnut',
    data: {
    datasets: [{
        data: data_curriculum,
        backgroundColor: bg_colors,
    }],
    labels: labels_curriculum
},
    options: {
        legend: {
            position: "bottom",
        },

        title : {
            display: true,
            text: "Curriculum Followed"
        }
    }
});

var contextDoughnutChart = new Chart(ctx_context, {
    type: 'doughnut',
    data: {
    datasets: [{
        data: data_context,
        backgroundColor: bg_colors,
    }],
    labels: labels_context
},
    options: {
        legend: {
            position: "bottom",
        },

        title : {
            display: true,
            text: "Context"
        }
    }
});



