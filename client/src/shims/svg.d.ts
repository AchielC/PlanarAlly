interface SVGPathElement {
    getPathData(): PathData[];
}

interface PathData {
    values: number[];
    type: string;
}