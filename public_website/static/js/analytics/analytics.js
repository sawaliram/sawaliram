bar_color = "#FEB740";
$(".hidden").hide();

var ctx = document.getElementById('nos_questions_graph');

var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels_lang,
        datasets: [{
            label: '#Questions',
            data: data_lang,
            backgroundColor: bar_color,
            borderWidth: 0.5,
            minHeight: 5,
        }]
    },
    options: {
        maintainAspectRatio : true,
        scales: {
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '#Questions'
                  },
                ticks: {
                    beginAtZero: true,
                    steps: 10,
                }
            }]
        },
   
    }
});


var dataset_without_filter = [{
            label: '#Questions',
            data: data_lang,
            backgroundColor: bar_color,
            borderWidth: 0.5,
            minHeight: 5,
        }];


function createGenderLanguageDatasets(){
        gender = ["Male", "Female", "NA"];
        male = [];
        female = [];
        na = [];
        for (lang_index in labels_lang){
                lang = labels_lang[lang_index];
                male.push(languageGenderDictionary[lang].Male);
                female.push(languageGenderDictionary[lang].Female);
                na.push(languageGenderDictionary[lang].NA);
            
        }

        var gender_lang_datasets =  [{
            label: 'Male',
            data: male,
            backgroundColor : "#c7ea46",
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Female',
            data: female,
            backgroundColor : "#e30ff6",
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'No Account',
            backgroundColor: "#ff8c00",
            data: na,
            borderWidth: 0.5,
            minHeight: 5,
        },
        ]
        return gender_lang_datasets;
}

function createGenderSubjectDatasets() {
        genders = ["Male", "Female", "NA"];
        maths = [];
        physics = [];
        chemistry = [];
        biology = [];

        for (gender_index in genders){
                gender = genders[gender_index];
                maths.push(genderSubjectDictionary[gender].Mathematics);
                physics.push(genderSubjectDictionary[gender].Physics);
                chemistry.push(genderSubjectDictionary[gender].Chemistry);
                biology.push(genderSubjectDictionary[gender].Biology);  
        }

        var gender_subject_datasets =  [{
            label: 'Mathematics',
            data: maths,
            backgroundColor : "#c7ea46",
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Physics',
            data: physics,
            backgroundColor : "#abcff6",
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Chemistry',
            backgroundColor: "#ff8c00",
            data: chemistry,
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Biology',
            backgroundColor: "#ff8cdf",
            data: biology,
            borderWidth: 0.5,
            minHeight: 5,
        },
        ]
        return gender_subject_datasets;
}


var gender_lang_datasets = createGenderLanguageDatasets();
var gender_subject_datasets = createGenderSubjectDatasets();

$("#lang_gender_split").click(function (){
        myChart.data.datasets = gender_lang_datasets;
        myChart.data.labels = labels_lang;
        myChart.update();
});

$("#gender_pcmb_split").click(function (){
        myChart.data.datasets = gender_subject_datasets;
        myChart.data.labels = labels_gender;
        myChart.update(); 
});

var current_clicked = "g_lang";
current_clicked_index = 0;
graphs_name = ["g_lang", "g_gender", "g_class", "g_medium", "g_year", "g_curriculum"];

var graphs = {
    g_lang: {
        data : data_lang,
        labels: labels_lang,
    },
    g_gender: {
        data : data_gender,
        labels: labels_gender,
    },
    g_class: {
        data : data_class,
        labels: labels_class,
    },
    g_medium: {
        data : data_medium,
        labels: labels_medium,
    },
    g_year: {
        data : data_year,
        labels: labels_year,
    },
    g_curriculum: {
        data : data_curriculum,
        labels: labels_curriculum,
    }
};

