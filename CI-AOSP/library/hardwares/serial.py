import sys

import pexpect

from library.configs import Configs
from library.terminal.tool_ssh import Ssh_raw


class Serial(Ssh_raw):
    def __init__(self, server, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)

    def picocom(self, device):
        try:
            self.ter.send_expect(f"sudo picocom -b 115200 {device}", f"password")
            self.ter.send_expect(f"{self.password}", f"Terminal ready")
            print(f"Serial available")
        except pexpect.ExceptionPexpect:
            print(f"Serial not available")
            self.ter.close()
            return None
        return self.ter

    def telnet(self, port):
        try:
            self.ter.send_expect(f"telnet {self.host_addr} {port}", f"ser2net")
            print(f"Serial available")
        except pexpect.ExceptionPexpect:
            print(f"Serial not available")
            self.ter.close()
            return None
        return self.ter


class serial_ter(Serial):
    def __init__(self, serial_id, log_file=sys.stdout):
        serial_conf = Configs().get_topology()["serials"][serial_id]
        server = Configs().get_topology()["servers"][serial_conf["server"]]
        super().__init__(server, log_file)
        self.device = serial_conf["device"]
        self.port = serial_conf["port"]

    def picocom_ter(self):
        return self.picocom(self.device)

    def telnet_com(self):
        return self.telnet(self.port)
