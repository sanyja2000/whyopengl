# whyopengl - a basic opengl based game engine
A simple opengl project created in python.

# Installation

Packages needed to install:

```pip install numpy Pillow pyrr pyaudio```

If pyaudio doesn't install you can try installing it via pipwin:
```
pip install pipwin
pipwin install pyaudio
```

## On linux
For glut to work you might need to install freeglut3-dev:
```sudo apt-get install freeglut3-dev```

After that you have to install 2 more packages via pip:
```pip install PyOpenGl PyOpenGl_accelerated```

Now you should be able to run the project.

## On Windows
For glut to work you need to download and install PyOpenGl and PyOpenGl-accelerate from one of the Unofficial Windows Binaries for Python Extension Packages websites (link for one: https://www.lfd.uci.edu/~gohlke/pythonlibs/).

After downloading you have to install the downloaded wheel files with:

`pip install PyOpenGL-3.1.5-cp38-cp38-win_amd64.whl` - for Python 3.8

`pip install PyOpenGL_accelerate-3.1.5-cp38-cp38-win_amd64.whl` - for Python 3.8

Now you should be able to run the project.
