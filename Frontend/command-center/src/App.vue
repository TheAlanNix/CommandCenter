<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

html, body {
  background-color: #fff;
  color: #636b6f;
  font-family: 'Nunito', sans-serif;
  font-weight: 200;
  height: 100vh;
  margin: 0;
}

#page-container {
  background-color: #f7f7f9;
  min-height: 100vh;
  padding-bottom: 15px;
  position: relative;
  width: 100%;
}
</style>
