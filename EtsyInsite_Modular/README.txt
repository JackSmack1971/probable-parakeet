# EtsyInsite 

EtsyInsite is a Python tool that retrieves active listings from an Etsy shop and updates a Google Sheets spreadsheet with relevant information about each listing. The tool is divided into five modules designed to work together synergistically: `etsy_api_wrapper.py`, `data_processing.py`, `main.py`, `google_sheets_integration.py`, and `EtsyInsite_GUI.py`. 

## Installation 

To install EtsyInsite, you need to follow these steps: 

1. Clone the EtsyInsite repository: 

git clone https://github.com/<username>/EtsyInsite.git


2. Navigate to the project directory: 

cd EtsyInsite


3. Install the required Python packages: 

pip install -r requirements.txt


4. Create a `config.ini` file with your Etsy API key, shop ID, Google Sheets credentials file path, and Google Sheets spreadsheet ID: 

[ETSY] API_KEY=<your Etsy API key> SHOP_ID=<your Etsy shop ID> 

[SHEET] service_account_file=<path to your Google Sheets credentials file> spreadsheet_id=<your Google Sheets spreadsheet ID>


## Usage 

To use EtsyInsite, you can either run the `main.py` script from the command line with the path to your `config.ini` file as an argument, or run the `EtsyInsite_GUI.py` script to use the graphical user interface. 

## License 

`EtsyInsite` is licensed under the MIT License. See the `LICENSE` file for details. 

## Contributing 

We welcome contributions to `EtsyInsite`! If you'd like to contribute, please follow these steps: 

1. Fork the `EtsyInsite` repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes and add tests if necessary.
4. Make sure all tests pass (`pytest`).
5. Create a pull request with a description of your changes. 

We'll review your pull request as soon as possible. 

## Support 

If you encounter any issues while using `EtsyInsite`, please open an issue on the `EtsyInsite` GitHub repository. We'll do our best to help you out as soon as possible. 

## Credits 

`EtsyInsite` was created by Jack Smack. 

## Contact 

If you have any questions about `EtsyInsite`, please contact jack smack at jacksmack@artofficialintelligence.store

