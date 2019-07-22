<template>
    <div class="chart-panel">
        <div class="row">
            <div class="col">
                <div class="chart-panel-content">
                    <highcharts :options="chartOptions"></highcharts>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {Chart} from 'highcharts-vue';

export default {
  props: ['title', 'chart_data'],
  components: {
    highcharts: Chart,
  },
  data() {
    return {
      chartOptions: {
        chart: {
          type: 'spline',
        },
        title: {
          text: this.title,
        },
        xAxis: {
          type: 'datetime',
          title: {
            text: 'Date'
          },
        },
        yAxis: {
          title: {
            text: 'Event Count'
          },
          min: 0
        },
        tooltip: {
          enabled: true,
          headerFormat: "<b>{point.key}</b><br/>",
          pointFormat: "Count: {point.y}",
        },
        plotOptions: {
          spline: {
            marker: {
              enabled: true,
            },
          },
        },
        series: [this.chart_data]
      },
    };
  },
  methods: {
    selected(event) {
      this.$emit('selected', event.target.name);
    },
    unselected(event) {
      this.$emit('unselected', event.target.name);
    },
  },
  watch: {
    chart_data: function(newValue) {
      this.chartOptions.series = newValue;
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

.chart-panel {
    background-color: #fff;
    border: 1px solid $border-color;
    border-radius: 5px;
    margin-top: 10px;
    position: relative;

    .chart-panel-header {
        border-bottom: 1px solid $border-color;
        color: #212529;
        font-size: 20px;
        padding: 10px 15px;
    }

    .chart-panel-content {
        //border-top: 1px solid $border-color;
        padding: 15px;
        max-height: 80vh;
        margin-bottom: 0px;
        overflow-y: scroll;

        .heading {
            font: 16px Nunito, sans-serif;
            color: #212529;
        }

        .content {
            display: block;
            font-size: 12px;
            margin-left: 20px;
        }
    }
}
</style>
