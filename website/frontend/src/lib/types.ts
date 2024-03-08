import createScatterplot from "regl-scatterplot";

export type ReglScatter = ReturnType<typeof createScatterplot>;
export type ScatterPoint = [number, number, number, number];
export type ScatterPoints = ScatterPoint[];
