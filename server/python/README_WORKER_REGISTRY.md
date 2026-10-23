# Distributed Worker Registry

The worker registry allows one research server to manage multiple Windows, macOS, and Linux research stations.

## Topology

```text
Browser / Desktop Clients
          |
       HTTPS/WSS
          v
   Python Research API
          |
          +---- MySQL
          |
          +---- Worker Registry
                  |
          +-------+-------+
          |       |       |
       Windows   macOS   Linux
       worker    worker   worker
          |
       Rust/Python simulation backends
```

## Registration

Set `SYNTHETIC_BRAIN_WORKER_REGISTRY_TOKEN` on the registry process and send it as a Bearer token.

1. `POST /api/v1/servers/register`
2. `POST /api/v1/workers/register`
3. Worker sends `POST /api/v1/workers/{worker_id}/heartbeat` periodically.
4. Research jobs can select a backend using worker capabilities.

The registry token is a deployment secret and is never committed to the repository.

## Capability document

A worker should advertise capabilities such as:

```json
{
  "cpu": {"logical_cores": 16},
  "memory_gb": 64,
  "gpu": {"vendor": "unknown", "backends": ["vulkan"]},
  "simulation": ["lif", "network", "brainscript"],
  "platform": "linux",
  "architectures": ["x86_64"]
}
```

Capability discovery is descriptive. A platform is not considered supported merely because a capability string exists; the worker must pass its own runtime self-test before reporting the capability as available.

## Production routing

The next orchestration layer should select a worker by:

- online heartbeat;
- requested backend (`python`, `rust`, or `hybrid`);
- required simulation features;
- CPU/GPU/memory requirements;
- project isolation and permissions;
- current worker load.

Long-running jobs should be queued asynchronously rather than holding the HTTP request open.
