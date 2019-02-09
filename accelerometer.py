from config import *
import smbus
import timeit
import time

class Accelerometer(object):
    """
    Inspired in https://github.com/xto-b/vibration/blob/master/adxl345.py
    """
    def __init__(self, address=0x53):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.set_bandwidth_rate(ACC_BW_RATE_1600HZ)
        self.set_range(ACC_RANGE_4G)
        self.enable_measurement()

    def enable_measurement(self):
        self.bus.write_byte_data(self.address, ACC_POWER_CTL, ACC_MEASURE)

    def set_bandwidth_rate(self, rate_flag):
        self.bus.write_byte_data(self.address, ACC_BW_RATE, rate_flag)

    def set_range(self, range_flag):
        """
        set the measurement range for 10-bit readings
        :param range_flag:
        :return:
        """
        value = self.bus.read_byte_data(self.address, ACC_DATA_FORMAT)
        value &= ~0x0F;
        value |= range_flag;
        value |= 0x08;

        self.bus.write_byte_data(self.address, ACC_DATA_FORMAT, value)

    def get_axes(self, gforce=False, apply_scaler=False):
        """
        Returns the current reading from the sensor for each axis

        :param gforce:
            False (default): result is returned in m/s^2
            True           : result is returned in gs
        :param apply_scaler:
            False (default): result is scaled down
            True           : result is returned in gs
        :return: dict
        """

        bytes = self.bus.read_i2c_block_data(self.address, ACC_AXES_DATA, 6)

        x = bytes[0] | (bytes[1] << 8)
        if (x & (1 << 16 - 1)):
            x = x - (1 << 16)

        y = bytes[2] | (bytes[3] << 8)
        if (y & (1 << 16 - 1)):
            y = y - (1 << 16)

        z = bytes[4] | (bytes[5] << 8)
        if (z & (1 << 16 - 1)):
            z = z - (1 << 16)

        if apply_scaler:
            x = x * ACC_SCALE_MULTIPLIER
            y = y * ACC_SCALE_MULTIPLIER
            z = z * ACC_SCALE_MULTIPLIER

        if gforce == False:
            x = x * ACC_EARTH_GRAVITY_MS2
            y = y * ACC_EARTH_GRAVITY_MS2
            z = z * ACC_EARTH_GRAVITY_MS2

        return {"x": x, "y": y, "z": z}

    def capture_x_seconds(self,seconds,gforce=True, apply_scaler=True,sample_frequency_hertz=1000):
        start = timeit.default_timer()
        frames = []
        while (timeit.default_timer() - start) <= seconds:
            # Read data from device
            axis = self.get_axes(gforce=gforce,apply_scaler=apply_scaler)
            frames.append(axis)
            time.sleep(1.0 / sample_frequency_hertz)
        return frames