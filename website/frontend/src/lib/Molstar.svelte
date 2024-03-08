<script lang="ts">
	import { onMount } from "svelte";

	export let url = "";
	export let format = "pdb";
	export let binary = false;
	export let width = 500;
	export let height = 500;

	// const url = `http://localhost:8000/protein/pdb/${proteinName}`;
	let divEl: HTMLDivElement;
	async function render() {
		// @ts-ignore
		const m = new PDBeMolstarPlugin(); // loaded through app.html
		divEl.innerHTML = "";
		const div = document.createElement("div");
		divEl.appendChild(div);
		await m.render(div, {
			customData: {
				url,
				format,
				binary,
			},
			bgColor: {
				r: 0,
				g: 0,
				b: 0,
			},
			subscribeEvents: false,
			selectInteraction: true,
			alphafoldView: true,
			reactive: true,
			sequencePanel: true,
			hideControls: true,
			hideCanvasControls: ["animation"],
		});
	}

	$: {
		if (url && divEl) {
			render();
			console.log("hit");
		}
	}
</script>

<div
	bind:this={divEl}
	id="myViewer"
	style="width: {width}px; height: {height}px;"
/>

<style>
	/* https://embed.plnkr.co/plunk/WlRx73uuGA9EJbpn */
	.msp-plugin ::-webkit-scrollbar-thumb {
		background-color: #474748 !important;
	}
	#myViewer {
		float: left;
		position: relative;
		z-index: 997;
	}
</style>
