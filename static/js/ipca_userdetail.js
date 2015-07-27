// this was the first attempt and shows just one user plot

var background_opacity = 0.1;
var role_opacity = 0.02;
var user_opacity = 0.4;

// Converts from degrees to radians.
to_radians = function(degrees) {
  return degrees * Math.PI / 180;
};
 
// Converts from radians to degrees.
to_degrees = function(radians) {
  return radians * 180 / Math.PI;
};

range = function(start, end)
{
    var array = new Array();
    for(var i = start; i < end; i++)
    {
        array.push(i);
    }
    return array;
};

d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
  	this.parentNode.appendChild(this);
  });
};

get_date_value = function (this_date) {
	var one_day=1000*60*60*24;
	//console.log(this_date)

	this_date = new Date(this_date);
	
 	value = parseInt(this_date - from_date) / one_day;
 	//console.log(this_date, start_date, value)
 	return value;
 }



var show_detailed_background = true;
var show_detailed_role = false;
var show_crosshair = false;
var use_radial_plot = false;

function set_show_detailed_role() {
	show_detailed_role = !show_detailed_role;
}

function set_show_detailed_role_as_radial() {
	use_radial_plot = !use_radial_plot;
}

var arclength = 0.3;
var arc_d3_newdetail = d3.svg.arc()
.innerRadius(function(d) { return (d[0]-1)/d[3]*(d[2]/2) } )
.outerRadius(function(d) { return (d[0])/d[3]*(d[2]/2) } )
.startAngle(function(d) { return to_radians( (d[1]-arclength)/24*360 )  } )
.endAngle(function(d) { return to_radians( (d[1]+arclength)/24*360 )  } );


var arc_d3_background = d3.svg.arc()
.innerRadius(function(d) { return 0 } )
.outerRadius(function(d) { return d[1] } )
.startAngle(function(d) { return to_radians( d[0] * (360/24) )  } )
.endAngle(function(d) { return to_radians( (d[0]+1) * (360/24) ) } );

function initialize_detailed_view(placement) {
	var w = h = 500;

    d3.select(placement).select("svg").remove();

	var svg = d3.select(placement)
		.append("svg")
		.attr("width", w)
		.attr("height", h);
}

