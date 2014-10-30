#!/bin/env python

import json
from datetime import datetime
import argparse
import os

class Pair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "({0} : {1})".format(self.key, self.value)
    
    def __repr__(self):
        return str(self)

class CommandEntry:
    def __init__(self, func, name, aliases, help):
        self.func = func
        self.name = name
        self.aliases = aliases
        self.help = help

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

    def __str__(self):
        result = "Command '{0}'".format(self.name)
        if self.aliases:
            result += "\n  aliases: '{0}'".format("', '".join(self.aliases))
        if self.help:
            result += "\n  {0}".format(self.help)
        return result

    def __repr__(self):
        return self.name

commands = []

def command(name, *, aliases=None, help=None):
    return lambda func: commands.append(CommandEntry(func, name, aliases, help))

class Time:
    ########## Static stuff ##########

    Format = "%Y-%m-%d %H:%M:%S, %A"

    def GetNow():
        return Time()

    def FromString(theString):
        return Time(theString)

    ########## Instance stuff ##########

    def __init__(self, dateString=None):
        if dateString is not None:
            self.DateTime = datetime.strptime(dateString, Time.Format)
        else:
            self.DateTime = datetime.now()

    def __str__(self):
        return self.DateTime.strftime(Time.Format)

    def GetDay(self):
        return self.DateTime.date()

########## Args ##########

argsParser = argparse.ArgumentParser()
argsParser.add_argument("-v", "--verbosity",
                        type=int,
                        default=1,
                        help="Set the level of verbosity.")
argsParser.add_argument("-f", "--file",
                        default="TimeRecords.json",
                        help="The file to use.")
argsParser.add_argument("-n", "--dry-run",
                        action="store_true",
                        help="Simulates the given command but prevents side-effects (other than printing...)")
argsParser.add_argument("command",
                        help="The command to execute.")

def checkRecordsFileContent(doc):
    if "current" not in doc:
        raise ValueError("Expected key 'current'.")
    if "records" not in doc:
        raise ValueError("Expected key 'records'.")
    if not isinstance(doc["records"], list):
        raise ValueError("Expected 'records' to be a list.")

########## Helpers ##########

def printCommands(subset=None):
    for command in subset or commands:
        print(command)

########## Commands ##########

@command("commands", help="Prints information about all available commands.")
def showCommands(args):
    printCommands()

@command("initialize", aliases=["init"])
def initializeRecordsFile(args):
    if os.path.exists(args.file) and os.path.isfile(args.file):
        input("Warning: File already exists. Press Enter to continue")

    with open(args.file, mode='w') as recordsFile:
        json.dump({ "current" : None, "records"  : [] }, recordsFile, indent=4)

@command("generate", aliases=["gen"], help="Generates a hours-worked report and prints that.")
def generate(args):
    timeTable = [] # Format: "day" : "numHours"
    def addToTimeTable(key, value):
        for existing in timeTable:
            if existing.key == key:
                # Found the entry with the given key.
                existing.value += value
                return
        # The key does not exist yet so we just create it
        timeTable.append(Pair(key, value))
    doc = None
    with open(args.file, mode='r') as recordsFile:
        doc = json.load(recordsFile)
    checkRecordsFileContent(doc)
    records = doc["records"]
    for rec in records:
        start = Time(rec["start"])
        end = Time(rec["end"])
        day = start.DateTime.date()
        delta = end.DateTime - start.DateTime
        if args.verbosity > 1:
            print("On {0}: {1} hours".format(day, delta))
        addToTimeTable(day, delta)
    timeTableString = ""
    for entry in timeTable:
        timeTableString += "{0}, {1:<9} => {2}\n".format(entry.key, "{0:%A}".format(entry.key), entry.value)
    print(timeTableString)

@command("start", aliases=["s"])
def start(args):
    doc = None
    with open(args.file, mode='r') as recordsFile:
        doc = json.load(recordsFile)

    checkRecordsFileContent(doc)

    assert doc["current"] == None, "You are already recording something."

    doc["current"] = { "start" : str(Time()), "end" : None }

    with open(args.file, mode='w') as recordsFile:
        json.dump(doc, recordsFile, indent=4)

@command("end", aliases=["e"])
def end(args):
    doc = None
    with open(args.file, mode='r') as recordsFile:
        doc = json.load(recordsFile)

    checkRecordsFileContent(doc)
    
    assert doc["current"] != None, "You are already recording something."

    doc["current"]["end"] = str(Time())
    doc["records"].append(doc["current"])
    doc["current"] = None

    with open(args.file, mode='w') as recordsFile:
        json.dump(doc, recordsFile, indent=4)

@command("print", aliases=["dump"])
def printRecordsFileContent(args):
    with open(args.file, mode='r') as recordsFile:
        lines = recordsFile.readlines()
        print("".join(lines))

########## Entry Point ##########

def main():
    args = argsParser.parse_args()
    args.dryRun = args.dry_run
    del args.dry_run

    if args.verbosity > 1:
        print("args: {0}".format(args))

    candidates = []
    # Iterate through all available commands and choose all that fit.
    for command in commands:
        if command.name.startswith(args.command):
            candidates.append(command)
            continue
        if command.aliases is None:
            continue
        for alias in command.aliases:
            if alias.startswith(args.command):
                candidates.append(command)
    if len(candidates) == 0:
        print("Error: Command not found: {0}".format(args.command))
        print("Available commands:")
        printCommands()
        return 1
    if len(candidates) > 1:
        print("Error: Given command name is ambiguous: {0}".format(args.command))
        print("Possible candidates:")
        printCommands(candidates)
        return 2

    # At this point we can be sure that there is exactly 1 candidate.
    command = candidates[0]
    if args.dryRun:
        print("Would execute {0}".format(command))
    else:
        if args.verbosity > 1:
            print("Executing {0}\n==========".format(command))
        return command(args)

if __name__ == '__main__':
    main()
