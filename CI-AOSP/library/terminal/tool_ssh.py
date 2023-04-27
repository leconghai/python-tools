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
        return ter

    def root_cmd(self, ter, command, expects=None):
        list_expect = ["password"]
        if expects is not None:
            list_expect.extend(expects)
        try:
            ter.sendline(command)
            i = ter.expect(list_expect)
            if i == 0:
                ter.sendline(self.password)
                if expects is not None:
                    ter.expect(expects)
        except pexpect.ExceptionPexpect as ex:
            self.ter.prompt()
            raise ex


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
            i = ter.expect(['password:', ssh_newkey])
            if i == 0:
                ter.sendline(self.password)
            elif i == 1:
                ter.sendline('yes')
                i = ter.expect(['password:'])
                if i == 0:
                    ter.sendline(self.password)
        except pexpect.ExceptionPexpect as ex:
            raise ex
        return ter

    def root_cmd(self, ter, command, expects=None):
        list_expect = ["password"]
        if expects is not None:
            list_expect.extend(expects)
        try:
            ter.sendline(command)
            i = ter.expect(list_expect)
            if i == 0:
                ter.sendline(self.password)
                if expects is not None:
                    ter.expect(expects)
        except pexpect.ExceptionPexpect as ex:
            self.ter.prompt()
            raise ex


class Terminal(spawn):
    def prompt(self):
        try:
            self.expect("XXXXXXXXXXXXX", timeout=1)
        except pexpect.ExceptionPexpect:
            pass

    def send_expect(self, cmd, expect, timeout=10):
        self.sendline(cmd)
        return self.expect(expect, timeout=timeout)
