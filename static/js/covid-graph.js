const margin = {
    top: 100,
    right: 200,
    bottom: 25,
    left: 100,
};

// Update dropdown options
jQuery(document).ready(function ($) {
    $.get("/r/get_dropdown_options", function (data) {
        var metric_options = [];
        data.Metric.forEach((value, index) => {
            metric_options.push({
                label: value,
                title: value,
                value: value
            });
        });

        metric_options.sort(function (a, b) {
            return a.title.localeCompare(b.title)
        });

        $('#metrics_menu').multiselect({
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            enableFullValueFiltering: true,
            maxHeight: 350
        }).multiselect('dataprovider', metric_options);

        var entity_groups = []
        Object.keys(data.Entity).forEach(function (key) {
            var group = {
                label: key,
                children: []
            }

            Array.from(data.Entity[key]).forEach((value, index) => {
                group.children.push({
                    label: value,
                    value: key + ":" + value
                });
            });

            group.children.sort(function (a, b) {
                return a.label.localeCompare(b.label)
            });
            entity_groups.push(group);
        });

        $('#entities_menu').multiselect({
            includeSelectAllOption: true,
            enableFiltering: true,
            maxHeight: 350,
            enableClickableOptGroups: true,
            enableCollapsibleOptGroups: true,
            collapseOptGroupsByDefault: true,
            enableCaseInsensitiveFiltering: true,
        }).multiselect('dataprovider', entity_groups);
    });

    $('#graph_action').on('click', function () {

        var metrics_menu = $('#metrics_menu').val();
        var entities_menu = $('#entities_menu').val();

        if ((metrics_menu != null) && (entities_menu != null)) {
            var request_string = generateRequestString(metrics_menu, entities_menu);
            render_graph(request_string);

            $('#entities_menu').multiselect('deselectAll', false);
            $('#entities_menu').multiselect('updateButtonText');

            setTimeout(null, 1000);
        }
    });


})

function generateRequestString(metrics_val, entities_val) {
    var metric_string = "metric=";
    metrics_val.forEach((val, index) => {
        if (index == 0) {
            metric_string = metric_string + val;
        } else {
            metric_string = metric_string + "," + val;
        }
    });

    var entities = {}
    entities_val.forEach((val) => {
        var split = val.split(":");
        var key = split[0];
        var actual_entity = split[1];

        if (key in entities) {
            entities[key].push(actual_entity);
        } else {
            entities[key] = [actual_entity];
        }
    })

    var entity_string = "entity=";
    var index = 0;
    Object.keys(entities).forEach((val) => {
        if (index == 0) {
            entity_string = entity_string + val;
        } else {
            entity_string = entity_string + "," + val;
        }

        index = index + 1;
    });

    var filter_string = "filters="
    var filterTypeIndex = 0;
    var filterDefinitionIndex = 0;

    Object.keys(entities).forEach((val) => {
        if (filterTypeIndex == 0) {
            filter_string = filter_string + val + ":";
        } else {
            filter_string = filter_string + "_" + val + ":";
        }

        filterDefinitionIndex = 0;
        entities[val].forEach((filterDefinition) => {
            if (filterDefinitionIndex == 0) {
                filter_string = filter_string + filterDefinition;
            } else {
                filter_string = filter_string + "," + filterDefinition;
            }

            filterDefinitionIndex = filterDefinitionIndex + 1;
        });

        filterTypeIndex = filterTypeIndex + 1;
    });

    var requestString = "/r/process?" + entity_string + "&" + metric_string + "&" + filter_string

    return requestString;
}
//------------------------1. PREPARATION------------------------//
//-----------------------------SVG------------------------------//
const width = window.innerWidth - margin.left - margin.right - 100;
const height = window.innerHeight - margin.top - margin.bottom - 100;

// we are appending SVG first
const svg = d3.select("div#container").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("text")
    .attr("class", "title")
    .attr("x", width / 2)
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .text("Covid-19 Visualizations");

