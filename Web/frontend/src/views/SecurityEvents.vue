<template>
  <div id="page-container">
    <MenuBar :events="events"></MenuBar>
      <div id="time-selection">
        <b-form inline>
          <label class="mr-sm-2" for="inlineFormCustomSelectPref">Timeframe: </label>
            <b-form-select v-model="timeframe_selected"
                           :options="timeframe_options"
                           size="sm"
                           @change="onTimeframeChange">
            </b-form-select>
          </b-form>
        </div>
        <div id="page-title">{{ page_title }} <i v-show="eventsLoading" id="loading" class="fa fa-refresh fa-spin fa-1x"></i></div>
        <div id="status-container" v-if="errors.length > 0">
          <div class="alert alert-danger text-left">
            <ul>
              <li>{{ errors[0].message }}</li>
            </ul>
          </div>
        </div>
        <!--<div id="filters-container" v-if="filterEventName || filterProduct">
            Filters: 
              <b-badge v-if="filterProduct">{{ filterProduct }}</b-badge>
              <b-badge v-if="filterEventName">{{ filterEventName }}</b-badge>
              <b-badge href="#" v-on:click="clearFilters" variant="danger">Clear</b-badge>
        </div>-->
        <div class="container-fluid">
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
                    <EventTable :events="displayedEvents" @rowSelected="onEventUpdate"></EventTable>
                </div>
                <div class="col-12 col-md-6">
                    <EventDetails v-if="selectedEvent"
                                  :selected_event="selectedEvent"></EventDetails>
                </div>
            </div>
        </div>
        <!--<div id="command-viewport" class="container-fluid">
            <div class="row">
                <HostView v-for="(event, index) in events"
                            :key="index"
                            :host_ip="event.src_ip"></HostView>
            </div>
        </div>-->
    </div>
</template>

<script>
import axios from 'axios';
import PieChart from '../components/charts/PieChart.vue';
import EventDetails from '../components/EventDetails.vue';
import EventTable from '../components/EventTable.vue';
// import HostView from './Host.vue';
import MenuBar from '../components/MenuBar.vue';

export default {
  name: 'SecurityEventsView',
  data() {
    return {
      displayedEvents: [],
      errors: [],
      events: [],
      eventsLoading: false,
      eventsByName: [],
      eventsByProduct: [],
      eventsBySource: [],
      filterEventName: null,
      filterProduct: null,
      interval: null,
      page_title: 'Security Events',
      timeframe_options: [
        { value: '1', text: 'Past Hour' },
        { value: '6', text: 'Past 6 Hours' },
        { value: '24', text: 'Past 24 Hours' },
        { value: '168', text: 'Past Week' },
        { value: '744', text: 'Past Month' },
      ],
      timeframe_selected: '6',
      selectedEvent: null,
    };
  },
  components: {
    PieChart,
    EventTable,
    EventDetails,
    MenuBar,
  },
  watch: {
    displayedEvents: function (val) {
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
    events: function (val) {
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
        let returnEvents = [];

        this.events.forEach(event => {

          let filterMet = true;

          if (this.filterProduct && event['product'] != this.filterProduct)
            filterMet = false;

          if (this.filterEventName && event['event_name'] != this.filterEventName)
            filterMet = false;

          if (filterMet)
            returnEvents.push(event);
        });

        this.displayedEvents = returnEvents;

      } else {
        this.displayedEvents = this.events;
      }
    },
    getEvents() {
      clearInterval(this.interval);
      this.eventsLoading = true;
      var path = `http://${location.hostname}:5000/api/events?timeframe=${this.timeframe_selected}`;
      console.log(path);
      if (this.filter_product)
        path = path + `&product=${encodeURIComponent(this.filter_product)}`;
      if (this.filter_event_name)
        path = path + `&event_name=${encodeURIComponent(this.filter_event_name)}`;
      axios.get(path)
        .then((res) => {
          console.log(res.data);
          this.events = res.data.events;
          this.eventsLoading = false;
          this.interval = setTimeout(() => {
            this.getEvents();
          }, 30000);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.unshift({ message: error });
          this.eventsLoading = false;
          this.interval = setTimeout(() => {
            this.getEvents();
          }, 30000);
        });
    },
    onEventUpdate(event) {
      this.selectedEvent = event;
    },
    onEventNameSelected(value) {
      console.log(value);
      this.filterEventName = value;
      this.filterEvents();
    },
    onEventNameUnselected(value) {
      console.log(value);
      if (value == this.filterEventName) {
        this.filterEventName = null;
      }
      this.filterEvents();
    },
    onProductSelected(value) {
      console.log(value);
      this.filterProduct = value;
      this.filterEventName = null;
      this.filterEvents();
    },
    onProductUnselected(value) {
      console.log(value);
      if (value == this.filterProduct) {
        this.filterProduct = null;
      }
      this.filterEvents();
    },
    onSourceSelected(value) {
      this.$router.push(`/host/${value}`);
    },
    onSourceUnselected(value) {
      console.log(value);
    },
    onTimeframeChange(value) {
      this.timeframe_selected = value;
      this.getEvents();
    },
    inArrayWithAttribute(array, attr, value) {
      for (var i = 0; i < array.length; i ++) {
        if(array[i][attr] === value) {
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
      events.forEach(event => {

        // Get the index of the event property
        var eventIndex = this.inArrayWithAttribute(eventCounts, 'name', event[property]);

        // Look to see if the Event Name exists
        if (eventIndex === -1) {
          // Store the event name
          eventCounts.push({
            name: event[property],
            y: 1
          });
        } else {
          // Iterate the count
          eventCounts[eventIndex].y++;
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
  beforeDestroy() {
    clearInterval(this.interval);
  },
  created() {
    this.getEvents();
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

html, body {
    background-color: #fff;
    color: #636b6f;
    font-family: 'Nunito', sans-serif;
    font-weight: 200;
    height: 100vh;
    margin: 0;
}

#page-container {
    background-color: #f7f7f9;
    min-height: 100vh;
    padding-bottom: 15px;
    position: relative;
    width: 100%;
}

#time-selection {
  float: right;
  margin: 20px 30px;
}

#page-title {
    font-size: 24px;
    margin: 20px 30px;
}

#filters-container {
  margin: 5px 40px;
}

#status-container {
    margin: 20px 0px;
    text-align: center;

    .alert {
        max-width: 40%;
        margin: auto;

        ul {
            margin-bottom: 0;
        }
    }
}
</style>
