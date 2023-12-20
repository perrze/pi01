use pwm_pca9685::{Address, Pca9685};

pub fn init_motors() {
    let dev = I2cdev::new("/dev/i2c-1").unwrap();
    let address = Address::default();
    let mut pwm = Pca9685::new(dev, address).unwrap();
    pwm.set_prescale(100).unwrap();
    pwm.set_mode();
    pwm.enable().unwrap();

    // Turn on channel 0 at 0 and off at 2047, which is 50% in the range `[0..4095]`.
    pwm.set_channel_on_off(Channel::C0, 0, 2047).unwrap();

    // Turn on channel 1 at 200, then off at 3271. These values comes from:
    // 0.000814 (seconds) * 60 (Hz) * 4096 (resolution) = 200
    // 4096 * 0.75 + 200 = 3272
    pwm.set_channel_on_off(Channel::C1, 200, 3272).unwrap();
}
