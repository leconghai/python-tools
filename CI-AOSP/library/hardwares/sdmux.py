import sys
from time import sleep
from library.terminal.tool_ssh import Ssh_tool


class SDmux(Ssh_tool):
    def __init__(self, server, device_file, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)
        self.ID = device_file
        self.wait_time = 1
        self.wait_mount = 3
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} get", ["password", "dut", "host", "off"])
        print(f"sdmux available")

    def mode_dut(self):
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} dut", [self.ter.PROMPT])
        sleep(self.wait_time)
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} get", ["dut"])
        sleep(self.wait_mount)

    def mode_host(self):
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} host", [self.ter.PROMPT])
        sleep(self.wait_time)
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} get", ["host"])
        sleep(self.wait_mount)