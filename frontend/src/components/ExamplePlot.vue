<template>
  <div>
    <h1>SNL Loss Development</h1>
      <div class="filter">
        <label for="program-filter">Program: </label>
        <select id="program-filter" v-model="selectedProgram" @change="updateChart">
          <option v-for="program in programs" :key="program" :value="program">
            {{ program }}
          </option>
      </select>
    </div>
    <svg ref="chart" :width="width" :height="height"></svg>
  </div>
</template>
<script>
    import * as d3 from "d3";

    export default {
      name: "LinePlot",
      data() {
        return {
          margin: { top: 20, right: 150, bottom: 50, left: 60 },
          width: 900,
          height: 500,
          apiUrl: "http://localhost:8000/api/triangle-data/",
          selectedProgram: "all",
          programs: [],
          historicalPointSize: 3,
          historicalLineOpacity: 0.1,
          historicalLineStroke: 'grey'
        };
      },
      mounted() {
        this.drawChart();
      },
      methods: {
        async drawChart() {
          const { margin, width, height, apiUrl } = this;
          // Calculate inner dimensions
          const innerWidth = width - margin.left - margin.right;
          const innerHeight = height - margin.top - margin.bottom;

          // Set up the SVG element.
          const svg = d3
            .select(this.$refs.chart)
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

          const parseDate = d3.timeParse("%Y-%m-%d");

          let data;
          try {
            data = await d3.json(apiUrl);
            this.programs = Array.from(new Set(data.map(d => d.program)));
          } catch (error) {
            console.error("Error fetching data:", error);
            return;
          }

          data.forEach(d => {
            d.period_start = parseDate(d.period_start);
            d.earned_premium = +d.earned_premium;
            d.reported_loss = +d.reported_loss;
            d.loss_ratio = d.reported_loss / d.earned_premium;
            d.dev_lag = +d.dev_lag;
          });

          // Group the data by dev_lag.
          const dataByDevLag = d3.group(data, d => d.dev_lag);

          // Create scales.
          const xScale = d3.scaleTime()
            .domain(d3.extent(data, d => d.period_start))
            .range([0, innerWidth]);
          const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.loss_ratio) * 1.1])
            .range([innerHeight, 0]);

          // Create color scale.
          const colorScale = d3.scaleOrdinal()
            .domain(Array.from(dataByDevLag.keys()))
            .range(d3.schemeCategory10);

          // Define the line generator.
          const lineGen = d3.line()
            .x(d => xScale(d.period_start))
            .y(d => yScale(d.loss_ratio))
            .curve(d3.curveLinear); // Use straight lines between points

          // Append the X axis.
          const xAxis = d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%Y"));
          svg.append("g")
            .attr("transform", `translate(0, ${innerHeight})`)
            .call(xAxis)
            .append("text")
              .attr("fill", "#000")
              .attr("x", innerWidth / 2)
              .attr("y", 35)
              .attr("text-anchor", "middle")
              .text("Period Start");

          // Append the Y axis.
          const yAxis = d3.axisLeft(yScale);
          svg.append("g")
            .call(yAxis)
            .append("text")
              .attr("fill", "#000")
              .attr("transform", "rotate(-90)")
              .attr("y", -50)
              .attr("x", -innerHeight / 2)
              .attr("dy", "0.71em")
              .attr("text-anchor", "middle")
              .text("Reported Loss Ratio");

          // Draw a line for each dev lag group.
          dataByDevLag.forEach((values, devLag) => {
            // Sort the values by period_start.
            values.sort((a, b) => d3.ascending(a.period_start, b.period_start));
            svg.append("path")
              .datum(values)
              .attr("class", "line")
              .attr("d", lineGen)
              .attr("stroke", colorScale(devLag))
              .attr("stroke-width", 2)
              // .attr("opacity", historicalLineOpacity)
              .attr("fill", "none")
              .attr("id", "line-" + devLag);

            svg.selectAll(".dot-" + devLag)
              .data(values)
              .enter().append("circle")
              .attr("class", "dot dot-" + devLag)
              // .attr("r", historicalPointSize)
              .attr("r", 5)
              .attr("fill", "white")
              .attr("stroke", "#000")
              .attr("stroke-width", 1)
              .attr("stroke-opacity", 0.25)
              .attr("cx", d => xScale(d.period_start))
              .attr("cy", d => yScale(d.loss_ratio))
              .on("mouseover", function(event, d) {
                // d3.select(this).attr("r", historicalPointSize * 1.5);
                // Optionally, show a tooltip here
              })
              .on("mouseout", function(event, d) {
                // d3.select(this).attr("r", historicalPointSize);
                // Optionally, hide the tooltip here
              });
          });

          // Add legend for the dev lag lines.
          const legend = svg.selectAll(".legend")
            .data(Array.from(dataByDevLag.keys()))
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", (d, i) => `translate(${innerWidth + 20}, ${i * 20})`);

          legend.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", d => colorScale(d));

          legend.append("text")
            .attr("x", 24)
            .attr("y", 14)
            .text(d => `Dev Lag: ${d}`);
        }
      }
    };
</script>

<style>
svg {
  border: 1px solid #ccc;
}
</style>
