//! Standalone server binary for the Synthetic Human Brain Rust backend.
//!
//! Loads settings from the environment (`SYNTHETIC_BRAIN_*` variables, see
//! `synthetic_brain_backend::settings::Settings`), performs a boot-check
//! simulation step through `BackendService`, and reports readiness on stdout.
//! Intended for the `dist/exe` release artifact; the full HTTP API lives in
//! the `rust/server` crate. This binary runs the backend service loop
//! directly for embedded/headless deployments.

use synthetic_brain_backend::settings::Settings;
use synthetic_brain_backend::BackendService;

fn main() {
    let settings = Settings::from_env();

    if settings.options.refuse_placeholder_secrets && settings.using_placeholder_secret() {
        eprintln!(
            "refusing to start: {} still contains a placeholder secret; set a real password",
            settings.database.password_env
        );
        std::process::exit(2);
    }

    println!(
        "synthetic-brain-server starting: {}:{} backend={} workers={} db={}@{}:{}/{}",
        settings.host,
        settings.port,
        settings.workers.backend,
        settings.workers.max_concurrent_jobs,
        settings.database.username,
        settings.database.host,
        settings.database.port,
        settings.database.database,
    );

    let mut service = BackendService::new();
    let spike = service.step(0.0, 1.0);
    println!(
        "backend service ready: simulation_time_ms={:.1} spikes_emitted={} boot_spike={}",
        service.simulation_time_ms, service.spikes_emitted, spike
    );

    println!("running; press Ctrl+C to stop");
    loop {
        std::thread::sleep(std::time::Duration::from_secs(1));
    }
}
