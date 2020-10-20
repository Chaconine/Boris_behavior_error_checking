# BORIS Behavior File Error Checker

## Created by Joseph Maa
## Email: josephgmaa@berkeley.edu
## Last updated: 10/19/20

This script takes in multiple BORIS behavior files and checks for errors (i.e. event chronology errors (START START / STOP STOP) and animal position errors (Left -> Right without passing center)).

1. BORIS files should be placed in folder "BORIS_files_input"

2. Open the terminal and move to the "BORIS behavior error checking" directory

3. Run bash script with command: "bash error_check.sh"

4. Output will be displayed in terminal as well as outputted to folder "error_check_results" as .txt files