const xScale = d3.scaleTime().range([0, width]);
const yScale = d3.scaleLinear().rangeRound([height, 0]);
const parseDate = d3.timeParse("%Y-%m-%d");

const color = d3.scaleOrdinal().range(d3.schemeCategory10);

const xAxis = d3.axisBottom().scale(xScale);
const yAxis = d3.axisLeft().scale(yScale);

function getColorForMetric(metric) {
    if (metric == 'Confirmed') {
        return "olivedrab";
    } else if (metric == 'Deaths') {
        return "darkred";
    } else if (metric == 'Hospitalized') {
        return "steelblue";
    } else {
        if (metric.includes("Confirmed")) {
            return "limegreen";
        } else if (metric.includes("Deaths")) {
            return "lightcoral";
        } else {
            return "skyblue";
        }
    }
}


// gridlines in x axis function
function make_x_gridlines() {
    return d3.axisBottom(xScale)
        .ticks(5)
}

// gridlines in y axis function
function make_y_gridlines() {
    return d3.axisLeft(yScale)
        .ticks(7)
}


// add the X gridlines
svg.append("g")
    .attr("class", "grid")
    .attr("transform", "translate(0," + height + ")")
    .call(make_x_gridlines()
        .tickSize(-height)
        .tickFormat("")
    )

// add the Y gridlines
svg.append("g")
    .attr("class", "grid")
    .call(make_y_gridlines()
        .tickSize(-width)
        .tickFormat("")
    )

