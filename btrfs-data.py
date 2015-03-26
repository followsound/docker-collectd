#!/usr/bin/env python

import os
import subprocess
import sys
import time

hostname = os.getenv("HOSTNAME", subprocess.check_output(["/bin/uname", "-n"])).strip()
interval = float(os.getenv("COLLECTD_INTERVAL", 10))
blocksize = pow(1024, 3)

def convert_value(value):
    exp = {'K':1, 'M':2, 'G':3}
    # different versions of btrfs tools display xiB as xiB or xB
    value = value.replace("iB","")
    value = value.replace("B","")
    if value[-1].isdigit():
        return float(value)
    else:
        num = float(value[0:-2])
        return num * pow(1024, exp[value[-1]])

def btrfs_filesystem_stats(fs):
    allocated = 0.0
    used = 0.0
    with open(fs) as btrfs:
        for line in btrfs:
            data = line.split(": ")[1].split(", ")
            t = data[0].split("=")[1]
            allocated += convert_value(t)
            u = data[1].split("=")[1]
            used += convert_value(u)
    df = subprocess.check_output(["df", "-B", str(blocksize), fs]).split("\n")
    total = float(df[1].split()[1]) * blocksize

    fs_name = fs.split("/")[-1]
    print("PUTVAL {}/exec-btrfs_{}/gauge-bytes_total interval={} N:{:.0f}".format(hostname, fs_name, interval, total))
    print("PUTVAL {}/exec-btrfs_{}/gauge-bytes_allocated interval={} N:{:.0f}".format(hostname, fs_name, interval, allocated))
    print("PUTVAL {}/exec-btrfs_{}/gauge-bytes_used interval={} N:{:.0f}".format(hostname, fs_name, interval, used))
 
while True:
    btrfs_filesystem_stats("/var/lib/btrfs-stats/root")
    sys.stdout.flush()
    time.sleep(interval)
