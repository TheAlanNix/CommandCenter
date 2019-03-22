<template>
    <div class="flex-center position-ref full-height">
        <div class="content">
            <div class="title">
                <img src="/static/Cisco_Logo.png"><span class="title-text">Command Center</span>
            </div>
            <div class="title-link">
                <router-link to="security-events">
                    <button type="button" class="btn btn-outline-primary">Enter</button>
                </router-link>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css?family=Nunito');
@import "@/assets/_variables.scss";

html, body {
    background-color: #fff;
    margin: 0;
}

.content {
    text-align: center;
}

.full-height {
    height: 100vh;
}

.flex-center {
    align-items: center;
    display: flex;
    justify-content: center;
}

.position-ref {
    position: relative;
}

.title {
    font-size: 48px;
    height: 87px;
    line-height: 87px;
    margin-bottom: 30px;
}

.title-text {
    color: #636b6f;
    font-family: 'Nunito', sans-serif;
    font-weight: 200;
    vertical-align: -10px;
}
</style>
