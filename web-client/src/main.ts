import { ResearchApi } from "./api";
import "./style.css";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Application root not found");

const api = new ResearchApi({
  baseUrl: window.location.origin,
  websocketUrl: `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`
});

app.innerHTML = `
  <main class="research-shell">
    <header class="titlebar">
      <div><div class="eyebrow">RESEARCHER BROWSER</div><h1>Synthetic Human Brain</h1></div>
      <span id="status" class="status">Offline</span>
    </header>
    <section id="login" class="login-panel">
      <h2>Research Station Login</h2>
      <p>Connect to the Python research API and its Rust simulation workers.</p>
      <form id="login-form">
        <input id="username" autocomplete="username" placeholder="Researcher username" required />
        <input id="password" type="password" autocomplete="current-password" placeholder="Password" required />
        <button type="submit">Sign in</button>
      </form>
      <p id="login-output" class="muted"></p>
    </section>
    <nav class="main-nav">
      <button data-page="Dashboard">Dashboard</button>
      <button data-page="Projects">Projects</button>
      <button data-page="Experiments">Experiments</button>
      <button data-page="Brain Regions">Brain Regions</button>
      <button data-page="Telemetry">Telemetry</button>
      <button data-page="Jobs">Jobs</button>
      <button data-page="Source">BrainScript</button>
      <button data-page="Servers">Servers</button>
      <button data-page="Admin">Admin</button>
    </nav>
    <section class="workspace">
      <aside><h2>Research Tree</h2><p>Projects</p><p>Experiments</p><p>Datasets</p><p>Brain Regions</p><p>BrainScript</p><p>Servers</p></aside>
      <article>
        <h2 id="page-title">Research Workspace</h2>
        <p id="page-description">Connect this browser to a Synthetic Brain server to begin.</p>
        <div class="actions"><button id="health">Check Server</button><button id="connect">Open Live Telemetry</button></div>
        <pre id="output"></pre>
      </article>
    </section>
  </main>
`;

document.querySelectorAll<HTMLButtonElement>("[data-page]").forEach((button) => {
  button.addEventListener("click", () => {
    const page = button.dataset.page ?? "Workspace";
    document.querySelector("#page-title")!.textContent = page;
    document.querySelector("#page-description")!.textContent = `${page} workspace ready for server-backed research.`;
  });
});

document.querySelector<HTMLButtonElement>("#health")?.addEventListener("click", async () => {
  const output = document.querySelector<HTMLPreElement>("#output");
  const status = document.querySelector<HTMLSpanElement>("#status");
  if (!output || !status) return;
  try {
    const health = await api.health();
    status.textContent = "Online";
    output.textContent = JSON.stringify(health, null, 2);
  } catch (error) {
    status.textContent = "Offline";
    output.textContent = String(error);
  }
});

document.querySelector<HTMLButtonElement>("#connect")?.addEventListener("click", () => {
  const output = document.querySelector<HTMLPreElement>("#output");
  if (!output) return;
  const socket = api.connectTelemetry((event) => {
    output.textContent = event.data;
  });
  socket.onopen = () => { output.textContent = "Telemetry WebSocket connected."; };
  socket.onerror = () => { output.textContent = "Telemetry WebSocket error."; };
});

document.querySelector<HTMLFormElement>("#login-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = document.querySelector<HTMLInputElement>("#username")!.value;
  const password = document.querySelector<HTMLInputElement>("#password")!.value;
  const output = document.querySelector<HTMLParagraphElement>("#login-output")!;
  try {
    output.textContent = JSON.stringify(await api.login(username, password));
  } catch (error) {
    output.textContent = String(error);
  }
});
