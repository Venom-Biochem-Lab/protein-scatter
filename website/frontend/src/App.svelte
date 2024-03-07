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
	import Molstar from "./lib/Molstar.svelte";
	import { Button, Search } from "flowbite-svelte";

	let colors = ["#22c695", "#c4c4c4"] as string[];
	let selectedName: string | undefined;
	let searchTable: string = "";
	let lassoedIdxs: number[] = [];

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
			let opacity = 0.2;
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
	function nameToCode(name: string) {
		const code = name.slice(3, 3 + 4);
		return code.toUpperCase();
	}

	function orderByDist(
		selectedName: string | undefined,
		lassoedIdxs: number[]
	) {
		if (selectedName === undefined && lassoedIdxs.length > 0)
			return lassoedIdxs;
		if (venomeMap && data && lassoedIdxs.length > 0) {
			const venomeVecs = venomeMap
				.get(selectedName)!
				.map((i) => [data.x[i], data.y[i]]);
			const restVecs = lassoedIdxs.map((i) => [data.x[i], data.y[i]]);
			// for each venome vec compute it's average distances to the rest of the vecs
			let smallestDists: number[] = [];
			let smallest = Infinity;
			let smallestIdx = -1;
			for (let i = 0; i < venomeVecs.length; i++) {
				const venome = venomeVecs[i];
				let sub = [];
				let summed = 0;
				for (let j = 0; j < restVecs.length; j++) {
					const rest = restVecs[j];
					const dist = Math.sqrt(
						(venome[0] - rest[0]) ** 2 + (venome[1] - rest[1]) ** 2
					);
					summed += dist;
					sub.push(dist);
				}
				if (summed < smallest) {
					smallest = summed;
					smallestIdx = i;
					smallestDists = [...sub];
				}
			}
			// cursed shit orders the idxs by the dists i found
			return lassoedIdxs
				.map((d, i) => {
					return { idx: d, dist: smallestDists[i] };
				})
				.toSorted((a, b) => a.dist - b.dist)
				.map((d) => d.idx);
		}
		return [];
	}
</script>

<div id="navbar"><b>Protein Scatter</b></div>
<div id="outer" style="display: flex; gap: 20px; position: relative;">
	{#if venomeInfo && data && scatterData.length > 0}
		<div class="sidebar">
			<div>
				<Search
					bind:value={searchTable}
					placeholder="Protein Search..."
				/>
			</div>
			<div
				class="flex gap-2 flex-wrap mt-5 content-start pl-2"
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
							? " --color: #18916d; --bg-color: #18916d30; "
							: ""}
						on:click={() => {
							if (selectedName === name) {
								selectedName = undefined;
							} else {
								selectedName = name;
							}
							reformatData();
						}}
					>
						{name.slice(0, name.indexOf(".")).replaceAll("_", " ")}
					</div>
				{/each}
			</div>
		</div>
		<div>
			<Scatterplot
				width={document.getElementById("outer").clientWidth}
				height={970}
				colorRange={colors}
				data={scatterData}
				on:lasso={(e) => {
					lassoedIdxs = e.detail;
				}}
			/>
		</div>
		{#if selectedName}
			<div
				id="top-right-sidebar"
				style="width: {400}px; height: {400}px; outline: grey;"
			>
				<Molstar
					width={400}
					height={400}
					url="http://localhost:8000/file/{selectedName}"
					format="pdb"
				/>
			</div>
		{/if}
		{#if lassoedIdxs.length > 0}
			<div id="right-sidebar">
				<div
					class="flex flex-row gap-2 flex-wrap"
					style="align-content: start;"
				>
					{#each orderByDist(selectedName, lassoedIdxs) as idx}
						{@const name = data.names[idx]}
						{@const code = nameToCode(name)}
						{#if !venomeInfo.names.includes(name)}
							<a
								href="https://www.rcsb.org/structure/{code}"
								class="pdb">{code}</a
							>
						{/if}
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.pdb {
		--color: rgba(20, 151, 253);
		--bg-color: rgba(20, 151, 253, 0.1);
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
	.pdb:hover {
		scale: 1.05;
	}
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
		--color: #22c695;
		--bg-color: #18916d30;
	}
	#navbar {
		padding: 15px;
		color: white;
		background: rgba(255, 255, 255, 0.148);
	}
	/* width */
	::-webkit-scrollbar {
		width: 3px;
	}

	/* Track */
	::-webkit-scrollbar-track {
		background: #37373750;
	}

	/* Handle */
	::-webkit-scrollbar-thumb {
		background: #88888850;
	}

	/* Handle on hover */
	::-webkit-scrollbar-thumb:hover {
		background: #55555550;
	}
	.sidebar {
		width: 250px;
		padding: 10px;
		border: 1px solid #374151;
		border-radius: 5px;
		position: absolute;
		left: 10px;
		top: 10px;
		backdrop-filter: blur(10px);
		background: #37415140;
	}
	#top-right-sidebar {
		width: 450px;
		height: 450px;
		border-radius: 5px;
		position: absolute;
		right: 10px;
		top: 10px;
		backdrop-filter: blur(10px);
		background: #37415140;
	}
	#right-sidebar {
		width: 400px;
		height: 500px;
		padding: 10px;
		border: 1px solid #374151;
		border-radius: 5px;
		position: absolute;
		right: 10px;
		bottom: 10px;
		backdrop-filter: blur(10px);
		background: #37415140;
		overflow-y: scroll;
	}
</style>
