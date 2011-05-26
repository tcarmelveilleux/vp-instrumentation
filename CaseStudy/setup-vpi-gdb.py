import vpi
import gdb
import re
import subprocess
import vpiFuncs

global BINARY_NAME
#BINARY_NAME = r'c:\xtratum\workspace\CCECE-test\Release\CCECE-test'

class PpcGdbDebuggerInterface(vpi.GdbDebuggerInterface, vpi.PpcApplicationBinaryInterface):
    def __init__(self, inferior):
        vpi.GdbDebuggerInterface.__init__(self, inferior)
        vpi.PpcApplicationBinaryInterface.__init__(self)

class PpcGdbVpiInterface(vpi.PpcVpiInterface, vpi.PpcGdbVpiTriggerMethod):
    def __init__(self, debuggerInterface):
        vpi.PpcVpiInterface.__init__(self, debuggerInterface)
        vpi.PpcGdbVpiTriggerMethod.__init__(self)

class VpiHandleCommand (gdb.Command):
    def __init__ (self, vpiInterface):
        super (VpiHandleCommand, self).__init__ ("vpi-handle", gdb.COMMAND_OBSCURE)
        self.vpiInterface = vpiInterface

    def invoke (self, arg, from_tty):
        self.vpiInterface.process()

# Initialize the VPI interfaces with the inferior
inferior = gdb.inferiors()[0]
debuggerInterface = PpcGdbDebuggerInterface(inferior)
vpiInterface = PpcGdbVpiInterface(debuggerInterface)
for func in vpiFuncs.functions:
    vpiInterface.register(func)

# Register the "vpi-handle" command
VpiHandleCommand(vpiInterface)

# Add watchpoint to dummy variable address

# Run objdump to get section headers
output = subprocess.Popen(["objdump", "-x", BINARY_NAME], stdout=subprocess.PIPE).communicate()[0]

# Get the .data section header start address and size
dataSectionMatch = re.search(r"^ *\d+ \.data *([0-9a-fA-F]+) *([0-9a-fA-F]+)", output, re.MULTILINE)
if dataSectionMatch:
    size = long(dataSectionMatch.group(1), 16)
    start = long(dataSectionMatch.group(2), 16)
    print "VPI dummy search in .data (start = 0x%x, size = %d)" % (start, size)
    print inferior
    print inferior.search_memory(0x10009290, 1136, "VPIvpiVPIvpiVPIvpiVPIvp")
    # Dummy variable is 4 bytes directly preceding marker string
    vpiDummyAddress = inferior.search_memory(start, size, "VPIvpiVPIvpiVPIvpiVPIvp") - 4
else:
    raise RuntimeError("Cannot obtain .data region from binary '%s'" % BINARY_NAME)

# Add an access watchpoint
vpiDummyWatchpoint = gdb.Breakpoint("*(unsigned long *)%ld" % vpiDummyAddress, gdb.BP_WATCHPOINT, gdb.WP_ACCESS)
vpiDummyWatchpoint.silent = True

# Set the watchpoint
tempFilename = "TEMP%d.gdb" % os.getpid()

outfile = file(tempFilename, "w+")
# Multi-line commands must be written to a temporary file
outfile.write("commands %d\nvpi-handle\ncontinue\nend\n" % vpiDummyWatchpoint.number)
outfile.close()

# Install vpi command handler indirectly
gdb.execute("source %s" % tempFilename)

# Delete temporary command file
if os.path.exists(tempFilename):
    try:
        os.remove(tempFilename)
    except OSError:
        pass

"""
# Extract the address of every "rlwimi r0,r0,0,0,9" instruction
# The file out.S is generated with powerpc-eabi-objdump -d -j .text ELF_FILE > out.S

vpi_re = re.compile(r"^\s+([0-9a-f]+):\s+[0-9a-f ]+\srlwimi\s+r0,r0,0,0,9", re.MULTILINE)
vpi_addresses = []

infile = file("C:\\xtratum\\workspace\\CCECE-test\\Debug\\out.S", "r")

for line in infile:
    match = vpi_re.search(line)
    if match:
        # Convert the address match (ie: "c0000123") to a number and save
        vpi_addresses.append(long(match.group(1),16))

infile.close()

# Set all required breakpoints
tempFilename = "TEMP%d.gdb" % os.getpid()

outfile = file(tempFilename, "w+")
for address in vpi_addresses:
    bp = gdb.Breakpoint("*0x%x" % address)
    # VPI Breakpoints are silent and run the vpi-handler
    bp.silent = True

    # Multi-line commands must be written to a temporary file
    outfile.write("command %d\nvpi-handle\ncontinue\nend\n" % bp.number)
outfile.close()

# Install vpi handlers on all breakpoints
gdb.execute("source %s" % tempFilename)

# Delete temporary command file
if os.path.exists(tempFilename):
    try:
        os.remove(tempFilename)
    except OSError:
        pass
"""