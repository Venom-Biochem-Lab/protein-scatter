<script lang="ts">
	import WebGlScatterplot from "./WebGLScatterplot.svelte";
	import { extent } from "d3-array";
	import { scaleLinear } from "d3-scale";
	import type { ScatterPoints } from "../types";

	// inputs from component props
	// data must be [x: number, y: number, color: number between 0 and 1, opacity: number between 0 and 1][]
	export let data: ScatterPoints = [];
	export let colorRange: string[] = [];
	export let width: number;
	export let height: number;

	let dataThatFitsInView: ScatterPoints = [];

	/**
	 * This component does the same thing
	 * as webglscatterplot, but fits the [x, y] points on the screen to start
	 * if points are not between [-1, 1] it won't fit, lets rescale!
	 * (this gets run everytime data updates)
	 */
	$: dataThatFitsInView = fitPointsInView(data);

	/**
	 * converts the x -> [-1, 1] range
	 * converts the y -> [-1, 1] range
	 */
	function fitPointsInView(
		data: ScatterPoints,
		xPadding = 0.3,
		yPadding = 0.3
	): ScatterPoints {
		const dataExists = data && data.length > 0;
		if (!dataExists) return [];

		// 1. get the current range of the data
		const xRange = extent(data, (d) => Number(d[0]));
		const yRange = extent(data, (d) => Number(d[1]));

		// 2. create linear maps
		const xMapper = scaleLinear()
			//@ts-ignore
			.domain(xRange)
			.range([-1 + xPadding, 1 - xPadding]);
		const yMapper = scaleLinear()
			//@ts-ignore
			.domain(yRange)
			.range([-1 + yPadding, 1 - yPadding]);

		// 3. map the data
		const newData = data.map((d) => [
			xMapper(d[0]),
			yMapper(d[1]),
			d[2],
			d[3],
		]) as ScatterPoints;
		return newData;
	}
</script>

<WebGlScatterplot
	data={dataThatFitsInView}
	{colorRange}
	{width}
	{height}
	on:lasso
/>
