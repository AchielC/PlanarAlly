<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import { mapState } from "vuex";

import SVGPathElement from "pathseg";

import ColorPicker from "@/core/components/colorpicker.vue";
import Game from "@/game/game.vue";
import AssetNode from "@/game/ui/menu/asset_node.vue";

import { uuidv4 } from "@/core/utils";
import { Note } from "@/game/comm/types/general";
import { layerManager } from "@/game/layers/manager";
import { gameStore } from "@/game/store";
import { EventBus } from "../../event-bus";
import { CircularToken } from "@/game/shapes/circulartoken";
import { getUnitDistance, l2g } from "@/game/units";
import { GlobalPoint, LocalPoint, Vector } from "@/game/geom";
import { gameSettingsStore } from "@/game/settings";
import { InvalidationMode, SyncMode } from "@/core/comm/types";
import { socket } from "@/assetManager/socket";
import { Polygon } from "@/game/shapes/polygon";

@Component({
    components: {
        "color-picker": ColorPicker,
        "asset-node": AssetNode,
    },
    computed: {
        ...mapState("game", ["assets", "notes", "markers"]),
    },
})
export default class MenuBar extends Vue {
    assetSearch = "";

    get IS_DM(): boolean {
        return gameStore.IS_DM || gameStore.FAKE_PLAYER;
    }
    get gridColour(): string {
        return gameStore.gridColour;
    }
    set gridColour(value: string) {
        gameStore.setGridColour({ colour: value, sync: true });
    }
    get fowColour(): string {
        return gameStore.fowColour;
    }
    set fowColour(value: string) {
        gameStore.setFOWColour({ colour: value, sync: true });
    }
    get rulerColour(): string {
        return gameStore.rulerColour;
    }
    set rulerColour(value: string) {
        gameStore.setRulerColour({ colour: value, sync: true });
    }
    get invertAlt(): boolean {
        return gameStore.invertAlt;
    }
    set invertAlt(value: boolean) {
        gameStore.setInvertAlt({ invertAlt: value, sync: true });
    }
    settingsClick(event: { target: HTMLElement }): void {
        if (
            event.target.classList.contains("menu-accordion") &&
            event.target.nextElementSibling!.classList.contains("menu-accordion-panel")
        ) {
            event.target.classList.toggle("menu-accordion-active");
        }
    }
    createNote(): void {
        const note = { title: "New note", text: "", uuid: uuidv4() };
        gameStore.newNote({ note, sync: true });
        this.openNote(note);
    }

    openNote(note: Note): void {
        (<Game>this.$parent.$parent).$refs.note.open(note);
    }

    openDmSettings(): void {
        EventBus.$emit("DmSettings.Open");
    }

    delMarker(marker: string): void {
        gameStore.removeMarker({ marker: marker, sync: true });
    }

    jumpToMarker(marker: string): void {
        gameStore.jumpToMarker(marker);
    }

    nameMarker(marker: string): string {
        const shape = layerManager.UUIDMap.get(marker);
        if (shape !== undefined) {
            return shape.name;
        } else {
            return "";
        }
    }

    openFile(event: { target: HTMLInputElement }): void {
        const input = event.target;
        const borderColour = "rgba(255, 0, 0, 1)";
        if (input.files == null || input.files.length == 0) {
            return;
        }
        const layer = layerManager.getLayer(layerManager.floor!.name, "fow");
        const fr = new FileReader();
        fr.onloadend = _e => {
            if (fr.result == null) {
                return;
            }
            const dp = new DOMParser();
            const doc: XMLDocument = dp.parseFromString(<string>fr.result, "image/svg+xml");
            for (const svgChild of doc.getElementsByTagNameNS("http://www.w3.org/2000/svg", "svg")) {
                for (const pathChild of svgChild.getElementsByTagNameNS("http://www.w3.org/2000/svg", "path")) {
                    let currentLocation = new GlobalPoint(0, 0);
                    const a = (<SVGPathElement>pathChild).pathSegList;
                    const points: GlobalPoint[] = [];
                    for (const seg of a) {
                        switch (seg.pathSegType) {
                            case 1: {
                                //ClosePath
                                currentLocation = points[0];
                                break;
                            }
                            case 2: {
                                //MoveToAbs
                                currentLocation = new GlobalPoint(seg.x, seg.y);
                                break;
                            }
                            case 3: {
                                //MoveToRel
                                currentLocation = currentLocation.add(new Vector(seg.x, seg.y));
                                break;
                            }
                            case 4: {
                                //LineToAbs
                                currentLocation = new GlobalPoint(seg.x, seg.y);
                                break;
                            }
                            case 5: {
                                //LineToRel
                                currentLocation = currentLocation.add(new Vector(seg.x, seg.y));
                                break;
                            }
                            case 12: {
                                //LineToHorizontalAbs
                                currentLocation = new GlobalPoint(seg.x, currentLocation.y);
                                break;
                            }
                            case 13: {
                                // LineToHorizontalRel
                                currentLocation = currentLocation.add(new Vector(seg.x, 0));
                                break;
                            }
                            case 14: {
                                // LineToVerticalAbs
                                currentLocation = new GlobalPoint(currentLocation.x, seg.y);
                                break;
                            }
                            case 15: {
                                // LineToVerticalRel
                                currentLocation = currentLocation.add(new Vector(0, seg.y));
                                break;
                            }
                            default: {
                                //throw error;
                                console.warn("Path contains unsupported segment: " + seg.pathSegType);
                                break;
                            }
                        }
                        points.push(currentLocation.clone());
                    }

                    const shape = new Polygon(points[0], points.slice(1), undefined, borderColour, 10, true);
                    shape.addOwner({ user: gameStore.username, editAccess: true, visionAccess: true }, false);
                    shape.movementObstruction = true;
                    shape.visionObstruction = true;
                    layer?.addShape(shape, SyncMode.FULL_SYNC, InvalidationMode.WITH_LIGHT);
                }
            }
            for (const imageChild of doc.getElementsByTagNameNS("http://www.w3.org/2000/svg", "image")) {
                console.log(imageChild);
            }
        };
        fr.readAsText(input.files[0]);
        if (layer === undefined) return;
    }
}
</script>

