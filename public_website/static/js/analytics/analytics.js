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
                    // labelString: '#Questions'
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


var total_gender = {};
total_gender.Male = data_gender[0];
total_gender.Female = data_gender[1];
total_gender.NonBinary = data_gender[2];
total_gender.NA = data_gender[3];

//Swiping for Mobile and Touch Devices
$(function() {      
      $("#graph-swipe").add("#graph-title").swipe( {
        swipeLeft:function(event, direction, distance, duration, fingerCount, fingerData) {
           old_clicked = current_clicked;
           $('.left-arrow').css("border-color", "green");
           myChart.data.datasets = dataset_without_filter;
           setTimeout(function(){$('.left-arrow').css("border-color","black");}, 300); //animating the arrows
           $('#graph-title').addClass("animate__backOutLeft");
           current_clicked_index = (current_clicked_index + 1)%graphs_name.length;
           current_clicked = graphs_name[current_clicked_index];
           if (old_clicked == current_clicked) return;
           changeGraph(old_clicked, current_clicked);

           setTimeout(function(){
            $('#graph-title').removeClass("animate__backOutLeft");
            $('#graph-title').html($("#" + current_clicked).attr("data-title"));
            $('#graph-title').addClass("animate__backInRight");
            setTimeout(function(){ 
                $('#graph-title').removeClass("animate__backInRight");
             }, 300);
        }, 300);
        },

        swipeRight:function(event, direction, distance, duration, fingerCount, fingerData) {
           old_clicked = current_clicked;
           myChart.data.datasets = dataset_without_filter;
           $('.right-arrow').css("border-color", "green");
           setTimeout(function(){$('.right-arrow').css("border-color", "black");}, 200);
           $('#graph-title').addClass("animate__backOutRight");
           if (current_clicked_index == 0) current_clicked_index = graphs_name.length;
           current_clicked_index = (current_clicked_index - 1)%graphs_name.length;
           current_clicked = graphs_name[current_clicked_index];
           if (old_clicked == current_clicked) return;
           changeGraph(old_clicked, current_clicked); //Modify the graph

           setTimeout(function(){
            $('#graph-title').removeClass("animate__backOutRight");
            $('#graph-title').html($("#" + current_clicked).attr("data-title"));
            $('#graph-title').addClass("animate__backInLeft");
            setTimeout(function(){ 
                $('#graph-title').removeClass("animate__backInLeft");
            }, 400);

        }, 300);
            },
        threshold:30,
    })
});
//Preventing scrolling in touch device in graph-swipe div
var graphSwipe = document.getElementById('graph-swipe');
graphSwipe.addEventListener('touchmove', function(e) {

        e.preventDefault();

}, false);

$('#param-choice input:radio').click(function() {
    old_clicked = current_clicked;
    myChart.data.datasets = dataset_without_filter;
    current_clicked = $(this).val();
    if (old_clicked == current_clicked) return;
    changeGraph(old_clicked, current_clicked);
    $('#graph-title').addClass("animate__backOutLeft");
    setTimeout(function(){
        $('#graph-title').removeClass("animate__backOutLeft");
        $('#graph-title').html($("#" + current_clicked).attr("data-title"));
        $('#graph-title').addClass("animate__backInLeft");
        setTimeout(function(){ 
                $('#graph-title').removeClass("animate__backInLeft");
            }, 500);
    }, 500);
    
});

function changeGraph(old_clicked, current_clicked){
    myChart.data.datasets = dataset_without_filter;
    $('.' + old_clicked + "_filter").addClass("animate__backOutLeft");
    myChart.data.datasets[0].data = graphs[current_clicked].data;
    myChart.data.labels = graphs[current_clicked].labels;
    myChart.update();
    setTimeout(function(){
        //Filter Buttons
        $('.' + old_clicked + "_filter").hide();
        $('.' + current_clicked + "_filter").show();
        $('.' + current_clicked+ "_filter").removeClass("animate__backOutLeft");
        $('.' + current_clicked + "_filter").addClass("animate__backInLeft");
        setTimeout(function(){ 
                $('.' + current_clicked + "_filter").removeClass("animate__backInLeft");
            }, 500);
    }, 500);

    // The filters button have a special attribute "data-pressed" which needs to be reset after each graph change
    $('.filter-button').prop('data-pressed', null);
    
}

var ctx_format  = document.getElementById("doughnut-format");
var ctx_context  = document.getElementById("doughnut-context");
var bg_colors = ["#fe6b00", "#22bdbf", "#0087bc", "#f93838", "#8029a8", "#5eaf10", "#bc7a0f", "#04487c"]; //Some arbitrary list of colors for all doughnut charts.


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


//helper function to sum the elements of a list
function sum(arr){
    sum1 = 0;
    arr.forEach(function(num){sum1+=parseFloat(num) || 0;});
    return sum1;
}

