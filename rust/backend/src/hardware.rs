use crate::platform::Platform;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HardwareKind {
    Virtual,
    Cpu,
    Gpu,
    Neural,
}

#[derive(Debug, Clone)]
pub struct HardwareCapabilities {
    pub platform: Platform,
    pub kind: HardwareKind,
    pub compute_units: u32,
    pub memory_bytes: u64,
    pub accelerator: Option<String>,
}

#[derive(Debug, Clone)]
pub struct HardwareDevice {
    pub id: String,
    pub name: String,
    pub capabilities: HardwareCapabilities,
    pub enabled: bool,
}

#[derive(Debug, Clone)]
pub struct HardwareError {
    pub message: String,
}

pub trait HardwarePlugin: Send + Sync {
    fn id(&self) -> &str;
    fn device(&self) -> &HardwareDevice;
    fn initialize(&mut self) -> Result<(), HardwareError>;
    fn shutdown(&mut self);
}

#[derive(Debug, Clone)]
pub struct VirtualHardware {
    device: HardwareDevice,
    initialized: bool,
}

impl VirtualHardware {
    pub fn new(id: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            device: HardwareDevice {
                id: id.into(),
                name: name.into(),
                capabilities: HardwareCapabilities {
                    platform: Platform::current(),
                    kind: HardwareKind::Virtual,
                    compute_units: 1,
                    memory_bytes: 0,
                    accelerator: None,
                },
                enabled: true,
            },
            initialized: false,
        }
    }

    pub fn initialized(&self) -> bool {
        self.initialized
    }
}

impl HardwarePlugin for VirtualHardware {
    fn id(&self) -> &str { &self.device.id }
    fn device(&self) -> &HardwareDevice { &self.device }

    fn initialize(&mut self) -> Result<(), HardwareError> {
        self.initialized = true;
        Ok(())
    }

    fn shutdown(&mut self) {
        self.initialized = false;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn virtual_device_lifecycle() {
        let mut device = VirtualHardware::new("virtual-0", "Virtual Neural Device");
        assert!(!device.initialized());
        device.initialize().unwrap();
        assert!(device.initialized());
        device.shutdown();
        assert!(!device.initialized());
    }
}
