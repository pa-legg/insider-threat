var margin = {top: 0, right: 10, bottom: 0, left: 10};
var x, y, dragging;


var line = d3.svg.line(),
    axis = d3.svg.axis().orient("left").tickFormat(d3.format(".2f")),
    background,
    foreground,
    dimensions;



function create_feature_view(cars, placement) {
  console.log('create_feature_view', cars);
    
    width = features_window[0] - margin.left - margin.right;
    height = 200 - margin.top - margin.bottom;

    x = d3.scale.ordinal().rangePoints([0, width], 1),
    y = {},
    dragging = {};
    

    d3.select(placement).select("svg").remove();

    var svg = d3.select(placement).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


      // Extract the list of dimensions and create a scale for each.
      x.domain(dimensions = d3.keys(cars[0]).filter(function(d) {
        return d != "id" && d != "name" && d != "name_id" && d != "user" &&  d != "date" &&  d != "pca_x" && d != "pca_y" && d != "selected" && (y[d] = d3.scale.linear()
            .domain(d3.extent(cars, function(p) { return +p[d]; }))
            .range([height, 0]));
      }));

      background = svg.append("g")
        .selectAll("path")
          .data(cars)
        .enter().append("path")
        .attr("class", "path_pc_features")
          .attr("d", path)
          .style("fill", "none")
          .style("stroke-opacity", 0.1)
          .style("stroke", function(d) {
            return paracoords_colours[d.name_id]; 
            })
          .style("shape-rendering", "crispEdges");

      foreground = svg.append("g")
        .selectAll("path")
          .data(cars)
          .enter()
          .append("path")
          .attr("class", "path_pc_features")
          .attr("d", path)
          .style("fill", "none")
          .style("stroke-opacity", 0.4)
          .style("stroke", function(d) {
            return paracoords_colours[d.name_id]; 
            })
          .on("mouseover", function(d) {
              document.getElementById("chart-feature_view-notes").innerHTML = "Selection: " + d.name;
              d.selected = true;
              console.log(d.id);
              d3.select(this).style("stroke-width", 2).style("stroke-opacity", 0.85);

              var this_id = d.id;
              d3.selectAll("circle.dot")
                  .filter(function (d) { return d.id == this_id})
                  .attr("r", 10);

            })
          .on("mouseout", function(d) {
            document.getElementById("chart-feature_view-notes").innerHTML = "Selection: ";
              d.selected = false;
              d3.select(this).style("stroke-width", 1).style("stroke-opacity", 0.1);

              var this_id = d.id;
              d3.selectAll("circle.dot")
                  .attr("r", 3.5);
          });

      // Add a group element for each dimension.
      var g = svg.selectAll(".dimension")
          .data(dimensions)
        .enter().append("g")
          .attr("class", "dimension")
          .attr("transform", function(d) { return "translate(" + x(d) + ")"; })
          .call(d3.behavior.drag()
            .origin(function(d) { return {x: x(d)}; })
            .on("dragstart", function(d) {
              dragging[d] = x(d);
              background.attr("visibility", "hidden");
            })
            .on("drag", function(d) {
              dragging[d] = Math.min(width, Math.max(0, d3.event.x));
              foreground.attr("d", path);
              dimensions.sort(function(a, b) { return position(a) - position(b); });
              x.domain(dimensions);
              g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
            })
            .on("dragend", function(d) {
              delete dragging[d];
              transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
              transition(foreground).attr("d", path);
              background
                  .attr("d", path)
                .transition()
                  .delay(500)
                  .duration(0)
                  .attr("visibility", null);
            })
          );

      // Add an axis and title.
      g.append("g")
          .attr("class", "paracoords_axis")
          .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
          .on("mouseover", function(d) {
            console.log("mouseover axis", d);
            document.getElementById("chart-feature_view-notes").innerHTML = "Selection: " + d;
          })
          .on("mouseout", function(d) {
            document.getElementById("chart-feature_view-notes").innerHTML = "Selection: "
          });

      // Add and store a brush for each axis.
      g.append("g")
          .attr("class", "paracoords_brush1")
          .each(function(d) {
            d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brushstart", brushstart1).on("brush", brush1));
          })
        .selectAll("rect")
          .attr("x", -8)
          .attr("width", 16);

          

}

