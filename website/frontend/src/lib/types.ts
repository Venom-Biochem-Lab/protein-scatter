import createScatterplot from "regl-scatterplot";

export type ReglScatter = ReturnType<typeof createScatterplot>;
export type Datum = [number, number, number, number];
export type Data = Datum[];
