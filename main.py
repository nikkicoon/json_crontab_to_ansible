import datetime
import json
import pathlib
import re
import sys
from json import JSONDecodeError

import click
from crontab import CronTab

@click.command()
@click.option("--infile", type=click.File('r'), default=sys.stdin)
@click.option("--outfile", default="ansible_from_json.yml")
@click.option("--cronfile", default="foo")
@click.option("--user", default="root")
@click.option("--indent", default=4)
@click.option("--defaultname", default=True)
@click.option("--defaultjobname", default=True)
@click.option("--active", default=True)
def main(infile: str|click.File, outfile: str, cronfile: str, user: str, indent: int, defaultname: bool, defaultjobname: bool, active: bool):
    """outputs an ansible entry.

    \b
    - name: foobar|ARG
      ansible.builtin.cron:
        cron_file: ARG
        user: str(command[0])
        minute: int
        hour: int
        name: description
        job: str(command[1:])
"""
    n = int(datetime.datetime.timestamp(datetime.datetime.now()))
    p = pathlib.Path(outfile)
    ext = "".join(p.suffixes)
    outfile = str(p).removesuffix(ext) + "." + str(n) + ".".join(p.suffixes)
    _tab_header = "  " * int(indent/2)
    _tab_header_two = _tab_header + "  "
    _tab_body = _tab_header_two + "  "
    with infile as f:
        try:
            data = json.load(f)
            list_of_crons = data["schedule"]
            if "schedule" not in data:
                return
        except JSONDecodeError as e:
            # todo: replace */60 with 0 for minute, */1 with *.
            data = CronTab(tabfile=infile.name)
            list_of_crons = data.crons
        if len(list_of_crons) > 0:
            with open(outfile, "a") as o:
                for k in list_of_crons:
                    if isinstance(k, dict):
                        command: str = k.get("command", "")
                    else:
                        command = k.command
                    command_parts = re.split(r"\s+", command)
                    cro = _tab_body + "cron_file: " + cronfile
                    if len(command_parts) > 1:
                        job = _tab_body + "job: " + "\"" + " ".join(command_parts[1:]).replace('\"', '\\"') + "\"" + "\n"
                    else:
                        job = None
                    if len(command_parts) > 0:
                        user = _tab_body + "user: " + command_parts[0]
                    else:
                        user = " ".join((_tab_body + "user:", user))
                    if isinstance(k, dict):
                        _minute = k.get("minute")
                    else:
                        _minute = [str(k.minute)]
                    if _minute is not None:
                        minute = _tab_body + "minute: " + "\"" + "".join(_minute) + "\"" if _minute != ["*"] else None
                    else:
                        minute = None
                    if isinstance(k, dict):
                        _hour = k.get("hour")
                    else:
                        _hour = [str(k.hour)]
                    if _hour is not None:
                        hour = _tab_body + "hour: " + "\"" + "".join(_hour) + "\"" if _hour != ["*"] else None
                    else:
                        hour = None
                    if isinstance(k, dict):
                        _month = k.get("month")
                    else:
                        _month = [str(k.month)]
                    if _month is not None:
                        month = _tab_body + "month: " + "\"" + "".join(_month) + "\"" if _month != ["*"] else None
                    else:
                        month = None
                    if isinstance(k, dict):
                        _day_of_month = k.get("day_of_month")
                    else:
                        _day_of_month = [str(k.dom)]
                    if _day_of_month is not None:
                        day = _tab_body + "day: " + "\"" + "".join(_day_of_month) + "\"" if _day_of_month != ["*"] else None
                    else:
                        day = None
                    if isinstance(k, dict):
                        _weekday = k.get("day_of_week")
                    else:
                        _weekday = [str(k.dow)]
                    if _weekday is not None:
                        weekday = _tab_body + "weekday: " + "\"" + "".join(_weekday) + "\"" if _weekday != ["*"] else None
                    else:
                        weekday = None
                    if defaultname and len(command_parts) > 1:
                        path = pathlib.Path("".join(command_parts[2:])).name
                        path = path.rstrip(")")
                        cronname = _tab_body + "name: " + "\"" + path + "\""
                    else:
                        cronname = _tab_body + "name: DESCRIBEME"
                    if defaultjobname:
                        # TODO: provide string
                        jobname = cronfile + " | + set cronjob for " + path if path != "" else ""
                    else:
                        jobname = "EDITME"
                    header = _tab_header + "- name: " + jobname + "\n" + _tab_header_two + "ansible.builtin.cron:"
                    state_str = _tab_body + "disabled: true" if not active else None
                    res = "\n".join(filter(None, (header, cro, user, minute, hour, month, day, weekday, cronname, job, state_str)))
                    print(res, file=o)
        else:
            print("input file empty, skipping output")


if __name__ == "__main__":
    main(max_content_width=120)