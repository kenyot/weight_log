"""weight_log

Usage:
weight_log.py record <datetime> <weight>
weight_log.py record <weight>
weight_log.py generate

Options:

-h --help   Show this screen.

"""

import sys
import os
import csv
from docopt import docopt
from datetime import datetime, timedelta, time

DEBUG = True
WEIGHT_LOG = "weight_log.txt"
OUTPUT_FILE = "output.csv"
TIME_FORMAT = "%Y-%m-%d-%H:%M"


class WeightLog(object):
    """ A collection of weight log entries to be read/processed/written, etc.

        Attributes:
            filename: A string representing the name of the weight log file
            num_entries: An integer count of the number of log entries
            ...
    """

    def __init__(self):
        self.filename = None
        self.num_entries = None
        self.start_date = None
        self.end_date = None
        self.log_entries = []
        self.weekly_averages = []


    def parse_log(self,filename):
        """ Loads and sorts weight log entries; initializes relevant attributes.

        Input file:
            A "weight log" is a text file that lists date & time vs weight.
            Entries are recorded one per line with each entry containing a date
            string ("%Y-%m-%d-%H:%M") with a corresponding float representing
            weight. Entries should be ordered by date with the most recent entry
            listed last. However, entries are sorted as soon as the log file is
            parsed (just to be safe).
        """

        if os.path.isfile(filename):

            self.filename = filename
            self.log_entries = []

            if DEBUG:
                print("Opening... {}".format(self.filename))

            with open(self.filename, "r") as infile:
                for line in infile:

                    datestring, weight = line.strip().split(",")
                    datetime = datestring_to_datetime(datestring)
                    weight = float(weight)

                    self.log_entries.append(LogEntry(datetime,weight))

            self.num_entries = len(self.log_entries)            
            if self.num_entries <= 0:
                error("Weight log devoid of any entries.")
            if DEBUG:
                print("Number of log entries: {}\n".format(self.num_entries))

            self.log_entries.sort()
            self.start_date = self.log_entries[0].datetime.date()
            self.end_date = self.log_entries[-1].datetime.date()
        else:
            error("Opening... {} : File not found.".format(self.filename))


    def compute_weekly_averages(self):
        """ Calculates average weight for each week ending on Sunday         
        """
        sundays = self.generate_sundays_in_range(self.start_date, self.end_date)
        try:
            previous_sunday = sundays[0] - timedelta(days=7)
        except IndexError:
            print("Error: Weight log entries must span at least one week to " \
                  "enable calculation of the weekly averages.")
            pass

        for sunday in sundays:
            total_weight = []
            for entry in self.log_entries:
                if (entry.datetime.date() > previous_sunday and
                    entry.datetime.date() <= sunday):

                    print(entry.datetime, " : ", entry.weight)
                    total_weight.append(entry.weight)

            previous_sunday = sunday
            if len(total_weight) > 0:
                entries = len(total_weight)
                average_weight = sum(total_weight) / entries

                if DEBUG:
                    print("Average Weight ({} entries): {:.1f} lbs". 
                    format(entries,average_weight))
                    print("\n")

                end_of_week = datetime.combine( sunday, time(23,59))
                self.weekly_averages.append( WeeklyAverage( end_of_week,
                                                            average_weight))

                


    def generate_sundays_in_range(self,start_date,end_date):
        """ Returns ordered list of dates representing all Sundays within range 
        """
        sundays = []
        date = self.find_first_sunday(start_date)

        while date <= end_date:

            sundays.append(date)
            date += timedelta(days=7)
        return sundays


    def find_first_sunday(self,start_date):
        """ Returns a date representing the first Sunday after the start date
        """
        # weekday() returns an integer: {Monday=0, Tuesday=1, ..., Sunday=6}
        days_to_first_sunday = 6 - start_date.weekday()
        first_sunday = start_date + timedelta(days=days_to_first_sunday)
        return first_sunday


    def write_to_csv(self,filename):
        """ Writes... 
        
            Output file:
            CSV, three columns: datetime (epoch), bodyweight, weekly average
        """
        entries_and_averages = []

        for entry in self.log_entries:
            datetime = datetime_to_epoch(entry.datetime)
            weight = entry.weight
            entries_and_averages.append([datetime,weight,""])

        for entry in self.weekly_averages:
            datetime = datetime_to_epoch(entry.datetime)
            average_weight = "{:.1f}".format(entry.weight)
            entries_and_averages.append([datetime,"",average_weight])

        entries_and_averages.sort()

        print("Writing... {}".format(filename))
        with open(filename,'w') as outfile:
            csv_outfile = csv.writer(outfile)
            csv_outfile.writerow(["Date","Bodyweight","Weekly Average"])
            csv_outfile.writerows(entries_and_averages)



class LogEntry(object):
    """ Attributes: 
            datetime: a datetime object from the datetime module
            weight: a float representing weight (lbs)
    """
    def __init__(self, datetime, weight):
        self.datetime = datetime
        self.weight = weight

    def __lt__(self, other):
        return self.datetime < other.datetime


class WeeklyAverage(object):
    """ Attributes: 
            datetime: a datetime object from the datetime module
            weight: a float representing weight (lbs)
    """
    def __init__(self,datetime,weight):
        self.datetime = datetime
        self.weight = weight

    def __lt__(self, other):
        return self.datetime < other.datetime


def record_weight(filename,date_string,weight):
    """ ... """
    inspect_datestring_format(date_string)
    weight = inspect_float(weight)

    print("Opening... {}".format(filename))
    print("New entry: {}  {}".format(date_string, weight))
    with open(filename, "a+") as outfile:
        csv_outfile = csv.writer(outfile)
        csv_outfile.writerow([date_string,weight])


def record_current_weight(filename,weight):
    date_string = datetime_to_datestring(datetime.now())
    record_weight(filename,date_string,weight)


def datestring_to_datetime(date_string):
    """ Converts string to datetime object if date is given in proper format """
    inspect_datestring_format(date_string)
    return datetime.strptime(date_string,TIME_FORMAT)


def datetime_to_epoch(time):
    """ Returns number of milliseconds since the beginning of the unix epoch """
    return int((time - datetime.utcfromtimestamp(0)).total_seconds() * 1000)


def datestring_to_epoch(date_string):
    return datetime_to_epoch(datestring_to_datetime(date_string))


def datetime_to_datestring(datetime):
    return datetime.strftime(TIME_FORMAT)


def inspect_datestring_format(date_string):
    try:
        datetime.strptime(date_string,TIME_FORMAT)
    except ValueError:
        error("Date string must conform to format: " + TIME_FORMAT)


def inspect_float(x):
    try:
        return float(x)
    except ValueError:
        error("{} must be a float that represents bodyweight (lbs)".format(x))


def error(message):
    sys.stderr.write("Error: " + message + "\n")
    sys.exit(-1)


def main(argv):

    record          = argv["record"]
    datetime        = argv["<datetime>"]
    weight          = argv["<weight>"]
    generate_output = argv["generate"]

    if record:
        if datetime is None:
            record_current_weight(WEIGHT_LOG, weight)
        else:
            record_weight(WEIGHT_LOG, datetime, weight)

    if generate_output:
        weight_log = WeightLog()
        weight_log.parse_log(WEIGHT_LOG)
        weight_log.compute_weekly_averages()
        weight_log.write_to_csv(OUTPUT_FILE)


if __name__ == "__main__":
    argv = docopt(__doc__)
    main(argv)
