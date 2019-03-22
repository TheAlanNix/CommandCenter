<template>
    <div :id="host_ip" class="col-12 col-md-4">
        <div class="host-panel">
            <div class="row">
                <div class="col">
                    <div class="host-panel-header">
                        {{ host_ip }}
                        <span class="host-panel-close" onclick="deleteHostpanel('host_')">
                            <i class="fa fa-times-circle" aria-hidden="true"></i>
                        </span>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    <div class="host-panel-map">
                        <i class="fa fa-refresh fa-spin fa-3x fa-fw"></i>
                    </div>
                </div>
                <div class="col-12">
                    <div class="host-panel-details">
                        <div class="row">
                            <div class="col-6">
                                <strong>SW Concern:</strong> 200%
                            </div>
                            <div class="col-6 ise-details"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <div class="host-panel-events">
                        <table class="table table-striped table-sm">
                            <thead>
                                <tr>
                                    <th scope="col">Product</th>
                                    <th scope="col">Event Name</th>
                                    <th scope="col">Event Details</th>
                                </tr>
                            </thead>
                            <tbody>

                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col host-panel-actions">
            <b-dropdown id="dropdownMenuButton" text="Playbooks" variant="outline-danger">
                <b-dropdown-item>Defcon 3</b-dropdown-item>
                <b-dropdown-item>Defcon 2</b-dropdown-item>
                <b-dropdown-item>Defcon 1</b-dropdown-item>
            </b-dropdown>
            <b-button variant="outline-success">Clear</b-button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  props: ['host_ip'],
};
</script>

<style lang="scss">
@import "@/assets/_variables.scss";

.host-panel {
    background-color: #fff;
    border: 1px solid $border-color;
    border-radius: 5px;
    margin-top: 10px;
    position: relative;

    .host-panel-header {
        border-bottom: 1px solid $border-color;
        color: #049fd9;
        padding: 10px 15px;

        .host-panel-close {
            float: right;
        }
    }

    .host-panel-map {
        height: 300px;
        text-align: center;

        .fa {
            margin: 100px auto;
        }
    }

    .host-panel-details {
        border-top: 1px solid $border-color;
        padding: 10px;
    }

    .host-panel-events {
        border-top: 1px solid $border-color;
        padding: 0px 5px;
        max-height: 200px;
        overflow-y: scroll;

        .table th {
            white-space: nowrap;
        }

        .table th, .table td {
            border-top: none;
        }
    }

    .host-panel-actions {
        border-top: 1px solid $border-color;
        padding: 15px;
    }
}
</style>
