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
                <span class="heading">Computer</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">
                    <a target="_blank" :href="'https://console.amp.cisco.com/computers/' +
                                                event.connector_guid +
                                                '/trajectory2?id=' +
                                                event.id">{{ event.computer.hostname }}</a>
                </span>
            </b-col>
        </b-row>
        <b-row v-if="event.computer.user != null">
            <b-col>
                <span class="heading">User</span>
            </b-col>
        </b-row>
        <b-row v-if="event.computer.user != null">
            <b-col>
                <span class="content">{{ event.computer.user }}</span>
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
                <span class="heading">Severity</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">{{ event.severity }}</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="heading">Action</span>
            </b-col>
        </b-row>
        <b-row>
            <b-col>
                <span class="content">
                    {{ event.event_name }} by AMP for Endpoints.  Detection: {{ event.detection }}
                </span>
            </b-col>
        </b-row>
        <b-row v-if="event.file != null">
            <b-col>
                <span class="heading">Disposition</span>
            </b-col>
        </b-row>
        <b-row v-if="event.file != null">
            <b-col>
                <span class="content">{{ event.file.disposition }}</span>
            </b-col>
        </b-row>
        <b-row v-if="event.file != null">
            <b-col>
                <span class="heading">File</span>
            </b-col>
        </b-row>
        <b-row v-if="event.file != null">
            <b-col>
                <span class="content">Disposition: {{ event.file.disposition }}</span>
                <span class="content">File Name: {{ event.file.file_name }}</span>
                <span class="content">File Path: {{ event.file.file_path }}</span>
                <span class="content">Hash (SHA-256): {{ event.file.identity.sha256 }}</span>
            </b-col>
        </b-row>
        <b-row v-if="event.file != null && event.file.parent != null">
            <b-col>
                <span class="heading">Parent Process</span>
            </b-col>
        </b-row>
        <b-row  v-if="event.file != null && event.file.parent != null">
            <b-col>
                <span class="content">Disposition: {{ event.file.parent.disposition }}</span>
                <span class="content">File Name: {{ event.file.parent.file_name }}</span>
                <span class="content">Hash (SHA-256): {{ event.file.parent.identity.sha256 }}</span>
            </b-col>
        </b-row>
    </div>
</template>

<script>
export default {
  props: ['event'],
};
</script>