function position(d) {
  var v = dragging[d];
  return v == null ? x(d) : v;
}

function transition(g) {
  return g.transition().duration(500);
}

// Returns the path for a given data point.
function path(d) {
  return line(dimensions.map(function(p) { return [position(p), y[p](d[p])]; }));
}

function brushstart1() {
  d3.event.sourceEvent.stopPropagation();
}

// Handles a brush event, toggling the display of foreground lines.
function brush1() {

  var actives = dimensions.filter(function(p) { console.log(y, y[p]); return !y[p].brush.empty(); }),
      extents = actives.map(function(p) { return y[p].brush.extent(); });

  foreground.style("display", function(d) {
    return actives.every(function(p, i) {
      return extents[i][0] <= d[p] && d[p] <= extents[i][1];
    }) ? null : "none";
  });

}

function adjust_feature_plot(this_id, temp_feature) {
  //console.log(this_id, temp_feature['result'][0]);
  new_data = []
  new_entry = {}
  for (j in all_data['axes']) {
    new_entry[all_data['axes'][j]] = temp_feature['result'][0][j]
  }
  new_data.push(new_entry);
  console.log(new_data);

  d3.select("#chart-feature_view").select("svg").select("path.path_pc_temp").remove();
  d3.select("#chart-feature_view").select("svg").append("g")
        .selectAll("path")
          .data(new_data)
          .enter()
          .append("path")
          .attr("class", "path_pc_temp")
          .attr("d", path)
          .style("fill", "none")
          .style("stroke-opacity", 1.0)
          .style("stroke-width", 2)
          .style("stroke", "black")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



  // d3.selectAll("path.path_pc_features")
  //     .filter(function (d) { return d.id == this_id} )
  //     .style("stroke-width",10)
  //     .attr("d", path);
}

function set_selected_features() {
  console.log("Set features")
  selected_features = []
  for (f in all_features) {
    if (document.getElementById(all_features[f]).checked) {
      selected_features.push(all_features[f]);
    }
  }
  console.log(selected_features)

}

function select_all_features(is_true) {

  for (f in all_features) {
    console.log(all_features[f]);
    if (is_true) {
      document.getElementById(all_features[f]).checked = true;
    } else {
      document.getElementById(all_features[f]).checked = false;
    }
  }

  set_selected_features();
}

function set_features(value) {
  console.log(value, document.getElementById(value).checked);
  //document.getElementById(value).checked = !document.getElementById(value).checked;
  set_selected_features();
}

function set_details(value) {
  console.log(value, document.getElementById(value).checked);
  //document.getElementById(value).checked = !document.getElementById(value).checked;
  set_selected_details();
}

function set_selected_details() {
  console.log("Set features")
  selected_details = []
  var activities = ['logon', 'device', 'http', 'file', 'email'];
  for (f in activities) {
    if (document.getElementById(activities[f]).checked) {
      selected_details.push(activities[f]);
    }
  }
  console.log(selected_details)

}

function create_feature_selection_view(placement) {

  var html = '';

  for (f in all_features) {
    html = html + "<input type='checkbox' onclick='set_features(value);' checked=true name='feature' id='" + all_features[f] + "' value='" + all_features[f] + "'>" + all_features[f] + "<br>"
  }
  html = html + "<br />"
  var activities = ['logon', 'device', 'http', 'file', 'email'];
  for (f in activities) {
    html = html + "<input type='checkbox' onclick='set_details(value);' checked=true name='detail' id='" + activities[f] + "' value='" + activities[f] + "'>" + activities[f] + "<br>"
  }
  var mydiv = document.getElementById("chart-featureselection_view").innerHTML = html;

}




