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
        <div class="container-fluid">
            <div class="row">
                <div class="col-12 col-md-6">
                    <EventTable :events="events" @update="onEventUpdate"></EventTable>
                </div>
                <div class="col-12 col-md-6">
                    <EventDetails :selected_event="selected_event"></EventDetails>
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
      hosts: [],
      interval: null,
      page_title: 'Security Events',
      timeframe_options: [
        { value: '1', text: 'Past Hour' },
        { value: '6', text: 'Past 6 Hours' },
        { value: '24', text: 'Past 24 Hours' },
        { value: '168', text: 'Past Week' },
        { value: '744', text: 'Past Month' },
      ],
      timeframe_selected: '24',
      selected_event: [],
    };
  },
  components: {
    EventTable,
    EventDetails,
    HostView,
    MenuBar,
  },
  methods: {
    getEvents() {
      const path = `http://localhost:5000/api/events?timeframe=${this.timeframe_selected}`;
      axios.get(path)
        .then((res) => {
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
    onTimeframeChange(value) {
      this.timeframe_selected = value;
      this.getEvents();
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