// For Filter Buttons
function createGenderLanguageDatasets(){
        gender = ["Male", "Female", "NonBinary", "Not known"];
        male = [];
        female = [];
        non_binary = [];
        na = [];
        for (lang_index in labels_lang){
                lang = labels_lang[lang_index];
                male.push(languageGenderDictionary[lang].Male);
                female.push(languageGenderDictionary[lang].Female);
                non_binary.push(languageGenderDictionary[lang].NonBinary);
                na.push(languageGenderDictionary[lang]["Not known"]);

            
        }


        var gender_lang_datasets =  [{
            label: 'Male',
            data: male,
            backgroundColor : bg_colors[0],
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Female',
            data: female,
            backgroundColor : bg_colors[1],
            borderWidth: 0.5,
            minHeight: 5,
        },

        {
            label: 'Non-binary',
            data: non_binary,
            backgroundColor : bg_colors[2],
            borderWidth: 0.5,
            minHeight: 5,
        },

        {
            label: 'Not known',
            backgroundColor: bg_colors[3],
            data: na,
            borderWidth: 0.5,
            minHeight: 5,
        },
        ]
        return gender_lang_datasets;
}

function createSTEMSplitDataset() {
        genders = ["Male", "Female","NonBinary", "Not known"];
        maths = [];
        physics = [];
        chemistry = [];
        biology = [];
        history_philosophy = [];
        earth_environment = [];


        for (gender_index in genders){
                gender = genders[gender_index];
                maths.push(genderSubjectDictionary[gender].Mathematics);
                physics.push(genderSubjectDictionary[gender].Physics);
                chemistry.push(genderSubjectDictionary[gender].Chemistry);
                biology.push(genderSubjectDictionary[gender].Biology);  
                history_philosophy.push(genderSubjectDictionary[gender]['History, Philosophy and Practice of Science']);  
                earth_environment.push(genderSubjectDictionary[gender]['Earth & Environment']);
        }

        var gender_subject_datasets =  [{
            label: 'Mathematics',
            data: maths,
            backgroundColor : bg_colors[0],
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Physics',
            data: physics,
            backgroundColor : bg_colors[1],
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Chemistry',
            backgroundColor: bg_colors[2],
            data: chemistry,
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'Biology',
            backgroundColor: bg_colors[3],
            data: biology,
            borderWidth: 0.5,
            minHeight: 5,
        },
        {
            label: 'History, Philosophy and Practice of Science',
            backgroundColor: bg_colors[4],
            data: history_philosophy,
            borderWidth: 0.5,
            minHeight: 5,
        },

        {
            label: 'Earth & Environment',
            backgroundColor: bg_colors[5],
            data: earth_environment,
            borderWidth: 0.5,
            minHeight: 5,
        },
        ]
        return gender_subject_datasets;
}


function createNonSTEMSplitDataset() {
        genders = ["Male", "Female", "NonBinary", "Not known"];
        non_stem = ['Humans & Society', 'Geography & History',  'Arts & Recreation', 'Language & Literature']
        total_stem = [];
        
        for (gender_index in genders){
                gender = genders[gender_index];
                total_stem.push(genderSubjectDictionary[gender].Mathematics+
                    genderSubjectDictionary[gender].Physics +
                    genderSubjectDictionary[gender].Chemistry + 
                    genderSubjectDictionary[gender].Biology + 
                    genderSubjectDictionary[gender]['History, Philosophy and Practice of Science'] + 
                    genderSubjectDictionary[gender]['Earth & Environment']); 
        }

        var getSubjectData = function(subject) {
            lst = [];
             for (gender_index in genders){
                gender = genders[gender_index];
                lst.push(genderSubjectDictionary[gender][subject]);
            }
            return lst;
        }
        
        var gender_subject_datasets =  [{
            label: 'STEM',
            data: total_stem,
            backgroundColor : bg_colors[5],
            borderWidth: 0.5,
            minHeight: 5,
        },
        ]

        for (subject_index in non_stem) {
            color = bg_colors[subject_index];
            subject = non_stem[subject_index];
            gender_subject_datasets.push({
                label : subject,
                data: getSubjectData(subject),
                backgroundColor : color,
                borderWidth: 0.5,
                minHeight: 5,
            });
        }
        return gender_subject_datasets;
}



var gender_lang_datasets = createGenderLanguageDatasets(); // the function call will also set the value of total_female... etc.
var gender_subject_datasets = createSTEMSplitDataset();
var gender_nonstem_datasets = createNonSTEMSplitDataset();


$("#gender_stem_split").click(function (){addFilterAction(this.id, gender_subject_datasets, labels_gender)});
$("#lang_gender_split").click(function (){addFilterAction(this.id, gender_lang_datasets, labels_lang)});
$("#gender_nonstem_split").click(function (){addFilterAction(this.id, gender_nonstem_datasets, labels_gender)});

var addFilterAction = function (button_id, f_datasets, f_labels){
    btn = $("#" + button_id);
    parent_id = btn.data().parent;  // parent_id holds the id of the button group that contains the given button
    if (parent_id != null) parent = $('#' + parent_id);
    else parent = false;

    if (btn.prop('data-pressed') == null) {
        if (parent) {
            parent.children().prop('data-pressed', null);
            parent.children().removeClass('pressed');
        }
        btn.addClass("pressed");
        myChart.data.datasets = f_datasets;
        myChart.data.labels = f_labels;
        myChart.update();
        btn.prop('data-pressed',true);
    }

    else {
        $("#" + button_id).prop('data-pressed', null);
        $("#" + button_id).removeClass("pressed");
        myChart.data.datasets = dataset_without_filter;
        myChart.data.datasets[0].data = graphs[current_clicked].data;
        myChart.data.labels = graphs[current_clicked].labels;
        myChart.update();
    }
};

