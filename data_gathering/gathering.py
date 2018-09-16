"""
Data gathering task

Gather author data from https://livelib.ru:
python gathering.py gather

Transform to tsv format:
python gathering.py transform

Calculate some statistics:
python gathering.py stats

"""

import logging

import sys
import pandas as pd
import numpy as np

from scrappers.scrapper import Scrapper
from storages.file_storage import FileStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SCRAPPED_AUTHORS = 'scrapped_authors.txt'
SCRAPPED_AUTHOR_INFO = 'scrapped_author_info.txt'
TABLE_FORMAT_FILE = 'data.tsv'


def gather_process():
    logger.info("gather")
    storage_authors = FileStorage(SCRAPPED_AUTHORS)
    storage_author_info = FileStorage(SCRAPPED_AUTHOR_INFO)

    scrapper = Scrapper()
    scrapper.scrap_process(storage_authors, storage_author_info)


def convert_data_to_table_format():
    logger.info("transform")

    # transform gathered data from txt file to pandas DataFrame and save as tsv
    output = open(TABLE_FORMAT_FILE, mode='w', encoding='utf-8')
    header = """name\tbirth_date\tbirth_place\tdeath_date\t"""
    header += """death_place\tnum_books\tadepts\treaders\n"""
    output.write(header)
    f = open(SCRAPPED_AUTHOR_INFO, encoding='utf-8')
    for line in f:
        output.write('\t'.join(line.split('\t')[1:]))


def stats_of_data():
    logger.info("stats")

    def dt_parse(x):  # standard parser does not work due to its ranges
        if x == "nan":
            return "nan"
        year, month, day = x.split('-')
        return pd.Period(
            year=int(year),
            month=int(month),
            day=int(day),
            freq='D')

    dataframe = pd.read_table(
        TABLE_FORMAT_FILE,
        parse_dates=['birth_date', 'death_date'],
        date_parser=dt_parse)
    print(dataframe.describe())
    dataframe.info()

    dataframe['lifespan'] = dataframe.apply(
        lambda x: 0 if x['death_date'] == "nan" or x['birth_date'] == "nan"
        else x['death_date'] - x['birth_date'], axis=1)
    values = np.argsort(dataframe.lifespan).values
    dataframeSorted = dataframe.iloc[values].tail(1)
    lifespan = dataframeSorted.lifespan.tolist()[0]
    dataframe.drop('lifespan', 1)
    # longest lifespan
    writer = dataframeSorted.name.tolist()[0]
    print("longest lifespan: {lifespan} days by writer {writer}".format(
        lifespan=lifespan,
        writer=writer))

    # maximum books written
    values = np.argsort(dataframe.num_books).values
    dataframeSorted = dataframe.iloc[values].tail(1)
    maximumBooks = dataframeSorted.num_books.tolist()[0]
    writer = dataframeSorted.name.tolist()[0]
    print("maximum books written: {maximumBooks} by writer {writer}".format(
        maximumBooks=maximumBooks,
        writer=writer))

    # average adepts
    avgAdepts = dataframe.mean().adepts
    print("average adepts:", avgAdepts)

if __name__ == '__main__':
    logger.info("Work started")

    if sys.argv[1] == 'gather':
        gather_process()

    elif sys.argv[1] == 'transform':
        convert_data_to_table_format()

    elif sys.argv[1] == 'stats':
        stats_of_data()

    logger.info("Work ended")
