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
                    print("name: EDITME", file=o)
                    print("ansible.builtin.cron:", file=o)
                    print("\tcron_file: " + cronfile, file=o)
                    print("\tuser: " + command_parts[0], file=o)
                    print("\tminute: " + "".join(k["minute"]), file=o)
                    print("\thour: " + "".join(k["hour"]), file=o)
                    print("\tmonth: " + "".join(k["month"]), file=o)
                    print("\tday: " + "".join(k["day_of_month"]), file=o)
                    print("\tweekday: " + "".join(k["day_of_week"]), file=o)
                    print("\tname: DESCRIBEME", file=o)
                    print("\tjob: " + "\"" + " ".join(command_parts[1:]) + "\"", file=o)
                    print("", file=o)

if __name__ == "__main__":
    main()