import sys

import pexpect
from pexpect import pxssh, spawn


class Ssh_tool:
    def __init__(self, server):
        self.host_addr = server["host_addr"]
        self.user_name = server["user_name"]
        self.password = server["password"]

    def create_ter(self, log_file=sys.stdout):
        try:
            ter = pxssh.pxssh(encoding='utf-8', logfile=log_file)
            ter.login(self.host_addr, self.user_name, self.password)
        except pxssh.ExceptionPexpect as ex:
            raise ex
            # print(str(ex))
            # return None
        return ter


class Ssh_raw:
    def __init__(self, server):
        self.host_addr = server["host_addr"]
        self.user_name = server["user_name"]
        self.password = server["password"]

    def create_ter(self, log_file=sys.stdout):
        ter = Terminal("/bin/bash", encoding='utf-8', logfile=log_file)
        try:
            ter.sendline(f"ssh {self.user_name}@{self.host_addr}")
            ssh_newkey = 'Are you sure you want to continue connecting'
            # i = ter.expect([ssh_newkey, 'password:'])
            # if i == 0:
            #     ter.sendline('yes')
            i = ter.expect([ssh_newkey, 'password:'])
            if i == 1:
                ter.sendline(self.password)
        except pexpect.ExceptionPexpect as ex:
            raise ex
            # print(str(ex))
            # return None
        return ter


class Terminal(spawn):
    def prompt(self):
        try:
            self.expect("-------------", timeout=1)
        except pexpect.ExceptionPexpect:
            pass

    def send_expect(self, cmd, expect, timeout=10):
        self.sendline(cmd)
        return self.expect(expect, timeout=timeout)
