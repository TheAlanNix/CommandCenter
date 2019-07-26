<template>
  <div id="page-container">
    <Header :pageTitle="pageTitle"/>
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <TimeSeriesChart title="Events Over Time"
                          :chart_data="eventsOverTime"></TimeSeriesChart>
        </div>
      </div>
      <div class="row">
        <div class="col-12 col-md-4">
          <PieChart title="Events by Product"
                    :chart_data="eventsByProduct"
                    @selected="onProductSelected"
                    @unselected="onProductUnselected"></PieChart>
        </div>
        <div class="col-12 col-md-4">
          <PieChart title="Events by Name"
                    :chart_data="eventsByName"
                    @selected="onEventNameSelected"
                    @unselected="onEventNameUnselected"></PieChart>
        </div>
        <div class="col-12 col-md-4">
          <PieChart title="Events by Source IP (Top 25)"
                    :chart_data="eventsBySource"
                    @selected="onSourceSelected"
                    @unselected="onSourceUnselected"></PieChart>
        </div>
      </div>
      <div class="row">
        <div class="col-12 col-md-6">
          <EventTable :events="filteredEvents" @rowSelected="onEventUpdate"></EventTable>
        </div>
        <div class="col-12 col-md-6">
          <EventDetails v-if="selectedEvent"
                        :selectedEvent="selectedEvent"></EventDetails>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import EventDetails from '../components/EventDetails.vue';
import EventTable from '../components/EventTable.vue';
import Header from '../components/Header.vue';
import PieChart from '../components/charts/PieChart.vue';
import TimeSeriesChart from '../components/charts/TimeSeriesChart.vue';

export default {
  name: 'SecurityEventsView',
  data() {
    return {
      eventsByName: [],
      eventsByProduct: [],
      eventsBySource: [],
      eventsOverTime: [],
      filteredEvents: [],
      filterEventName: null,
      filterProduct: null,
      pageTitle: 'Security Events',
      selectedEvent: null,
    };
  },
  components: {
    EventTable,
    EventDetails,
    Header,
    PieChart,
    TimeSeriesChart,
  },
  computed: {
    events() {
      return this.$store.state.events;
    },
    timeframe() {
      return this.$store.state.timeframe;
    },
  },
  watch: {
    filteredEvents: function (val) {
      if (this.filterProduct && !this.filterEventName) {
        this.eventsByName = this.summarizePieChartData(val, 'event_name');
        this.eventsBySource = this.summarizePieChartData(val, 'src_ip', 25);
      } else if (!this.filterProduct && this.filterEventName) {
        this.eventsByProduct = this.summarizePieChartData(val, 'product');
        this.eventsBySource = this.summarizePieChartData(val, 'src_ip', 25);
      } else if (this.filterProduct && this.filterEventName) {
        this.eventsBySource = this.summarizePieChartData(val, 'src_ip', 25);
      } else {
        this.eventsByName = this.summarizePieChartData(val, 'event_name');
        this.eventsByProduct = this.summarizePieChartData(val, 'product');
        this.eventsBySource = this.summarizePieChartData(val, 'src_ip', 25);
      }
    },
    events: function () {
      this.getEventsOverTime();
      this.filterEvents();
    },
    filterEventName: function () {
      this.getEventsOverTime();
      this.filterEvents();
    },
    filterProduct: function () {
      this.getEventsOverTime();
      this.filterEvents();
    },
  },
  methods: {
    clearFilters() {
      this.filter_event_name = null;
      this.filter_product = null;
      this.getEvents();
    },
    filterEvents() {
      if (this.filterProduct || this.filterEventName) {
        const returnEvents = [];

        this.events.forEach((event) => {
          // Initialize a boolean to use
          let filterMet = true;

          if (this.filterProduct && event.product !== this.filterProduct) filterMet = false;
          if (this.filterEventName && event.event_name !== this.filterEventName) filterMet = false;
          if (filterMet) returnEvents.push(event);
        });

        this.filteredEvents = returnEvents;
      } else {
        this.filteredEvents = this.events;
      }
    },
    getEventsOverTime() {
      let path = `http://${window.location.hostname}:5000/api/events-over-time?timeframe=${this.timeframe}`;
      console.log(path);
      if (this.filterProduct) path = `${path}&product=${encodeURIComponent(this.filterProduct)}`;
      if (this.filterEventName) path = `${path}&event_name=${encodeURIComponent(this.filterEventName)}`;
      axios.get(path)
        .then((res) => {
          console.log(res.data);

          const returnData = {
            name: 'Current Timeframe',
            data: [],
          };

          // Format the data for how Highcharts wants it
          res.data.event_counts.forEach((eventCount) => {
            // Create a date object
            const date = new Date(eventCount._id.$date);

            // Push the data onto a return array
            returnData.data.push([
              date.getTime(),
              eventCount.count,
            ]);
          });

          this.eventsOverTime = returnData;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    onEventUpdate(event) {
      this.selectedEvent = event;
    },
    onEventNameSelected(value) {
      console.log(`Event Name ${value} was selected.`);
      this.filterEventName = value;
    },
    onEventNameUnselected(value) {
      console.log(`Event Name ${value} was unselected.`);
      if (value === this.filterEventName) {
        this.filterEventName = null;
      }
    },
    onProductSelected(value) {
      console.log(`Product ${value} was selected.`);
      this.filterProduct = value;
      this.filterEventName = null;
    },
    onProductUnselected(value) {
      console.log(`Product ${value} was unselected.`);
      if (value === this.filterProduct) {
        this.filterProduct = null;
      }
    },
    onSourceSelected(value) {
      this.$router.push(`/host/${value}`);
    },
    onSourceUnselected(value) {
      console.log(value);
    },
    inArrayWithAttribute(array, attr, value) {
      for (let i = 0; i < array.length; i += 1) {
        if (array[i][attr] === value) {
          return i;
        }
      }
      return -1;
    },
    sortCompare(a, b) {
      if (a.y < b.y) {
        return 1;
      }
      if (a.y > b.y) {
        return -1;
      }
      return 0;
    },
    summarizePieChartData(events, property, count = 0) {
      let eventCounts = [];

      // Iterate through all events
      events.forEach((event) => {
        // Get the index of the event property
        const eventIndex = this.inArrayWithAttribute(eventCounts, 'name', event[property]);

        // Look to see if the Event Name exists
        if (eventIndex === -1) {
          // Store the event name
          eventCounts.push({
            name: event[property],
            y: 1,
          });
        } else {
          // Iterate the count
          eventCounts[eventIndex].y += 1;
        }
      });

      // Sort the array by the 'y' property
      eventCounts.sort(this.sortCompare);

      // Get the top X
      if (count > 0) {
        eventCounts = eventCounts.slice(0, count);
      }

      return eventCounts;
    },
  },
};
</script>

<style lang="scss">
#filters-container {
  margin: 5px 40px;
}
</style>
