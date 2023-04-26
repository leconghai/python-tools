import sys
from time import sleep

import pexpect

from library.configs import Configs
from library.terminal.tool_ssh import Ssh_raw, Ssh_tool


class SDmux(Ssh_tool):
    def __init__(self, server, device_file, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)
        self.ID = device_file
        self.wait_time = 1
        self.wait_mount = 3
        try:
            self.ter.sendline(f"sudo usbsdmux {self.ID} get")
            i = self.ter.expect(["password", "dut", "host", "off"])
            if i == 0:
                self.ter.sendline(self.password)
                self.ter.expect(["dut", "host", "off"])
            print(f"sdmux available")
        except pexpect.ExceptionPexpect as ex:
            self.ter.prompt()
            raise ex

    def mode_dut(self):
        self.ter.sendline(f"sudo usbsdmux {self.ID} dut")
        i = self.ter.expect(["password", self.ter.PROMPT])
        if i == 0:
            self.ter.sendline(self.password)
            self.ter.prompt()
        sleep(self.wait_time)
        self.ter.sendline(f"sudo usbsdmux {self.ID} get")
        self.ter.prompt()
        if "dut" not in self.ter.before:
            print("sdmux set dut faild")
            return None
        sleep(self.wait_mount)

    def mode_host(self):
        self.ter.sendline(f"sudo usbsdmux {self.ID} host")
        i = self.ter.expect(["password", self.ter.PROMPT])
        if i == 0:
            self.ter.sendline(self.password)
            self.ter.prompt()
        sleep(self.wait_time)
        self.ter.sendline(f"sudo usbsdmux {self.ID} get")
        self.ter.prompt()
        if "host" not in self.ter.before:
            print("sdmux set host faild")
            return None
        sleep(self.wait_mount)


class switch_sd(SDmux):
    def __init__(self, sdmux_id, log_file=sys.stdout):
        sdmux_conf = Configs().get_topology()["sdmux"][sdmux_id]
        server = Configs().get_topology()["servers"][sdmux_conf["server"]]
        super().__init__(server, sdmux_conf["device"], log_file)
