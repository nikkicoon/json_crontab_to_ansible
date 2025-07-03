import datetime
import json
import re
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
@click.option("--infile", default="crontabs.json")
@click.option("--outfile", default="ansible_from_json.yml")
@click.option("--cronfile", default="foo")
def main(infile: str, outfile: str, cronfile: str):
    n = int(datetime.datetime.timestamp(datetime.datetime.now()))
    outfile = outfile + "." + str(n)
    with open(infile, "r") as f:
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
                    minute = "\tminute: " + "".join(k["minute"])
                    hour = "\thour: " + "".join(k["hour"])
                    month = "\tmonth: " + "".join(k["month"])
                    day = "\tday: " + "".join(k["day_of_month"])
                    weekday = "\tweekday: " + "".join(k["day_of_week"])
                    cronname = "\tname: DESCRIBEME"
                    job = "\tjob: " + "\"" + " ".join(command_parts[1:]) + "\"" + "\n"
                    res = "\n".join((header, cro, user, minute, hour, month, day, weekday, cronname, job))
                    print(res, file=o)

if __name__ == "__main__":
    main()