#!/bin/env python

import json
from datetime import datetime
import argparse
import os

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
        return result + "\n"

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

########## Args ##########

argsParser = argparse.ArgumentParser()
argsParser.add_argument("-v", "--verbosity",
                        type=int,
                        default=1,
                        help="Set the level of verbosity.")
argsParser.add_argument("-f", "--file",
                        default="TimeRecords.json",
                        help="The file to use.")
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

def printCommands():
    for command in commands:
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
    print("generate!")

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
    if args.verbosity > 1:
        print("args: {0}".format(args))

    for command in commands:
        if command.name == args.command or command.aliases and args.command in command.aliases:
            command(args)
            return
    print("Error: Command not found: {0}".format(args.command))
    print("Available commands:")
    printCommands()
    return 1

if __name__ == '__main__':
    main()
