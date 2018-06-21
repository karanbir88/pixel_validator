#! /usr/bin/python

import requests
import sys
from datetime import datetime
import logging
import traceback
from unidecode import unidecode
import csv
import ast
import re

# Standard Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s(%(lineno)s) - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
headers = {
    'Cache-Control': "no-cache",
    'Postman-Token': "1777e1b4-89af-496c-ba7f-3bcf84d5427a"
}

# Output file naming convention
output_file = 'bad_pixels_report_%s.txt' % datetime.now()


def chkInput():
    # Validate input should match format "python pixel_validator.py
    # <tactic_file.csv"
    if len(sys.argv) != 2:
        logger.error(
            'Incorrect usage. Should be "python pixel_validator.py <tactic_file.csv>". Try again?')
        return False
    elif '.csv' not in sys.argv[1]:
        logger.error('Invalid file provided. Must be a CSV')
        return False
    else:
        return True


def readFile(file):
    # Finds the tactic_id and impression_pixel_json columns, and returns a
    # list of dictionaries, that are keyed off the tactic-id and represent the
    # list of pixels for a tactic. Also, returns the total number of pixels to
    # be tested
    f = csv.reader(open(file, 'rU'))
    tactic_data = []
    pixel_count = 0
    for (i, line) in enumerate(f, 1):
        logger.debug('Line # %d is %s', i, str(line))
        # Find impression_pixel_json column
        if i == 1:
            if ('tactic_id' not in line) or ('impression_pixel_json' not in line):
                logger.error(
                    'Could not find Tactic ID and/or Impression Pixel columns. Please check the file headers and try again.')
                return False
            else:
                tactic_col = line.index('tactic_id')
                pixel_col = line.index('impression_pixel_json')
        # Create list of dictionaries of tactic_id:[list of impression_pixels]
        else:
            tactic = {}
            tactic_id = int(line[tactic_col])
            pixel_list = []
            if not line[pixel_col] == 'NULL':
                try:
                    pixel_list = ast.literal_eval(line[pixel_col])
                except Exception as e:
                    logger.info(
                        'Found an incorrectly formatted pixel. Skipping tactic %d with pixels %s', tactic_id, line[pixel_col])
                pixel_count += len(pixel_list)
            tactic[tactic_id] = pixel_list
            tactic_data.append(tactic)
            logger.debug(tactic)
        logger.debug(tactic_data)
    return (tactic_data, pixel_count)


def collectTrash(bad_pixel):
    # Writes the output of bad tactic-pixel mappings in dictionary format to a
    # txt file
    log = open(output_file, "a+")
    log.write(str(bad_pixel))


def main():
    start_time = datetime.now()

    # Validate Input
    if not chkInput():
        logger.error('Invalid Input. Exiting...')
        return False
    logger.info('Starting Validator Process...')

    # Populate list of Tactic -> Impression_pixels dictionaries
    tactic_data = readFile(sys.argv[1])
    if not tactic_data[0]:  # Handle Missing/Invalid Data
        logger.error('No tactic/pixel data found in file. Exiting...')
        return False
    bad_pixels = []
    num_pixels = tactic_data[1]  # Total no. of pixels across tactics
    fail = 0
    logger.info('Found %d tactics containing %d impression_pixels',
                len(tactic_data[0]), num_pixels)  # Summarizing the request

    # Tactic is a dictionary keyed off tactic-id
    for (i, tactic) in enumerate(tactic_data[0], 1):
        logger.debug('Testing tactic # %d of %d', i, len(tactic_data[0]))
        # Progress tracker if your file is very large
        if i == (len(tactic_data[0]) / 10):
            logger.debug('A tenth of the way  done in %s seconds...',
                         (datetime.now() - start_time))
        if i == (len(tactic_data[0]) / 2):
            logger.info('Half-way done in %s seconds...',
                        (datetime.now() - start_time)
        for tactic_id in tactic:
            bad_pixel={}  # A dictionary of bad tactic-pixel mapping
            # A list of pixels associated with a tactic-id
            pixel_list=tactic[tactic_id]
            logger.debug(pixel_list)
            for pixel in pixel_list:
                # Unescape URL by removing backslashes in pixel
                clean_pixel=pixel.replace('\\', '')
                logger.debug(
                    'Going to test pixel "%s" on tactic_id = %d', clean_pixel, tactic_id)  # Log this to investigate exceptions
                try:
                    r=requests.request("GET", clean_pixel, headers=headers)
                    response=r.status_code
                    if response > 399:  # Look for erroneous response codes
                        logger.debug(
                            'Got a %s response on pixel %s with tactic %d.', response, clean_pixel, tactic_id)
                        fail += 1
                        if tactic_id not in bad_pixel:
                            bad_pixel[tactic_id]=[]
                            bad_pixel[tactic_id].append(clean_pixel)
                        else:
                            bad_pixel[tactic_id].append(clean_pixel)
                except Exception as e:
                    logger.debug(
                        'Could not reach pixel %s with tactic %d.', clean_pixel, tactic_id)  # Look for connection errors
                    fail += 1
                    if tactic_id not in bad_pixel:
                        bad_pixel[tactic_id]=[]
                        bad_pixel[tactic_id].append(clean_pixel)
                    else:
                        bad_pixel[tactic_id].append(clean_pixel)
        if len(bad_pixel) != 0:
            bad_pixels.append(bad_pixel)
            # Outputs all bad tactic-pixels to a file
            collectTrash('%s\n' % bad_pixel)
    logger.info(
        'Checked all %d pixels and found %d bad ones and %d good ones!', num_pixels, fail, int(num_pixels - fail))
    logger.info(
        'Here are the failing combinations of Tactic ID: [Impression_pixels]: \n \n %s', bad_pixels)
    logger.info(
        '---- All Done! Look for all failing pixels in this file: %s ----', output_file)
    # Measure performance
    logger.info('--%s seconds--', (datetime.now() - start_time))


if __name__ == '__main__':
    try:
        main()
    except:
        # Print traceback for unhandled exceptions
        logger.info(traceback.format_exc())
        pass
