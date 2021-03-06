<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { Prop } from "vue-property-decorator";

import { gameSettingsStore } from "../../settings";
import { LocationOptions } from "../../comm/types/settings";

@Component
export default class GridSettings extends Vue {
    @Prop() location!: number | null;

    get defaults(): LocationOptions {
        return gameSettingsStore.defaultLocationOptions!;
    }

    get options(): Partial<LocationOptions> {
        if (this.location === null) return this.defaults;
        return gameSettingsStore.locationOptions[this.location] ?? {};
    }

    get useGrid(): boolean {
        return gameSettingsStore.useGrid;
    }
    set useGrid(value: boolean) {
        gameSettingsStore.setUseGrid({ useGrid: value, location: this.location, sync: true });
    }
    get unitSize(): number {
        return gameSettingsStore.unitSize;
    }
    set unitSize(value: number) {
        if (typeof value !== "number") return;
        gameSettingsStore.setUnitSize({ unitSize: value, location: this.location, sync: true });
    }
    get unitSizeUnit(): string {
        return gameSettingsStore.unitSizeUnit;
    }
    set unitSizeUnit(value: string) {
        gameSettingsStore.setUnitSizeUnit({ unitSizeUnit: value, location: this.location, sync: true });
    }
    get gridSize(): number {
        return gameSettingsStore.gridSize;
    }
    set gridSize(value: number) {
        if (typeof value !== "number") return;
        gameSettingsStore.setGridSize({ gridSize: value, location: this.location, sync: true });
    }

    reset(key: keyof LocationOptions): void {
        if (this.location === null) return;
        gameSettingsStore.reset({ key, location: this.location });
    }
}
</script>

<template>
    <div class="panel restore-panel">
        <div class="spanrow">
            <i style="max-width: 40vw">
                <template v-if="location === null">
                    Some of these settings can be overriden by location specific settings
                </template>
                <template v-else>Settings that override the campaign defaults are highlighted</template>
            </i>
        </div>
        <div class="row" :class="{ overwritten: location !== null && options.useGrid !== undefined }">
            <label :for="'useGridInput-' + location">Use grid</label>
            <div>
                <input :id="'useGridInput-' + location" type="checkbox" v-model="useGrid" />
            </div>
            <div
                v-if="location !== null && options.useGrid !== undefined"
                @click="reset('useGrid')"
                title="Reset to the campaign default"
            >
                <i class="fas fa-times-circle"></i>
            </div>
            <div v-else></div>
        </div>
        <div class="row" :class="{ overwritten: location !== null && options.gridSize !== undefined }">
            <label :for="'gridSizeInput-' + location">Grid Size (in pixels):</label>
            <div>
                <input :id="'gridSizeInput-' + location" type="number" min="0" v-model.number="gridSize" />
            </div>
            <div
                v-if="location !== null && options.gridSize !== undefined"
                @click="reset('gridSize')"
                title="Reset to the campaign default"
            >
                <i class="fas fa-times-circle"></i>
            </div>
            <div v-else></div>
        </div>
        <div class="row" :class="{ overwritten: location !== null && options.unitSizeUnit !== undefined }">
            <div>
                <label :for="'unitSizeUnit-' + location">Size Unit</label>
            </div>
            <div>
                <input :id="'unitSizeUnit-' + location" type="text" v-model="unitSizeUnit" />
            </div>
            <div
                v-if="location !== null && options.unitSizeUnit !== undefined"
                @click="reset('unitSizeUnit')"
                title="Reset to the campaign default"
            >
                <i class="fas fa-times-circle"></i>
            </div>
            <div v-else></div>
        </div>
        <div class="row" :class="{ overwritten: location !== null && options.unitSize !== undefined }">
            <div>
                <label :for="'unitSizeInput-' + location">Unit Size (in {{ unitSizeUnit }})</label>
            </div>
            <div>
                <input :id="'unitSizeInput-' + location" type="number" v-model.number="unitSize" />
            </div>
            <div
                v-if="location !== null && options.unitSize !== undefined"
                @click="reset('unitSize')"
                title="Reset to the campaign default"
            >
                <i class="fas fa-times-circle"></i>
            </div>
            <div v-else></div>
        </div>
    </div>
</template>

<style scoped>
/* Force higher specificity without !important abuse */
.panel.restore-panel {
    grid-template-columns: [setting] 1fr [value] 1fr [restore] 30px [end];
}

.restore-panel .row.overwritten * {
    color: #7c253e;
    font-weight: bold;
}
</style>