function render_graph(endpoint) {
    d3.json(endpoint)
        .then(function (data) {

            svg.selectAll("*").remove();

            svg.append("text")
                .attr("class", "title")
                .attr("x", width / 2)
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle")
                .text("Covid-19 Visualizations");

            // Define the div for the tooltip
            var div = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            // add the X gridlines
            svg.append("g")
                .attr("class", "grid")
                .attr("transform", "translate(0," + height + ")")
                .call(make_x_gridlines()
                    .tickSize(-height)
                    .tickFormat("")
                )

            // add the Y gridlines
            svg.append("g")
                .attr("class", "grid")
                .call(make_y_gridlines()
                    .tickSize(-width)
                    .tickFormat("")
                )



            var min_date;
            var max_date;
            var min_val;
            var max_val;

            var slices = [];

            for (const metric of Object.keys(data)) {
                data[metric] = JSON.parse(data[metric])

                for (const entity of Object.keys(data[metric])) {
                    these_values = []
                    data[metric][entity].Date.forEach(function (part, index, arr) {
                        arr[index] = parseDate(arr[index]);

                        these_values.push({
                            date: arr[index],
                            val: data[metric][entity].Metric[index]
                        })
                    });

                    slices.push({
                        metric: metric,
                        id: entity,
                        values: these_values
                    })

                    var thisMinDate = Math.min.apply(null, data[metric][entity].Date);
                    if (min_date == undefined) {
                        min_date = thisMinDate;
                    } else {
                        min_date = Math.min(thisMinDate, min_date);
                    }

                    var thisMaxDate = Math.max.apply(null, data[metric][entity].Date);
                    if (max_date == undefined) {
                        max_date = thisMaxDate;
                    } else {
                        max_date = Math.max(thisMaxDate, max_date);
                    }

                    var thisMinValue = Math.min.apply(null, data[metric][entity].Metric)
                    var thisMaxValue = Math.max.apply(null, data[metric][entity].Metric)

                    if (min_val == undefined) {
                        min_val = thisMinValue;
                    } else {
                        min_val = Math.min(thisMinValue, min_val);
                    }

                    if (max_val == undefined) {
                        max_val = thisMaxValue;
                    } else {
                        max_val = Math.max(thisMaxValue, max_val);
                    }
                }
            }

            max_date = new Date(max_date);
            min_date = new Date(min_date);

            //----------------------------SCALES----------------------------//
            xScale.domain([min_date, max_date]);
            yScale.domain([min_val, 1.1 * max_val]);

            //----------------------------DOTS-----------------------------//    
            svg.selectAll("dot").remove()
            slices.forEach(element => {
                var node = svg.selectAll("dot")
                    .data(element.values)
                    .enter()

                let this_color = getColorForMetric(element.metric)
                node.append("circle")
                    .attr("class", "dot")
                    .attr("cx", function (d) {
                        return xScale(d.date);
                    })
                    .attr("cy", function (d) {
                        return yScale(d.val);
                    })
                    .style("fill", this_color)
                    .attr("r", 7)
                    .on("mouseenter", function (d) {
                        div.style("opacity", .9);
                        const selection = d3.select(this);
                        selection.style("r", 14);
                        var str;
                        if (element.metric.includes("%")) {
                            str = d.date.getFullYear() + "-" + (d.date.getMonth() + 1) + "-" +
                                d
                                .date.getDate() + ": " + d.val + '%';
                        } else {
                            str = d.date.getFullYear() + "-" + (d.date.getMonth() + 1) + "-" +
                                d
                                .date.getDate() + ": " + d.val;
                        }
                        div.html(str)
                            .style("left", (d3.event.pageX) + "px")
                            .style("top", (d3.event.pageY - 28) + "px");
                    })
                    .on("mouseleave", function (d) {
                        const selection = d3.select(this);
                        selection.style("r", 7);
                        div.style("opacity", 0);
                    });
            });

            //----------------------------LINES-----------------------------//
            var line = d3.line()
                .x(function (d) {
                    return xScale(d.date);
                })
                .y(function (d) {
                    return yScale(d.val);
                })
                .curve(d3.curveCardinal);


            //-------------------------2. DRAWING---------------------------//
            //-----------------------------AXES-----------------------------//
            svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(xScale));

            svg.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(yScale))

            //----------------------------LINES-----------------------------//
            const lines = svg.selectAll("lines")
                .data(slices)
                .enter()
                .append("g");

            lines.append("path")
                .attr("class", "line")
                .attr("d", function (d) {
                    return line(d.values);
                });


            lines.append("text")
                .attr("class", "serie_label")
                .datum(function (d) {
                    var max_y = -1;
                    var max_date = 0;
                    d.values.forEach(val => {
                        if (val.val > max_y) {
                            max_y = val.val;
                            max_date = val.date;
                        }
                    })
                    return {
                        metric: d.metric,
                        id: d.id,
                        value: {
                            date: max_date,
                            val: max_y
                        }
                    };
                })
                .attr("transform", function (d) {
                    return "translate(" + (xScale(d.value.date) + 10) +
                        "," + (yScale(d.value.val) - 5) + ")";
                })
                .text(function (d) {
                    return d.id + ": " + d.metric;
                });


            const ghost_lines = lines.append("path")
                .attr("class", "ghost-line")
                .attr("d", function (d) {
                    return line(d.values);
                });

            //---------------------------EVENTS-----------------------------// 
            svg.selectAll(".ghost-line")
                .on('dblclick', function () {
                    const selection = d3.select(this).raise();

                    var associated_metric = selection.data()[0].metric;
                    var color = getColorForMetric(associated_metric);

                    selection
                        .transition()
                        .duration("10")
                        .style("opacity", "2")
                        .style("stroke-width", "2.5")
                        .style("stroke", color);

                    // add the legend action
                    const legend = d3.select(this.parentNode)
                        .select(".serie_label");
                    legend
                        .transition()
                        .delay("100")
                        .duration("10")
                        .style("fill", "black")
                        .style("font-weight", "bold");
                }).on('click', function () {
                    const selection = d3.select(this);
                    selection
                        .transition()
                        .duration("10")
                        .style("stroke", "#454545")
                        .style("opacity", "0")
                        .style("stroke-width", "5");
                    // add the legend action
                    const legend = d3.select(this.parentNode)
                        .select(".serie_label");
                    legend
                        .transition()
                        .delay("100")
                        .duration("10")
                        .style("fill", "#454545")
                        .style("font-weight", "normal");
                });
        });
}