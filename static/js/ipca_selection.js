var start_date = new Date("January 1, 2013 00:00:00");
var end_date = new Date("January 1, 2014 00:00:00");
var from_date = new Date("January 1, 2013 00:00:00");
var to_date = new Date("January 1, 2014 00:00:00");

var cmu_data = true
if (cmu_data) {
	start_date = new Date("January 1, 2010 00:00:00");
	end_date = new Date("January 1, 2011 00:00:00");
	from_date = new Date("January 1, 2010 00:00:00");
	to_date = new Date("January 1, 2011 00:00:00");
}


var one_day=1000*60*60*24;

var number_of_days = parseInt(to_date - from_date) / one_day;

var timeline_data = []

// for (var i=0; i < 365; i++) {
// 	var new_entry = {}
// 	new_entry['date'] = addDays(start_date, i)
// 	new_entry['count'] = Math.random()*100;
// 	timeline_data.push(new_entry);
// }

function createTimelineVisualization(placement) {

	//var parseDate = d3.time.format("%Y-%m-%d").parse;

	var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;
	
	//for (d in timeline_data) {
	//	timeline_data[d]['date'] = parseDate(timeline_data[d]['yearMonthDay']);
	//}

	for (d in timeline_data) {
		//console.log(parseDate(timeline_data[d]['_id']));
		timeline_data[d]['date'] = parseDate(timeline_data[d]['_id']);
	}

	//for (d in timeline_data) {
	//	timeline_data[d]['date'] = parseDate(timeline_data[d]['_id']['yearMonthDay']);
	//}
	
	var margin = {top: 10, right: 10, bottom: 100, left: 40},
	    margin2 = {top: 130, right: 10, bottom: 20, left: 40},
	    width = selection_window[0] - margin.left - margin.right,
	    height = (selection_window[1]/2) - margin.top - margin.bottom,
	    height2 = (selection_window[1]/2) - margin2.top - margin2.bottom;

	var x = d3.time.scale().range([0, width]),
	    x2 = d3.time.scale().range([0, width]),
	    y = d3.scale.linear().range([height, 0]),
	    y2 = d3.scale.linear().range([height2, 0]);

	var xAxis = d3.svg.axis().scale(x).orient("bottom"),
	    xAxis2 = d3.svg.axis().scale(x2).orient("bottom"),
	    yAxis = d3.svg.axis().scale(y).orient("left");

	var area = d3.svg.area()
	    .interpolate("monotone")
	    .x(function(d) { return x(d.date); })
	    .y0(height)
	    .y1(function(d) { return y(d.count); });

	var area2 = d3.svg.area()
	    .interpolate("monotone")
	    .x(function(d) { return x2(d.date); })
	    .y0(height2)
	    .y1(function(d) { return y2(d.count); });

	var brush = d3.svg.brush()
	    .x(x2)
	    .on("brush", function (d) {
	    	x.domain(brush.empty() ? x2.domain() : brush.extent());
	  		focus.select(".area").attr("d", area);
	  		focus.select(".x.axis").call(xAxis);
	  		var extent = brush.extent();
			from_date = extent[0];
			to_date = extent[1];
			document.getElementById("chart-selection_view-notes").innerHTML = "Selection: " + from_date.toUTCString() + " - " + to_date.toUTCString();
	    })
	    .on("brushend", function (d) {
	    	var extent = brush.extent();
	    	from_date = extent[0];
			to_date = extent[1];
	    	if (from_date == to_date) {
	    		from_date = new Date("January 1, 2010 00:00:00");
				to_date = new Date("January 1, 2011 00:00:00");
	    	}
			
			number_of_days = parseInt(to_date - from_date) / one_day;

			$.ajax({
		    	url : "set_date_range",
		    	data : {'start_date':from_date.toUTCString(), 'end_date':to_date.toUTCString()}, 
		    	success : function(data) {
		    		getDataForUserRoleVisualization();
		    		document.getElementById("chart-selection_view-notes").innerHTML = "Selection: " + from_date.toUTCString() + " - " + to_date.toUTCString();
		    	}
		  	});
	    });


	d3.select(placement).select("svg").remove();

	var svg = d3.select(placement).append("svg")
    	.attr("width", width + margin.left + margin.right)
    	.attr("height", height + margin.top + margin.bottom);

    svg.append("defs").append("clipPath")
	    .attr("id", "clip")
	  	.append("rect")
	    .attr("width", width)
	    .attr("height", height);

	var focus = svg.append("g")
	    .attr("class", "focus")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var context = svg.append("g")
	    .attr("class", "context")
	    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

	x.domain([start_date,end_date]);
	y.domain([0, d3.max(timeline_data.map(function(d) { return d.count; }))]); // d.count

	x2.domain(x.domain());
	y2.domain(y.domain());


	  focus.append("path")
	      .datum(timeline_data)
	      .attr("class", "area")
	      .attr("d", area);

	  focus.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis);

	  focus.append("g")
	      .attr("class", "y axis")
	      .call(yAxis);

	  context.append("path")
	      .datum(timeline_data)
	      .attr("class", "area")
	      .attr("d", area2);

	  context.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height2 + ")")
	      .call(xAxis2);

	  context.append("g")
	      .attr("class", "x brush")
	      .call(brush)
	      .selectAll("rect")
	      .attr("y", -6)
	      .attr("height", height2 + 7);
}

function addDays(theDate, days) {
    return new Date(theDate.getTime() + days*24*60*60*1000);
}

function getDataForTimelineVisualization() {
	//$.get(
	$.ajax({
    	//url="get_counts_by_date",
    	//url="get_new_counts_by_date",
    	//url : "get_new_counts_by_date_revised",
    	url : "get_anomaly_data_for_timeline",
    	data : {'start_date':from_date.toUTCString(), 'end_date':to_date.toUTCString()}, 
    	beforeSend : function() { $('#chart-selection_view').css('background', "url(" + image_path + ") no-repeat")},//  '#BADA55')}, // 'url(/static/images/ajax-loader.gif)') },
    	complete : function() { $('#chart-selection_view').css('background', 'none') },
    	success : function(data) {
    		timeline_data = JSON.parse(data);
    		// we can splice the first 30 entries to avoid the timeline being scaled by the initial anomalous activity (i.e., activity recorded in January)
    		timeline_data.splice(0,30);
    		console.log(timeline_data);
    		createTimelineVisualization("#chart-selection_view");
    	}
  	});
}