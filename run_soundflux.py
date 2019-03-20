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
    feature_queue = Queue()
    # Instantiate shared memory signals
    go = Value('i', 1)

    # Define processes
    processes = {
        "data_capturer":
        Process(target=data_capture_worker, args=(mic, acc, sound_queue, go,)),
        "feature_extractor":
        Process(target=extract_features_worker, args=(sound_queue, go, save_spectrograms))
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
