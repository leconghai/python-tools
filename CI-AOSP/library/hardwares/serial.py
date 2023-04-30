import sys

import pexpect
from library.terminal.tool_ssh import Ssh_raw


class Serial(Ssh_raw):
    def __init__(self, server, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)

    def picocom(self, device):
        self.root_cmd(self.ter, f"sudo picocom -b 115200 {device}", ["Terminal ready"])
        print(f"Serial available")
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

