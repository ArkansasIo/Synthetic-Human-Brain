import { ResearchApi } from "./api";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Application root not found");

const api = new ResearchApi({
  baseUrl: window.location.origin,
  websocketUrl: `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`
});

app.innerHTML = `
  <main class="research-shell">
    <header><h1>Synthetic Human Brain Researcher</h1><span id="status">Disconnected</span></header>
    <nav><button>Dashboard</button><button>Projects</button><button>Experiments</button><button>Brain Regions</button><button>Telemetry</button><button>Jobs</button><button>Source</button></nav>
    <section class="workspace">
      <aside><h2>Research Tree</h2><p>Projects</p><p>Experiments</p><p>Datasets</p><p>Brain Regions</p><p>Servers</p></aside>
      <article><h2>Research Workspace</h2><p>Connect this browser to a Synthetic Brain server to begin.</p><button id="health">Check Server</button><pre id="output"></pre></article>
    </section>
  </main>
`;

document.querySelector<HTMLButtonElement>("#health")?.addEventListener("click", async () => {
  const output = document.querySelector<HTMLPreElement>("#output");
  if (!output) return;
  try {
    const health = await api.health();
    output.textContent = JSON.stringify(health, null, 2);
  } catch (error) {
    output.textContent = String(error);
  }
});
