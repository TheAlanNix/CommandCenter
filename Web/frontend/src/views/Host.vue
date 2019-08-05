<template>
  <div id="page-container">
    <Header :pageTitle="pageTitle" :hostIp="hostIp" />
    <div class="container-fluid">
      <div class="row">
        <div class="col-12 col-md-6">
          <IseHostPanel :hostIp="hostIp"></IseHostPanel>
          <AmpHostPanel :hostIp="hostIp"></AmpHostPanel>
          <StealthwatchHostPanel :hostIp="hostIp"></StealthwatchHostPanel>
        </div>
        <div class="col-12 col-md-6">
          <TimeSeriesChart
            v-if="eventsOverTime.data && eventsOverTime.data.length"
            :title="'Events Over Time for ' + hostIp"
            :chartData="eventsOverTime"
          ></TimeSeriesChart>
          <EventTable :events="filteredEvents" @rowSelected="onEventUpdate"></EventTable>
          <EventDetails v-if="selectedEvent" :selectedEvent="selectedEvent"></EventDetails>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import EventDetails from '../components/EventDetails.vue';
import EventTable from '../components/EventTable.vue';
import Header from '../components/Header.vue';
import AmpHostPanel from '../components/product_panels/AmpHostPanel.vue';
import IseHostPanel from '../components/product_panels/IseHostPanel.vue';
import StealthwatchHostPanel from '../components/product_panels/StealthwatchHostPanel.vue';
import TimeSeriesChart from '../components/charts/TimeSeriesChart.vue';

export default {
  name: 'HostView',
  props: ['hostIp'],
  data() {
    return {
      eventsOverTime: [],
      filteredEvents: [],
      hostSnapshot: [],
      pageTitle: `Host ${this.hostIp}`,
      selectedEvent: null,
    };
  },
  components: {
    AmpHostPanel,
    EventDetails,
    EventTable,
    Header,
    IseHostPanel,
    StealthwatchHostPanel,
    TimeSeriesChart,
  },
  computed: {
    ...mapState([
      'events',
      'timeframe',
    ]),
  },
  watch: {
    events() {
      this.getEventsOverTime();
      this.filterEvents();
      this.$store.dispatch('setTimeout', setTimeout(() => {
        this.$store.dispatch('getEvents', this.hostIp);
      }, 30000));
    },
  },
  methods: {
    getEventsOverTime() {
      const path = `http://${window.location.hostname}:5000/api/events-over-time?timeframe=${this.timeframe}&host_ip=${this.hostIp}`;
      console.log(path);
      axios
        .get(path)
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
            returnData.data.push([date.getTime(), eventCount.count]);
          });

          this.eventsOverTime = returnData;
        })
        .catch((error) => {
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
    filterEvents() {
      const returnEvents = [];

      this.events.forEach((event) => {
        if (this.hostIp === event.src_ip) {
          returnEvents.push(event);
        }
      });

      this.filteredEvents = returnEvents;
    },
    onEventUpdate(event) {
      this.selectedEvent = event;
    },
  },
  beforeDestroy() {
    this.$store.dispatch('clearTimeout');
  },
  created() {
    this.$store.dispatch('getEvents', this.hostIp);
    this.$store.dispatch('setTimeout', setTimeout(() => {
      this.$store.dispatch('getEvents', this.hostIp);
    }, 30000));
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

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
