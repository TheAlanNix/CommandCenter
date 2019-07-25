<template>
  <div>
    <MenuBar/>
    <StatusBar/>
    <TimeframeSelect/>
    <div id="page-title">{{ pageTitle }} <i v-show="this.$store.state.loading"
                                            id="loading"
                                            class="fa fa-refresh fa-spin fa-1x"></i>
    </div>
  </div>
</template>

<script>
import MenuBar from './MenuBar.vue';
import StatusBar from './StatusBar.vue';
import TimeframeSelect from './TimeframeSelect.vue';

export default {
  name: 'Header',
  props: ['pageTitle'],
  components: {
    MenuBar,
    StatusBar,
    TimeframeSelect,
  },
  beforeDestroy() {
    clearInterval(this.$store.state.interval);
  },
  created() {
    this.$store.dispatch('fetchEvents');
  },
};
</script>

<style lang="scss">
  #page-title {
    font-size: 24px;
    margin: 20px 30px;
  }
</style>
