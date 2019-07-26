<template>
    <div class="host-panel">
        <div class="row">
            <div class="col">
                <div class="host-panel-header">
                    <i v-show="flowsLoading" id="loading" class="fa fa-refresh fa-spin fa-1x"></i>
                    Flow Graph
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div class="host-panel-content">
                    <VisNetwork id="network-view"
                                ref="network"
                                :edges="edges"
                                :nodes="nodes"
                                :options="options"
                                :events="['stabilized']"
                                @stabilized="onGraphStabilized"
                                style="height: 45vh"></VisNetwork>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {Network} from 'vue2vis';

export default {
  components: {
    VisNetwork: Network,
  },
  props: ['flows', 'flowsLoading', 'hostIp', 'hostSnapshot'],
  data() {
    return {
      edges: [],
      nodes: [],
      network: null,
      options: {
        nodes: {
            shape: 'dot',
        },
        edges: {
            scaling: {
                label: {
                    enabled: false
                }
            }
        },
        physics: {
            barnesHut: {
                gravitationalConstant: -7000,
                damping: 0.25
            }
        },
        groups: {
            0: {color: {border: "#41A906", background: "#7BE141", highlight: {border: "#41A906", background: "#A1EC76"}, hover: {border: "#41A906", background: "#A1EC76"}}},
            1: {color: {border: "#2B7CE9", background: "#97C2FC", highlight: {border: "#2B7CE9", background: "#D2E5FF"}, hover: {border: "#2B7CE9", background: "#D2E5FF"}}},
            2: {color: {border: "#FFA500", background: "#FFFF00", highlight: {border: "#FFA500", background: "#FFFFA3"}, hover: {border: "#FFA500", background: "#FFFFA3"}}},
            3: {color: {border: "#FA0A10", background: "#FB7E81", highlight: {border: "#FA0A10", background: "#FFAFB1"}, hover: {border: "#FA0A10", background: "#FFAFB1"}}},
        }
      },
    };
  },
  methods: {
    processFlows() {

      this.edges = [];
      this.nodes = [];

      var edges = [];

      this.flows.forEach(flow => {

        var serverNodeId = this.processNode(flow.server);
        var clientNodeId = this.processNode(flow.client);

        if (!edges.includes(clientNodeId+serverNodeId)) {
          edges.push(clientNodeId+serverNodeId);
          this.edges.push({
            from: clientNodeId,
            to: serverNodeId,
            arrows: "to",
          });
        }
      });

      console.log(this.nodes);
    },
    processNode(node) {

      // Get the node ID / IP
      var hostId = node['@ip-address'];
      var hostIp = node['@ip-address'];

      // Get the host Country
      var hostCountry = node['@country'];

      // Get the byte count
      var hostValue = node['@bytes'];

      // Placeholders
      var hostGroup;
      var hostLabel;

      // Check to see if it's an inside host, then group by country
      if (["XR", "XU", "XL"].includes(hostCountry)) {
        hostLabel = hostIp;
        if (hostIp == this.hostIp)
            hostGroup = 0;
        else
            hostGroup = 1;
      } else {
        hostId = hostCountry;
        hostLabel = hostCountry;
        hostGroup = 2;
      }

      var nodeExists = false;

      this.nodes.forEach(node => {
        if (node.id == hostId) {
          nodeExists = true;
          node = {
            id: hostId,
            label: hostLabel,
            group: hostGroup,
            value: node.value + hostValue,
          }
        }
      });

      if (!nodeExists) {
        this.nodes.push({
            id: hostId,
            label: hostLabel,
            group: hostGroup,
            value: hostValue,
        })
      }

      return hostId

    },
    processEdge(edge) {

      // Get the edge IDs
      var clientId = edge.client['@ip-address'];
      var serverId = edge.server['@ip-address'];

      // Get the service
      var service = edge['@service'];

    },
    onGraphStabilized(event) {
      this.$refs.network.fit({ animation: true });
    },
  },
  watch: {
    flows: function (newVal, oldVal) {
      if (oldVal.length == 0) {
        this.$refs.network.moveTo({ scale: 0.3 });
      }
      this.processFlows();
    },
  },
}
</script>

<style lang="scss" scoped>
#loading {
    float: right;
    padding: 5px;
}
</style>
