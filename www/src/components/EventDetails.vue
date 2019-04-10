<template>
    <div class="event-details-panel">
        <div class="row">
            <div class="col">
                <div class="event-details-panel-header">
                    Event Details
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div v-if="selected_event.length == 0">
                    <div class="text-center my-2">
                        No Event Selected
                    </div>
                </div>
                <AmpEvent v-if="selected_event.product == 'AMP for Endpoints'"
                                        :event="selected_event"></AmpEvent>
                <StealthwatchEvent v-if="selected_event.product == 'Stealthwatch'"
                                        :event="selected_event"></StealthwatchEvent>
                <UmbrellaEvent v-if="selected_event.product == 'Umbrella'"
                                        :event="selected_event"></UmbrellaEvent>
            </div>
        </div>
    </div>
</template>

<script>
import AmpEvent from './event_types/AmpEvent';
import StealthwatchEvent from './event_types/StealthwatchEvent';
import UmbrellaEvent from './event_types/UmbrellaEvent';

export default {
  props: ['selected_event'],
  components: {
    AmpEvent,
    StealthwatchEvent,
    UmbrellaEvent,
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

.event-details-panel {
    background-color: #fff;
    border: 1px solid $border-color;
    border-radius: 5px;
    margin-top: 10px;
    position: relative;

    .event-details-panel-header {
        border-bottom: 1px solid $border-color;
        color: #212529;
        font-size: 20px;
        padding: 10px 15px;
    }

    .event-details-panel-content {
        //border-top: 1px solid $border-color;
        padding: 15px;
        max-height: 80vh;
        margin-bottom: 0px;
        overflow-y: scroll;

        .heading {
            font: 16px Nunito, sans-serif;
            color: #212529;
        }

        .content {
            display: block;
            font-size: 12px;
            margin-left: 20px;
        }
    }
}
</style>
