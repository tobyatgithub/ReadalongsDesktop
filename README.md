# ReadalongsDesktop

This library is a desktop app with GUI for the [readalongs studio](https://github.com/ReadAlongs/Studio) project.  
Readalongs is an audiobook alignment tool for indigenous language.

## Table of Contents

- [Readalongs Desktop](#ReadalongsDesktop)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)

## Background

A desktop version of readalongs is developed in order to overcome these three main challenges:

1. Direct users may not be familiar with Linux, Python, and Docker.
2. Users may have limited access to the internet
3. Communities would prefer to proform tasks offline. (data privacy)

As a result, this desktop version of readalong will allow users to perform tasks by clicks, and support all functionalities without needing the internet.

## Install

0. (Optional) Create a conda env, notice that python version has to be >= 3.7

```bash
# create
conda create --name readalongsDesktop python=3.7

# activate
source activate readalongsDesktop
```

1. Install packages

```bash
pip install -r requirements.txt
```

2. (TODO: need fix) package with pyinstaller to distribute
   (fixed g2p pkl missing)
   (soundswallower not working for now.)

```bash
pip install pyinstaller
pyinstaller desktopApp.py --add-binary ../g2p/g2p/mappings/langs/langs.pkl:g2p/mappings/langs --add-binary ../g2p/g2p/mappings/langs/network.pkl:g2p/mappings/langs

pyinstaller desktopApp.py --add-data ../g2p/g2p/mappings/langs/langs.pkl:g2p/mappings/langs --add-data ../g2p/g2p/mappings/langs/network.pkl:g2p/mappings/langs --add-data ../SoundSwallower/model/en-us/mdef:/SoundSwallower/model/en-us
```

To see the error code:

```bash
#go to -> dist -> desktopApp -> desktopApp (executable)
cd dist/desktopApp
```

Double click on the `desktopApp` executable (wait for 20-30 seconds) and you will see the running results (rihgt now it shows can not find the g2p mapping file)

## Usage

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
