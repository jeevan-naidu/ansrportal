#!/usr/bin/env python
import os
import sys
import signal
import traceback

if __name__ == "__main__":
    # print stack trace on USR1
    #signal.signal(signal.SIGUSR1, lambda sig, stack: traceback.print_stack(stack))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "timetracker.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

