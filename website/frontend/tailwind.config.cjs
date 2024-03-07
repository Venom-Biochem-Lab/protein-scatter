const config = {
	content: [
		"./src/**/*.{html,js,svelte,ts}",
		"./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}",
	],

	plugins: [require("flowbite/plugin")],

	darkMode: "class",

	theme: {
		extend: {
			colors: {
				// flowbite-svelte
				primary: {
					50: "#22c695",
					100: "#22c695",
					200: "#22c695",
					300: "#22c695",
					400: "#22c695",
					500: "#22c695",
					600: "#22c695",
					700: "#22c695",
					800: "#22c695",
					900: "#22c695",
				},
			},
		},
	},
};

module.exports = config;
