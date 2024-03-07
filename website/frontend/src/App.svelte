<script lang="ts">
	import {
		Backend,
		type DataResponse,
		type InfoVenomeResponse,
	} from "./lib/backend";
	import Scatterplot from "./lib/scatterplot/Scatterplot.svelte";
	import * as d3 from "d3";
	import type { Data } from "./lib/types";
	import { onMount } from "svelte";

	let colors = d3.schemeCategory10 as string[];
	let selectedName: string;

	/**
	 * Takes a function that produces colors from numbers into a fixed sized array
	 *
	 * @returns string array of hex colors
	 */
	function interpolateToStringArray(
		colorInterpolate: (x: number) => string,
		length: number,
		padLeft = 0,
		padRight = 0,
		reverse = false
	) {
		const colors: string[] = new Array(length);
		const interval = 1 / (length - padLeft - padRight);
		let inputValue = 0 + padLeft;
		for (let i = 0; i < length; i++) {
			// must be a normalized value
			if (inputValue > 1) {
				inputValue = 1;
			} else if (inputValue < 0) {
				inputValue = 0;
			}

			// from continuous function to string hex
			const rgbString = colorInterpolate(
				reverse ? 1 - inputValue : inputValue
			);
			colors[i] = d3.color(rgbString)!.formatHex();
			inputValue += interval;
		}

		return colors;
	}

	let data: DataResponse;
	let venomeInfo: InfoVenomeResponse;

	onMount(async () => {
		// data = await Backend.getData();
		venomeInfo = await Backend.getInfoVenome();
	});

	function reformatData(data: DataResponse): Data {
		let result: Data = [];
		for (let i = 0; i < data.x.length; i++) {
			let color = 0;
			let opacity = 0.1;
			result.push([data.x[i], data.y[i], color, opacity]);
		}
		return result;
	}
	function nameToCode(name: string) {
		const code = name.slice(3, 3 + 4);
		return code;
	}
	function idxToName(idx: number): string {
		const filename = data.names[idx];
		return filename;
	}
	let names: string[] = [];
</script>

<div style="display: flex; gap: 20px;">
	{#if venomeInfo}
		<!-- <div>
			<Scatterplot
				width={700}
				height={700}
				colorRange={colors}
				data={reformatData(data)}
				on:lasso={(e) => {}}
			/>
		</div> -->
		<div style="width: 800px;">here</div>
		<div style="width: 400px;">
			<h1>{selectedName}</h1>

			<div class="flex gap-2 flex-wrap">
				{#each venomeInfo.names as name}
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<div
						class="venome"
						style={selectedName == name ? "--color: red;" : ""}
						on:click={() => {
							selectedName = name;
						}}
					>
						{name.slice(0, name.indexOf(".")).replaceAll("_", " ")}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.venome {
		--color: #17bebb;
		padding: 2px;
		padding-left: 5px;
		padding-right: 5px;
		border: 1px solid var(--color);
		background: #17bebb10;
		color: var(--color);
		border-radius: 5px;
		cursor: pointer;
		transition: all ease-in-out 0.2s;
	}
	.venome:hover {
		scale: 1.05;
	}
</style>
