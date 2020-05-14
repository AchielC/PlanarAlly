export interface AssetList {
    [inode: string]: AssetList | AssetFile[];
}

export interface AssetFile {
    name: string;
    hash: string;
}

export interface Asset {
    id: number;
    name: string;
    file_hash?: string;
    children?: Asset[];
}

export enum SyncMode {
    NO_SYNC,
    TEMP_SYNC,
    FULL_SYNC,
}

export enum InvalidationMode {
    NO,
    NORMAL, // repaint of the screen without recalculating lighting
    WITH_LIGHT, // repaint of the screen with recalculating lighting
}
