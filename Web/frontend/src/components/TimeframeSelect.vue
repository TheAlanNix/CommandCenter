<template>
  <div id="time-selection">
    <b-form inline>
      <label class="mr-sm-2" for="inlineFormCustomSelectPref">Timeframe: </label>
      <b-form-select v-model="timeframeSelected"
                     :options="timeframeOptions"
                     size="sm"
                     @change="onTimeframeChange">
        </b-form-select>
      </b-form>
    </div>
</template>

<script>
export default {
  name: 'TimeframeSelect',
  data() {
    return {
      timeframeOptions: [
        { value: '1', text: 'Past Hour' },
        { value: '6', text: 'Past 6 Hours' },
        { value: '24', text: 'Past 24 Hours' },
        { value: '168', text: 'Past Week' },
        { value: '744', text: 'Past Month' },
      ],
      timeframeSelected: this.$store.state.timeframe,
    };
  },
  methods: {
    onTimeframeChange(value) {
      this.$store.commit('SET_TIMEFRAME', value);
      this.$store.dispatch('getEvents');
    },
  },
};
</script>

<style lang="scss">
  #time-selection {
    float: right;
    margin: 20px 30px;
  }
</style>
