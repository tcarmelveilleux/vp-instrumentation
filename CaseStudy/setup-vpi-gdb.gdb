set logging off
set pagination off
python import sys
python import os
python sys.path.append(os.getcwd())
target remote 127.0.0.1:9123
#target remote | "C:\\Program Files (x86)\\CodeSourcery\\Sourcery G++-new\\bin\\powerpc-eabi-qemu-system.exe" -S -p stdio,quit-on-eof --semihosting --serial null --monitor null -kernel nul -M dummy --cpu 7400
#target remote 127.0.0.1:1234
file "c:\\xtratum\\workspace\\CCECE-test\\Release\\CCECE-test"
load
source setup-vpi-gdb.py
# ADD SIMULATION TIMING CODE
cont

