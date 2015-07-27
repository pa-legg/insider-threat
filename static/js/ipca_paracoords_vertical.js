function create_eigenvalue_view(cars2, placement) {
  console.log('create_eigenvalue_view');
    var margin = {top: 50, right: 10, bottom: 10, left: 10},
        width = eigenvalue_window[1] - margin.left - margin.right,
        height = eigenvalue_window[0] - margin.top - margin.bottom;

    var x2 = d3.scale.ordinal().rangePoints([0, width], 1),
        y2 = {},
        dragging = {};

    var line = d3.svg.line(),
        axis = d3.svg.axis().orient("left").tickFormat(d3.format(".2f")),
        background,
        foreground;

    d3.select(placement).select("svg").remove();

    var svg = d3.select(placement).append("svg")
        .attr("width", height + margin.top + margin.bottom)
        .attr("height", width + margin.left + margin.right)
      .append("g")
        .attr("transform", "rotate(90), translate(0,-" + (height + margin.bottom) + ")");


      // Extract the list of dimensions and create a scale for each.
      x2.domain(dimensions2 = d3.keys(cars2[0]).filter(function(d) {
        return d != "id" && d != "name" && d != "name_id" && d != "user" &&  d != "date" &&  d != "pca_x" && d != "pca_y" && d != "selected" && (y2[d] = d3.scale.linear()
            .domain(d3.extent(cars2, function(p) { return +p[d]; }))
            .range([height, 0]));
      }));

      background = svg.append("g")
        .selectAll("path")
          .data(cars2)
        .enter().append("path")
        .attr("class", "path_pc")
          .attr("d", path2)
          .style("fill", "none")
          .style("stroke-opacity", 0.1)
          .style("stroke", function(d) {
            return paracoords_colours[d.name_id]; 
            })
          .style("shape-rendering", "crispEdges");

      foreground = svg.append("g")
        .selectAll("path")
          .data(cars2)
        .enter().append("path")
        .attr("class", "path_pc")
          .attr("d", path2)
          .style("fill", "none")
          .style("stroke-opacity", 0.4)
          .style("stroke", function(d) {
            return paracoords_colours[d.name_id]; 
            })
          .on("mouseover", function(d) {
              document.getElementById("chart-eigenvalue_view-notes").innerHTML = "Selection: " + d.name;
              d.selected = true;
              console.log(d.id);
              d3.select(this).style("stroke-width", 2).style("stroke-opacity", 0.85);

              var this_id = d.id;
              d3.selectAll("circle.dot")
                  .filter(function (d) { return d.id == this_id})
                  .attr("r", 10);

            })
          .on("mouseout", function(d) {
            document.getElementById("chart-eigenvalue_view-notes").innerHTML = "Selection: ";
              d.selected = false;
              d3.select(this).style("stroke-width", 1).style("stroke-opacity", 0.1);

              var this_id = d.id;
              d3.selectAll("circle.dot")
                  .attr("r", 3.5);
          });

      // Add a group element for each dimension.
      var g = svg.selectAll(".dimension2")
          .data(dimensions2)
          .enter().append("g")
          .attr("class", "dimension")
          .attr("transform", function(d) { return "translate(" + x2(d) + ")"; })
          .call(d3.behavior.drag()
            .origin(function(d) { return {x: x2(d)}; })
            .on("dragstart", function(d) {
              dragging[d] = x2(d);
              background.attr("visibility", "hidden");
            })
            .on("drag", function(d) {
              dragging[d] = Math.min(width, Math.max(0, d3.event.x));
              foreground.attr("d", path2);
              dimensions2.sort(function(a, b) { return position2(a) - position2(b); });
              x2.domain(dimensions2);
              g.attr("transform", function(d) { return "translate(" + position2(d) + ")"; })
            })
            .on("dragend", function(d) {
              delete dragging[d];
              transition(d3.select(this)).attr("transform", "translate(" + x2(d) + ")");
              transition(foreground).attr("d", path2);
              background
                  .attr("d", path2)
                  .transition()
                  .delay(500)
                  .duration(0)
                  .attr("visibility", null);
            }));

      // Add an axis and title.
      g.append("g")
          .attr("class", "paracoords_axis2")
          .each(function(d) { d3.select(this).call(axis.scale(y2[d])); })
          .append("text")
          .style("text-anchor", "middle")
          .attr("y", -9)
          .attr("transform", "rotate(-30), translate(-15,0)")
          .text(function(d) { return d; });

      g.append("g")
          .attr("class", "paracoords_box")
          .append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", 10)
          .attr("height", 10)
          .attr("transform", "translate(-5,-15)")
          .style("stroke", "black")
          .style("fill", "green")
          .style("fill-opacity", function(d) {
            if (projection_axes.indexOf(d) != -1) {
              return 0.8;
            } else {
              return 0.1;
            }
          })
          .on("click", function(d) {
            console.log(d);
            if (projection_axes.indexOf(d) != -1) {
              projection_axes.splice(projection_axes.indexOf(d), 1);
              d3.select(this).style("fill-opacity",0.1);
            } else {
              if (projection_axes.length < 2) {
                projection_axes.push(d);
                d3.select(this).style("fill-opacity",0.8);
              }
            }

            console.log(projection_axes);
          });

      // Add and store a brush for each axis.
      g.append("g")
          .attr("class", "paracoords_brush2")
          .each(function(d) {
            d3.select(this).call(y2[d].brush = d3.svg.brush().y(y2[d]).on("brushstart", brushstart2).on("brush", brush2));
          })
        .selectAll("rect")
          .attr("x", -8)
          .attr("width", 16);


    function position2(d) {
      var v = dragging[d];
      return v == null ? x2(d) : v;
    }

    function transition(g) {
      return g.transition().duration(500);
    }

    // Returns the path for a given data point.
    function path2(d) {
      return line(dimensions2.map(function(p) { return [position2(p), y2[p](d[p])]; }));
    }

    function brushstart2() {
      d3.event.sourceEvent.stopPropagation();
    }

    // Handles a brush event, toggling the display of foreground lines.
    function brush2() {

      var actives = dimensions2.filter(function(p) { console.log(y2, y2[p], p); return !y2[p].brush.empty(); }),
          extents = actives.map(function(p) { return y2[p].brush.extent(); });

      foreground.style("display", function(d) {
        return actives.every(function(p, i) {
          return extents[i][0] <= d[p] && d[p] <= extents[i][1];
        }) ? null : "none";
      });
      
    }
}