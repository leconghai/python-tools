import sys
from time import sleep

import pexpect

from library.configs import Configs
from library.terminal.tool_ssh import  Ssh_raw


class Relay(Ssh_raw):
    def __init__(self, server, device_id, log_file=sys.stdout):
        super().__init__(server)
        self.ter = self.create_ter(log_file)
        self.ID = device_id
        self.wait_time = 1
        try:
            i = self.ter.send_expect(f"sudo hidusb-relay-cmd state", ["password", self.ID])
            if i == 0:
                self.ter.sendline(self.password)
            self.ter.prompt()
            print(f"relay available")
        except pexpect.ExceptionPexpect as ex:
            self.ter.prompt()
            raise ex

    def p_off(self, port):
        self.ter.sendline(f"sudo hidusb-relay-cmd ID={self.ID} OFF {port}")
        self.ter.prompt()
        sleep(self.wait_time)

    def p_on(self, port):
        self.ter.sendline(f"sudo hidusb-relay-cmd ID={self.ID} ON {port}")
        self.ter.prompt()
        sleep(self.wait_time)


class Reset_device(Relay):
    def __init__(self, reset_id_js, log_file=sys.stdout):
        reset_devices = Configs().get_topology()["reset_devices"][reset_id_js]
        relay = Configs().get_topology()["relays"][reset_devices["relay"]]
        server = Configs().get_topology()["servers"][relay["server"]]
        super().__init__(server, relay["name"], log_file)
        self.port = reset_devices["port"]

    def power_reset(self):
        self.p_off(self.port)
        self.p_on(self.port)

    def power_off(self):
        self.p_off(self.port)

    def power_on(self):
        self.p_on(self.port)