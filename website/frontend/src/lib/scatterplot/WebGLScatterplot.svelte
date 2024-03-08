<script lang="ts">
	import createScatterplot from "regl-scatterplot";
	import { onMount, createEventDispatcher } from "svelte";
	import type { ScatterPoints, ReglScatter } from "../types";

	// create function for signaling back to parent component
	const dispatch = createEventDispatcher();

	// inputs from component props
	// data must be [x: number, y: number, color: number between 0 and 1, opacity: number between 0 and 1][]
	export let data: ScatterPoints = [];
	export let colorRange: string[] = [];
	export let width: number;
	export let height: number;

	let canvasEl: HTMLCanvasElement;
	let scatterPtr: ReglScatter;

	// everytime data is changed, redraw the scatterplot with those points
	$: drawData(scatterPtr, data);

	// when the component mounts, initialize the canvas
	onMount(() => {
		scatterPtr = initScatterplot();
		defineDataEncoding(scatterPtr, colorRange); // defines the category to color and value to opacity
		defineLassoSelection(scatterPtr); // defines the lasso selection signal to the parent component
	});

	function drawData(scatterPtr: ReglScatter, data: ScatterPoints) {
		if (scatterPtr) {
			scatterPtr.draw(data);
		}
	}
	function initScatterplot() {
		const scatterPtr = createScatterplot({
			canvas: canvasEl,
			width,
			height,
			// backgroundColor: "#000000",
			lassoColor: "#f66c02",
		});
		return scatterPtr;
	}
	function defineDataEncoding(scatterPtr: ReglScatter, colorRange: string[]) {
		scatterPtr.set({
			colorBy: "category",
			pointColor: colorRange,
		});
		const range = opacityRange(20);
		scatterPtr.set({
			opacityBy: "value",
			opacity: range,
		});
		scatterPtr.set({
			sizeBy: "value",
			pointSize: [1, 4, 8, 16],
		});
	}
	function defineLassoSelection(scatterPtr: ReglScatter) {
		if (scatterPtr) {
			scatterPtr.subscribe(
				"deselect",
				() => {
					dispatch("lasso", []);
				},
				undefined
			);
			scatterPtr.subscribe(
				"select",
				(d) => {
					if (d) {
						dispatch("lasso", d["points"]);
					}
				},
				undefined
			);
		}
	}

	/* returns [0, ..., 1] with n elements */
	function opacityRange(n = 10) {
		return new Array(n).fill(0).map((_, i) => (i + 1) / n);
	}
</script>

<canvas bind:this={canvasEl} {width} {height} />
