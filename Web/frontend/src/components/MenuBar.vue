<template>
  <div id="header">
    <span id="title">
      <img id="title-img" src="@/assets/Cisco_Logo.png">
      <span id="title-text">Command Center</span>
    </span>
    <ul class="navbar">
      <li>
        <router-link to="/security-events">
          <i class="fa fa-exclamation-triangle" aria-hidden="true"></i>
          Security Events
          <span class="badge badge-primary">{{ eventCount }}</span>
        </router-link>
      </li>
      <li>
        <router-link to="/hosts">
          <i class="fa fa-desktop" aria-hidden="true"></i>
          Hosts
        </router-link>
      </li>
        <!--<li>
          <a href="/threat">
            <i class="fa fa-crosshairs" aria-hidden="true"></i>
            Top Threats
          </a>
        </li>-->
      </ul>
      <!--
      <router-link id="settings" to="settings">
          <i class="fa fa-cogs"></i> Settings
      </router-link>
      -->
    </div>
</template>

<script>
export default {
  computed: {
    eventCount() {
      return this.$store.state.events.length;
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

#header {
  background-color: #fff;
  padding: 3px 15px;
  border-bottom: 1px solid $border-color;

  #title {
    float: left;

    #title-img {
      height: 43px;
    }

    #title-text {
      height: 43px;
    }
  }

  #settings {
    float: right;
    padding: 10px 5px;
    text-decoration: none;
  }

  ul {
    border: none;
    display: inline;
    list-style-type: none;
    margin: 0px;
    padding: 0;
    overflow: hidden;

    li {
      display: inline-block;

      &:first-child {
        margin-left: 20px;
      }

      a {
        display: block;

        text-align: center;
        padding: 10px 12px;
        text-decoration: none;

        &:hover {
            background-color: #f7f7f9;
        }
      }
    }
  }
}
</style>
