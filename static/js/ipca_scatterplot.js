function create_projection_view(placement) {

    //d3.select(placement).style("width")

    var margin = {top: 10, right: 10, bottom: 10, left: 10},
        width =  projection_window[0] - margin.left - margin.right,
        height = projection_window[1] - margin.top - margin.bottom;

    // setup x 
    var xValue = function(d) { return d.pca_x; }, // data -> value
        xScale = d3.scale.linear().range([0, width]), // value -> display
        xMap = function(d) { return xScale(xValue(d)); }, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    // setup y
    var yValue = function(d) { return d.pca_y; }, // data -> value
        yScale = d3.scale.linear().range([height, 0]), // value -> display
        yMap = function(d) { return yScale(yValue(d));}, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");

    d3.select(placement).select("svg").remove();

    var zoom = d3.behavior.zoom()
        .scaleExtent([1, 32])
        .on("zoom", zoomed);

    var svg = d3.select(placement).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .call(zoom);
       //.call(d3.behavior.zoom().scaleExtent([1, 8]).on("zoom", zoom))
        

        var tooltip = d3.select(placement).append("div")
            .style("position", "absolute")
            .style("width", 200)
            .style("height", 28)
            .style("opacity", 0);

        // don't want dots overlapping axis, so add in buffer to data domain
        xScale.domain([d3.min(scatter_data, xValue), d3.max(scatter_data, xValue)]);
        yScale.domain([d3.min(scatter_data, yValue), d3.max(scatter_data, yValue)]);

        //xScale.domain([-axis_value, axis_value]);
        //yScale.domain([-axis_value, axis_value]);

        //xScale.domain([-1, 1]);
        //yScale.domain([-1, 1]);

        // x-axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height/2 + ")")
            .call(xAxis)
            .append("text")
            .attr("class", "label")
            .attr("x", width)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text("x");

        // y-axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + width/2 + ",0)")
            .call(yAxis)
            .append("text")
            .attr("class", "label")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("y");

        var drag_start = [0,0];

        // draw dots
        svg.selectAll(".dot")
            .data(scatter_data)
            .enter().append("circle")
            .attr("class","dot")
            .attr("r", 3.5)
            .attr("cx", xMap)
            .attr("cy", yMap)
            .style("stroke", "rgb(31, 119, 180)")
            .style("stroke-width", 1)
            .style("fill-opacity", 0.25)
            .style("fill", function(d) {
                return paracoords_colours[d.name_id]; 
            })
            .on("mouseover", function(d) {
                //console.log(d);

                var radius = 10;
                document.getElementById("chart-projection_view-notes").innerHTML = "Selection: " + d.date + " " + d.user + " " + d.name;
                d3.select(this).attr("r", radius);
                d.selected = true;
                

                var this_id = d.id;
                d3.selectAll("path.path_pc")
                    .style("stroke-opacity", 0.1)
                    .filter(function (d) { return d.id == this_id})
                    .style("stroke-opacity", 0.85)
                    .style("stroke-width", 3);

                d3.selectAll("path.path_pc_features")
                    .style("stroke-opacity", 0.1)
                    .filter(function (d) { return d.id == this_id})
                    .style("stroke-opacity", 0.85)
                    .style("stroke-width", 3);

            })
            .on("mouseout", function(d) {

                d3.select(this).attr("r",3.5);
                d.selected = false;
                var this_id = d.id;
                d3.selectAll("path.path_pc")
                    .style("stroke-opacity", 0.1)
                    .style("stroke-width", 1);

                d3.selectAll("path.path_pc_features")
                    .style("stroke-opacity", 0.1)
                    .style("stroke-width", 1);

            })
            .on('click', function(d) {
                get_detailed_plot(d.name, d.user);
            })
            .call(d3.behavior.drag()
                .on("dragstart", function(d) {
                    drag_start[0] = d3.select(this).attr("cx");
                    drag_start[1] = d3.select(this).attr("cy");
                })
                .on("drag", function(d) {
                  var mouse_pos = d3.mouse(this);
                  d3.select(this).attr("cx", mouse_pos[0]).attr("cy", mouse_pos[1]).attr("r", 10).style("fill-opacity", 0.1);
                  var coordinate_pos = [xScale.invert(mouse_pos[0]-margin.left), yScale.invert(mouse_pos[1]-margin.top)];

                  $.ajax({
                    url : "inverse_pca",
                    data : {"pca_x": coordinate_pos[0], "pca_y": coordinate_pos[1]},
                    success : function(data) { 
                        temp_features = JSON.parse(data);
                        adjust_feature_plot(d.id, temp_features)
                    }
                  });

                  svg.select("line.line_temp").remove();

                  svg.append("line")
                      .attr("class", "line_temp")
                      .attr("x1", drag_start[0])
                      .attr("y1", drag_start[1])
                      .attr("x2", mouse_pos[0])
                      .attr("y2", mouse_pos[1])
                      .style("stroke-opacity", 0.2)
                      .style("stroke-width", 1)
                      .style("stroke", "black");


                })
                .on("dragend", function(d) {
                  //console.log("dragend");
                  d3.select(this).attr("cx", drag_start[0]).attr("cy", drag_start[1]).attr("r", 3.5).style("fill-opacity", 0.25);
                    d3.select("#chart-feature_view").select("svg").select("path.path_pc_temp").remove();
                    svg.select("line.line_temp").remove();
                })
            );


        var draw_legend = false;
        if (draw_legend) {
            //draw legend
            var legend = svg.selectAll(".legend")
               .data(color.domain())
             .enter().append("g")
               .attr("class", "legend")
               .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

            //draw legend colored rectangles
            legend.append("rect")
                .attr("x", width - 18)
                .attr("width", 18)
                .attr("height", 18)
                .style("fill", color);

            // draw legend text
            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9)
                .attr("dy", ".35em")
                .style("text-anchor", "end")
                .text(function(d) { return d;})

        }
    //}

    function zoomed() {
      svg.select(".x axis").call(xAxis);
      svg.select(".y axis").call(yAxis);
    }

    // function zoom() {
    //     console.log("zooming...");
    //     svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    // }

}

function highlight_user_in_scatter_plot(username, is_selected) {
    console.log("highlight_user_in_scatter_plot");
    if (is_selected) {
        d3.select("#chart-projection_view").selectAll("circle")
            .filter(function (d) { return d.user == username; })
            .attr("r", 10);
    } else {
        d3.select("#chart-projection_view").selectAll("circle")
            .filter(function (d) { return d.user == username; })
            .attr("r", 3.5);
    }

}