<template>
  <div class="event-details-panel-content">
    <b-row>
      <b-col>
        <span class="heading">Date</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.formatted_timestamp }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Event Name</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.event_name }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Snort ID</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.snort_id }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Sensor</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.sensor_name }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Source</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">
          {{ event.src_ip }}
          <span v-if="event.src_port">:{{ event.src_port }}</span>
          (<router-link :to="'/host/' + event.src_ip">Examine Host</router-link>)
        </span>
      </b-col>
    </b-row>
    <b-row v-if="event.dst_ip != null">
      <b-col>
        <span class="heading">Destination</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">
          {{ event.dst_ip }}
          <span v-if="event.dst_port">:{{ event.dst_port }}</span>
          (<router-link :to="'/host/' + event.dst_ip">Examine Host</router-link>)
        </span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Protocol</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.protocol }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Impact Level</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.impact_level }}</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="heading">Classification</span>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <span class="content">{{ event.classification }}</span>
      </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
  props: ['event'],
};
</script>
