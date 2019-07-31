<template>
  <div class="chart-panel">
    <div class="row">
      <div class="col">
        <div class="chart-panel-content">
          <Highcharts :options="chartOptions"></Highcharts>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart } from 'highcharts-vue';

export default {
  props: ['title', 'chartData'],
  components: {
    Highcharts: Chart,
  },
  data() {
    return {
      chartOptions: {
        chart: {
          type: 'pie',
        },
        title: {
          text: this.title,
        },
        tooltip: {
          enabled: true,
          headerFormat: '<b>{point.key}</b><br/>',
          pointFormat: 'Count: {point.y}',
        },
        plotOptions: {
          pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
              enabled: true,
              formatter() {
                const maxLength = 15;
                if (this.key.length > maxLength) {
                  const newKey = `${this.key.substring(0, maxLength)}...`;
                  return `<b>${newKey}</b> (${this.y})`;
                }
                return `<b>${this.key}</b> (${this.y})`;
              },
            },
            innerSize: 150,
            minSize: 180,
            point: {
              events: {
                select: this.selected,
                unselect: this.unselected,
              },
            },
          },
        },
        series: [
          {
            data: this.chartData,
          },
        ],
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
    chartData(newValue) {
      this.chartOptions.series[0].data = newValue;
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
