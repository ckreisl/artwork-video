"""
MIT License

Copyright (c) 2019 Christoph Kreisl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import cv2 as cv
import time
import os
import sys
import signal
import argparse
import threading
import readline
from subprocess import call
# was renamed in python 3 (python 2 Queue)
if sys.version_info[0] < 3:
    import Queue as queue
    from Queue import Queue
else:
    import queue
    from queue import Queue


commands = ["ArtWork", "artwork", "Artwork", "artWork", ".mp4", ".avi", ".mov", ".xml"]


def ArtWorkScriptError(error):
    """
    Dummy error printer
    :param error:
    :return:
    """
    print(error)
    exit(0)


def signal_handler(signum, frame):
    if os.path.exists("frames"):
        call(["rm", "-Rf", "frames"])
    sys.exit()


def completer(text, state):
    options = [x for x in commands if x.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None


def process_frame_queue(path_to_artwork, path_to_xml):
    while True:
        try:
            frameVal = q.get(True, 0.05)
            call(path_to_artwork + " -i " + frameVal + " -o " + frameVal + " " + path_to_xml, shell=True)
            q.task_done()
        except queue.Empty:
            break


if __name__ == '__main__':

    # add signal handler if user exits the script with CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    # add autocomplete to command line arguments
    readline.set_completer(completer)
    readline.parse_and_bind("tab: completer")

    # add argument parser for command line arguments from user
    parser = argparse.ArgumentParser(description="ArtWork-Video-Script: Converts an video into an artwork video.",
                                     epilog="For more information check www.github.com/ckreisl",
                                     conflict_handler="resolve")
    parser.add_argument("-i",
                        metavar="[video]",
                        help="Loads the video from a given file path",
                        required=True,
                        type=str)
    parser.add_argument("-o",
                        metavar="[name]",
                        help="Saves the processed video under the denoted output name",
                        required=True,
                        type=str)
    parser.add_argument("-a",
                        metavar="[artwork]",
                        help="Path to your compiled artwork executable",
                        required=True,
                        type=str)
    parser.add_argument("-s",
                        metavar="[xml]",
                        help="Path to your rendersettings XML file",
                        required=True,
                        type=str)
    parser.add_argument("-p",
                        metavar="[CORES]",
                        help="How many threads should be used (default: 4)",
                        type=int,
                        default=4)
    parser.add_argument("-f",
                        metavar="[FPS]",
                        help="Set FPS for your output video (default: FPS_INPUT_VIDEO)",
                        type=float)
    parser.add_argument("-n",
                        metavar="[FRAME]",
                        help="Convert every N frame only (default: 1 this means convert every single frame)",
                        type=int,
                        default=1)

    # get user input from command line parameters
    args = vars(parser.parse_args())

    (first, second, third) = cv.__version__.split('.')

    # check used OpenCV version
    if int(first) < 3:
        ArtWorkScriptError("OpenCV v." + str(cv.__version__) + " < 3 not supported by this script")

    # check if we are on unix linux system
    if not sys.platform == "linux" and not sys.platform == "linux2":
        ArtWorkScriptError("This script is currently only running with Unix Linux. \n"
              "If you like to change this, let me know or send me a pull request.")

    # parse command line arguments
    NUM_THREADS = args["p"]
    FPS_VIDEO = args["f"]
    N_FRAME = args["n"]
    pathToVideo = args["i"]
    outputName = args["o"]
    pathToArtWork = args["a"]
    pathToXML = args["s"]

    # artwork is in current directory
    if "/" not in pathToArtWork:
        pathToArtWork = "./" + pathToArtWork

    # check given path to ArtWork executable
    if not os.path.isfile(pathToArtWork):
        ArtWorkScriptError("ArtWork executable could not be found in: " + pathToArtWork + " path.")

    # check if video input file exists
    if not os.path.isfile(pathToVideo):
        ArtWorkScriptError("Video file could not be found in: " + pathToVideo + " path.")

    # check if XML file exists
    if not os.path.isfile(pathToXML):
        ArtWorkScriptError("XML file could not be found in: " + pathToXML + " path.")

    # process image and convert frames
    videoIn = cv.VideoCapture(pathToVideo)
    success, image = videoIn.read()

    if not success:
        ArtWorkScriptError("Could not load frame from video")

    # set output fps to input fps
    if FPS_VIDEO is None:
        FPS_VIDEO = videoIn.get(cv.CAP_PROP_FPS)

    # frame width and height
    WIDTH, HEIGHT, LAYERS = image.shape
    LENGTH_VIDEO = videoIn.get(cv.CAP_PROP_FRAME_COUNT) / videoIn.get(cv.CAP_PROP_FPS)

    # python queue for multithreading
    q = Queue()

    print(("Start processing with ... \n"
          "NUM_THREADS:  {} \n"
          "VIDEO_HEIGH:  {} \n"
          "VIDEO_WIDTH:  {} \n"
          "VIDEO_FPS:    {} \n"
          "VIDEO_LENGTH: {} \n"
          "N_FRAME:      {} \n"
          "OUTPUT_NAME:  {}").format(NUM_THREADS, WIDTH, HEIGHT, FPS_VIDEO, LENGTH_VIDEO, N_FRAME, outputName))

    # convert images in multiple threads
    thread_list = []
    for i in range(0, NUM_THREADS):
        t = threading.Thread(target=process_frame_queue, args=(pathToArtWork, pathToXML,))
        t.start()
        thread_list.append(t)

    # create separated folder where frames will be temporarily saved
    if os.path.exists("frames"):
        call(["rm", "-Rf", "frames"])
    call(["mkdir", "frames"])

    path = os.getcwd() + "/frames"
    success = True
    count = 0

    print("Starting saving frames from video and converting them with your ArtWork executable")
    # start timer and add data for multithreading
    start = time.time()
    while success:
        name = "frame%d.png" % count
        cv.imwrite(os.path.join(path, name), image)
        # put work to queue for multithreading
        if count % N_FRAME == 0:
            q.put(os.path.join(path, name))
        success, image = videoIn.read()
        count += 1

    q.join()
    for t in thread_list:
        t.join()
    print("Finished converting ... ")
    image_converting_time = time.time()-start
    print("Processing time artworks-frames [frame->artwork]: {0:.3f}s".format(image_converting_time))

    # convert generated images into video (.avi)
    # VIDEO CODEC CAN BE CHANGED HERE
    # (check if codec is supported by your system)
    # ********************************************
    CODEC_fourcc = cv.VideoWriter_fourcc(*'MJPG')
    # ********************************************
    videoOut = cv.VideoWriter(outputName + ".avi", CODEC_fourcc, FPS_VIDEO, (HEIGHT, WIDTH))

    # reload video
    videoIn.release()
    videoIn = cv.VideoCapture(pathToVideo)
    
    count = 0
    start = time.time()
    while videoIn.isOpened():
        ret, frame = videoIn.read()
        if ret:
            # load manipulated frame and write to video
            frame = cv.imread(os.path.join(path, "frame{}.png".format(count)))
            videoOut.write(frame)
            count += 1
        else:
            break

    video_converting_time = time.time()-start
    print("Processing time artwork-video [frames->video]: {0:.3f}s".format(video_converting_time))
    final_runtime = video_converting_time + image_converting_time
    print("Final runtime {}s for an ({}x{}) video running {}s".format(final_runtime, WIDTH, HEIGHT, LENGTH_VIDEO))

    # clean up, remove all created images
    videoIn.release()
    videoOut.release()
    call(["rm", "-Rf", "frames"])
