# test: unsafe os.system should be detected by security/semgrep/rules.yml
import os

def do_bad():
    os.system("echo hello")  # <- This should trigger proj-no-os-system
