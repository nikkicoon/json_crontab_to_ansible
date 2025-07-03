import datetime
import json
import re
import sys

import click


@click.command()
@click.option("--infile", type=click.File('r'), default=sys.stdin)
@click.option("--outfile", default="ansible_from_json.yml")
@click.option("--cronfile", default="foo")
@click.option("--user", default="root")
def main(infile: str, outfile: str, cronfile: str, user: str):
    """outputs an ansible entry.

    \b
    name: foobar|ARG
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
    with infile as f:
        data = json.load(f)
        # print(data)
        if "schedule" in data:
            with open(outfile, "a") as o:
                for k in data["schedule"]:
                    if "command" in k:
                        command: str = k["command"]
                        command_parts = re.split(r"\s+", command)
                        # print(command_parts)
                    header = "name: EDITME\nansible.builtin.cron:"
                    cro = "\tcron_file: " + cronfile
                    if len(command_parts) > 0:
                        user = "\tuser: " + command_parts[0]
                    else:
                        user = " ".join(("\tuser:", user))
                    if "minute" in k:
                        minute = "\tminute: " + "".join(k["minute"]) if k["minute"] != ["*"] else None
                    if "hour" in k:
                        hour = "\thour: " + "".join(k["hour"]) if k["hour"] != ["*"] else None
                    if "month" in k:
                        month = "\tmonth: " + "".join(k["month"]) if k["month"] != ["*"] else None
                    if "day_of_month" in k:
                        day = "\tday: " + "".join(k["day_of_month"]) if k["day_of_month"] != ["*"] else None
                    if "day_of_week" in k:
                        weekday = "\tweekday: " + "".join(k["day_of_week"]) if k["day_of_week"] != ["*"] else None
                    cronname = "\tname: DESCRIBEME"
                    if len(command_parts) > 1:
                        job = "\tjob: " + "\"" + " ".join(command_parts[1:]) + "\"" + "\n"
                    else:
                        job = None
                    res = "\n".join(filter(None, (header, cro, user, minute, hour, month, day, weekday, cronname, job)))
                    print(res, file=o)


if __name__ == "__main__":
    main(max_content_width=120)