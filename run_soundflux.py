from multiprocessing import Process, Queue, Value

from accelerometer import Accelerometer
from soundflux import SoundFlux
from workers import *


def run(save_spectrograms=True):

    # Instantiate Devices
    mic = SoundFlux(live_feed=True)
    acc = Accelerometer()

    # Instantiate Queues
    sound_queue = Queue()
    accelerometer_queue = Queue()
    # Instantiate shared memory signals
    go = Value('i', 1)

    # Define processes
    processes = {
"""        "sound_data_capturer":
        Process(target=audio_capture_worker, args=(mic,sound_queue, go,)),
        "sound_feature_extractor":
        Process(target=extract_audio_features_worker, args=(sound_queue, go,True)),
        """
        "acc_data_capturer":
        Process(target=vibration_capture_worker, args=(acc,accelerometer_queue, go,)),
        "acc_feature_extractor":
        Process(target=extract_vibration_features_worker, args=(accelerometer_queue, go,False))
        }

    # Start processes as daemons
    for process in processes.keys():
        processes[process].daemon = True
        processes[process].start()

    # Listen for entry in stdin to stop pipeline
    input("Listening and running inference... Enter any value to stop the pipeline: ")
    go.value = 0
    print("Pipeline finishing...")
    for process in processes.keys():
        processes[process].join()
    print("Pipeline complete!")

if __name__ == '__main__':
    run()
