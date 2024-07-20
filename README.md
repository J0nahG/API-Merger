# API Merger by J0nahG
A simple user-friendly application to combine multiple external antisnipers into one for an overlay.

## Installation Instructions:

### As executable:
* Find the latest release on the releases page and download API-Merger.exe
* Double click on the executable to run it (yes, it is that simple)

### As source code:
In the directory where you downloaded the source code, create a virtual environment
```shell
python -m venv venv
```

Activate the environment
```shell
venv\Scripts\activate
```

Install the dependencies
```shell
pip install -r requirements.txt
```

#### To run:
* Activate the virtual environment (if not already active)
```shell
venv\Scripts\activate
```
* Run the program
```shell
python main.py
```

## Usage
* Add as many external APIs as you would like by inputting the URL that you would put in your overlay.
* Set custom external antisniper to http://127.0.0.1:8000/cubelify?id={{id}}&name={{name}}&sources={{sources}}
