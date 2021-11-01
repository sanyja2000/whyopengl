# whyopengl - a basic opengl based game engine
A simple opengl project created in python.

# Installation

The project requires Python 3.6 or newer.

Packages needed to install:

```pip install numpy Pillow pyrr pyaudio```

If the command above fails, you have to run the command again, and try to install pyaudio with pipwin:
```
pip install numpy Pillow pyrr
pip install pipwin
pipwin install pyaudio
```

### On Linux
For glut to work you might need to install freeglut3-dev:

```sudo apt-get install freeglut3-dev```

After that you have to install 2 more packages via pip:

```pip install PyOpenGl PyOpenGl_accelerated```

Now you should be able to run the project.

### On Windows
For glut to work you need to download and install PyOpenGl and PyOpenGl-accelerate from one of the Unofficial Windows Binaries for Python Extension Packages websites
(link for one: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl).

Once you have downloaded the files for your respective python version, you have to install the downloaded wheel files with:

`pip install PyOpenGL-3.1.5-cp38-cp38-win_amd64.whl` - for Python 3.8, change file to the downloaded

`pip install PyOpenGL_accelerate-3.1.5-cp38-cp38-win_amd64.whl` - for Python 3.8, change file to the downloaded

Now you should be able to run the project.

### To run the project
For now, start 
```python prototype2.py```