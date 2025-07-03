import datetime
import json
import re
import sys

import click

"""
name: foobar|ARG
ansible.builtin.cron:
    cron_file: ARG
    user: str(command[0])
    minute: int
    hour: int
    name: description
    job: str(command[1:])
"""

@click.command()
@click.option("--infile", type=click.File('r'), default=sys.stdin)
@click.option("--outfile", default="ansible_from_json.yml")
@click.option("--cronfile", default="foo")
def main(infile: str, outfile: str, cronfile: str):
    n = int(datetime.datetime.timestamp(datetime.datetime.now()))
    outfile = outfile + "." + str(n)
    with infile as f:
        data = json.load(f)
        # print(data)
        if "schedule" in data:
            for k in data["schedule"]:
                with open(outfile, "a") as o:
                    command: str = k["command"]
                    command_parts = re.split(r"\s+", command)
                    # print(command_parts)
                    header = "name: EDITME\nansible.builtin.cron:"
                    cro = "\tcron_file: " + cronfile
                    user = "\tuser: " + command_parts[0]
                    minute = "\tminute: " + "".join(k["minute"]) if k["minute"] != ["*"] else None
                    hour = "\thour: " + "".join(k["hour"]) if k["hour"] != ["*"] else None
                    month = "\tmonth: " + "".join(k["month"]) if k["month"] != ["*"] else None
                    day = "\tday: " + "".join(k["day_of_month"]) if k["day_of_month"] != ["*"] else None
                    weekday = "\tweekday: " + "".join(k["day_of_week"]) if k["day_of_week"] != ["*"] else None
                    cronname = "\tname: DESCRIBEME"
                    job = "\tjob: " + "\"" + " ".join(command_parts[1:]) + "\"" + "\n"
                    res = "\n".join(filter(None, (header, cro, user, minute, hour, month, day, weekday, cronname, job)))
                    print(res, file=o)

if __name__ == "__main__":
    main()