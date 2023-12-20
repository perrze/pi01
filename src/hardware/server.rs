mod types;

use std::io::{self, prelude::*};
use std::os::unix::net::{UnixListener, UnixStream};
use std::thread;

use anyhow::Context;

use types::*;

fn bind_socket() -> io::Result<UnixListener> {
    // In case the socket isn't properly removed...
    if std::fs::metadata(SOCKET_PATH).is_ok() {
        std::fs::remove_file(SOCKET_PATH)
            .with_context(|| format!("could not delete previous socket at {:?}", SOCKET_PATH))
            .expect("Failed to delete socket");
    }

    UnixListener::bind(SOCKET_PATH)
}

fn main() -> anyhow::Result<()> {
    let unix_listener = bind_socket().context("Could not create the unix socket")?;
    for connection in unix_listener.incoming() {
        match connection {
            Ok(stream) => {
                thread::spawn(|| handle_stream(stream));
            }
            Err(err) => {
                println!("[ERROR] Error occured: {:?}", err);
                break;
            }
        }
    }
    Ok(())
}

fn handle_stream(mut stream: UnixStream) -> anyhow::Result<()> {
    let mut buffer = [0; 12];
    stream
        .read(&mut buffer)
        .context("Failed at reading the stream")?;
    // println!("{:?}", TransformData::from_bytes(&buffer[..12]));
    stream.write(&[42])?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::*;

    #[test]
    fn server_connect_to_socket() {
        let unix_listener = bind_socket().context("Could not create the unix socket");
        // Check that the stream is Ok()
        unix_listener.unwrap();
    }
}
