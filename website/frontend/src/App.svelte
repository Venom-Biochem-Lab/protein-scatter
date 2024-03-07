<script lang="ts">
	import {
		Backend,
		type DataResponse,
		type InfoVenomeResponse,
	} from "./lib/backend";
	import Scatterplot from "./lib/scatterplot/Scatterplot.svelte";
	import * as d3 from "d3";
	import type { ScatterPoints } from "./lib/types";
	import { onMount } from "svelte";
	import { Button, Search } from "flowbite-svelte";

	let colors = ["#f22952", "#FFFFFF"] as string[];
	let selectedName: string;
	let searchTable: string = "";

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
	let scatterData: ScatterPoints = [];
	let venomeInfo: InfoVenomeResponse;
	let venomeMap: Map<string, number[]>;

	onMount(async () => {
		data = await Backend.getData();
		venomeInfo = await Backend.getInfoVenome();
		venomeMap = venomeToDataMap(venomeInfo, data);
		reformatData();
		console.log(venomeMap);
	});

	function venomeToDataMap(
		venomeInfo: InfoVenomeResponse,
		data: DataResponse
	) {
		const mapper = new Map<string, number[]>();
		for (let i = data.names.length - 1; i >= 0; i--) {
			const name = data.names[i];
			const isVenomeProtein = venomeInfo.names.includes(name);
			if (mapper.has(name)) {
				mapper.get(name)!.push(i);
			} else if (isVenomeProtein) {
				mapper.set(name, [i]);
			} else {
				break;
			}
		}
		return mapper;
	}
	function reformatData() {
		let result: ScatterPoints = [];
		for (let i = 0; i < data.x.length; i++) {
			let color = 1;
			let opacity = 0.1;
			result.push([data.x[i], data.y[i], color, opacity]);
		}

		if (selectedName) {
			venomeMap.get(selectedName)!.forEach((i) => {
				result[i][2] = 0;
				result[i][3] = 0.99;
			});
		}

		scatterData = result;
	}
</script>

<div id="navbar"><b>Protein Scatter</b></div>
<div style="display: flex; gap: 20px;">
	{#if venomeInfo && data && scatterData.length > 0}
		<div>
			<Scatterplot
				width={1000}
				height={1000}
				colorRange={colors}
				data={scatterData}
				on:lasso={(e) => {}}
			/>
		</div>
		<div style="width: 400px;">
			<div class="mt-5">
				<Search
					bind:value={searchTable}
					placeholder="Search for a venom protein"
				/>
			</div>
			<div
				class="flex gap-2 flex-wrap mt-5 content-start"
				style="height: 800px; overflow-y: scroll;"
			>
				{#each venomeInfo.names.filter((d) => !searchTable || d
							.toLowerCase()
							.includes(searchTable.toLowerCase())) as name}
					<!-- svelte-ignore a11y-click-events-have-key-events -->
					<!-- svelte-ignore a11y-no-static-element-interactions -->
					<div
						class="venome"
						style={selectedName == name
							? "--color: #f22952; --bg-color: #f2295230;"
							: ""}
						on:click={() => {
							selectedName = name;
							reformatData();
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
		--color: #ffffff;
		--bg-color: #ffffff30;
		padding: 2px;
		padding-left: 5px;
		padding-right: 5px;
		border: 1px solid var(--color);
		background: var(--bg-color);
		color: var(--color);
		border-radius: 5px;
		cursor: pointer;
		transition: all ease-in-out 0.2s;
	}
	.venome:hover {
		scale: 1.05;
		--color: #f22952;
		--bg-color: #f2295230;
	}
	#navbar {
		padding: 15px;
		color: white;
		background: rgba(255, 255, 255, 0.148);
	}
</style>
