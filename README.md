# pycat-demo

This is a simple plotly/dash demo that is relevant to pyCAT.  It just reads in a series of 10 stereo images and plots them.  Interactivity is added by means of a slider to toggle through the images and a drop-down menu to select the color scale.

The instructions for running this application on your own system are as follows.

Step 1: clone the repository
----------------------------

Clone this repository to your computer and enter the directory as follows:

```bash
git clone https://github.com/mmiesch/pycat-demo
cd pycat-demo
```

Throughout these instructions, this will be referred to as the root directory for the pycat-demo application.

Step 2: Install dependencies
----------------------------

This is probably easiest if you create a python virtual environment.

From the root directory, enter (this assumes that your default python is python3):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Step 3: Download test data
--------------------------

Ten arbitrary, processed coronagraph images from the COR2 detector on STEREO-A have been made available [in this google drive folder](https://drive.google.com/drive/u/1/folders/1Lb0Z_u7U1rSMKnE5qcFP-U_DHr0VPfpS) as fits files.

From the root directory, create a subdirectory called `data` and put the stereo test files there.

Note: Users outside of NOAA may have to request access to this folder.

Step 4: Run the application
---------------------------

To run the application, enter, e.g. (this is for app3.py - execute the other numbered apps in a similar way):

```bash
python app3.py
```

If it's running correctly, you should see a message that reads something like this:

```bash
Dash is running on http://127.0.0.1:8050/
```

Open this link in a browser and you should be all set to play around with it.

To exit the application at any time, enter `Ctrl-c` in the window where you started the application.
