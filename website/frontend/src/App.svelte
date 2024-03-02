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
			result.push([data.x[i], data.y[i], 3, 1]);
		}
		return result;
	}
</script>

<div style="outline: 1px solid grey;">
	{#if data}
		<Scatterplot
			width={1000}
			height={1000}
			colorRange={schemeCategory10}
			data={reformatData(data)}
			on:lasso={(e) => console.log(e.detail)}
		/>
	{/if}
</div>
