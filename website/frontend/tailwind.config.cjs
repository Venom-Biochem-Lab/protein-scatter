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
					50: "#f22952",
					100: "#f22952",
					200: "#f22952",
					300: "#f22952",
					400: "#f22952",
					500: "#f22952",
					600: "#f22952",
					700: "#f22952",
					800: "#f22952",
					900: "#f22952",
				},
			},
		},
	},
};

module.exports = config;
