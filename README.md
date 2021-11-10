# ReadalongsDesktop
![python badge](https://img.shields.io/badge/python-3.7-blue) 
![gui](https://img.shields.io/badge/GUI-qtpy-green)
![license badge](https://img.shields.io/github/license/tobyatgithub/ReadalongsDesktop)

This library is a desktop app with GUI for the [readalongs studio](https://github.com/ReadAlongs/Studio) project.  
Readalongs is an audiobook alignment tool for indigenous language.

## Table of Contents

- [Readalongs Desktop](#ReadalongsDesktop)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Install](#Install)
  - [Usage](#Usage)
  - [License](#License)

## Background

A desktop version of readalongs is developed in order to overcome these three main challenges:

1. Direct users may not be familiar with Linux/Unix, Python, and Docker technologies (e.g. we shall not require users to understand how to use terminal to use this app.)
2. Users may have limited access to the internet.
3. Communities would prefer to perform tasks offline. (data privacy)

As a result, this desktop version of readalong will allow users to perform tasks by clicks, and support all functionalities without needing the internet.

## Install

### 0. (Optional) Create a conda env, notice that python version has to be >= 3.7

```bash
# create
conda create --name readalongsDesktop python=3.7

# activate
source activate readalongsDesktop
```

### 1. Git clone and install packages

```bash
git clone https://github.com/tobyatgithub/ReadalongsDesktop.git
cd ReadalongsDesktop
pip install -r requirements.txt
```

### 2. Pick a Qt library to install:

For licensing reason, the user will need to pick their own qt library to install in the same python environment, the common options are pyqt4, pyqt5, pyside2, and pyside6.

For example, you can install pyqt5 with:

```bash
pip install PyQt5
```

At this point, you shall be able to run the GUI app on your local machine with:

```bash
python desktopapp.py
```

(To test:) user may need to install `g2p`, `Studio`, and `SoundSwallower` in the same root directory to make it work.

### 3. Package this app with pyinstaller to distribute

In the `ReadalongsDesktop` folder, install the `pyinstaller` and run the following command (depends on windows/mac)

```bash
pip install pyinstaller
```

Notice we will need to use different command on windows vs. mac. On windows (to test):

```bash
pyinstaller desktopApp.py --add-binary ../g2p/g2p/mappings/langs/langs.pkl:g2p/mappings/langs --add-binary ../g2p/g2p/mappings/langs/network.pkl:g2p/mappings/langs --add-binary ../SoundSwallower:SoundSwallower
```

On mac (tested on intel chip):

```
pyinstaller desktopApp.py --add-data ../g2p/g2p/mappings/langs/langs.pkl:g2p/mappings/langs --add-data ../g2p/g2p/mappings/langs/network.pkl:g2p/mappings/langs --add-data ../SoundSwallower:SoundSwallower
```

Then, go to -> dist -> desktopApp. You shall find an executable file named as `desktopApp`

Double click on the `desktopApp` executable (wait for a little while) and you shall see the GUI.

PS: For mac m1 users, you may need to install upx first

https://macappstore.org/upx/

```bash
arch -arm64 brew install --build-from-source upx
```

## Usage

In this repo, we also included a small example to run:

1. Start the Desktop app via terminal

```bash
python desktopApp.py
```

2. Run with provided testing file:

- click the first "Browse" button to upload the sample txt file `1.Welcome.txt`
- click the second "Browse" button to upload the sample audio file `1.Welcome.mp3`
- select `iku` as the mapping from the drop done, click "Confirm"
- click "Next Step"
- Open a browser and go to `http://localhost:7000/`

3. Exit (need fix) by hit control-C in terminal

## License
