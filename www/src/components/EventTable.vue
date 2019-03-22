<template>
    <div class="col-12 col-md-6">
        <div class="event-panel">
            <div class="row">
                <div class="col">
                    <div class="event-panel-header">
                        Events
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <div class="event-panel-table">
                        <b-table small striped hover selectable show-empty
                                    select-mode="single"
                                    selectedVariant="warning"
                                    :items="events"
                                    :fields="fields"
                                    @row-selected="rowSelected">
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
    </div>
</template>

<script>
export default {
  props: ['events', 'selected_event'],
  data() {
    return {
      fields: ['product', 'event_name', 'event_details', 'timestamp'],
    };
  },
  methods: {
    rowSelected(items) {
      if (items.length > 0) {
        this.$emit('update', items[0]);
      } else {
        this.$emit('update', []);
      }
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
        max-height: 80vh;
        overflow-y: scroll;
    }
}

.table {
    th {
        border-top: 0px;
    }

    td{
        font-size: 12px;
    }
}
</style>
