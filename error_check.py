#!/use/bin/env python

from io import StringIO

import argparse
import glob
import os
import pandas as pd
import re
import subprocess
import sys

"""Generate the parser for the command line"""

parser = argparse.ArgumentParser(
    description='Check for errors in BORIS behavior file scoring')
parser.add_argument(
    '--path', help='Input a string path to the folder boris_files_input')

args = parser.parse_args()

# Prompt user for path if argument is empty or path directory is empty


def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


if not args.path:
    print("Please enter a path argument to input files with --path (i.e. --path='User/etc/boris_files_input'). Script will now exit!")
    sys.exit()
elif len(listdir_nohidden(args.path)) == 0:
    print("Directory is empty, please place files into boris_files_input folder")
    sys.exit()


def preprocess_behavior_file(path, reader="csv", frametimes_path=""):
    """This function preprocesses csv exports from BORIS files and returns a DataFrame object. It also checks 
    for erroneous BORIS event inputs (i.e. START followed by another START event or STOP followed by another 
    STOP event)"""

    if (reader == "csv"):
        df = pd.read_csv(path)
    elif (reader == "xlsx"):
        df = pd.read_excel(path)

    if (frametimes_path):
        frametimes = pd.read_csv(frametimes_path)

    df.columns = df.iloc[14].to_list()
    df = df.drop(df.index[0:15])
    df = df.drop(["Media file path", "Total length", "FPS",
                  "Subject", "Behavioral category", "Comment"], axis=1)

    # Save the old row numbers as a new column, then drop point events and any intervention events
    df['Row index'] = df.index

    df = df[df.Status != "POINT"]
    df = df[df.Behavior != "Intervention"]
    df = df[df.Behavior != "Don't Score"]
    df = df[df.Behavior != "Disconnected"]

    # Reset the index after dropping events to make later calculations simpler
    df = df.reset_index()
    df.loc[0, "Duration"] = "NaN"

    # Convert the time column to a float from a string
    df["Time"] = df["Time"].apply(lambda x: float(x))
    if frametimes_path:
        df["Frametime"] = df["Time"].apply(lambda x: frametimes.iloc[round(x * 20), 0] if (
            round(x * 20) <= frametimes.shape[0] - 1) else frametimes.iloc[frametimes.shape[0] - 1, 0])
        start_time = df["Frametime"][0]
        df["Time"] = df["Frametime"].apply(lambda x: x - start_time)

    # Generate the Duration column
    for i in range(0, len(df)):
        if i % 2 != 0:
            if (frametimes_path):
                df.loc[i, "Duration"] = float(
                    df.loc[i, "Frametime"]) - float(df.loc[i - 1, "Frametime"])
            else:
                df.loc[i, "Duration"] = float(
                    df.loc[i, "Time"]) - float(df.loc[i - 1, "Time"])
        else:
            df.loc[i, "Duration"] = 0
    df["Duration"] = pd.to_numeric(df["Duration"])

    # Generate the Location column that maps behaviors to locations
    mapping = {"Center": "Center", "Huddle left": "Left", "Huddle right": "Right", "Interact left": "Left", "Interact right":
               "Right", "Left": "Left", "Right": "Right", "Sniff left": "Left", "Sniff right": "Right"}

    df["Location"] = df["Behavior"]
    df["Location"] = df["Location"].map(mapping)

    # Check for errors in BORIS event inputs
    current = "START"

    for i in range(len(df)):
        if df.loc[i, "Status"] != current:
            print("Check for repeated status event at row for file: " +
                  path + " at " + str(i))
        elif current == "START":
            current = "STOP"
        else:
            current = "START"

    previous_location = "Center"
    for i in range(len(df)):
        current_location = df.loc[i, "Location"]
        if current_location != previous_location:
            if previous_location == "Left":
                if current_location == "Right":
                    row = str(df.loc[i, "Row index"])
                    print("Check for location error at row for file: " +
                          path + " at " + row)
            elif previous_location == "Right":
                if current_location == "Left":
                    row = str(df.loc[i, "Row index"])
                    print("Check for location error at row for file: " +
                          path + " at " + row)
            previous_location = current_location

    return df


class Animal:
    """An object representing a single animal that contains information about the animal including a BORIS behavior file."""
    animal_id: str
    behavior_file: str
    behavior_dataframe: pd.DataFrame

    def __init__(self, animal_id: str, behavior_file: str = "") -> None:
        if behavior_file:
            self.behavior_dataframe = preprocess_behavior_file(behavior_file)
        self.animal_id = animal_id

    def __str__(self) -> str:
        return self.animal_id

    def set_behavior_file(self, df: pd.DataFrame) -> None:
        self.behavior_file = df

    def get_behavior_file(self, path: str) -> pd.DataFrame:
        """Takes in a string path to a BORIS csv file and returns a pandas dataframe"""
        return pd.read_csv(path)

    def get_animal_id(self) -> str:
        return self.animal_id


class Cohort:
    """An object representing a cohort of animals that contains information about the cohort including a cohort id, the sex
    of the cohort, the genotype of the cohort, and the cohort of animals"""
    cohort = set()
    cohort_id: str
    sex: str
    genotype: str

    def __init__(self, cohort_id, cohort=set()) -> None:
        self.cohort_id = cohort_id
        if len(cohort) != 0:
            self.cohort = cohort

    def __str__(self) -> str:
        res = 'The current animals in the cohort are: \n'
        for animal in self.cohort:
            res += animal.get_animal_id() + '\n'
        return res

    def add_animal_to_cohort(self, animal: Animal):
        self.cohort.add(animal)


cohort = Cohort('test')

# Generate test cohort of animals from test directory and adding to cohort
for file in glob.glob(args.path + '/*'):
    a = re.search('[V][0-9][0-9][0-9][0-9]', file)
    animal_id = a.group(0)
    animal = Animal(animal_id, file)
    cohort.add_animal_to_cohort(animal)
