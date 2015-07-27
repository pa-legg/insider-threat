

var userrole_data = []

// for (var i=0; i < Math.random()*100; i++) {
// 	var new_entry = {}
// 	new_entry['name'] = 'role_' + i
// 	new_entry['count'] = 0
// 	new_entry['selected'] = false;
// 	new_entry['children'] = []
// 	for (var j=0; j < Math.random()*100; j++) {
// 		var new_user = {}
// 		new_user['name'] = 'user_' + i + "_" + j
// 		new_user['count'] = Math.random()*100;
// 		new_user['selected'] = false;
// 		new_entry['children'].push(new_user);
// 		new_entry['count'] = new_entry['count'] + new_user['count'];
		
// 	}
// 	userrole_data.push(new_entry);
// }

//console.log(userrole_data);

var margin = {top: 10, right: 10, bottom: 100, left: 40},
    margin2 = {top: 150, right: 10, bottom: 50, left: 40},
    width = 400 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom,
    height2 = 200 - margin2.top - margin2.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
    .range([height, 0]);

var x2 = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y2 = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickFormat("");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .ticks(5);

var xAxis2 = d3.svg.axis()
    .scale(x2)
    .orient("bottom")
    .tickFormat("");

var yAxis2 = d3.svg.axis()
    .scale(y2)
    .orient("left")
    .ticks(5);

function createUserRoleVisualization(placement) {

	var scale_role_by_user_count = false;
	d3.select(placement).select("svg").remove();

	margin = {top: 10, right: 10, bottom: 100, left: 40},
	    margin2 = {top: 150, right: 10, bottom: 50, left: 40},
	    width = userrole_window[0] - margin.left - margin.right,
	    height = (userrole_window[1]/2) - margin.top - margin.bottom,
	    height2 = (userrole_window[1]/2) - margin2.top - margin2.bottom;

	
	

	x = d3.scale.ordinal()
	    .rangeRoundBands([0, width], .1);

	y = d3.scale.linear()
	    .range([height, 0]);

	x2 = d3.scale.ordinal()
	    .rangeRoundBands([0, width], .1);

	y2 = d3.scale.linear()
	    .range([height, 0]);

	 xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom")
	    .tickFormat("");

	yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .ticks(5);

	xAxis2 = d3.svg.axis()
	    .scale(x2)
	    .orient("bottom")
	    .tickFormat("");

	yAxis2 = d3.svg.axis()
	    .scale(y2)
	    .orient("left")
	    .ticks(5);



	var svg = d3.select(placement).append("svg")
    	.attr("width", width + margin.left + margin.right)
    	.attr("height", height + margin.top + margin2.top + margin2.bottom);

    console.log(userrole_data);

    	if (scale_role_by_user_count) {
    		x.domain(userrole_data.map(function(d) { return d.name; }));
	  		y.domain([0, d3.max(userrole_data, function(d) { return d.count / d.children.length; })]);

    		x2.domain(userrole_data[0].children.map(function(d) { return d.name; }));
	  		y2.domain([0, d3.max(userrole_data[0], function(d) { return d.count / d.children.length; })]);

    	} else {
    		x.domain(userrole_data.map(function(d) { return d.name; }));
	  		y.domain([0, d3.max(userrole_data, function(d) { return d.count; })]);

	  		x2.domain(userrole_data[0].children.map(function(d) { return d.name; }));
	  		y2.domain([0, d3.max(userrole_data[0], function(d) { return d.count; })]);
    	}

	  

	  


	  var role_chart = svg.append("g")
	  		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	  var user_chart = svg.append("g")
	  		.attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

	  

	  role_chart.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis)
	      .selectAll("text")  
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", function(d) {
                return "rotate(-65)" 
                });

	  role_chart.append("g")
	      .attr("class", "y axis")
	      .call(yAxis);
	      // .append("text")
	      // .attr("transform", "rotate(-90)")
	      // .attr("y", 6)
	      // .attr("dy", ".71em")
	      // .style("text-anchor", "end")
	      // .text("Frequency");

	  role_chart.selectAll(".rolebar")
	      .data(userrole_data)
	      .enter().append("rect")
	      .attr("name", function(d) { return d.name; })
	      .attr("fill", function(d) { if (d.selected) { return "brown" } else { return "steelblue" } } )
	      .attr("fill-opacity", 0.5)
	      .attr("x", function(d) { return x(d.name); })
	      .attr("width", x.rangeBand())
	      .attr("y", function(d) { return y(d.count); })
	      .attr("height", function(d) { return height - y(d.count); })
	      .on("mouseover", function(d) {
	      	d3.select(this)
	      		.attr("fill-opacity", 1.0).attr("fill", "brown");
		      	document.getElementById("chart-selection_view-notes").innerHTML = "Selection: " + d.name;
		      	

		      	user_chart.selectAll("g").remove();
		      	user_chart.selectAll("rect").remove();

		  		draw_user_plot(user_chart, d.name, d.children);

	      })
	      .on("mouseout", function(d) {
	      	d3.select(this).attr("fill-opacity", 0.5)
	      		.attr("fill", function(d) { if (d.selected) { return "brown" } else { return "steelblue" } } )
	      	document.getElementById("chart-selection_view-notes").innerHTML = "Selection: ";
	      	//d3.select(this).transition().duration(300).attr("fill", "steelblue")
	      })
	      .on("click", function(d) {

	      	d.selected = !(d.selected);
    		if (d.selected) {
    			d3.select(this).attr("fill", "red");
    		} else {
    			d3.select(this).attr("fill", "steelblue");
    		}

    		for (child in d.children) {
    			d.children[child].selected = d.selected;
    		}

    		draw_user_plot(user_chart, d.name, d.children);

	      	$.ajax({
		    	//url="get_counts_by_date",
		    	//url="get_new_counts_by_date",
		    	url : "update_server_on_role_selection",
		    	data : {'rolename':d.name, 'add':d.selected}, 
		    	//beforeSend : function() { $('#chart-graph_view').css('background', "url(https://dl.dropboxusercontent.com/u/1451082/plegg-current/images/ajax-loader.gif) no-repeat")},//  '#BADA55')}, // 'url(/static/images/ajax-loader.gif)') },
    			//complete : function() { $('#chart-graph_view').css('background', 'none') },
		    	success : function(data) {
		    		user_role_data = JSON.parse(data);
		    		//console.log(user_role_data);
		    		
		    		

		    		//getDataForScatterPlotVisualization();
		    		
    			}
		  	});

	      });

	//draw_user_plot(user_chart, userrole_data[0]['children']);

}

