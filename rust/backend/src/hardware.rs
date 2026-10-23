#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HardwareKind { Virtual, Cpu, Gpu, NeuralInterface }

#[derive(Debug, Clone)]
pub struct HardwareDevice { pub id: String, pub name: String, pub kind: HardwareKind, pub enabled: bool }

pub trait HardwarePlugin: Send + Sync {
    fn device(&self) -> &HardwareDevice;
    fn initialize(&mut self) -> Result<(), String>;
    fn shutdown(&mut self) -> Result<(), String>;
}

#[derive(Debug, Default)]
pub struct VirtualHardware { devices: Vec<HardwareDevice> }

impl VirtualHardware {
    pub fn new() -> Self { Self::default() }
    pub fn register(&mut self, device: HardwareDevice) { self.devices.push(device); }
    pub fn devices(&self) -> &[HardwareDevice] { &self.devices }
}