//Swiping for Mobile and Touch Devices
$(function() {      
      $("#graph-swipe").add("#graph-title").swipe( {
        swipeLeft:function(event, direction, distance, duration, fingerCount, fingerData) {
           old_clicked = current_clicked;
           $('.left-arrow').css("border-color", "green");
           myChart.data.datasets = dataset_without_filter;
           setTimeout(function(){$('.left-arrow').css("border-color","black");}, 300); //animating the arrows
           $('#graph-title').addClass("fadeOutLeft");
           current_clicked_index = (current_clicked_index + 1)%graphs_name.length;
           current_clicked = graphs_name[current_clicked_index];
           if (old_clicked == current_clicked) return;
           changeGraph(old_clicked, current_clicked);

           setTimeout(function(){
            $('#graph-title').removeClass("fadeOutLeft");
            $('#graph-title').html($("#" + current_clicked).attr("data-title"));
            $('#graph-title').addClass("fadeInRight");
            setTimeout(function(){ 
                $('#graph-title').removeClass("fadeInRight");
             }, 300);
        }, 300);
        },

        swipeRight:function(event, direction, distance, duration, fingerCount, fingerData) {
           old_clicked = current_clicked;
           myChart.data.datasets = dataset_without_filter;
           $('.right-arrow').css("border-color", "green");
           setTimeout(function(){$('.right-arrow').css("border-color", "black");}, 200);
           $('#graph-title').addClass("fadeOutRight");
           if (current_clicked_index == 0) current_clicked_index = graphs_name.length;
           current_clicked_index = (current_clicked_index - 1)%graphs_name.length;
           current_clicked = graphs_name[current_clicked_index];
           if (old_clicked == current_clicked) return;
           changeGraph(old_clicked, current_clicked); //Modify the graph

           setTimeout(function(){
            $('#graph-title').removeClass("fadeOutRight");
            $('#graph-title').html($("#" + current_clicked).attr("data-title"));
            $('#graph-title').addClass("fadeInLeft");
            setTimeout(function(){ 
                $('#graph-title').removeClass("fadeInLeft");
            }, 400);

        }, 300);
            },
        threshold:30,
    })
});
        


$('#param-choice input:radio').click(function() {
    old_clicked = current_clicked;
    myChart.data.datasets = dataset_without_filter;
    current_clicked = $(this).val();
    if (old_clicked == current_clicked) return;
    changeGraph(old_clicked, current_clicked);
    $('#graph-title').addClass("fadeOutLeft");
    setTimeout(function(){
        $('#graph-title').removeClass("fadeOutLeft");
        $('#graph-title').html($("#" + current_clicked).attr("data-title"));
        $('#graph-title').addClass("fadeInLeft");
        setTimeout(function(){ 
                $('#graph-title').removeClass("fadeInLeft");
            }, 500);
    }, 500);
    
});

function changeGraph(old_clicked, current_clicked){
    myChart.data.datasets = dataset_without_filter;
    $('.' + old_clicked + "_filter").addClass("fadeOutLeft");
    myChart.data.datasets[0].data = graphs[current_clicked].data;
    myChart.data.labels = graphs[current_clicked].labels;
    myChart.update();
    setTimeout(function(){
        //Filter Buttons
        $('.' + old_clicked + "_filter").hide();
        $('.' + current_clicked + "_filter").show();
        $('.' + current_clicked+ "_filter").removeClass("fadeOutLeft");
        $('.' + current_clicked + "_filter").addClass("fadeInLeft");
        setTimeout(function(){ 
                $('.' + current_clicked + "_filter").removeClass("fadeInLeft");
            }, 500);
    }, 500);
    
}

var ctx_format  = document.getElementById("doughnut-format");
var ctx_context  = document.getElementById("doughnut-context");
var bg_colors = ["orange", "lightgreen", "blue", "pink", "lightgoldenrodyellow", "yellow"]; //Some arbitrary list of colors for all doughnut charts.


var doughnutLegendcallback = function(chart) { 
            var text = []; 
            text.push('<ul class="' + chart.id + '-legend">'); 
            for (var i = 0; i < chart.data.labels.length; i++) { 
                text.push('<li><span class="legend-color" style="background-color:' + 
                           chart.data.datasets[0].backgroundColor[i] + 
                           '"></span>'); 
                if (chart.data.labels[i]) { 
                    text.push(chart.data.labels[i]); 
                } 
                text.push('</li>'); 
            } 
            text.push('</ul>'); 
            return text.join(''); 
        };

var formatDoughnutChart = new Chart(ctx_format, {
    type: 'doughnut',
    data: {
    datasets: [{
        data: data_format,
        backgroundColor: bg_colors,
    }],
    labels: labels_format
},
   options: {
        maintainAspectRatio: true,
        legend: {
                display:false,
            },
        legendCallback: doughnutLegendcallback,

        // title : {
        //     display: true,
        //     text: "How was the question originally asked?"
        // }
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
        maintainAspectRatio: true,
        legend: {
            display:false,
        },
        legendCallback: doughnutLegendcallback,

        // title : {
        //     display: true,
        //     text: "When were the questions asked?"
        // }
    }
});


//Create the HTML legends for the doughnut charts
$('#doughnut-format-legends').html(formatDoughnutChart.generateLegend());
$('#doughnut-context-legends').html(contextDoughnutChart.generateLegend());

//Filters


