<template>
    <div v-if="ise_data" class="host-panel">
        <div class="row">
            <div class="col">
                <div class="host-panel-header">
                    Identity Services Engine
                    <b-dropdown v-if="mac_address" id="remediation_button"
                                text="Remediate"
                                size="sm"
                                variant="outline-danger">
                        <b-dropdown-item v-on:click="clearIseAncStatus(mac_address, '')">None</b-dropdown-item>
                        <b-dropdown-item v-for="(action, index) in actions"
                                         v-on:click="setIseAncStatus(mac_address, action.name)"
                                         :key="index">
                            {{ action.name }}
                        </b-dropdown-item>
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
                            <span v-if="ise_data.macAddress" class="content">
                                <div>MAC Address: {{ ise_data.macAddress }}</div>
                                <div>Endpoint Profile: {{ ise_data.endpointProfile }}</div>
                                <div>Endpoint OS: {{ ise_data.endpointOperatingSystem }}</div>
                                IP Address(es):
                                <ul>
                                    <li v-for="(ip_address, index) in ise_data.ipAddresses" :key="index">{{ ip_address }}</li>
                                </ul>
                            </span>
                        </b-col>
                    </b-row>
                    <b-row v-if="ise_data.adUserResolvedIdentities">
                        <b-col>
                            <span class="heading">User</span>
                        </b-col>
                    </b-row>
                    <b-row v-if="ise_data.adUserResolvedIdentities">
                        <b-col>
                            <span class="content">
                                {{ ise_data.adUserResolvedIdentities }}
                            </span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span class="heading">ANC Policy</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col v-if="anc_policy">
                            <span class="content">
                                <b-badge variant="danger">{{ anc_policy }}</b-badge>
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
                            <span v-if="ise_data.ctsSecurityGroup" class="heading">Security Group</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span v-if="ise_data.ctsSecurityGroup" class="content">
                                {{ ise_data.ctsSecurityGroup }}
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
                                <div>NAS Profile: {{ ise_data.networkDeviceProfileName }}</div>
                                <div>NAS IP Address: {{ ise_data.nasIpAddress }}</div>
                                <div v-if="ise_data.nasPortId">NAS Port: {{ ise_data.nasPortId }}</div>
                                <div>NAS Type: {{ ise_data.nasPortType }}</div>
                                <div>RADIUS Type: {{ ise_data.radiusFlowType }}</div>
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
      anc_policy: null,
      interval: null,
      ise_data: [],
      mac_address: null,
    }
  },
  props: ['host_ip'],
  watch: {
    host_ip: function () {
      this.getIseSessionData();
    },
  },
  methods: {
    getActions() {
      const path = 'http://localhost:5000/api/ise_actions';
      axios.get(path)
        .then((res) => {
          this.actions = res.data.SearchResult.resources;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    getIseSessionData() {
      const path = `http://localhost:5000/api/ise_session_data/${this.host_ip}`;
      axios.get(path)
        .then((res) => {
          this.ise_data = res.data;
          if (res.data.macAddress) {
            this.mac_address = res.data.macAddress;
            this.getIseAncStatus(this.mac_address);
          } else {
            this.mac_address = null;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    getIseAncStatus(mac_address) {
      const path = `http://localhost:5000/api/ise_anc_status/${this.mac_address}`;
      axios.get(path)
        .then((res) => {
          if (res.data.policyName) {
            this.anc_policy = res.data.policyName;
          } else {
            this.anc_policy = null;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    setIseAncStatus(mac_address, anc_policy) {
      const path = 'http://localhost:5000/api/ise_anc_status';
      const payload = {
        anc_policy: anc_policy,
        mac_address: mac_address,
      };
      axios.post(path, payload)
        .then((res) => {
          console.log(res);
          this.getIseAncStatus();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
    clearIseAncStatus(mac_address) {
      const path = `http://localhost:5000/api/ise_anc_status/${this.mac_address}`;
      axios.delete(path)
        .then((res) => {
          console.log(res);
          this.getIseAncStatus();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.errors.push({ message: error });
        });
    },
  },
  created() {
    this.getActions();
    this.getIseSessionData();
    this.interval = setInterval(() => {
      // this.getIseSessionData();
    }, 10000);
  },
}
</script>

<style lang="scss" scoped>
#remediation_button {
    float: right;
}
</style>
