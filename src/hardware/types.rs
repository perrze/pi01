use cgmath::Rad;

pub static SOCKET_PATH: &str = "hardware.sock";

#[allow(unused)]
#[derive(bytemuck::Zeroable, bytemuck::Pod, Clone, Copy, Debug)]
#[repr(C)]
pub struct TransformData {
    relative_position: [f32; 2],
    relative_rotation: f32,
}

#[allow(unused)]
impl TransformData {
    pub fn new<A: Into<Rad<f32>>>(x: f32, y: f32, r: A) -> TransformData {
        TransformData {
            relative_position: [x, y],
            relative_rotation: r.into().0,
        }
    }

    pub fn to_bytes(&self) -> &[u8] {
        bytemuck::bytes_of(self)
    }

    pub fn from_bytes<'a>(bytes: &'a [u8]) -> TransformData {
        *bytemuck::from_bytes::<TransformData>(bytes)
    }
}
