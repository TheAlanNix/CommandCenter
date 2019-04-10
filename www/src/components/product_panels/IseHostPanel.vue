<template>
    <div class="host-panel">
        <div class="row">
            <div class="col">
                <div class="host-panel-header">
                    Identity Services Engine
                    <b-dropdown id="remediation_button"
                                text="Remediate"
                                size="sm"
                                variant="outline-danger">
                        <b-dropdown-item v-for="(action, index) in actions"
                                            :key="index">
                            {{ action.name }}
                        </b-dropdown-item>
                    </b-dropdown>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div class="host-panel-content">
                    <b-row>
                        <b-col>
                            <span class="heading">Device</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span v-if="ise_data.macAddress" class="content">
                                <div>MAC Address: {{ ise_data.macAddress }}</div>
                                <div>Endpoint Profile: {{ ise_data.endpointProfile }}</div>
                                <div>Endpoint OS: {{ ise_data.endpointOperatingSystem }}</div>
                                IP Address(es):
                                <ul>
                                    <li v-for="(ip_address, index) in ise_data.ipAddresses" :key="index">{{ ip_address }}</li>
                                </ul>
                            </span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span class="heading">User</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span v-if="ise_data.adUserResolvedIdentities" class="content">
                                {{ ise_data.adUserResolvedIdentities }}
                            </span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span class="heading">Security Group</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span v-if="ise_data.ctsSecurityGroup" class="content">
                                {{ ise_data.ctsSecurityGroup }}
                            </span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span class="heading">Network Device</span>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col>
                            <span class="content">
                                <div>NAS Profile: {{ ise_data.networkDeviceProfileName }}</div>
                                <div>NAS IP Address: {{ ise_data.nasIpAddress }}</div>
                                <div v-if="ise_data.nasPortId">NAS Port: {{ ise_data.nasPortId }}</div>
                                <div>NAS Type: {{ ise_data.nasPortType }}</div>
                                <div>RADIUS Type: {{ ise_data.radiusFlowType }}</div>
                            </span>
                        </b-col>
                    </b-row>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: ['actions', 'ise_data'],
}
</script>

<style lang="scss" scoped>
#remediation_button {
    float: right;
}
</style>
