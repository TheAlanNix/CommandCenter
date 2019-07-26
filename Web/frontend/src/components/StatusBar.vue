<template>
  <div id="status-container" v-if="errors.length > 0">
    <b-alert v-for="(error, index) in errors" :key="index"
             fade
             show
             dismissible
             variant="danger">
      {{ error.message }}
    </b-alert>
  </div>
</template>

<style lang="scss">
#status-container {
  margin: 0px 0px;
  text-align: center;

  .alert {
    // max-width: 40%;
    border-radius: 0;
    margin: auto;

    ul {
      margin-bottom: 0;
    }
  }
}
</style>

<script>
export default {
  computed: {
    errors() {
      return this.$store.state.errors;
    },
  },
};
</script>
