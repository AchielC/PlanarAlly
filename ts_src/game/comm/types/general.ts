import { ServerShape } from "./shapes";

export interface ServerLocation {
    name: string;
    use_grid: boolean;
    unit_size: number;
    full_FOW: boolean;
    fow_opacity: number;
    fow_LOS: boolean;
}

export interface ClientOptions {
    gridColour: string;
    fowColour: string;
    rulerColour: string;
    locationOptions: {
        [name: string]: {
            panX: number;
            panY: number;
            zoomFactor: number;
        };
    };
}

export interface InitiativeData {
    uuid: string;
    initiative?: number;
    owners: string[];
    visible: boolean;
    group: boolean;
    src: string;
    has_img: boolean;
    effects: InitiativeEffect[];
}

export interface InitiativeEffect {
    uuid: string;
    name: string;
    turns: number;
}

export interface ServerLayer {
    name: string;
    layer: string;
    shapes: ServerShape[];
    grid: boolean;
    selectable: boolean;
    player_editable: boolean;
    size: number;
}

export interface BoardInfo {
    locations: string[];
    layers: ServerLayer[];
}

export interface Note {
    name: string;
    text: string;
    uuid: string;
}