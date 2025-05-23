import sys
from time import sleep
from library.terminal.tool_ssh import Ssh_tool
import pexpect


class SDmux(Ssh_tool):
    def __init__(self, server, device_file, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)
        self.ID = device_file
        self.wait_time = 2
        self.wait_mount = 5
        self.root_cmd(self.ter, f"sudo usbsdmux {self.ID} get", ["dut", "host", "off"])
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

    def get_disk_device(self):
        found = 0
        list_sdcard = ["sda", "sdb", "sdc", "sdd"]
        for disk in list_sdcard:
            try:
                self.root_cmd(self.ter,f"sudo fdisk -l /dev/{disk}", ["sdmux HS-SD/MMC"])
            except pexpect.ExceptionPexpect as ex:
                continue
            found = 1
            break
        if found == 1:
            print(f"Disk is: /dev/{disk}")
            return disk
        else:
            print(f"can not found disk")
            raise ex