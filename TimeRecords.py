#!/bin/env python

import json
from datetime import datetime

class Time:
    Format = "%Y-%m-%d %H:%M:%S, %A"

    def __init__(self, dateString=None):
        if dateString is not None:
            self.DateTime = datetime.strptime(dateString, Time.Format)
        else:
            self.DateTime = datetime.now()

    def GetNow():
        return Time()
    def FromString(theString):
        return Time(theString)

    def __str__(self):
        return self.DateTime.strftime(Time.Format)

def main():
    now = Time()
    print("now:             {0}".format(now))

    nowString = str(now)
    print("nowString:       {0}".format(nowString))

    deserializedNow = Time(nowString)
    print("deserializedNow: {0}".format(deserializedNow))

if __name__ == '__main__':
    main()