function draw_user_plot(user_chart, rolename, data) {

	x2.domain(data.map(function(d) { return d.name; }));
	y2.domain([0, d3.max(data, function(d) { return d.count; })]);

	user_chart.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis2)
	      .selectAll("text")  
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", function(d) {
                return "rotate(-65)" 
                });

	  user_chart.append("g")
	      .attr("class", "y axis")
	      .call(yAxis2);
	      // .append("text")
	      // .attr("transform", "rotate(-90)")
	      // .attr("y", 6)
	      // .attr("dy", ".71em")
	      // .style("text-anchor", "end")
	      // .text("Frequency");

	  //console.log("Range bands", x2.rangeBand());

	  user_chart.selectAll(".bar")
	      .data(data)
	      .enter().append("rect")
	      .attr("name", function(d) { return d.name; })
	      .attr("fill", function(d) { if (d.selected) { return "brown" } else { return "steelblue" } } )
	      .attr("fill-opacity", 0.5)
	      .attr("x", function(d) { return x2(d.name); })
	      .attr("width", x2.rangeBand())
	      .attr("y", function(d) { return y2(d.count); })
	      .attr("height", function(d) { return height - y2(d.count); })
	      .on("mouseover", function(d) {
	      	d3.select(this)
	      		.attr("fill-opacity", 1.0).attr("fill", "brown");
	      	document.getElementById("chart-selection_view-notes").innerHTML = "Selection: " + rolename + " : " + d.name;

	      	highlight_user_in_scatter_plot(d.name, true);

	      })
	      .on("mouseout", function(d) {
	      	d3.select(this)
	      		.attr("fill-opacity", 0.5)
	      		.attr("fill", function(d) { if (d.selected) { return "brown" } else { return "steelblue" } } )
	      	document.getElementById("chart-selection_view-notes").innerHTML = "Selection: ";

	      	highlight_user_in_scatter_plot(d.name, false);
	      })
	      .on("click", function(d) {

	      	d.selected = !(d.selected);
    		if (d.selected) {
    			d3.select(this).attr("fill", "red");
    		} else {
    			d3.select(this).attr("fill", "steelblue");
    		}

			$.ajax({
		    	//url="get_counts_by_date",
		    	//url="get_new_counts_by_date",
		    	url : "update_server_on_user_selection",
		    	data : {'username':d.name, 'add':d.selected}, 
		    	//beforeSend : function() { $('#chart-graph_view').css('background', "url(https://dl.dropboxusercontent.com/u/1451082/plegg-current/images/ajax-loader.gif) no-repeat")},//  '#BADA55')}, // 'url(/static/images/ajax-loader.gif)') },
    			//complete : function() { $('#chart-graph_view').css('background', 'none') },
		    	success : function(data) {
		    		user_role_data = JSON.parse(data);
		    		console.log(user_role_data);

		    		//getDataForScatterPlotVisualization();
    			}
		  	});

  			
  			
	      });
}



function getDataForUserRoleVisualization() {
	$.ajax({
    	//url="get_counts_by_date",
    	//url="get_new_counts_by_date",
    	//url : "get_new_activity_for_all_users_and_all_roles_revised",
    	url : "get_new_anomalies_for_all_users_and_all_roles_revised",
    	data : {'start_date':from_date.toUTCString(), 'end_date':to_date.toUTCString()}, 
    	beforeSend : function() { $('#chart-userrole_view').css('background', "url(" + image_path + ") no-repeat")},
    	complete : function() { $('#chart-userrole_view').css('background', 'none') },
    	success : function(data) {
    		userrole_data = JSON.parse(data);
    		console.log(userrole_data);
    		createUserRoleVisualization("#chart-userrole_view");
    	}
  	});

}
