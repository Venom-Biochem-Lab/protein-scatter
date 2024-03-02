<script lang="ts">
	import { Backend, type DataResponse } from "./lib/backend";
	import Scatterplot from "./lib/scatterplot/Scatterplot.svelte";
	import { schemeCategory10 } from "d3";
	import type { Data } from "./lib/types";

	let data: DataResponse;
	Backend.getData(100_000).then((d) => (data = d));
	function reformatData(data: DataResponse): Data {
		let result: Data = [];
		for (let i = 0; i < data.x.length; i++) {
			let color = 3;
			let opacity = 0.05;
			if (i < 386) {
				color = 0;
				opacity = 1;
			}
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
	{#if data}
		<div>
			<Scatterplot
				width={700}
				height={700}
				colorRange={schemeCategory10}
				data={reformatData(data)}
				on:lasso={(e) => {
					const idxs = e.detail;
					names = idxs.map((d) => idxToName(d));
				}}
			/>
		</div>
		<div style="display: flex; flex-direction: column; gap:5px;">
			{#each names as name}
				<div>
					<a
						href="https://www.rcsb.org/structure/{nameToCode(
							name
						).toUpperCase()}">{name}</a
					>
				</div>
			{/each}
		</div>
	{/if}
</div>
