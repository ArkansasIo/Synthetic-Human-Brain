use crate::platform::Platform;
use crate::cl1_labs_bridge;

/// Hardware plugin exposing the CL1-Neural-labs 64-channel simulated dish
/// as a virtual device with the Cortical Labs channel map.
pub struct Cl1LabsVirtualDevice {
    inner: VirtualHardware,
}

impl Cl1LabsVirtualDevice {
    pub fn new(id: impl Into<String>) -> Self {
        Self {
            inner: VirtualHardware::new(id, "CL1-Neural-labs Virtual Dish"),
        }
    }

    /// Underlying device descriptor (id, name, capabilities).
    pub fn device(&self) -> &HardwareDevice {
        self.inner.device()
    }

    /// True after `HardwarePlugin::initialize` has been called.
    pub fn is_initialized(&self) -> bool {
        self.inner.initialized()
    }

    /// Valid stim channels per the CL1 protocol (excludes grounded/reference).
    pub fn stim_channels(&self) -> Vec<usize> {
        (0..cl1_labs_bridge::TOTAL_CHANNELS)
            .filter(|ch| cl1_labs_bridge::is_stim_channel(*ch))
            .collect()
    }

    /// Decode a broadcast frame into per-channel µV ranges and flags.
    pub fn decode(&self, frame: &[u8]) -> Vec<cl1_labs_bridge::ChannelFrame> {
        cl1_labs_bridge::decode_frame(frame)
    }
}

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

    #[test]
    fn cl1_labs_device_channel_map() {
        let device = Cl1LabsVirtualDevice::new("cl1-labs-0");
        let stim = device.stim_channels();
        // 64 channels minus 4 grounded minus 1 reference = 59 stim channels.
        assert_eq!(stim.len(), 59);
        assert!(!stim.contains(&0) && !stim.contains(&7) && !stim.contains(&4));
        assert!(stim.contains(&1) && stim.contains(&10));
    }
}
