<template>
  <div>
    <h1>Data Visualization</h1>
    <svg ref="chart" :width="width" :height="height"></svg>
  </div>
</template>

<script>
import axios from "axios";
import * as d3 from "d3";

export default {
  data() {
    return {
      width: 400,
      height: 300,
      data: null,
    };
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/data/");
        this.data = response.data;
        this.renderChart();
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
    renderChart() {
      if (!this.data) return;

      const svg = d3.select(this.$refs.chart);
      svg.selectAll("*").remove(); // Clear any existing content

      const { labels, values } = this.data;

      const xScale = d3
        .scaleBand()
        .domain(labels)
        .range([0, this.width])
        .padding(0.1);

      const yScale = d3
        .scaleLinear()
        .domain([0, d3.max(values)])
        .range([this.height, 0]);

      svg
        .selectAll("rect")
        .data(values)
        .enter()
        .append("rect")
        .attr("x", (_, i) => xScale(labels[i]))
        .attr("y", (d) => yScale(d))
        .attr("width", xScale.bandwidth())
        .attr("height", (d) => this.height - yScale(d))
        .attr("fill", "steelblue");

      svg
        .append("g")
        .attr("transform", `translate(0, ${this.height})`)
        .call(d3.axisBottom(xScale));

      svg.append("g").call(d3.axisLeft(yScale));
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style>
svg {
  border: 1px solid #ccc;
}
</style>
