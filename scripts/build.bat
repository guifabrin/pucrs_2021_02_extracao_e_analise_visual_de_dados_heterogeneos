cd ..
pyinstaller --onefile .\fetch_and_store.py --paths .\libs
pyinstaller --onefile .\scrapper_selenium.py --paths .\libs