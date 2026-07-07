# Grimoire
A D&D 5e tool to generate spellbook pages.

## Setup
Using Python 3.11 or higher, create a virtual environment and install the dependencies:
```py
git submodule update --init

python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

This project uses WeasyPrint to generate PDFs. You may need to install additional dependencies for WeasyPrint to work properly. Please refer to the [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for your operating system.

## Running
Use the following commands to activate the virtual environment and run the program:
```py
source venv/Scripts/activate
python grimoire
```