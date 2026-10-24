//! Hardware data pipeline mirroring `src/synthetic_brain/hardware_pipeline.py`
//! and `docs/HARDWARE_ARCHITECTURE.md`.
//!
//! Stages: sensor interface config, analog front end model, digitizer with
//! dropped-sample detection, synchronization clock, versioned transport
//! packets, and raw/derived storage separation. Rust side is intended for the
//! edge-compute block: high-rate ingest, quality flagging, packetization.

/// Versioned packet schema identifier (must match the Python constant).
pub const PIPELINE_FORMAT: &str = "synthetic-brain-hardware-pipeline-v1";

/// Per-sample quality flags from the digitizer stage (bitfield).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct QualityFlags(pub u8);

impl QualityFlags {
    pub const OK: Self = Self(0);
    pub const SATURATED: Self = Self(1 << 0);
    pub const DROPPED: Self = Self(1 << 1);
    pub const OUT_OF_RANGE: Self = Self(1 << 2);
    pub const UNSYNCED: Self = Self(1 << 3);

    pub fn contains(self, other: Self) -> bool {
        self.0 & other.0 == other.0
    }

    pub fn bits(self) -> u8 {
        self.0
    }
}

/// Analog front end configuration the digitizer uses to interpret signals.
#[derive(Debug, Clone)]
pub struct AnalogFrontEndConfig {
    pub gain: f64,
    pub high_pass_hz: f64,
    pub low_pass_hz: f64,
    pub notch_hz: Option<f64>,
}

impl AnalogFrontEndConfig {
    pub fn validate(&self) -> Result<(), String> {
        if self.gain <= 0.0 {
            return Err("gain must be positive".into());
        }
        if self.high_pass_hz >= self.low_pass_hz {
            return Err("high_pass_hz must be below low_pass_hz".into());
        }
        Ok(())
    }
}

/// One timestamped digital sample for one channel.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct DigitizerSample {
    pub channel: usize,
    pub timestamp_ns: u64,
    pub value: f64,
    pub quality: QualityFlags,
}

/// Digitizer with dropped-sample detection.
pub struct Digitizer {
    pub sample_rate_hz: f64,
    pub channels: usize,
    expected_period_ns: u64,
    tolerance_ns: u64,
    last_timestamp: Vec<Option<u64>>,
}

impl Digitizer {
    pub fn new(sample_rate_hz: f64, channels: usize) -> Self {
        assert!(sample_rate_hz > 0.0, "sample_rate_hz must be positive");
        assert!(channels >= 1, "channels must be positive");
        let expected_period_ns = (1e9 / sample_rate_hz) as u64;
        Self {
            sample_rate_hz,
            channels,
            expected_period_ns,
            tolerance_ns: expected_period_ns / 2,
            last_timestamp: vec![None; channels],
        }
    }

    /// Digitize one buffer for one channel; flags gaps as DROPPED.
    pub fn digitize(&mut self, channel: usize, raw: &[f64], start_ns: u64) -> Vec<DigitizerSample> {
        assert!(channel < self.channels, "channel out of range");
        let mut samples = Vec::with_capacity(raw.len());
        for (index, value) in raw.iter().enumerate() {
            let timestamp = start_ns + index as u64 * self.expected_period_ns;
            let mut quality = QualityFlags::OK;
            if let Some(previous) = self.last_timestamp[channel] {
                if timestamp - previous > self.expected_period_ns + self.tolerance_ns {
                    quality = QualityFlags::DROPPED;
                }
            }
            self.last_timestamp[channel] = Some(timestamp);
            samples.push(DigitizerSample {
                channel,
                timestamp_ns: timestamp,
                value: *value,
                quality,
            });
        }
        samples
    }
}

/// Versioned transport packet: identity, time, data, units, quality, source.
#[derive(Debug, Clone, PartialEq)]
pub struct TransportPacket {
    pub schema: String,
    pub channel: usize,
    pub timestamp_ns: u64,
    pub samples: Vec<f64>,
    pub units: String,
    pub quality: u8,
    pub source_id: String,
}

impl TransportPacket {
    pub fn new(channel: usize, timestamp_ns: u64, samples: Vec<f64>, units: &str, quality: u8, source_id: &str) -> Self {
        Self {
            schema: PIPELINE_FORMAT.to_string(),
            channel,
            timestamp_ns,
            samples,
            units: units.to_string(),
            quality,
            source_id: source_id.to_string(),
        }
    }

    /// Serialize to the same JSON shape the Python side emits.
    pub fn to_json(&self) -> String {
        let samples: Vec<String> = self.samples.iter().map(|value| format!("{value}")).collect();
        format!(
            r#"{{"schema":"{}","channel":{},"timestamp_ns":{},"samples":[{}],"units":"{}","quality":{},"source_id":"{}"}}"#,
            self.schema,
            self.channel,
            self.timestamp_ns,
            samples.join(","),
            self.units,
            self.quality,
            self.source_id
        )
    }
}

/// Raw storage, separate from derived datasets.
#[derive(Default)]
pub struct PacketStorage {
    raw: Vec<TransportPacket>,
}

impl PacketStorage {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn append(&mut self, packet: TransportPacket) {
        assert_eq!(packet.schema, PIPELINE_FORMAT, "packet schema mismatch");
        self.raw.push(packet);
    }

    pub fn raw(&self) -> &[TransportPacket] {
        &self.raw
    }

    /// Derive values with provenance kept implicit in the caller's name.
    pub fn derive(&self, name: &str, transform: impl Fn(&TransportPacket) -> f64) -> Vec<(String, f64)> {
        self.raw
            .iter()
            .map(|packet| (name.to_string(), transform(packet)))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn digitizer_flags_dropped_samples() {
        let mut digitizer = Digitizer::new(1000.0, 2);
        let first = digitizer.digitize(0, &[1.0, 2.0], 0);
        assert!(first.iter().all(|sample| sample.quality == QualityFlags::OK));
        // A gap of 10 periods should be flagged as dropped.
        let second = digitizer.digitize(0, &[3.0], 10_000_000);
        assert!(second[0].quality.contains(QualityFlags::DROPPED));
    }

    #[test]
    fn packet_roundtrip_through_json() {
        let packet = TransportPacket::new(3, 123, vec![1.5, -2.5], "µV", QualityFlags::OK.bits(), "mea-1");
        let json = packet.to_json();
        assert!(json.contains("\"schema\":\"synthetic-brain-hardware-pipeline-v1\""));
        assert!(json.contains("\"channel\":3"));
        assert!(json.contains("\"units\":\"µV\""));
    }

    #[test]
    fn storage_separates_raw_and_derived() {
        let mut storage = PacketStorage::new();
        storage.append(TransportPacket::new(0, 1, vec![1.0], "µV", 0, "s"));
        let derived = storage.derive("peak", |packet| packet.samples[0]);
        assert_eq!(storage.raw().len(), 1);
        assert_eq!(derived[0].0, "peak");
        assert_eq!(derived[0].1, 1.0);
    }
}
