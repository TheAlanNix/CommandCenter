<template>
  <div v-if="ampData" class="host-panel">
    <div class="row">
      <div class="col">
        <div class="host-panel-header">
          AMP for Endpoints
          <b-dropdown
            class="remediation-button"
            text="Move to Group"
            size="sm"
            variant="outline-danger"
          >
            <b-dropdown-item
              v-for="(group, index) in ampGroups"
              v-on:click="setAmpGroup(ampGroups[index].guid)"
              :key="index"
            >{{ group.name }}</b-dropdown-item>
          </b-dropdown>
          <b-button
            v-if="ampIsolationAvailable
                  && (ampIsolationStatus == 'isolated' || ampIsolationStatus == 'pending_start')"
            v-on:click="deleteAmpIsolation()"
            class="remediation-button"
            size="sm"
            variant="outline-success"
          >Un-Isolate</b-button>
          <b-button
            v-if="ampIsolationAvailable
                  && (ampIsolationStatus == 'not_isolated' || ampIsolationStatus == 'pending_stop')"
            v-on:click="putAmpIsolation()"
            class="remediation-button"
            size="sm"
            variant="outline-danger"
          >Isolate</b-button>
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
      ampConnectorGuid: null,
      ampData: null,
      ampGroups: [],
      ampIsolationAvailable: false,
      ampIsolationStatus: null,
    };
  },
  props: ['hostIp'],
  watch: {
    hostIp() {
      this.getAmpData();
    },
    ampData() {
      if (this.ampData != null) {
        this.ampConnectorGuid = this.ampData.connector_guid;
        this.getAmpGroups();
      } else {
        this.ampConnectorGuid = null;
      }
    },
  },
  methods: {
    getAmpData() {
      const path = `http://${window.location.hostname}:5000/api/amp/computer/${this.hostIp}`;
      axios.get(path)
        .then((res) => {
          console.log(res);
          if (res.status === 204) return;
          [this.ampData] = res.data;
          this.ampIsolationAvailable = this.ampData.isolation.available;
          this.ampIsolationStatus = this.ampData.isolation.status;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
    getAmpGroups() {
      const path = `http://${window.location.hostname}:5000/api/amp/groups`;
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          if (res.status === 204) return;
          this.ampGroups = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
    setAmpGroup(groupGuid) {
      const path = `http://${window.location.hostname}:5000/api/amp/computer/${this.ampConnectorGuid}/group`;
      const data = {
        group_guid: groupGuid,
      };
      axios
        .post(path, data)
        .then((res) => {
          console.log(res);
          if (res.status === 204) return;
          setTimeout(() => {
            this.getAmpData();
          }, 2000);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
    putAmpIsolation() {
      const path = `http://${window.location.hostname}:5000/api/amp/computer/${this.ampConnectorGuid}/isolation`;
      const data = {
        comment: 'This host has been isolated by Command Center.',
        unlock_code: 'commandcenter',
      };
      axios
        .put(path, data)
        .then((res) => {
          console.log(res);
          if (res.status === 200) {
            this.$store.dispatch('addNotification', 'AMP Isolation Status Successfully Set');
            this.getAmpData();
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
    deleteAmpIsolation() {
      const path = `http://${window.location.hostname}:5000/api/amp/computer/${this.ampConnectorGuid}/isolation`;
      const data = {
        comment: 'This host has been un-isolated by Command Center.',
      };
      axios
        .delete(path, data)
        .then((res) => {
          console.log(res);
          if (res.status === 200) {
            this.$store.dispatch('addNotification', 'AMP Isolation Status Successfully Deleted');
            this.getAmpData();
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.$store.dispatch('addError', { message: error });
        });
    },
  },
  created() {
    this.getAmpData();
  },
};
</script>

<style lang="scss" scoped>
.remediation-button {
  float: right;
  margin-left: 5px;
}
</style>
