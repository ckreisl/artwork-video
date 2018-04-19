# **Artwork-Video Script**
This Python script uses the [ArtWork](https://github.com/ckreisl/artwork) executable to convert a normal video into an artwork video. The rendering time depends on the video length, the frame size and the render settings which are set in the XML file.

The output is an `.avi` video encoded with `MJPG`. The video codec can be changed within the script in line **172**. OpenCV can use any codec provided by [FOURCC](http://www.fourcc.org/codecs.php), but at least you have to install the correct libraries to encode your video.

At this time this script **only** runs on Unix / Linux systems (tested on Ubuntu 16.04, 04/19/2018).

<center>
![Example](gif/example.gif)
</center>

## Dependencies
* [Python](https://www.python.org/) (version 3.5)
* [OpenCV](https://opencv.org/) (version 3.4.0)

## Usage
As said above, at this time this script is only implemented for Unix / Linux systems. If you like to extend this script for other operating systems just send me a pull request.
### Linux
The script runs via command line. With `python3.5 artworkvideo.py -h` you get the following help message.

```
artworkvideo.py [-h] -i [video] -o [name] -a [artwork] -s [xml]
                       [-p [CORES]] [-f [FPS]] [-n [FRAME]]

ArtWork-Video-Script: Converts an video into an artwork video.

optional arguments:
  -h, --help    show this help message and exit
  -i [video]    Loads the video from a given file path
  -o [name]     Saves the processed video under the denoted output name
  -a [artwork]  Path to your compiled artwork executable
  -s [xml]      Path to your rendersettings XML file
  -p [CORES]    How many threads should be used (default: 4)
  -f [FPS]      Set FPS for your output video (default: FPS_INPUT_VIDEO)
  -n [FRAME]    Convert every N frame only (default: 1 this means convert
                every single frame)

For more information check www.github.com/ckreisl
```

The first four parameters **-i, -o, -a, -s** are required to run the script.

Converting the frames into artworks is running in multiple threads. The amount of used threads can be modified with the **-p** argument. In Addition you can set the frame rate [FPS] of your generated output video with **-f**. At least you can set which frames should be converted into artworks. This is possible with the **-n** parameter. This gives a flickering effect between original video frame and the converted frame.
### Windows
(maybe coming soon)
### MacOS
(maybe coming soon)

## Status
Copyright (c) Christoph Kreisl
