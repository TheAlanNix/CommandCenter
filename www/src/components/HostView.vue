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
        <div id="page-title">
            Host: <b-form-input id="host-input"
                                size="sm"
                                :value="this.host_ip"
                                @change="onHostIpChange"></b-form-input>
        </div>
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
                    <IseHostPanel :host_ip="host_ip"></IseHostPanel>
                    <StealthwatchHostPanel :flows="flows"
                                           :flows_loading="flows_loading"
                                           :host_ip="host_ip"
                                           :host_snapshot="host_snapshot"></StealthwatchHostPanel>
                </div>
                <div class="col-12 col-md-6">
                    <EventTable :events="events" @update="onEventUpdate"></EventTable>
                    <EventDetails v-if="selected_event"
                                  :selected_event="selected_event"></EventDetails>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import EventDetails from './EventDetails';
import EventTable from './EventTable';
import IseHostPanel from './product_panels/IseHostPanel';
import StealthwatchHostPanel from './product_panels/StealthwatchHostPanel';
import MenuBar from './MenuBar';

export default {
  name: 'HostView',
  props: ['host_ip'],
  watch: {
    host_ip: function () {
      this.getEvents();
      this.resetFlowInterval();
      this.getFlows();
    },
  },
  data() {
    return {
      errors: [],
      events: [],
      event_interval: null,
      flows: [],
      flows_loading: false,
      flows_interval: null,
      host_snapshot: [],
      timeframe_options: [
        { value: '1', text: 'Past Hour' },
        { value: '6', text: 'Past 6 Hours' },
        { value: '24', text: 'Past 24 Hours' },
        { value: '168', text: 'Past Week' },
        { value: '744', text: 'Past Month' },
      ],
      timeframe_selected: '6',
      selected_event: null,
    };
  },
  components: {
    EventDetails,
    EventTable,
    IseHostPanel,
    StealthwatchHostPanel,
    MenuBar,
  },
  methods: {
    getEvents() {
      const path = `http://${location.hostname}:5000/api/events?host_ip=${this.host_ip}&timeframe=${this.timeframe_selected}`;
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
    getFlows() {
      this.flows_loading = true;
      const path = `http://${location.hostname}:5000/api/stealthwatch/flows?host_ip=${this.host_ip}&timeframe=${this.timeframe_selected}`;
      axios.get(path)
        .then((res) => {
          this.flows = res.data.getFlowsResponse['flow-list'].flow;
          this.flows_loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    getHostSnapshot() {
      const path = `http://${location.hostname}:5000/api/stealthwatch/host-snapshot?host_ip=${this.host_ip}`;
      axios.get(path)
        .then((res) => {
          this.host_snapshot = res.data.getHostSnapshotResponse['host-snapshot'];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    resetFlowInterval() {
      clearInterval(this.flows_interval);
      this.flows_interval = setInterval(() => {
        this.getFlows();
      }, 60000)
    },
    onEventUpdate(event) {
      this.selected_event = event;
    },
    onHostIpChange(host_ip) {
      this.$router.push(`/host/${host_ip}`);
    },
    onTimeframeChange(value) {
      this.timeframe_selected = value;
      this.getEvents();
      this.resetFlowInterval();
      this.getFlows();
    },
  },
  beforeDestroy() {
    clearInterval(this.event_interval);
    clearInterval(this.flows_interval);
  },
  created() {
    this.getEvents();
    this.event_interval = setInterval(() => {
      this.getEvents();
    }, 5000);
    this.getFlows();
    this.resetFlowInterval();
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

#host-input {
    display: inline;
    width: 150px;
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

.host-panel {
    background-color: #fff;
    border: 1px solid $border-color;
    border-radius: 5px;
    margin-top: 10px;
    position: relative;

    .host-panel-header {
        border-bottom: 1px solid $border-color;
        color: #212529;
        font-size: 20px;
        padding: 10px 15px;
    }

    .host-panel-content {
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
