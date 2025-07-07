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
@click.option("--filetype", default="json")
@click.option("--indent", default=4)
@click.option("--defaultname", default=True)
@click.option("--defaultjobname", default=True)
def main(infile: str|click.File, outfile: str, cronfile: str, user: str, filetype: str, indent: int, defaultname: bool, defaultjobname: bool):
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
    outfile = outfile + "." + str(n)
    _tab_header = "  " * int(indent/2)
    _tab_header_two = _tab_header + "  "
    _tab_body = _tab_header_two + "  "
    with infile as f:
        match filetype:
            case "json":
                try:
                    data = json.load(f)
                except JSONDecodeError as e:
                    print(f"json decoding error with file {f.name}")
                    sys.exit(1)
                # print(data)
                if "schedule" in data:
                    with open(outfile, "a") as o:
                        for k in data["schedule"]:
                            if "command" in k:
                                command: str = k["command"]
                                command_parts = re.split(r"\s+", command)
                                # print(command_parts)
                            cro = _tab_body + "cron_file: " + cronfile
                            if len(command_parts) > 0:
                                user = _tab_body + "user: " + command_parts[0]
                            else:
                                user = " ".join((_tab_body + "user:", user))
                            if "minute" in k:
                                minute = _tab_body + "minute: " + "".join(k["minute"]) if k["minute"] != ["*"] else None
                            if "hour" in k:
                                hour = _tab_body + "hour: " + "".join(k["hour"]) if k["hour"] != ["*"] else None
                            if "month" in k:
                                month = _tab_body + "month: " + "".join(k["month"]) if k["month"] != ["*"] else None
                            if "day_of_month" in k:
                                day = _tab_body + "day: " + "".join(k["day_of_month"]) if k["day_of_month"] != ["*"] else None
                            if "day_of_week" in k:
                                weekday = _tab_body + "weekday: " + "".join(k["day_of_week"]) if k["day_of_week"] != ["*"] else None
                            if len(command_parts) > 1:
                                job = _tab_body + "job: " + "\"" + " ".join(command_parts[1:]) + "\"" + "\n"
                            else:
                                job = None
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
                            res = "\n".join(filter(None, (header, cro, user, minute, hour, month, day, weekday, cronname, job)))
                            print(res, file=o)
            case "cron":
                data = CronTab(tabfile=infile.name)
                with open(outfile, "a") as o:
                    for k, v in data.env.items():
                        if k == "MAILTO":
                            print(k, v)
                    for k in data.crons:
                        job = k.command
                        command_parts = re.split(r"\s+", job)
                        if len(command_parts) > 1:
                            job = "\tjob: " + "\"" + " ".join(command_parts[1:]) + "\"" + "\n"
                        else:
                            job = None
                        if len(command_parts) > 0:
                            user = "\tuser: " + command_parts[0]
                        else:
                            user = " ".join(("\tuser:", user))
                        header = "name: EDITME\nansible.builtin.cron:"
                        cro = "\tcron_file: " + cronfile
                        cronname = "\tname: DESCRIBEME"
                        minute = "\tminute: " + str(k.minute) if str(k.minute) != "*" else None
                        hour = "\thour: " + str(k.hour) if str(k.hour) != "*" else None
                        month = "\tmonth: " + str(k.month) if str(k.month) != "*" else None
                        day = "\tday: " + str(k.dom) if str(k.dom) != "*" else None
                        weekday = "\tweekday: " + str(k.dow) if str(k.dow) != "*" else None
                        res = "\n".join(filter(None, (header, cro, user, minute, hour, month, day, weekday, cronname, job)))
                        print(res, file=o)


if __name__ == "__main__":
    main(max_content_width=120)