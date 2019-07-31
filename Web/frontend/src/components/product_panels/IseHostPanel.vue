<template>
  <div v-if="iseData" class="host-panel">
    <div class="row">
      <div class="col">
        <div class="host-panel-header">
          Identity Services Engine
          <b-dropdown
            v-if="macAddress"
            id="remediation_button"
            text="Remediate"
            size="sm"
            variant="outline-danger"
          >
            <b-dropdown-item v-on:click="clearIseAncStatus(macAddress, '')">None</b-dropdown-item>
            <b-dropdown-item
              v-for="(action, index) in actions"
              v-on:click="setIseAncStatus(macAddress, action.name)"
              :key="index"
            >{{ action.name }}</b-dropdown-item>
          </b-dropdown>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <div class="host-panel-content">
          <b-row>
            <b-col>
              <span class="heading">Device</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span v-if="iseData.macAddress" class="content">
                <div>MAC Address: {{ iseData.macAddress }}</div>
                <div>Endpoint Profile: {{ iseData.endpointProfile }}</div>
                <div>Endpoint OS: {{ iseData.endpointOperatingSystem }}</div>IP Address(es):
                <ul>
                  <li v-for="(ipAddress, index) in iseData.ipAddresses" :key="index">
                    {{ ipAddress }}
                  </li>
                </ul>
              </span>
            </b-col>
          </b-row>
          <b-row v-if="iseData.adUserResolvedIdentities">
            <b-col>
              <span class="heading">User</span>
            </b-col>
          </b-row>
          <b-row v-if="iseData.adUserResolvedIdentities">
            <b-col>
              <span class="content">{{ iseData.adUserResolvedIdentities }}</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span class="heading">ANC Policy</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col v-if="ancPolicy">
              <span class="content">
                <b-badge variant="danger">{{ ancPolicy }}</b-badge>
              </span>
            </b-col>
            <b-col v-else>
              <span class="content">
                <b-badge variant="secondary">None</b-badge>
              </span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span v-if="iseData.ctsSecurityGroup" class="heading">Security Group</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span v-if="iseData.ctsSecurityGroup" class="content">
                {{ iseData.ctsSecurityGroup }}
              </span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span class="heading">Network Device</span>
            </b-col>
          </b-row>
          <b-row>
            <b-col>
              <span class="content">
                <div>NAS Profile: {{ iseData.networkDeviceProfileName }}</div>
                <div>NAS IP Address: {{ iseData.nasIpAddress }}</div>
                <div v-if="iseData.nasPortId">NAS Port: {{ iseData.nasPortId }}</div>
                <div>NAS Type: {{ iseData.nasPortType }}</div>
                <div>RADIUS Type: {{ iseData.radiusFlowType }}</div>
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
      actions: [],
      ancPolicy: null,
      interval: null,
      iseData: null,
      macAddress: null,
    };
  },
  props: ['hostIp'],
  watch: {
    hostIp() {
      this.getIseSessionData();
    },
  },
  methods: {
    getActions() {
      const path = `http://${window.location.hostname}:5000/api/ise_actions`;
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          this.actions = res.data.SearchResult.resources;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    getIseSessionData() {
      const path = `http://${window.location.hostname}:5000/api/ise_session_data/${this.hostIp}`;
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          this.iseData = res.data;
          if (res.data.macAddress) {
            this.macAddress = res.data.macAddress;
            this.getIseAncStatus(this.macAddress);
          } else {
            this.macAddress = null;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    getIseAncStatus(macAddress) {
      const path = `http://${window.location.hostname}:5000/api/ise_anc_status/${macAddress}`;
      axios
        .get(path)
        .then((res) => {
          if (res.data.policyName) {
            this.ancPolicy = res.data.policyName;
          } else {
            this.ancPolicy = null;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    setIseAncStatus(macAddress, ancPolicy) {
      const path = `http://${window.location.hostname}:5000/api/ise_anc_status`;
      const payload = {
        anc_policy: ancPolicy,
        mac_address: macAddress,
      };
      axios
        .post(path, payload)
        .then((res) => {
          console.log(res);
          this.getIseAncStatus();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
    clearIseAncStatus(macAddress) {
      const path = `http://${window.location.hostname}:5000/api/ise_anc_status/${macAddress}`;
      axios
        .delete(path)
        .then((res) => {
          console.log(res);
          this.getIseAncStatus();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.commit('ADD_ERROR', { message: error });
        });
    },
  },
  created() {
    this.getActions();
    this.getIseSessionData();
    // this.interval = setInterval(() => {
    //   this.getIseSessionData();
    // }, 30000);
  },
};
</script>

<style lang="scss" scoped>
.dropdown-menu > .dropdown-item {
  padding: 0.25rem 1rem;
}

#remediation_button {
  float: right;
}
</style>
