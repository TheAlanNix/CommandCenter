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
        <div id="page-title">{{ page_title }}</div>
        <div id="status-container" v-if="errors.length > 0">
            <div class="alert alert-danger text-left">
                <ul>
                    <li v-for="(error, index) in errors" :key="index">{{ error.message }}</li>
                </ul>
            </div>
        </div>
        <div id="filters-container" v-if="filter_event_name || filter_product">
            Filters: 
              <b-badge v-if="filter_product">{{filter_product}}</b-badge>
              <b-badge v-if="filter_event_name">{{filter_event_name}}</b-badge>
              <b-badge href="#" v-on:click="clearFilters" variant="danger">Clear</b-badge>
        </div>
        <div class="container-fluid">
            <div class="row">
                <div class="col-12 col-md-4">
                    <PieChart title="Events by Product"
                                :chart_data="events_by_product"
                                @selected="onProductSelected"
                                @unselected="onProductUnselected"></PieChart>
                </div>
                <div class="col-12 col-md-4">
                    <PieChart title="Events by Name"
                                :chart_data="events_by_name"
                                @selected="onEventNameSelected"
                                @unselected="onEventNameUnselected"></PieChart>
                </div>
                <div class="col-12 col-md-4">
                    <PieChart title="Events by Source IP"
                                :chart_data="events_by_source"
                                @selected="onSourceSelected"
                                @unselected="onSourceUnselected"></PieChart>
                </div>
            </div>
            <div class="row">
                <div class="col-12 col-md-6">
                    <EventTable :events="events" @update="onEventUpdate"></EventTable>
                </div>
                <div class="col-12 col-md-6">
                    <EventDetails v-if="selected_event"
                                  :selected_event="selected_event"></EventDetails>
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
import PieChart from './charts/PieChart';
import EventDetails from './EventDetails';
import EventTable from './EventTable';
import HostView from './HostView';
import MenuBar from './MenuBar';

export default {
  name: 'SecurityAlertsView',
  data() {
    return {
      errors: [],
      events: [],
      events_by_name: [],
      events_by_product: [],
      events_by_source: [],
      filter_event_name: null,
      filter_product: null,
      interval: null,
      page_title: 'Security Events',
      timeframe_options: [
        { value: '1', text: 'Past Hour' },
        { value: '6', text: 'Past 6 Hours' },
        { value: '24', text: 'Past 24 Hours' },
        { value: '168', text: 'Past Week' },
        { value: '744', text: 'Past Month' },
      ],
      timeframe_selected: '1',
      selected_event: null,
    };
  },
  components: {
    PieChart,
    EventTable,
    EventDetails,
    MenuBar,
  },
  watch: {
    events: function (val) {
      this.events_by_name = this.summarizeEventNames(val);
      this.events_by_product = this.summarizeProducts(val);
      this.events_by_source = this.summarizeSourceIps(val);
    },
  },
  methods: {
    clearFilters() {
      this.filter_event_name = null;
      this.filter_product = null;
      this.getEvents();
    },
    getEvents() {
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
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    onEventUpdate(event) {
      this.selected_event = event;
    },
    onEventNameSelected(value) {
      console.log(value);
      this.filter_event_name = value;
      this.getEvents();
    },
    onEventNameUnselected(value) {
      console.log(value);
      this.filter_event_name = null;
      this.getEvents();
    },
    onProductSelected(value) {
      console.log(value);
      this.filter_product = value;
      this.getEvents();
    },
    onProductUnselected(value) {
      console.log(value);
      this.filter_product = null;
      this.getEvents();
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
    summarizeEventNames(events) {
      var event_counts = [];
      var event_names = [];

      // Iterate through all events
      events.forEach(event => {

        // If we've already seen this event name, increment it's count
        if (event_names.includes(event.event_name)) {

          // Go through the event_counts and increment when we get a event name match
          event_counts.forEach(function(event_type) {
            if (event_type.name == event.event_name) {
              event_type.y ++;
            }
          });

        } else {
          
          // Push the event name onto our array
          event_names.push(event.event_name);

          // Store the event name
          event_counts.push({
            name: event.event_name,
            y: 1
          });
        }
      });

      return event_counts;
    },
    summarizeProducts(events) {
      var event_counts = [];
      var event_products = [];

      // Iterate through all events
      events.forEach(event => {

        // If we've already seen this product, increment it's count
        if (event_products.includes(event.product)) {

          // Go through the event_counts and increment when we get a product match
          event_counts.forEach(function(event_type) {
            if (event_type.name == event.product) {
              event_type.y ++;
            }
          });

        } else {
          
          // Push the product onto our array
          event_products.push(event.product);

          // Store the product
          event_counts.push({
            name: event.product,
            y: 1
          });
        }
      });

      return event_counts;
    },
    summarizeSourceIps(events) {
      var event_counts = [];
      var event_hosts = [];

      // Iterate through all events
      events.forEach(event => {

        // If we've already seen this host, increment it's count
        if (event_hosts.includes(event.src_ip)) {

          // Go through the event_counts and increment when we get a product match
          event_counts.forEach(function(event_src) {
            if (event_src.name == event.src_ip) {
              event_src.y ++;
            }
          });

        } else {
          
          // Push the host onto our array
          event_hosts.push(event.src_ip);

          // Store the event host
          event_counts.push({
            name: event.src_ip,
            y: 1
          });
        }
      });

      return event_counts;
    },
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  created() {
    this.getEvents();
    this.interval = setInterval(() => {
      this.getEvents();
    }, 5000);
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
