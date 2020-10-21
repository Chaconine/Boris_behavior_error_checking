# BORIS Behavior File Error Checker
### Last updated: 10/19/20

#### <ins>Created by Joseph Maa</ins>
#### Email: josephgmaa@berkeley.edu


This script takes in multiple BORIS behavior files and checks for errors (i.e. event chronology errors (START START / STOP STOP) and animal position errors (Left -> Right without passing center)).



1. Open the terminal and move to the "BORIS behavior error checking" directory.

2. Extract .csv files from behavior files in BORIS. 

3. Place BORIS files in folder "BORIS_files_input" as **.csv** files. If they are not .csv files, the program will error! 

4. Determine absolute path to "BORIS_files_input". Use this in command below. 

Example:
"/Users/josephgmaa/Research/BORIS behavior error checking/boris_files_input"

5. Run python script with command: "python3 error_check.py --path=YOUR_PATH_HERE"

Testing (Currently working on automating):

1. If there are errors during runtime, try running the .csvs in the test_boris_files

![](errors.png)
