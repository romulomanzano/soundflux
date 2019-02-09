import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


import smbus
import time
def warn(*args, **kwargs):
        pass
import warnings
warnings.warn = warn
import librosa
import soundfile
import feature_generation as fg

def test_time_load(file_name='/home/pi/github/falldetection/tests/wav/hello.wav'):
    start = timeit.default_timer()
    #loading
    samples, sample_rate = soundfile.read(file_name)
    features = fg.extract_spectrogram(samples,sample_rate)
    features.shape
    #time
    stop = timeit.default_timer()
    print('Time with pythonspeech ', stop - start)
    #less than a second
    assert stop - start < 1

def test_accelerometer_read():
    # Distributed with a free-will license.
    # Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
    # ADXL345
    # This code is designed to work with the ADXL345_I2CS I2C Mini Module available from ControlEverything.com.
    # https://www.controleverything.com/content/Accelorometer?sku=ADXL345_I2CS#tabs-0-product_tabset-2

    # Get I2C bus
    bus = smbus.SMBus(1)

    # ADXL345 address, 0x53(83)
    # Select bandwidth rate register, 0x2C(44)
    #		0x0A(10)	Normal mode, Output data rate = 100 Hz
    bus.write_byte_data(0x53, 0x2C, 0x0A)
    # ADXL345 address, 0x53(83)
    # Select power control register, 0x2D(45)
    #		0x08(08)	Auto Sleep disable
    bus.write_byte_data(0x53, 0x2D, 0x08)
    # ADXL345 address, 0x53(83)
    # Select data format register, 0x31(49)
    #		0x08(08)	Self test disabled, 4-wire interface
    #					Full resolution, Range = +/-2g
    bus.write_byte_data(0x53, 0x31, 0x08)

    time.sleep(0.5)

    # ADXL345 address, 0x53(83)
    # Read data back from 0x32(50), 2 bytes
    # X-Axis LSB, X-Axis MSB
    data_0 = bus.read_byte_data(0x53, 0x32)
    data_1 = bus.read_byte_data(0x53, 0x33)

    # Convert the data to 10-bits
    x_accl = ((data_1 & 0x03) * 256) + data_0
    if x_accl > 511:
        x_accl -= 1024

    # ADXL345 address, 0x53(83)
    # Read data back from 0x34(52), 2 bytes
    # Y-Axis LSB, Y-Axis MSB
    data_0 = bus.read_byte_data(0x53, 0x34)
    data_1 = bus.read_byte_data(0x53, 0x35)

    # Convert the data to 10-bits
    y_accl = ((data_1 & 0x03) * 256) + data_0
    if y_accl  > 511:
        y_accl -= 1024

    # ADXL345 address, 0x53(83)
    # Read data back from 0x36(54), 2 bytes
    # Z-Axis LSB, Z-Axis MSB
    data_0 = bus.read_byte_data(0x53, 0x36)
    data_1 = bus.read_byte_data(0x53, 0x37)

    # Convert the data to 10-bits
    z_accl = ((data_1 & 0x03) * 256) + data_0
    if z_accl > 511:
        z_accl -= 1024

    # Output data to screen
    print("Acceleration in X-Axis : %d" % x_accl)
    print("Acceleration in Y-Axis : %d" % y_accl)
    print("Acceleration in Z-Axis : %d" % z_accl)

if __name__ == '__main__':
    arg = sys.argv[1]
    if arg == "test_sound_recording":
        file = sys.argv[2]
        test_time_load(file)
    if arg == "test_accelerometer_read":
        test_accelerometer_read()
