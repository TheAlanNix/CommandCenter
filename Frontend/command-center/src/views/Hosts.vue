<template>
  <div id="page-container">
    <Header :pageTitle="pageTitle"/>
  </div>
</template>

<script>
// import axios from 'axios';
import Header from '../components/Header.vue';

export default {
  name: 'HostsView',
  data() {
    return {
      pageTitle: 'Top Hosts',
    };
  },
  components: {
    Header,
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
    events() {
      // this.filterEvents();
    },
  },
  methods: {
    inArrayWithAttribute(array, attr, value) {
      for (let i = 0; i < array.length; i += 1) {
        if (array[i][attr] === value) {
          return i;
        }
      }
      return -1;
    },
    sortCompare(a, b) {
      if (a.y < b.y) {
        return 1;
      }
      if (a.y > b.y) {
        return -1;
      }
      return 0;
    },
  },
};
</script>

<style lang="scss">

</style>