<template>
    <!-- SETTINGS -->
    <div id="menu" @click="settingsClick" ref="settings">
        <div style="width:200px;overflow-y:auto;overflow-x:hidden;">
            <!-- ASSETS -->
            <template v-if="IS_DM">
                <button class="menu-accordion">Assets</button>
                <div id="menu-assets" class="menu-accordion-panel">
                    <input id="asset-search" v-if="assets" v-model="assetSearch" placeholder="Search" />
                    <a class="actionButton" href="/assets" target="blank" title="Open asset manager">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                    <div class="directory" id="menu-tokens">
                        <asset-node :asset="assets" :search="assetSearch"></asset-node>
                        <div v-if="!assets">No assets</div>
                    </div>
                </div>
                <!-- NOTES -->
                <button class="menu-accordion">Notes</button>
                <div class="menu-accordion-panel">
                    <div class="menu-accordion-subpanel" id="menu-notes">
                        <a class="actionButton" @click="createNote" title="Create note">
                            <i class="far fa-plus-square"></i>
                        </a>
                        <div v-for="note in notes" :key="note.uuid" @click="openNote(note)" style="cursor:pointer">
                            {{ note.title || "[?]" }}
                        </div>
                        <div v-if="!notes.length">No notes</div>
                    </div>
                </div>
                <!-- DM OPTIONS -->
                <button class="menu-accordion" @click="openDmSettings">DM Options</button>
            </template>
            <!-- MARKERS -->
            <button class="menu-accordion">Markers</button>
            <div class="menu-accordion-panel">
                <div class="menu-accordion-subpanel" id="menu-markers">
                    <div v-for="marker in markers" :key="marker" style="cursor:pointer">
                        <div @click="jumpToMarker(marker)" class="menu-accordion-subpanel-text">
                            {{ nameMarker(marker) || "[?]" }}
                        </div>
                        <div @click="delMarker(marker)" title="Delete marker">
                            <i class="far fa-minus-square"></i>
                        </div>
                    </div>
                    <div v-if="!markers.length">No markers</div>
                </div>
            </div>
            <!-- CLIENT OPTIONS -->
            <button class="menu-accordion">Client Options</button>
            <div class="menu-accordion-panel">
                <div class="menu-accordion-subpanel">
                    <label for="gridColour">Grid Colour:</label>
                    <color-picker id="gridColour" :color.sync="gridColour" />
                    <label for="fowColour">FOW Colour:</label>
                    <color-picker id="fowColour" :color.sync="fowColour" />
                    <label for="rulerColour">Ruler Colour:</label>
                    <color-picker id="rulerColour" :color.sync="rulerColour" />
                    <label for="invertAlt">Invert ALT behaviour</label>
                    <div><input id="invertAlt" type="checkbox" v-model="invertAlt" /></div>
                </div>
            </div>
            <input type="file" @input="openFile" />
        </div>
        <router-link
            to="/dashboard"
            class="menu-accordion"
            style="width:200px;box-sizing:border-box;text-decoration:none;display:inline-block;"
        >
            Exit
        </router-link>
    </div>
</template>

<style scoped>
.menu-accordion-active + #menu-assets {
    display: flex;
    flex-direction: column;
}

#asset-search {
    text-align: center;
}

#asset-search::placeholder {
    text-align: center;
}

/*
DIRECTORY.CSS changes

* Collapse all folders by default, use js to toggle visibility on click.
* On hover over folder show some visual feedback
* On hover over file show the image

*/
.folder > * {
    display: none;
}

.directory > .folder,
.directory > .file {
    display: block;
}

.folder:hover {
    font-weight: bold;
    cursor: pointer;
}

.folder:hover > * {
    font-weight: normal;
}

#menuContainer {
    position: absolute;
    z-index: 20;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    pointer-events: none;
}

#menu {
    grid-area: menu;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #fa5a5a;
    overflow: auto;
    pointer-events: auto;
    max-width: 200px;
}

.actionButton {
    margin: 5px;
    align-self: flex-end;
    margin-bottom: -30px;
    z-index: 11;
}

.menu-accordion {
    background-color: #eee;
    color: #444;
    cursor: pointer;
    padding: 18px;
    text-align: left;
    border: none;
    outline: none;
    transition: 0.4s;
    border-top: solid 1px #82c8a0;
    width: 100%;
    width: -moz-available;
    width: -webkit-fill-available;
    width: stretch;
}

.menu-accordion-active,
.menu-accordion:hover {
    background-color: #82c8a0;
}

.menu-accordion-panel {
    background-color: white;
    display: none;
    overflow: hidden;
    min-height: 2em;
}

.menu-accordion-active + .menu-accordion-panel {
    display: block;
}

.menu-accordion-subpanel {
    display: flex;
    flex-direction: column;
    width: 100%;
}

.menu-accordion-subpanel > * {
    padding: 5px;
    display: flex;
    justify-content: space-evenly;
    align-items: center;
}

.menu-accordion-subpanel > *:hover {
    background-color: #82c8a0;
}

.menu-accordion-subpanel-text {
    text-align: left;
    justify-content: flex-start;
    flex: 1;
}
</style>
