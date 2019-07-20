<template>
    <div class="host-panel">
        <div class="row">
            <div class="col">
                <div class="host-panel-header">
                    <i v-show="flows_loading" id="loading" class="fa fa-refresh fa-spin fa-1x"></i>
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
  props: ['flows', 'flows_loading', 'host_ip', 'host_snapshot'],
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

        var server_node_id = this.processNode(flow.server);
        var client_node_id = this.processNode(flow.client);

        if (!edges.includes(client_node_id+server_node_id)) {
          edges.push(client_node_id+server_node_id);
          this.edges.push({
            from: client_node_id,
            to: server_node_id,
            arrows: "to",
          });
        }
      });

      console.log(this.nodes);
    },
    processNode(node) {

      // Get the node ID / IP
      var host_id = node['@ip-address'];
      var host_ip = node['@ip-address'];

      // Get the host Country
      var host_country = node['@country'];

      // Get the byte count
      var host_value = node['@bytes'];

      // Placeholders
      var host_group;
      var host_label;

      // Check to see if it's an inside host, then group by country
      if (["XR", "XU", "XL"].includes(host_country)) {
        host_label = host_ip;
        if (host_ip == this.host_ip)
            host_group = 0;
        else
            host_group = 1;
      } else {
        host_id = host_country;
        host_label = host_country;
        host_group = 2;
      }

      var node_exists = false;

      this.nodes.forEach(node => {
        if (node.id == host_id) {
          node_exists = true;
          node = {
            id: host_id,
            label: host_label,
            group: host_group,
            value: node.value + host_value,
          }
        }
      });

      if (!node_exists) {
        this.nodes.push({
            id: host_id,
            label: host_label,
            group: host_group,
            value: host_value,
        })
      }

      return host_id

    },
    processEdge(edge) {

      // Get the edge IDs
      var client_id = edge.client['@ip-address'];
      var server_id = edge.server['@ip-address'];

      // Get the service
      var service = edge['@service'];

    },
    onGraphStabilized(event) {
      this.$refs.network.fit({animation: true});
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

#network-view {
    //min-height: 500px;
}
</style>
