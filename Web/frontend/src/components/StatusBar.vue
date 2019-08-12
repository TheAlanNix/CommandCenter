<template>
  <div id="status-container" v-if="errors.length > 0 || notification">
    <b-alert v-if="notification"
             :show="notificationSeconds"
             dismissible
             fade
             variant="success"
             @dismiss-count-down="notificationCountdownChanged">
      {{ notification }}
      <button type="button" aria-label="Close" class="close" v-on:click="deleteError(index)">×</button>
    </b-alert>
    <b-alert v-for="(error, index) in errors" :key="index"
             show
             variant="danger">
      {{ error.message }}
      <button type="button" aria-label="Close" class="close" v-on:click="deleteError(index)">×</button>
    </b-alert>
  </div>
</template>

<style lang="scss">
#status-container {
  margin: 0px 0px;
  text-align: center;

  .alert {
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
  data() {
    return {
      notificationSeconds: 0
    }
  },
  computed: {
    errors() {
      return this.$store.state.errors.slice(0, 5);
    },
    notification() {
      return this.$store.state.notification;
    },
  },
  methods: {
    notificationCountdownChanged(newValue) {
      this.notificationSeconds = newValue;
      if (newValue === 0) {
        this.$store.dispatch('deleteNotification');
      }
    },
    deleteError(index) {
      console.log(index);
      this.$store.dispatch('deleteError', index);
    },
  },
  watch: {
    notification() {
      if (this.notification) {
        this.notificationSeconds = 5;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.alert > .close {
  position: absolute;
  top: 0px;
  right: 0px;
  padding: 0.75rem 1.25rem;
  color: inherit;
}
</style>


