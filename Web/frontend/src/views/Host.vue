<template>
  <div id="page-container">
    <Header :pageTitle="pageTitle"/>
      <div class="container-fluid">
        <div class="row">
          <div class="col-12 col-md-6">
            <IseHostPanel :hostIp="hostIp"></IseHostPanel>
            <StealthwatchHostPanel :flows="flows"
                                   :flowsLoading="flowsLoading"
                                   :hostIp="hostIp"
                                   :hostSnapshot="hostSnapshot"></StealthwatchHostPanel>
          </div>
          <div class="col-12 col-md-6">
            <EventTable :events="filteredEvents" @rowSelected="onEventUpdate"></EventTable>
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
import IseHostPanel from '../components/product_panels/IseHostPanel.vue';
import StealthwatchHostPanel from '../components/product_panels/StealthwatchHostPanel.vue';

export default {
  name: 'HostView',
  props: ['hostIp'],
  data() {
    return {
      filteredEvents: [],
      flows: [],
      flowsLoading: false,
      hostSnapshot: [],
      pageTitle: `Host ${this.hostIp}`,
      selectedEvent: null,
    };
  },
  components: {
    EventDetails,
    EventTable,
    Header,
    IseHostPanel,
    StealthwatchHostPanel,
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
    events: function () {
      // this.getEventsOverTime();
      this.filterEvents();
      this.getFlows();
      // this.getHostSnapshot();
    },
  },
  methods: {
    filterEvents() {
      const returnEvents = [];

      this.events.forEach((event) => {
        if (this.hostIp === event.src_ip) {
          returnEvents.push(event);
        }
      });

      this.filteredEvents = returnEvents;
    },
    getFlows() {
      this.flowsLoading = true;
      const path = `http://${window.location.hostname}:5000/api/stealthwatch/flows?host_ip=${this.hostIp}&timeframe=${this.timeframe}`;
      axios.get(path)
        .then((res) => {
          this.flows = res.data.getFlowsResponse['flow-list'].flow;
          this.flowsLoading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    getHostSnapshot() {
      const path = `http://${window.location.hostname}:5000/api/stealthwatch/host-snapshot?host_ip=${this.hostIp}`;
      axios.get(path)
        .then((res) => {
          this.hostSnapshot = res.data.getHostSnapshotResponse['host-snapshot'];
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
