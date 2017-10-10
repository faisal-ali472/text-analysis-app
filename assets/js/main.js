/*
 * Main Javascript file for analyzerapp.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require('jquery');
require('font-awesome-webpack');
require('bootstrap');
import * as d3 from 'd3';   // import d3 modules

// import React js modules
import React from 'react';
import ReactDOM from 'react-dom';
//import App from './App.jsx';

// Your own code
require('./plugins.js');
require('./script.js');

// Test ReactJS code
export default class App extends React.Component {
  render() {
    return (
     <div style={{textAlign: 'center'}}>
        <h1>Hello World</h1>
      </div>);
  }
}
ReactDOM.render(<App />, document.getElementById('root'));

// To-Do: move visualizations to  graph-lib.js
// attach graphs functions with ID of HTML Tag/Component
$("#graph-click").click(createGraph);


// Define Graph functions
function createGraph() {
   var svg = d3.select("svg"),
    margin = {top: 20, right: 20, bottom: 30, left: 80},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;

    var tooltip = d3.select("body").append("div").attr("class", "toolTip");

    var x = d3.scaleLinear().range([0, width]);
    var y = d3.scaleBand().range([height, 0]);

    var g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var url = "/data"
    d3.json(url, function(error, data) {
        if (error) throw error;

        data.sort(function(a, b) { return a.value - b.value; });
        // Using manual data
//    var data = [
//        {"area": "central ", "value": 18000},
//        {"area": "Riverside ", "value": 17000},
//        {"area": "Picton ", "value": 80000},
//        {"area": "Everton ", "value": 55000},
//        {"area": "Kensington ", "value": 100000},
//        {"area": "Kirkdale", "value": 50000}
//    ];
//    data.sort(function(a, b) { return a.value - b.value; });

        x.domain([0, d3.max(data, function(d) { return d.value; })]);
        y.domain(data.map(function(d) { return d.area; })).padding(0.1);

        g.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x).ticks(5).tickFormat(function(d) { return parseInt(d / 1000); }).tickSizeInner([-height]));

        g.append("g")
            .attr("class", "y axis")
            .call(d3.axisLeft(y));

        g.selectAll(".bar")
            .data(data)
          .enter().append("rect")
            .attr("class", "bar")
            .attr("x", 0)
            .attr("height", y.bandwidth())
            .attr("y", function(d) { return y(d.area); })
            .attr("width", function(d) { return x(d.value); })
            .on("mousemove", function(d){
                tooltip
                  .style("left", d3.event.pageX - 50 + "px")
                  .style("top", d3.event.pageY - 70 + "px")
                  .style("display", "inline-block")
                  .html((d.area) + "<br>" + "£" + (d.value));
            })
            .on("mouseout", function(d){ tooltip.style("display", "none");});
        });
    }
