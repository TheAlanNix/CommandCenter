<template>
    <div class="event-details-panel-content">
        <b-row>
            <b-col>
                <span class="heading">Date</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">{{ event.timestamp }}</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Origin</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">{{ event.originLabel }}</span>
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
                <span class="content">{{ event.destination }}</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Action</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">Umbrella {{ event.actionTaken }} this destination.</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Categories</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content" v-for="(category, index) in event.categories"
                                      :key="index">{{ category }}</span>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
  props: ['event'],
};
</script>
