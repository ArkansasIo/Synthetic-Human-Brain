//! CL1-Neural-labs protocol bridge for the Rust layer.
//!
//! Mirrors `integration/cl1_labs_ts/server.ts` and
//! `src/simulation/neuralCulture.ts` so the Rust backend can decode/encode the
//! same binary frames and serve the same discovery payload as the Node
//! simulator. See `docs/cl1-labs/CL1_LABS_INTEGRATION.md`.

/// Total MEA channels (8x8 grid).
pub const TOTAL_CHANNELS: usize = 64;
/// Channels shorted to ground in the Cortical Labs protocol.
pub const GROUNDED_CHANNELS: [usize; 4] = [0, 7, 56, 63];
/// Reference (inactive) channel.
pub const REFERENCE_CHANNELS: [usize; 1] = [4];
/// Microvolt per raw ADC unit.
pub const UV_PER_RAW_ADC: f64 = 0.195;
/// Per-channel flag bit: a spike was detected.
pub const FLAG_HAS_SPIKE: u8 = 1 << 0;
/// Per-channel flag bit: a stim was delivered.
pub const FLAG_HAS_STIM: u8 = 1 << 1;

/// Per-channel values in a broadcast frame (min, max, flags — all int16 LE).
pub const FRAME_STRIDE: usize = 3;
/// Total frame size in bytes: 64 channels x 3 int16 x 2 bytes = 384.
pub const FRAME_BYTES: usize = TOTAL_CHANNELS * FRAME_STRIDE * 2;

/// True when the channel may receive stimulation.
pub fn is_stim_channel(channel: usize) -> bool {
    !GROUNDED_CHANNELS.contains(&channel) && !REFERENCE_CHANNELS.contains(&channel)
}

/// A stim request mirroring `POST /api/stim` in server.ts.
#[derive(Debug, Clone)]
pub struct StimRequest {
    pub channels: Vec<usize>,
}

impl StimRequest {
    /// Channels that are grounded or reference (invalid for stimulation).
    pub fn invalid_channels(&self) -> Vec<usize> {
        self.channels
            .iter()
            .copied()
            .filter(|ch| !is_stim_channel(*ch))
            .collect()
    }

    /// Valid stim channels sorted ascending.
    pub fn valid_channels(&self) -> Vec<usize> {
        let mut valid: Vec<usize> = self
            .channels
            .iter()
            .copied()
            .filter(|ch| is_stim_channel(*ch))
            .collect();
        valid.sort_unstable();
        valid
    }
}

/// One decoded channel frame: voltage range plus spike/stim flags.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ChannelFrame {
    pub channel: usize,
    pub min_uv: f64,
    pub max_uv: f64,
    pub has_spike: bool,
    pub has_stim: bool,
}

/// Decode a binary broadcast frame (three little-endian int16 per channel,
/// 384 bytes total — exactly what `server.ts` emits via `Int16Array`).
pub fn decode_frame(data: &[u8]) -> Vec<ChannelFrame> {
    let mut frames = Vec::with_capacity(TOTAL_CHANNELS);
    for channel in 0..TOTAL_CHANNELS {
        let offset = channel * FRAME_STRIDE * 2;
        if offset + 5 >= data.len() {
            break;
        }
        let min_raw = i16::from_le_bytes([data[offset], data[offset + 1]]);
        let max_raw = i16::from_le_bytes([data[offset + 2], data[offset + 3]]);
        let flags = data[offset + 4] as i16 | ((data[offset + 5] as i16) << 8);
        frames.push(ChannelFrame {
            channel,
            min_uv: min_raw as f64 * UV_PER_RAW_ADC,
            max_uv: max_raw as f64 * UV_PER_RAW_ADC,
            has_spike: flags & FLAG_HAS_SPIKE as i16 != 0,
            has_stim: flags & FLAG_HAS_STIM as i16 != 0,
        });
    }
    frames
}

/// Encode a broadcast frame from raw per-channel `(min, max, flags)` triples.
pub fn encode_frame(payload: &[(i16, i16, u8)]) -> Vec<u8> {
    let mut values: Vec<i16> = Vec::with_capacity(FRAME_BYTES / 2);
    for channel in 0..TOTAL_CHANNELS {
        let (min_raw, max_raw, flags) = payload
            .get(channel)
            .copied()
            .unwrap_or((0, 0, 0));
        values.push(min_raw);
        values.push(max_raw);
        values.push(flags as i16 & 0x7FFF);
    }
    let mut buffer = Vec::with_capacity(FRAME_BYTES);
    for value in &values {
        buffer.extend_from_slice(&value.to_le_bytes());
    }
    buffer
}

/// Discovery payload mirroring `GET /_/config`.
pub fn cl1_config_json(port: u16) -> String {
    format!(
        r#"{{"device_id":"CL1-SIM-001","name":"Cortical Labs CL1 Bio-Computer Simulator","channel_count":{TOTAL_CHANNELS},"sampling_frequency":25000,"overview_url":"ws://localhost:{port}/_/ws/overview","websocket_url":"ws://localhost:{port}"}}"#
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grounded_and_reference_channels_reject_stim() {
        let request = StimRequest { channels: vec![0, 4, 7, 63, 10] };
        assert_eq!(request.invalid_channels(), vec![0, 4, 7, 63]);
        assert_eq!(request.valid_channels(), vec![10]);
    }

    #[test]
    fn frame_roundtrip_preserves_flags_and_uv() {
        let mut payload = [(0i16, 0i16, 0u8); TOTAL_CHANNELS];
        for (channel, slot) in payload.iter_mut().enumerate().take(3) {
            *slot = (0, 410, FLAG_HAS_SPIKE | FLAG_HAS_STIM);
            let _ = channel;
        }
        let encoded = encode_frame(&payload);
        assert_eq!(encoded.len(), FRAME_BYTES);
        let decoded = decode_frame(&encoded);
        assert_eq!(decoded.len(), TOTAL_CHANNELS);
        assert!(decoded[0].has_spike && decoded[0].has_stim);
        assert!((decoded[0].max_uv - 410.0 * UV_PER_RAW_ADC).abs() < 1e-9);
        // Channels beyond the payload default to silent.
        assert!(!decoded[10].has_spike);
        assert_eq!(decoded[10].max_uv, 0.0);
    }
}
