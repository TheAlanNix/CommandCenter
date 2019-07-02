<template>
    <div class="event-details-panel-content">
        <b-row>
            <b-col>
                <span class="heading">Date</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">
                    <div>First Active Time: {{ event.firstActiveTime }}</div>
                    <div>Last Active Time: {{ event.lastActiveTime }}</div>
                </span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Source IP</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">
                    {{ event.src_ip }}
                    (<router-link :to="'/host/' + event.src_ip">Examine Host</router-link>)
                    <ul>
                        <li v-for="(tag, index) in event.source.tags" :key="index">
                            {{ tag.name }}
                        </li>
                    </ul>
                </span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Destination</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">
                    {{ event.target.ipAddress }}
                    (<router-link :to="'/host/' + event.target.ipAddress">Examine Host</router-link>)
                    <ul>
                        <li v-for="(tag, index) in event.target.tags" :key="index">
                            {{ tag.name }}
                        </li>
                    </ul>
                </span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Event Name</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">{{ event.event_name }} ({{ event.hitCount }})</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Event Details</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">{{ event.event_details }}</span>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
  props: ['event'],
};
</script>
