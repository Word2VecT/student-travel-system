/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from "@/plugins";

// Components
import Particles from "particles.vue3";
import App from "./App.vue";
import router from "./router";

// Composables
import { createApp } from "vue";

const app = createApp(App).use(router).use(Particles);

registerPlugins(app);

app.mount("#app");
