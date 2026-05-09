#!/usr/bin/env python3

import os
import sys
from subprocess import check_call
from glob import glob
import better_exchook
better_exchook.install()

def cmd(args):
    print("$", " ".join(map(repr, args)))
    check_call(args)


destination = "server.az2000.de:azmacbookpro2014-backup/"
includes = [
    ".ssh",
    "*.py",
    "*.sh",
    "old_backup",
    "old_backup_2",
    "cd-backup",
    "ArGo Software Design",
    "db",
    "i6",
    "Programmierung/sparsernn",
    "Programmierung/ParseOggVorbis",
    "Programmierung/inmationdev",
    "Programmierung/AI",
    "Programmierung/AI2",
    "Programmierung/AZNNet",
    "Programmierung/backup_system",
    "Programmierung/coding-exercise",
    "Programmierung/intelligent-system",
    "Programmierung/intelligent-patcher",
    "Programmierung/intelligent-builder",
    "Programmierung/live-helper",
    "Programmierung/mgmt-sys",
    "Programmierung/NeuralNets",
    "Programmierung/organizer",
    "Programmierung/PictureSlider",
    "Programmierung/personal_assistant",
    "Programmierung/ProblemSolverFramework",
    "Programmierung/turingmachine",
    "Library/Application Support/Slack",
    "Library/Application Support/Tunnelblick",
    "Library/Application Support/com.albertzeyer.MusicPlayer",
    "Library/Application Support/TimeCapture",
    "Library/Application Support/Skype",
    "Spiele/Alt",
    "Spiele/ALBERT",
    "sound-records ccccamp2011",
    ]

# StackOverflow 9952000 Using Rsync include and exclude ...
include_args = []
for incl in includes:
    if "*" in incl:
        assert len(glob(incl)) > 0
    else:
        assert os.path.exists(incl)
    incl_parts = incl.split("/")
    for i in range(len(incl_parts)):
        incl_sub = "/".join(incl_parts[:i + 1])
        if incl_sub not in include_args:
            include_args += ["--include", incl_sub]
    if os.path.isdir(incl):
        include_args += ["--include", incl + "/***"]

cmd(["rsync"] + sys.argv[1:] + ["-avP", ".", "--delete"] + include_args + ["--exclude=*", destination])
