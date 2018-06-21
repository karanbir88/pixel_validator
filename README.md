# TL Impression Pixel Validator

A simple script to test a number of impression_pixels to ensure validity

## Preparation & running the script

1. Ensure your incoming file has a header row, specifying a "tactic_id" column and an "impression_pixel_json" column
2. Remove duplicate combinations of tactic_id and impression_pixel_json beforehand
3. Install the requirements with pip install -r requirements.txt
4. Run the script as "python pixel_validator.py <tactic_file.csv>"
5. Turn on logging debug mode to diagnose any issues

## Running the tests

In order to run the tests, you must ensure you test against the original tactic_sample.csv file. As long as it's in the same directory, run the test with:

python tests.py

### Break down into end to end tests

The test essentially ensures that the ReadFile method is creating the list of dictionaries in the required format. It does NOT test the pixels itself
