[![Travis Build Status][travis_img]][travis]


Gretacierge
=========
![catcierge](https://raw.githubusercontent.com/JoakimSoderberg/catcierge-examples/master/diy/small_logo.jpg)

Gretacierge is a fork of the [catcierge][catcierge]-project, developed by Joakim Soderberg. 

Our cat (named Greta) is quite a talented hunteress and every new prey brought home brings some
new troubles into our family...
  
Thanks to him and his fabulous project, Greta can kill the whole population of huntable animals - my wife
doesn't have to bother about...

I modified some parts to make it fit into my enviroment. For further informations about
the original project see [catcierge][catcierge].

Build status
------------

| Service               | Status                                                                                                                                                     |
|-----------------------|----------------------------------------------------------|
| Travis-CI (Linux/OSX) | [![Travis Build Status][travis_img]][travis]             |

Background
----------
The [Catcierge][catcierge] project came about to solve the problem of our cat having the
nasty habit of delivering "gifts" through our cat door in the form
of dead, or partly dead / fully alive rodents or birds.

Instead of simply not allowing our cat to use the cat door like normal people
I of course set out to find a high-tech solution to solve my perdicament.

I found the [Flo Control project][flo_control] project and based the general idea
on that setup (detecting prey based on the cats head profile).

The first implementation used a simple template matching technique, but after
evaluating that for a while I realised a better solution was needed.
Instead I trained a Haar Cascade recognizer to find the cats head, and then
used various other techniques to detect if it has prey in it's mouth or not.
This technique has turned out to be very reliable and successful with
hardly any false positives. The training data and results for the Haar cascade
training can be found in a separate repository
[https://github.com/JoakimSoderberg/catcierge-samples](catcierge-samples)

Hardware design details
-----------------------
To read more about how to build your own hardware that this code can run on, and the development story, see the webpage: [http://joakimsoderberg.github.io/catcierge/](http://joakimsoderberg.github.io/catcierge/)

Dependencies
------------
For the image recognition catcierge uses OpenCV via the
[raspicam_cv library][raspicam_cv] written by [Emil Valkov][emil_valkov]
(which is included in the catcierge source).

Full getting started guide for Raspberry Pi
-------------------------------------------
See [doc/](doc/README.md) for a full getting started guide.

Compiling
---------
Catcierge uses the CMake build system. To compile:

### Raspberry Pi:

First, to install OpenCV on raspbian:

```bash
$ sudo apt-get install cmake libopencv-dev build-essential
```

Then to build:

```bash
$ git clone https://github.com/katerasrael/gretacierge.git
$ cd gretacierge
$ git submodule update --init # For the included repositories sources.
### $ ./build_userland.sh
### get userland
$ cd ..
$ git clone https://github.com/raspberrypi/userland.git
$ cd userland
$ sh ./buildme
$ cd ../gretacierge
$ mkdir build && cd build
$ cmake .. -DRPI_USERLAND=/home/shares/users/userland -DWITH_ZMQ=OFF -DWITH_RFID=OFF -DCATCIERGE_WITH_MEMCHECK=OFF -DCATCIERGE_COVERALLS_UPLOAD=OFF -DGPIO_NEW=ON -DROI_DELTA=ON # Raspbian has no CZMQ package.
$ make
```

For the use of [pigpio](https://github.com/joan2937/pigpio)-support use:

```bash
$ sudo apt-get install pigpio
```

Add -DGPIO_NEW=ON (default is ON) to the cmake args. Turn it OFF, to get back to the original GPIO-handling.

 


If you want ZMQ support:

```bash
$ sudo apt-get install libzmq3-dev
```

```bash
$ git clone git@github.com:zeromq/czmq.git
$ cd czmq
$ mkdir build
$ cd build
$ cmake ..
$ make
$ make install  # either this, or see below

# Or specify the locations manually where you built it.
$ cmake -DWITH_ZMQ=ON -DCZMQ_LIBRARIES=/path/to/czmq/src/libczmq.so -D CZMQ_INCLUDE_DIRS=/path/to/czmq/include ..
```

If you don't have any [RFID cat chip reader][rfid_cat] you can exclude
it from the compilation:

```bash
$ cmake -DWITH_RFID=OFF ..
```

If you already have a version of the [raspberry pi userland libraries][rpi_userland] built,
you can use that instead:

```bash
$ cmake -DRPI_USERLAND=/path/to/rpi/userland ..
```

However, note that the program only has been tested with the submodule version of
the userland sources.

### Linux / OSX

Use your favorite package system to install OpenCV.

You can also use your own build of OpenCV when compiling:

from git [https://github.com/itseez/opencv](https://github.com/itseez/opencv)

or download: [http://opencv.org/downloads.html](http://opencv.org/downloads.html)

```bash
$ git clone <url>
$ cd catcierge
$ mkdir build && cd build
$ cmake --build .
```

If OpenCV is not automatically found, build your own (See above for downloads)
and point CMake to that build:

```bash
... # Same as above...
$ cmake -DOpenCV_DIR=/path/to/opencv/build .. # This should be the path containing OpenCVConfig.cmake
$ cmake --build .
```

### Windows

Download OpenCV 2.x for Windows: [http://opencv.org/downloads.html](http://opencv.org/downloads.html)

Unpack it to a known path (you need this when compiling).

Assuming you're using [git bash](http://git-scm.com/) and [Visual Studio Express](http://www.visualstudio.com/downloads/download-visual-studio-vs) (or more advanced version).

**NOTE**: If you are using Visual Studio 2015+ at the time of writing this, the precompiled
version of OpenCV does not include a compatible version, so you will need to build it yourself:

```bash
$ cd /c/opencv-2.4.13
$ mkdir build_static && cd build_static  # Another build directory already exists.
$ cmake -DBUILD_SHARED_LIBS=OFF ../sources  # We want static so we don't have to copy DLLs around.
$ cmake --build .  # This takes a long time :)
```

Then compile catcierge itself (note use the correct build directory below if you built OpenCV yourself).

```bash
$ git clone <url>
$ cd catcierge
$ mkdir build && cd build
$ cmake -DOpenCV_DIR=/c/PATH/TO/OPENCV/build_static .. # The OpenCV path must contain OpenCVConfig.cmake
$ cmake --build .     # Either build from command line...
$ start catcierge.sln # Or launch Visual Studio and build from there...

$ ctest # Run all tests
        # If all these fail with OTHER_FAULT you have probably not linked statically
        # and it is not finding the DLLs in the build directory.
        # Run command below to get proper error messages.
$ bin/catcierge_regress # Run the raw test executable without ctest involved.
```

Running the main program
------------------------
The main program is named [catcierge_grabber](src/catcierge_grabber.c) which
performs all the logic of doing the image recognition, RFID detection and
deciding if the door should be locked or not.

For more help on all the settings:

```bash
$ ./catcierge_grabber --help
```

Test programs
-------------
While developing and testing I have created a few small helper programs.
See `--help` for all of these.

### Finite State Machine (FSM) Tester ###

This program tests the entire matching sequence as if it was fully running,
except that you only feed it with 4 input images, instead of it using the
camera image live like [catcierge_grabber](src/catcierge_grabber.c).

This is what you want to use most of the time. It can output full debug images
of each step of the matching algorithms.

```bash
$ catcierge_fsm_tester --haar --cascade /path/to/catcierge.xml --images 01.png 02.png 03.png 04.png --save_steps
```

### Image recognition ###

To test the image recognition there is a test program
[catcierge_tester](src/catcierge_tester.c) that allows you to specify an image
to match against. This ONLY tests the image recognition part.

Haar matcher:

```bash
$ catcierge_tester --haar --cascade /path/to/catcierge.xml --images *.png --show
```

Template matcher (this is inferior to the haar matcher):

```bash
$ catcierge_tester --templ --snout /path/to/image/of/catsnout.png --images *.png --show
```

### RFID ###

Likewise for the RFID matching:

```bash
$ catcierge_rfid_tester
```

### Background ###

Stop the catcierge-service

```bash
$ systemctl stop catcierge
```

First of all, capture a image via (use the right rotation that fits your situation!) with --width and --height set, otherwise the rapsi is quite slow trying to calculate and display the found borders:

```bash
$ raspistill --rotation 90 --width 320 --height 240 --output bg_test_image.png
```

There is a program that helps you tweak background settings:

```bash
$ catcierge_bg_tester --interactive bg_test_image.png
```

With the found threshhold (in example: 123) start the catcierge_grabber-command

```bash
$ catcierge_grabber --auto_roi --save_auto_roi outimage.png --auto_roi_thr 123
```

Watch the output, the obstruction region of interest will be displayed (eg x: 2 y: 25 w: 312 h: 144). Put these values in the config file

roi=2	#x  
roi=25	#y  
roi=312	#width  
roi=144	#height  


Start the catcierge-service

```bash
$ systemctl start catcierge
```


Testing
----------

```bash
$ export DISPLAY=:10.0; sudo ./build/bin/catcierge_grabber --show --highlight
```

Prototypes
----------

**!Note! The below prototype is quite outdated. For the Haar cascade matcher the
prototype can be found in the [catcierge-samples][catcierge_samples] repository.**

These are prototypes written in Python. The Python and C versions of OpenCV
behaves slightly differently in some cases.

To test different matching strategies there's a Python prototype as well
in the aptly named "protoype/" directory. The prototype is named after my
cat [higgs.py](prototype/higgs.py). This was the first prototype used to
create the Template matcher technique.

It has some more advanced options that allows you to create montage
pictures of the match result of multiple images. This was used to
compare the result of different matching strategies during development.

For this to work you will need to have [ImageMagick][imagemagick] installed.
Specifically the program `montage`.

```bash
$ cd prototype/
$ python higgs.py --help
```

Test a load of test images and create a montage from them using two
snout images to do the match:
(Note that it is preferable if you clear the output directory before
creating the montage, so outdated images won't be included).

```bash
$ rm -rf <path/to/output> # Clear any old images.
$ python higgs.py --snout snouts/snout{1,2}.png --output <path/to/output> --noshow --threshold 0.8 --avg --montage
```

### OpenCV/Python in Docker ###
If you don't have a Python + OpenCV setup ready on your computer I would recommend
you use docker. Here's an example where I mount the `catcierge-examples/` images
so they could be passed to the script.

```bash
$ docker run
    -v $PWD:/app
    -v ~/dev/catcierge/examples:/examples
    ibotdotout/python-opencv
    python find_backlight.py --threshold 140 /examples/some/image.png
```

[catcierge]: https://github.com/JoakimSoderberg/catcierge
[imagemagick]: http://www.imagemagick.org/
[flo_control]: http://www.quantumpicture.com/Flo_Control/flo_control.htm]
[raspicam_cv]: https://github.com/robidouille/robidouille/tree/master/raspicam_cv
[emil_valkov]: http://www.robidouille.com/
[rfid_cat]: http://www.priority1design.com.au/shopfront/index.php?main_page=product_info&cPath=1&products_id=23
[rpi_userland]: https://github.com/raspberrypi/userland
[catcierge_samples]: https://github.com/JoakimSoderberg/catcierge-samples

[travis_img]: https://travis-ci.org/katerasrael/gretacierge.svg?branch=master
[travis]: https://travis-ci.org/JoakimSoderberg/catcierge
