<template>
  <div v-if="ampData" class="host-panel">
    <div class="row">
      <div class="col">
        <div class="host-panel-header">
          AMP for Endpoints
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <div class="host-panel-content">
          <b-row v-if="ampData.hostname">
            <b-col>
              <span class="heading">Hostname</span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.hostname">
            <b-col>
              <span class="content">
                {{ ampData.hostname }}
              </span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.policy">
            <b-col>
              <span class="heading">Policy</span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.policy">
            <b-col>
              <span class="content">
                {{ ampData.policy.name }}
              </span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.operating_system">
            <b-col>
              <span class="heading">Operating System</span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.operating_system">
            <b-col>
              <span class="content">
                {{ ampData.operating_system }}
              </span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.isolation">
            <b-col>
              <span class="heading">Isolation Status</span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.isolation">
            <b-col>
              <span class="content">
                {{ ampData.isolation.status }}
              </span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.last_seen">
            <b-col>
              <span class="heading">Last Seen</span>
            </b-col>
          </b-row>
          <b-row v-if="ampData.last_seen">
            <b-col>
              <span class="content">
                {{ ampData.last_seen }}
              </span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span class="heading">Connector</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span class="content">
                <div>GUID: {{ ampData.connector_guid }}</div>
                <div>Version: {{ ampData.connector_version }}</div>
              </span>
            </b-col>
          </b-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      ampData: null,
    };
  },
  props: ['hostIp'],
  watch: {
    hostIp() {
      this.getAmpData();
    },
  },
  methods: {
    getAmpData() {
      const path = `http://${window.location.hostname}:5000/api/amp/computer/${this.hostIp}`;
      axios.get(path)
        .then((res) => {
          console.log(res.data[0]);
          this.ampData = res.data[0];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
  },
  created() {
    this.getAmpData();
  },
};
</script>
