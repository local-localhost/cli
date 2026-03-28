import subprocess
from argparse import Namespace

from caelestia.utils.paths import c_cache_dir

DEFAULT_LOG_RULES = ";".join([
    "qt.qml.propertyCache.append.warning=false",
    "quickshell.dbus.objectmanager.warning=false",
    "quickshell.io.fileview.warning=false",
    "quickshell.service.notifications.warning=false",
])


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.show:
            # Print the ipc
            self.print_ipc()
        elif self.args.log:
            # Print the log
            self.print_log()
        elif self.args.kill:
            # Kill the shell
            self.shell("kill")
        elif self.args.message:
            # Send a message
            self.message(*self.args.message)
        else:
            # Start the shell
            args = ["qs", "-c", "caelestia", "-n"]
            args.extend(["--log-rules", self.log_rules()])
            if self.args.daemon:
                args.append("-d")
                subprocess.run(args)
            else:
                shell = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)

                # Ensure stdout is not None for the type checker
                if shell.stdout:
                    for line in shell.stdout:
                        if self.filter_log(line):
                            print(line, end="")

    def shell(self, *args: str) -> str:
        return subprocess.check_output(["qs", "-c", "caelestia", "--log-rules", self.log_rules(), *args], text=True)

    def log_rules(self) -> str:
        return self.args.log_rules or DEFAULT_LOG_RULES

    def filter_log(self, line: str) -> bool:
        return f"Cannot open: file://{c_cache_dir}/imagecache/" not in line

    def print_ipc(self) -> None:
        print(self.shell("ipc", "show"), end="")

    def print_log(self) -> None:
        log = self.shell("log", "-r", self.log_rules())
        # FIXME: remove when logging rules are added/warning is removed
        for line in log.splitlines():
            if self.filter_log(line):
                print(line)

    def message(self, *args: list[str]) -> None:
        print(self.shell("ipc", "call", *args), end="")
