let r = 57;      //r,g,b for graph choropleth
let g = 106;
let b = 177;


$('.india-map').css("height", screen.height*0.6);

/**
    Function getRGB returns a shade of the color given by (r,g,b) based on the valuePercent.
    Return Value: String representation of a color
**/
function getRGB(valuePercent,r,g,b){
    rval = r*valuePercent;
    gval = g*valuePercent;
    bval = b*valuePercent;
    return 'rgb(' + r*valuePercent + ',' + g*valuePercent + ',' + b*valuePercent + ')';
}

let bubbles = [];  // data for bubble map will be stored in bubbles array
let data = {};     // data for default choropleth store in data object
let totalQCounts = state_counts.reduce((x,y) => x+ y, 0);

//Initialize the data
for (i=0; i<state_names.length; i++){
    valuePercent = (state_counts[i]/totalQCounts) ;
    valuePercentColor = 1 - valuePercent;
    if (valuePercent < 0.2){
        radiusPercent = 0.2
    }
    else {
        radiusPercent = valuePercent
    }
    
    bubbles.push({
         centered: state_codes[i],
         radius: 40*radiusPercent,
         valuePercent: valuePercent, 
         count: state_counts[i],
         state: state_names[i],
         borderWidth: 0.01,
         fillKey: "MEDIUM",
     });

    data[state_codes[i]] = {
        state: state_names[i],
        valuePercent: valuePercent,
        count: state_counts[i],
        fillColor: getRGB(valuePercentColor,r,g,b),
    }
}
$( document ).ready(function() {      
    let isMobile = window.matchMedia("only screen and (max-width: 760px)").matches;

    if (isMobile == true) {
        projection_center = [110.9629, 15.5937];
        projection_scale = 600;
    }
    else {
        projection_center = [90.9629, 23.5937];
        projection_scale = 1000;
    }

    // Create the choropleth for Question Map
    var india_map = new Datamap({
        element: document.getElementById('india-map'),
        scope: 'india',
        responsive: true,
        geographyConfig: {
            popupOnHover: true,
            highlightOnHover: true,
            highlightFillColor: '#63C5DA',
            highlightBorderColor: 'rgba(250, 15, 160, 0.2)',
            highlightBorderWidth: 2,
            highlightBorderOpacity: 1,
            borderColor: 'black',
            borderWidth: 0.3,
            dataUrl: indianTopoURL,
            popupTemplate: function (geo, data) {
                if (data==null){
                    return `<div class="hoverinfo-india">
                            <h3 style="padding: 0.3em 0.9em; margin: 0px; font-weight: normal; font-size: 1em;">${geo.properties.name}</h3>
                            <div style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.8em;"><span>No question found</span><br></div>
                             <div><p style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.7em; opacity: 0.6;"></p></div>
                            </div>`;
                }
                per = Math.round(data.valuePercent*10000)/100;
                return `<div class="hoverinfo-india">
                            <h3 style="padding: 0.3em 0.9em; margin: 0px; font-weight: normal; font-size: 1em;">${geo.properties.name}</h3>
                            <div style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.8em;"><span>Questions Asked: ${data.count}</span><br></div>
                             <div><p style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.7em; opacity: 0.6;">Percantage: ${per.toFixed(2)}%</p></div>
                            </div>`;
            },
        },
        fills: {
            'MAJOR': '#ff0011',
            'MEDIUM': '#0fa0fa',
            'MINOR': '#bada55',
            defaultFill: 'rgba(240,240,255,0.91)',
        },
        data:data, 
        setProjection: function (element) {
            var projection = d3.geo.mercator()
                .center(projection_center) // in [East Latitude, North Longitude]
                .scale(projection_scale);
            var path = d3.geo.path().projection(projection);
            return { path: path, projection: projection };
        }
    });


    // Create the bubble Question Map.
    var bubble_map = new Datamap({
        element: document.getElementById('india-bubble-map'),
        scope: 'india',
        responsive: true,
        geographyConfig: {
            popupOnHover: true,
            highlightOnHover:true,
            highlightFillColor: 'lightblue',
            borderColor: 'black',
            borderWidth: 0.3,
            dataUrl: indianTopoURL,
            popupTemplate: function (geo, data) {
                return `<div class="hoverinfo-india">
                            <h3 style="padding: 0.3em 0.9em; margin: 0px; font-weight: normal; font-size: 1em;">${geo.properties.name}</h3>
                            </div>`;
            },
        },

        fills: {
            'MAJOR': '#ff0011',
            'MEDIUM': '#0fa0fa',
            'MINOR': '#bada55',
            defaultFill: 'rgba(240,240,255,0.91)',
        },

        setProjection: function (element) {
            var projection = d3.geo.mercator()
                .center(projection_center) // in [East Latitude, North Longitude]
                .scale(projection_scale);
            var path = d3.geo.path().projection(projection);
            return { path: path, projection: projection };
        }
    });

    // Set the width of the maps to the screen width



    setTimeout(() => { // only start drawing bubbles on the map when map has rendered completely, hence using the timeout of 5 seconds
       bubble_map.bubbles(bubbles, {   
        popupTemplate: function (data) {
                per = Math.round(data.valuePercent*10000)/100;
                return `<div class="hoverinfo-india">
                            <h3 style="padding: 0.3em 0.9em; margin: 0px; font-weight: normal; font-size: 1em;">${data.state}</h3>
                            <div style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.8em;"><span>Questions Asked: ${data.count}</span><br></div>
                             <div><p style="margin: 0px; padding: 0.3em 0.9em; font-size: 0.7em; opacity: 0.6;">Percantage: ${per.toFixed(2)}%</p></div>
                            </div>`;
            },
       });
    }, 2000);

    let bubble_view_btn = $('#bubble-view');     //button to switch to bubble map
    bubble_view_btn.prop("checked", false);
    $("#india-bubble-map").hide(500);

    
    function bubble_btn_change (){
    if (bubble_view_btn.prop("checked")){
         $("#india-map").hide(1000);
         $("#india-bubble-map").show(1000);
    }
    else {
        $("#india-bubble-map").hide(1000);
        $("#india-map").show(1000);
    }
}


    bubble_view_btn.change(bubble_btn_change);

});
