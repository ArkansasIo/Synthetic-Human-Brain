#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Platform { Windows, MacOS, Linux }

impl Platform {
    pub fn current() -> Self {
        if cfg!(target_os = "windows") { Self::Windows }
        else if cfg!(target_os = "macos") { Self::MacOS }
        else { Self::Linux }
    }

    pub fn name(self) -> &'static str {
        match self { Self::Windows => "Windows", Self::MacOS => "macOS", Self::Linux => "Linux" }
    }
}
