ImageScraper
ImageScraper is a Python script for scraping and downloading images from a search query on a website.

Usage
Install the necessary packages by running pip install -r requirements.txt.
Replace "https://www.examplegallery.com" in the ImageScraper constructor with the URL of the website to be scraped.
Execute the run() method of the ImageScraper instance.
The script will open a GUI for the user to input their search query and other parameters.
Once the user clicks the "Search" button, the script will scrape the images, navigate through the search results pages, and download the images asynchronously.
The progress of the download will be displayed in a progress bar. If any errors occur, a message box will be displayed with an error message.
Requirements
The following packages are required:

aiohttp==3.7.4
beautifulsoup4==4.9.3
selenium==3.141.0
Note that Tkinter is included in the standard Python library and does not need to be installed separately.

Contributing
Contributions to this project are welcome. You can contribute by submitting bug reports, feature requests, or pull requests. Please ensure that your code adheres to the PEP 8 style guide.

License
This project is licensed under the MIT License. See the LICENSE file for more information.
