#!/bin/env python

import json
from datetime import datetime
import argparse
import os

class CommandEntry:
    def __init__(self, func, name, aliases):
        self.func = func
        self.name = name
        self.aliases = aliases

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

commands = []

def command(name, *, aliases=None):
    def registerCommand(func):
        commands.append(CommandEntry(func, name, aliases))
    return registerCommand

class Time:
    ### Static stuff ############################

    Format = "%Y-%m-%d %H:%M:%S, %A"

    def GetNow():
        return Time()

    def FromString(theString):
        return Time(theString)

    ### Instance stuff ##########################

    def __init__(self, dateString=None):
        if dateString is not None:
            self.DateTime = datetime.strptime(dateString, Time.Format)
        else:
            self.DateTime = datetime.now()

    def __str__(self):
        return self.DateTime.strftime(Time.Format)

### Args ########################################

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

def main():
    args = argsParser.parse_args()
    if args.verbosity > 1:
        print("args: {0}".format(args))

    for command in commands:
        if command.name == args.command or args.command in command.aliases:
            command(args)
            return
    print("Error: Command not found: {0}".format(args.command))
    return 1

def checkRecordsFileContent(doc, expectedState):
    state = doc.get("state", None)
    if state is None:
        raise ValueError("Expected key 'state'")
    if state != expectedState:
        raise ValueError("Expected 'state' to be '{0}' but is '{1}'.".format(expectedState, state))
    if "records" not in doc:
        raise ValueError("Expected key 'records'.")
    records = doc["records"]
    if not isinstance(records, list):
        raise ValueError("Expected 'records' to be a list.")

### Commands ####################################

@command("initialize", aliases=["init"])
def initializeRecordsFile(args):
    if os.path.exists(args.file) and os.path.isfile(args.file):
        input("Warning: File already exists. Press Enter to continue")

    with open(args.file, mode='w') as recordsFile:
        json.dump({ "state" : "ended", "records"  : [] }, recordsFile, indent=4)

@command("generate", aliases=["gen"])
def generate(args):
    print("generate!")

@command("start", aliases=["s"])
def start(args):
    doc = None
    with open(args.file, mode='r') as recordsFile:
        doc = json.load(recordsFile)

    checkRecordsFileContent(doc, "ended")

    doc["records"].append(str(Time()))
    doc["state"] = "started"

    with open(args.file, mode='w') as recordsFile:
        json.dump(doc, recordsFile, indent=4)

@command("end", aliases=["e"])
def end(args):
    doc = None
    with open(args.file, mode='r') as recordsFile:
        doc = json.load(recordsFile)

    checkRecordsFileContent(doc, "started")

    doc["records"].append(str(Time()))
    doc["state"] = "ended"

    with open(args.file, mode='w') as recordsFile:
        json.dump(doc, recordsFile, indent=4)

@command("print", aliases=["dump"])
def printRecordsFileContent(args):
    with open(args.file, mode='r') as recordsFile:
        lines = recordsFile.readlines()
        print("".join(lines))

### Entry Point #################################
if __name__ == '__main__':
    main()
