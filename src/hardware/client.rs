mod types;

use std::io::prelude::*;
use std::os::unix::net::UnixStream;

use anyhow::Context;
use cgmath::Rad;
use types::*;

fn main() -> anyhow::Result<()> {
    // Move forward by one unit
    let data = TransformData::new(1., 0., Rad(0.));

    let mut unix_stream =
        UnixStream::connect(SOCKET_PATH).context("Could not connect to stream")?;
    // Network byte order
    let bytes = data.to_bytes();
    unix_stream
        .write(&bytes)
        .context("Failed to write onto the unix stream")?;

    let mut buf: [u8; 12] = [0; 12];
    unix_stream.read(&mut buf)?;
    let [delta_x, delta_y, delta_r] =
        bytemuck::try_from_bytes::<[f32; 3]>(&buf).expect("Failed read floats from bytes");

    println!("{delta_x} {delta_y} {delta_r}");

    Ok(())
}