function draw_detailed_view(placement, rolename, username, rolejson) {
	console.log("draw_detailed_view");
	var w = h = eigenvalue_window[0];

	var plot_w = plot_h = eigenvalue_window[0];

    d3.select(placement).select("svg").remove();
    


    if (use_radial_plot) {

		var svg = d3.select(placement)
			.append("svg")
			.attr("width", w)
			.attr("height", h)
			.on('mouseover', function(d) {

				if (show_crosshair) {
			    	var mouse_pos = d3.mouse(this);
			    	var center = [d3.select(this).attr("width") / 2, d3.select(this).attr("height") / 2];
			    	var radius = Math.sqrt( ( (mouse_pos[0]-center[0]) * (mouse_pos[0]-center[0]) ) + ( (mouse_pos[1]-center[1]) * (mouse_pos[1]-center[1]) ) )

			    	svg.select("line.detail_temp_line").remove();
			    	svg.select("circle.detail_temp_circle").remove();

			    	svg.append("line")
		              .attr("class", "detail_temp_line")
		              .attr("x1", center[0])
		              .attr("y1", center[1])
		              .attr("x2", mouse_pos[0])
		              .attr("y2", mouse_pos[1])
		              .style("stroke-opacity", 0.5)
		              .style("stroke-width", 2)
		              .style("stroke", "black");

		            svg.append("circle")
		              .attr("class", "detail_temp_circle")
		              .attr("cx", center[0])
		              .attr("cy", center[1])
		              .attr("r", radius)
		              .style("stroke-opacity", 0.5)
		              .style("stroke-width", 2)
		              .style("stroke", "black")
		              .style("fill", "none");

		          }
		    });

		var max_radius = rolejson['max_radius'];

		console.log(rolejson);


		if (show_detailed_background) {
			svg.selectAll(".background")
				.data([0])
			    .enter()
			    .append("g")
			    .attr("width", plot_w)
				.attr("height", plot_h)
			    .selectAll(".background_segments")
			     .data(d3.range(24))
				      .enter()
				      .append("path")
				      .attr("transform", function (d, i) { return "translate(" + plot_w/2 + "," + plot_h/2 + ")" })
				      .attr("d", function (d) { return arc_d3_background([d, plot_w/2]); })
				      .attr("fill", function (d) { if (d % 2 == 0) { return 'rgb(200,200,200)' } else { return 'rgb(130,130,130)' }; })
				      //.attr("stroke", function (d) { return 'rgb(0,0,0)'; })
				      .attr("fill-opacity", background_opacity);

		}


		if('children' in rolejson) {
			console.log('children in rolejson');

			if (show_detailed_role) {
				svg.selectAll(".detailed_role")
					.data(rolejson['children'])
				    .enter()
				    .append("g")
				    .attr("width", plot_w)
					.attr("height", plot_h)
				    .selectAll(".role_segments")
				     .data(function (d) { return d['children'] })
					      .enter()
					      .append("path")
					      .attr("transform", function (d, i) { return "translate(" + plot_w/2 + "," + plot_h/2 + ")" })
					      .attr("d", function (d) { return arc_d3_newdetail([d.radius, d.angle, plot_w, max_radius]); })
					      .attr("fill", function (d) { return 'rgb(' + d.colour[0] + ',' + d.colour[1] + ',' + d.colour[2] + ')'; })
					      .attr("fill-opacity", role_opacity);
			}

			if (username != "none") {
				svg.selectAll(".detailed_user")
					.data(rolejson['children'].filter(function(d) { return d.name == username }))
				    .enter()
				    .append("g")
				    .attr("width", plot_w)
					.attr("height", plot_h)
				    .selectAll(".users_segments")
				     .data(function (d) { return d['children'] })
				      .enter()
				      .append("path")
				      .attr("d", function (d) { return arc_d3_newdetail([d.radius, d.angle, plot_w, max_radius]); })
				      .attr("transform", function (d) { return "translate(" + plot_w/2 + "," + plot_h/2 + ")" })
				      .style("fill", function (d) { return 'rgb(' + d.colour[0] + ',' + d.colour[1] + ',' + d.colour[2] + ')'; })
				      .style("fill-opacity", user_opacity)
				      .on('mouseover', function(d) {
				    	d3.select(this)
				    	.style("fill-opacity", 1.0).moveToFront();
				    	var my_string = "Selection:";
				    	//console.log(d);
				    	if ("to" in d) {
				    		my_string = my_string + "<br/>Date: " + d["date"] 
				    		my_string = my_string + "<br/>User: " + d["user"] 
				    		my_string = my_string + "<br/>Email to: " + d["to"]
			    		} else if ("url" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>URL: " + d["url"]
			    		} else if ("activity" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>Activity: " + d["activity"]
			    		} else if ("filepath" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>Filepath: " + d["filepath"]
			    		}

				    	document.getElementById("chart-eigenvalue_view-notes")
				    		.innerHTML = my_string;
			          })
				    .on('mouseout', function(d) {
				    	d3.select(this).style("fill-opacity", user_opacity);
			                  //console.log(d);
			                  document.getElementById("chart-eigenvalue_view-notes")
				    		.innerHTML = "Selection:";
			              })
				    .on('click', function(d) {
				    	//d3.select(this).moveToFront();
			              //    console.log(d);
			              });
			}

		}

	} else {

		w = eigenvalue_window[0];
		h = eigenvalue_window[1];

		plot_w = eigenvalue_window[0];
		plot_h = eigenvalue_window[1];

		// if not using a radial plot then let's use a standard rectagular grid plot
		var svg = d3.select(placement)
			.append("svg")
			.attr("width", w)
			.attr("height", h)
			.on('mouseover', function(d) {


		    	var mouse_pos = d3.mouse(this);
		    	
		    	svg.select("line.detail_temp_line1").remove();
		    	svg.select("line.detail_temp_line2").remove();

		    	if (show_crosshair) {
					svg.append("line")
			          .attr("class", "detail_temp_line1")
			          .attr("x1", 0)
			          .attr("y1", mouse_pos[1])
			          .attr("x2", plot_w)
			          .attr("y2", mouse_pos[1])
			          .style("stroke-opacity", 0.5)
			          .style("stroke-width", 2)
			          .style("stroke", "black");

			        svg.append("line")
			          .attr("class", "detail_temp_line2")
			          .attr("x1", mouse_pos[0])
			          .attr("y1", 0)
			          .attr("x2", mouse_pos[0])
			          .attr("y2", plot_h)
			          .style("stroke-opacity", 0.5)
			          .style("stroke-width", 2)
			          .style("stroke", "black");

			      }

		    	
		    });

		var max_radius = rolejson['max_radius'];

		//console.log(rolejson);

		if (show_detailed_background) {
			svg.selectAll(".background")
				.data([0])
			    .enter()
			    .append("g")
			    .attr("width", plot_w)
				.attr("height", plot_h)
			    .selectAll(".background_segments")
			     .data(d3.range(24))
				      .enter()
				      .append("rect")
				      .attr("x", function (d) { return d / 24 * plot_w; })
				      .attr("y", 0)
				      .attr("width", plot_w/24)
				      .attr("height", plot_h)
				      .attr("fill", function (d) { if (d % 2 == 0) { return 'rgb(200,200,200)' } else { return 'rgb(130,130,130)' }; })
				      .attr("fill-opacity", background_opacity);

		}

		

		if('children' in rolejson) {
			console.log('children in rolejson');

			if (show_detailed_role) {

				svg.selectAll(".detailed_role")
					.data(rolejson['children'])
				    .enter()
				    .append("g")
				    .attr("width", plot_w)
					.attr("height", plot_h)
				    .selectAll(".role_segments")
				     .data(function (d) { return d['children'] })
					      .enter()
					      .append("rect")
					      .attr("x", function (d) { return d.angle / 24 * plot_w; })
					      .attr("y", function (d) { return d.radius / max_radius * plot_h; })
					      .attr("width", 2)
					      .attr("height", plot_h / max_radius)
					      .attr("fill", function (d) { return 'rgb(' + d.colour[0] + ',' + d.colour[1] + ',' + d.colour[2] + ')'; })
					      .attr("fill-opacity", role_opacity);
			}

			if (username != "none") {
				svg.selectAll(".detailed_user")
					.data(rolejson['children'].filter(function(d) { return d.name == username }))
				    .enter()
				    .append("g")
				    .attr("width", plot_w)
					.attr("height", plot_h)
				    .selectAll(".users_segments")
				     .data(function (d) { return d['children'] })
				      .enter()
				      .append("rect")
				      .attr("x", function (d) { return d.angle / 24 * plot_w; })
				      .attr("y", function (d) { return d.radius / max_radius * plot_h; })
				      .attr("width", 2)
				      .attr("height", plot_h / max_radius)
				      .style("fill", function (d) { return 'rgb(' + d.colour[0] + ',' + d.colour[1] + ',' + d.colour[2] + ')'; })
				      .style("fill-opacity", user_opacity)
				      .on('mouseover', function(d) {
				    	d3.select(this)
				    	.style("fill-opacity", 1.0).moveToFront();
				    	var my_string = "Selection:";
				    	//console.log(d);
				    	if ("to" in d) {
				    		my_string = my_string + "<br/>Date: " + d["date"] 
				    		my_string = my_string + "<br/>User: " + d["user"] 
				    		my_string = my_string + "<br/>Email to: " + d["to"]
			    		} else if ("url" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>URL: " + d["url"]
			    		} else if ("activity" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>Activity: " + d["activity"]
			    		} else if ("filepath" in d) {
							my_string = my_string + "<br/>Date: " + d["date"] 
							my_string = my_string + "<br/>User: " + d["user"]
							my_string = my_string + "<br/>PC: " + d["pc"]
							my_string = my_string + "<br/>Filepath: " + d["filepath"]
			    		}

				    	document.getElementById("chart-eigenvalue_view-notes")
				    		.innerHTML = my_string;
			          })
				    .on('mouseout', function(d) {
				    	d3.select(this).style("fill-opacity", user_opacity);
			                  //console.log(d);
			                  document.getElementById("chart-eigenvalue_view-notes")
				    		.innerHTML = "Selection:";
			              })
				    .on('click', function(d) {
				    	//d3.select(this).moveToFront();
			              //    console.log(d);
			              });
			}
		}
	}
}

function draw_detailed_view_grid(placement, rolename, username, rolejson, rows, cols) {

}

function get_detailed_plot(role, user) {
	console.log("get_detailed_plot")
	details = selected_details.toString()
	console.log(details);
	$.ajax({
        url : "get_detailed_glyph_for_this_user",
        data : {'rolename':role, 'details':details}, 
        beforeSend : function() { $('#chart-eigenvalue_view').css('background', "url(" + image_path + ") no-repeat")},
        complete : function() { $('#chart-eigenvalue_view').css('background', 'none') },
        success : function(data) {

            
            console.log("get_detailed_plot done");
            console.log(data);
            var detailed_glyph_data = JSON.parse(data);
            console.log(detailed_glyph_data);
            draw_detailed_view("#chart-eigenvalue_view", role, user, detailed_glyph_data);
        }
    });
}
	