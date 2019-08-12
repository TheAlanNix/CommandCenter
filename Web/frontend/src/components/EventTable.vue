<template>
  <div class="event-panel">
    <b-row>
      <b-col>
        <div class="event-panel-header">Events ({{ latestEvents.length }})</div>
      </b-col>
    </b-row>
    <div class="row">
      <div class="col">
        <div class="event-panel-table">
          <b-table
            small
            striped
            hover
            selectable
            show-empty
            select-mode="single"
            selectedVariant="warning"
            :items="latestEvents"
            :fields="fields"
            @row-selected="rowSelected"
            ref="eventTable"
          >
            <template slot="empty" slot-scope="scope">
              <div class="text-center my-2">
                {{ scope.emptyText }}. You're completely secure. :-)
              </div>
            </template>
          </b-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['events'],
  data() {
    return {
      fields: [
        'product',
        'event_name',
        'event_details',
        { key: 'formatted_timestamp', label: 'Timestamp' },
      ],
      latestEvents: [],
      selectedEvent: null,
    };
  },
  methods: {
    getLatestEvents(events) {
      this.latestEvents = events.slice(0, 1000);
    },
    rowSelected(items) {
      if (items.length > 0) {
        [this.selectedEvent] = items;
        this.$emit('rowSelected', items[0]);
      } else {
        this.selectedEvent = null;
        this.$emit('rowSelected', null);
      }
    },
    selectFirstEvent() {
      if (this.selectedEvent === null) {
        const eventTable = this.$refs.eventTable.$el;
        const tableBody = eventTable.getElementsByTagName('tbody')[0];
        const tableRows = tableBody.getElementsByTagName('tr');
        tableRows[0].click();
      }
    },
  },
  watch: {
    events() {
      this.getLatestEvents(this.events);
    },
  },
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

.event-panel {
  background-color: #fff;
  border: 1px solid $border-color;
  border-radius: 5px;
  margin-top: 10px;
  position: relative;

  .event-panel-header {
    border-bottom: 1px solid $border-color;
    color: #212529;
    font-size: 20px;
    padding: 10px 15px;
  }

  .event-panel-table {
    //border-top: 1px solid $border-color;
    padding: 0px 5px;
    max-height: 50vh;
    overflow-y: scroll;
  }
}

.table {
  th {
    border-top: 0px;
    white-space: nowrap;
  }

  td {
    font-size: 12px;
  }
}
</style>
