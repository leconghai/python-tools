import sys
from time import sleep
from library.terminal.tool_ssh import  Ssh_tool


class Relay(Ssh_tool):
    def __init__(self, server, device_id, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)
        self.ID = device_id
        self.wait_time = 1
        self.root_cmd(self.ter, f"sudo hidusb-relay-cmd state", [self.ID])
        print(f"relay available")

    def p_off(self, port):
        self.root_cmd(self.ter, f"sudo hidusb-relay-cmd ID={self.ID} OFF {port}", [self.ter.PROMPT])
        sleep(self.wait_time)

    def p_on(self, port):
        self.root_cmd(self.ter, f"sudo hidusb-relay-cmd ID={self.ID} ON {port}", [self.ter.PROMPT])
        sleep(self.wait_time)
