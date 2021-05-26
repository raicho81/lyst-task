#!/usr/bin/env python
import sys
import re
import logging
import itertools
import time


logging.Formatter.converter = time.gmtime   # Use UTC time when logging
logging.basicConfig(filename='scheduler.error.log', format='%(asctime)s.%(msecs)03d %(message)s', filemode='a',
                    datefmt='%m/%d/%Y %H:%M:%S')


class Task:
    def __init__(self):
        self.h = 0
        self.m = 0
        self.cmd = ""
        self.day = ""


class Scheduler:
    """"
        Scheduler class. The __init__ method throws ValueError if the current time is invalid
    """
    class TimeValueError(ValueError):
        def __init__self(self, msg, obj=None):
            super(TimeValueError, self).__init__(msg, obj)

    def __init__(self, cur_time):
        super(Scheduler, self).__init__()
        self.tasks = []
        self.input_lines = None
        pattern = re.compile("\d{1,2}?:\d{1,2}?")

        if not pattern.match(cur_time):
            raise ValueError("Invalid current time value: {}".format(cur_time))

        split_cur_time = cur_time.split(":")
        self.cur_h = int(split_cur_time[0])
        if self.cur_h > 23:
            raise ValueError("Invalid current time hour value: {}".format(self.cur_h))

        self.cur_m = int(split_cur_time[1])
        if self.cur_m > 59:
            raise ValueError("Invalid current time minute value: {}".format(self.cur_m))

    def print_tasks(self):
        if len(self.tasks) == 0:
            return

        for task in self.tasks:
            print("{:}:{:02} {} - {}".format(task.h, task.m, task.day, task.cmd))

    def get_input(self):
        self.input_lines = [_.rstrip() for _ in sys.stdin]

    def parse_line(self, line):
        pattern = re.compile("\s+")
        split_line = pattern.split(line)
        cmd_m = split_line[0]
        cmd_h = split_line[1]
        cmd = split_line[2]
        t = Task()
        t.cmd = cmd

        if cmd_h == "*" and cmd_m == "*":
            t.h = self.cur_h
            t.m = self.cur_m
            t.day = "today"

        if cmd_h != "*" and cmd_m != "*":
            t.h = int(cmd_h)
            if t.h > 23:
                raise self.TimeValueError("Invalid command hour value: {}".format(t.h))
            t.m = int(cmd_m)
            if t.m > 59:
                raise self.TimeValueError("Invalid command minute value: {}".format(t.m))
            if t.h >= self.cur_h and t.m >= self.cur_m:
                t.day = "today"
            else:
                t.day = "tomorrow"

        if cmd_h != "*" and cmd_m == "*":
            t.h = int(cmd_h)
            if t.h > 23:
                raise self.TimeValueError("Invalid command hour value: {}".format(t.h))
            t.m = 0
            if t.h < self.cur_h:
                t.day = "tomorrow"
            if t.h == self.cur_h and self.cur_m == 0:
                t.day = "today"
            if t.h > self.cur_h:
                t.day = "today"

        if cmd_h == "*" and cmd_m != "*":
            t.m = int(cmd_m)
            if t.m > 59:
                raise self.TimeValueError("Invalid command minute value: {}".format(t.m))
            if t.m == self.cur_m:
                t.h = self.cur_h
                t.day = "today"
            if t.m < self.cur_m:
                t.h = self.cur_h + 1
                if t.h > 23:
                    t.h = 0
                    t.day = "tomorrow"
                else:
                    t.day = "today"
            if t.m > self.cur_m:
                t.h = self.cur_h
                t.day = "today"
        return t

    def check_and_parse_input(self):
        pattern = re.compile("(\d{1,2}|\*)[ |\t]+(\d{1,2}|\*)[ |\t]+.+")
        line_num = 0

        for line, line_num in zip(self.input_lines, itertools.count(1)):
            if pattern.match(line):
                try:
                    self.tasks.append(self.parse_line(line))
                except self.TimeValueError as ex:
                    logging.error(str(ex) + ", input line number: {}".format(line_num))
            else:
                logging.error("Invalid scheduler task input format, input line number: {}, input line: {}"
                              .format(line_num, line))

    def run(self):
        self.get_input()
        self.check_and_parse_input()
        self.print_tasks()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./scheduler.py <HH:MM>")
        print("The input is read from STDIN")
        print("Example: ./scheduler.py 2:10 < config")
        sys.exit(1)
    try:
        sched = Scheduler(sys.argv[1])
    except ValueError as ex:
        print(ex)
        sys.exit(1)
    sched.run()
