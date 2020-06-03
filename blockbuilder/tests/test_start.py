import os
import sys
import subprocess
from blockbuilder.app import start


def test_start(qtbot):
    builder = start.main(True)
    qtbot.addWidget(builder)


def test_subprocess_start(qapp, fake_process):
    command = [
        sys.executable, '-uc',
        'from blockbuilder.app import start; start.main()'
    ]
    env = os.environ
    env["BB_TESTING"] = "True"
    fake_process.register_subprocess(command)
    process = subprocess.Popen(command, env=env)
    out, _ = process.communicate()
    assert process.returncode == 0
