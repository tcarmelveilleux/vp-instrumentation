"""
Case study data generation script for the VPI framework paper.

Created on: December 16, 2010
Author: Tennessee Carmel-Veilleux (tcv -at- ro.boto.ca)
Revision: $Id: caseStudyRunner.py 237 2011-01-31 21:11:20Z veilleux $

Description:
Case study data generation script for the VPI framework paper.

License (BSD):
Copyright 2010 Tennessee Carmel-Veilleux and
Ecole de technologie superieure (University of Quebec).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
    * Neither the name of Tennessee Carmel-Veilleux or Ecole de
Technologie Superieure (ETRS) nor the names of its contributors may be
used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
import os
import process
import sys
import time

# (trigger, printf, trace)
cases = { "Simics" : [("NONE","C","NONE"),],
          "Qemu" : (("NONE","C","NONE"),) }

"""
cases = { "Simics" : (("MAGIC", "SEMI","NONE"),
                      ("MAGIC", "VPI","NONE"),
                       ("MAGIC", "C","NONE"),
                       ("MAGIC", "NONE","NONE"),
                       ("GDB", "SEMI","NONE"),
                      ("GDB", "VPI","NONE"),
                       ("GDB", "NONE","NONE"),
                       ("GDB", "C","NONE"),
                       ("NONE", "NONE","NONE")),
          "Qemu" : [] }
"""
"""
          "Qemu": (("GDB", "VPI","NONE"),
                   ("GDB", "NONE","NONE"),
                   ("NONE", "NONE", "NONE"))}

cases = { "Qemu" : (   ("GDB", "NONE","NONE"),
                       ("GDB", "VPI","NONE"),
                       ("GDB", "C","NPNE"),
                       ("NONE", "NONE", "NONE")),
          "Simics": []}
"""

"""
cases = { "Simics" : (("GDB", "VPI","NONE"),
                       ("GDB", "C","PLATFORM"),
                       ("GDB", "C","VPI"),
                       ("GDB", "NONE","NONE"),
                       ("MAGIC", "VPI","NONE"),
                       ("MAGIC", "C","PLATFORM"),
                       ("MAGIC", "C","VPI"),
                       ("MAGIC", "NONE","NONE"),
                       ("NONE", "C","PLATFORM"),
                       ("NONE", "NONE","NONE")),
          "Qemu": []}

          "Qemu": (("GDB", "VPI","NONE"),
                   ("GDB", "C","PLATFORM"),
                   ("GDB", "C","VPI"),
                   ("GDB", "NONE","NONE"))}
"""
# Simulate every case "N_TRIALS" times to eliminate system jitter
N_TRIALS = 25

# Whether we must simulate or note
MUST_SIMULATE = True

# Pool of started processes
processPool = []

linkerScripts = {"Qemu" : "qemu-hosted.ld", "Simics" : "MPC8641HPCN-uboot.ld"}
Benchmarks = ("QURT",)

mainCompilerCommand = 'powerpc-eabi-gcc -I../../VPI/include -DPLATFORM_%(virtualPlatform)s -DBENCHMARK_%(benchmark)s -DVPI_TRIGGER_METHOD_%(triggerMethod)s -DPRINTF_%(printf)s -DTRACE_%(trace)s -O%(optLevel)s %(extraCaseStudyCompileArgs)s -Wall -c -fmessage-length=0 -fno-common -mcpu=7400 -te600 -o "VPI-case-study.o" "VPI-case-study.c"'
vpiCompilerCommand = 'powerpc-eabi-gcc -I../../VPI/include -DVPI_TRIGGER_METHOD_%(triggerMethod)s -O%(optLevel)s -Wall -c -fmessage-length=0 -fno-common -mcpu=7400 -te600 -o vpi.o ../../VPI/src/vpi.c'
linkCommand = 'powerpc-eabi-gcc -te600 -Xlinker -Map="test.map" -T ./%(linkerScript)s -o "%(binFilename)s" VPI-case-study.o vpi.o'

gdbSetup = r"""
set logging off
set pagination off
set architecture powerpc:common
python import sys
python import os
python import time
python sys.path.append(os.getcwd())
python sys.path.append(os.path.normpath(os.getcwd()+"/../../VPI"))
target %(target)s
python time.sleep(2.0)
#target remote 127.0.0.1:9123
#target remote | "C:\\Program Files (x86)\\CodeSourcery\\Sourcery G++-new\\bin\\powerpc-eabi-qemu-system.exe" -S -p stdio --semihosting --serial null --monitor null -kernel nul -M dummy --cpu 7400
#target remote 127.0.0.1:1234
#set debug remote 1
python BINARY_NAME = "%(binFilename)s"
%(setupTest)s
python simStartTime = time.clock()
cont
python simStopTime = time.clock()
python cpuStartTime = int(gdb.execute("x/1dw %(startTimeAddr)d",False,True).split("\t")[1])
python cpuStopTime = int(gdb.execute("x/1dw %(stopTimeAddr)d",False,True).split("\t")[1])
python print "###### CASE_STUDY1 ######\t%%d\t%%d" %% (cpuStartTime, cpuStopTime)
python print "###### CASE_STUDY2 ######\t%%.6f\t%%s" %% ((simStopTime-simStartTime), time.strftime("%%b %%d, %%Y %%H:%%M:%%S"))
quit
"""

simicsSetup = r"""
read-configuration "C:\\Users\\veilleux\\Desktop\\Schoolwork\\Maitrise\\AREXIMAS\\(THESIS) Debugging\\CaseStudy\\Simics\\CaseStudy.ckpt"

# Setup paths
add-directory "C:\\Users\\veilleux\\Desktop\\Schoolwork\\Maitrise\\AREXIMAS\\(THESIS) Debugging\\CaseStudy\\bin"
add-directory "C:\\Users\\veilleux\\Desktop\\Schoolwork\\Maitrise\\AREXIMAS\\(THESIS) Debugging\\CaseStudy"
@import sys
@sys.path.append("C:\\Users\\veilleux\\Desktop\\Schoolwork\\Maitrise\\AREXIMAS\\(THESIS) Debugging\\CaseStudy")
@sys.path.append("C:\\Users\\veilleux\\Desktop\\Schoolwork\\Maitrise\\AREXIMAS\\(THESIS) Debugging\\VPI")

# Redirect console
con0.disable-quiet

# Load binary
load-binary "%(binFilename)s"

# Input command to cause program to run
con0.input "go 40000\n" 0

# Create symtable
new-symtable symtable
symtable.load-symbols "%(binFilename)s"

# Setup context
new-context cpu0_context
cpu0_context->symtable = symtable
cpu0.set-context cpu0_context
"""

simicsForGDB = r"""
# Start GDB debuggers
new-gdb-remote "gdb-cpu0" 9123 cpu0

# Start binary by issuing GO command at U-Boot prompt
script-branch {
   con0.wait-for-string "rc = 0x0"
   gdb-cpu0.signal 2
   #quit
}
"""

simicsForMagic = r"""
# Load binary
load-binary "%(binFilename)s"

# Setup magic haps if necessary
%(magicSetup)s

# Input command to cause program to run
con0.input "go 40000\n" 0

# Start binary by issuing GO command at U-Boot prompt
script-branch {
   @simStartTime = time.clock()
   con0.wait-for-string "rc = 0x0"
   @simStopTime = time.clock()

   @cpuStartTime = quiet_run_command("phys_mem.get %(startTimeAddr)s 4")[0]
   @cpuStopTime = quiet_run_command("phys_mem.get %(stopTimeAddr)s 4")[0]
   @print "###### CASE_STUDY1 ######\t%%d\t%%d" %% (cpuStartTime, cpuStopTime)
   @print "###### CASE_STUDY2 ######\t%%.6f\t%%s" %% ((simStopTime-simStartTime), time.strftime("%%b %%d, %%Y %%H:%%M:%%S"))

   quit
}

run
"""

QurtResult = """
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.015000+0.140624j) x2 = (0.015000-0.140624j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.010000+0.099499j) x2 = (0.010000-0.099499j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
Roots: x1 = (0.020000+0.282135j) x2 = (0.020000-0.282135j)
"""

def clean_dead_processes():
    """
    Kill all still running processes
    """
    global processPool

    for process in processPool:
        if process.poll() == None:
            process.kill()

def run(command, stdout = sys.stdout, timeout = 1000.0):
    """
    Run a command and wait for it to be done
    """

    global processPool
    # Show command we want to run (emulating a shell console)
    print command

    trials = 0
    success = False

    while trials < 5:
        # Try running the tool until successful or too many attempts have been tried
        try:
            cmdProcess = process.ProcessOpen(command, stdout = stdout, stderr = stdout)

            # Save process in pool for later killing
            processPool.append(cmdProcess)

            # Wait for process to finish with return code 0 (no error)
            retcode = cmdProcess.wait(timeout = timeout)
            if retcode != 0:
                print "### Tool run problem: retcode %d, retrying... " % retcode
                trials += 1
                continue
            else:
                success = True
                break
        except process.ProcessError, e:
            print "### Tool run problem: %s, retrying... " % (str(e))
            trials += 1
            continue

    clean_dead_processes()

    if not success:
        raise RuntimeError("### Could not get tool running !")

def run_background(command, stdout = sys.stdout):
    """
    Run a command in the background. We expect it to finish on its own.
    """

    global processPool
    # Show command we want to run (emulating a shell console)
    print command + " &"

    # Run the command proper, killing all children on error
    try:
        cmdProcess = process.ProcessOpen(command, stdout = stdout, stderr = stdout)

        processPool.append(cmdProcess)
    except process.ProcessError, e:
        print >>sys.stderr, "Execution failed:", e
        clean_dead_processes()
        raise RuntimeError("Tool run problem !")

def get_timing_addresses(binFilename):
    """
    Find the symbol address of CASE_STUDY_START_TIME and CASE_STUDY_STOP_TIME from test.map
    generated by linking of the last compile cycle.

    - binFilename is the binary filename of the last compiled, only used for error
    messages.
    """
    fin = file("test.map", "r")
    mapContents = fin.read()
    fin.close()

    match = re.search(r"^\s*0x([a-fA-F0-9]+)\s*CASE_STUDY_START_TIME$", mapContents, re.MULTILINE)

    if match:
        startTimeAddr = int(match.group(1),16)
        print match.group(1)
    else:
        raise RuntimeError("Cannot find CASE_STUDY_START_TIME in binary %s" % binFilename)

    match = re.search(r"^\s*0x([a-fA-F0-9]+)\s*CASE_STUDY_STOP_TIME$", mapContents, re.MULTILINE)
    if match:
        stopTimeAddr = int(match.group(1),16)
        print match.group(1)
    else:
        raise RuntimeError("Cannot find CASE_STUDY_STOP_TIME in binary %s" % binFilename)

    print startTimeAddr, stopTimeAddr
    return (startTimeAddr, stopTimeAddr)

def compile(context):
    # Compile current version of test program
    run(mainCompilerCommand % context)
    run(vpiCompilerCommand % context)
    run(linkCommand % context)

    # Output information about the binary we just compiled to a log file
    textSize, dataSize, rodataSize, bssSize = gather_section_sizes(binFilename)

    lineData = []
    lineData.append(context["binFilename"])
    lineData.append(context["virtualPlatform"])
    lineData.append(context["benchmark"])
    lineData.append(context["triggerMethod"])
    lineData.append(context["printf"])
    lineData.append("NONE") # for putc (backward compatibility)
    lineData.append(context["trace"])
    lineData.append(context["optLevel"])
    lineData.append("%d" % textSize)
    lineData.append("%d" % dataSize)
    lineData.append("%d" % rodataSize)
    lineData.append("%d" % bssSize)

    print >> context["binariesResultsFile"], "\t".join(lineData)

def run_gdb(context):
    # Runs GDB in the current test context
    context["setupTest"] = ""

    # Prepare the GDB environment according to the test-specific options
    if context["virtualPlatform"] == "Qemu":
        # QEMU requires loading of the binary through GDB
        context["setupTest"] += "load\n"

    if context["triggerMethod"] == "GDB":
        # If triggering through GDB, setup the VPI trigger by running a GDB python script
        context["setupTest"] += "source ../setup-vpi-gdb.py"
    else:
        # For other cases, the triggering is setup externally from GDB
        context["setupTest"] += ""

    binFilename = context["binFilename"]
    gdbScriptFilename = binFilename[:-4] + ".gdb"
    fout = file(gdbScriptFilename, "w+")
    print >> fout, gdbSetup % context
    fout.close()

    logFilename = "../temp/" + os.path.basename(binFilename)[:-4] + ".log"

    logFile = file(logFilename, "w+")
    run("powerpc-eabi-gdb -x %s %s" % (gdbScriptFilename, binFilename), stdout = logFile)
    logFile.close()

def run_simics(context, background = True):
    if context["triggerMethod"] == "GDB":
        context["simicsScript"] = simicsSetup + simicsForGDB
    else:
        if context["triggerMethod"] == "MAGIC":
            context["magicSetup"] = "enable-magic-breakpoint\nrun-python-file filename = setup-vpi-test-haps.py"
        else:
            context["magicSetup"] = ""

        context["simicsScript"] = simicsSetup + simicsForMagic

    binFilename = context["binFilename"]
    simicsScriptFilename = binFilename[:-4] + ".simics"
    fout = file(simicsScriptFilename, "w+")
    print >> fout, context["simicsScript"] % context
    fout.close()

    try:
        logFile = file(context["logFilename"], "w+")
    except:
        clean_dead_processes()
        time.sleep(0.5)
        logFile = file(logFilename, "w+")

    simicsCommand = r"cmd /c C:\Users\veilleux\Desktop\simics-workspace\simics.bat -no-win -no-wmultithread -x %s" % (simicsScriptFilename)
    if background:
        run_background(simicsCommand, stdout = logFile)
    else:
        run(simicsCommand, stdout = logFile)

    #runBackground(r"env", stdout = logFile)
    time.sleep(2.0)

def gather_test_data(filename):
    """
    Reads a test log from "filename" to gather test timing data.

    Returns a tuple (cpuStartTime, cpuStopTime, simTimeDuration, simDate)
    """
    fin = file(filename, "r")
    testLog = fin.read()
    fin.close()

    cputTimesRegExp = re.compile(r"^###### CASE_STUDY1 ######\t(\d+)\t(\d+)$", re.MULTILINE)
    testRunRegExp = re.compile(r"^###### CASE_STUDY2 ######\t([-+]?\b[0-9]*\.?[0-9]+\b)\t([a-zA-Z0-9,: ]+)$", re.MULTILINE)

    match = cputTimesRegExp.search(testLog)
    if match:
        cpuStartTime = int(match.group(1))
        cpuStopTime = int(match.group(2))
    else:
        return None

    match = testRunRegExp.search(testLog)
    if match:
        simTimeDuration = float(match.group(1))
        simDate = match.group(2).strip()
    else:
        return None

    #return ((0xFFFFFFFFL - cpuStartTime), (0xFFFFFFFFL - cpuStopTime), simTimeDuration, simDate)
    return (cpuStartTime, cpuStopTime, simTimeDuration, simDate)

def gather_section_sizes(binFilename):
    """
    Returns a tuple (textSize, dataSize, rodataSize, bssSize) from
    data gathered with objdump on "binFilename".
    """
    logFile = file("objdumpOut.txt", "w+")
    run('powerpc-eabi-objdump -h -j .text -j .data -j .rodata -j .bss "%s"' % (binFilename), stdout = logFile)
    logFile.close()

    fin = file("objdumpOut.txt", "r")
    objDumpLog = fin.read()
    fin.close()

    sizes = []
    for sectionName in ("text", "data", "rodata", "bss"):
        match = re.search(r"^ *\d+ \.%s *([0-9a-fA-F]+) *([0-9a-fA-F]+)" % sectionName, objDumpLog, re.MULTILINE)

        if match:
            sizes.append(int(match.group(1), 16))
        else:
            return None

    return tuple(sizes)

def simulate(context):
    # Run a single simulation of a test case

    binFilename = context["binFilename"]
    triggerMethod = context["triggerMethod"]
    virtualPlatform = context["virtualPlatform"]

    # Find start time and stop time addresses to get the values

    context["startTimeAddr"], context["stopTimeAddr"] = get_timing_addresses(binFilename)

    # Run the simulation
    if triggerMethod == "GDB" or virtualPlatform == "Qemu":
        # GDB case

        if virtualPlatform == "Qemu":
            context["target"] = "qemu 7400"
        elif virtualPlatform == "Simics":
            context["target"] = "remote 127.0.0.1:9123"
            run_simics(context)

        run_gdb(context)
        # Kill the leftover running Simics
        clean_dead_processes()
    else:
        # Simics case
        run_simics(context, background = False)

    # Obtain simulation results
    cpuStartTime, cpuStopTime, simTimeDuration, simDate = gather_test_data(context["logFilename"])

    # Log results to file
    lineData = []
    lineData.append(context["binFilename"])
    lineData.append("%d" % cpuStartTime)
    lineData.append("%d" % cpuStopTime)
    lineData.append("%.3f" % simTimeDuration)
    lineData.append(simDate)

    print >> context["simResultsFile"], "\t".join(lineData)

if __name__ == "__main__":
    # Make sure we kill all children on exit
    import atexit
    atexit.register(clean_dead_processes)

    # Change to correct work dir
    os.chdir(r'C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\src')

    # Prepare log file for compiled binaries
    binariesResultsFilename = "../temp/binaries.tsv"
    binariesResultsFile = file(binariesResultsFilename, "w+")
    print >> binariesResultsFile, "binFilename\tvirtualPlatform\tbenchmark\ttriggerMethod\tprintf\tputc\ttrace\toptLevel\ttextSize\tdataSize\trodataSize\tbssSize"

    # Prepare log file for simulation results
    simResultsFilename = "../temp/simResults.tsv"
    simResultsFile = file(simResultsFilename, "w+")
    print >> simResultsFile, "binFilename\tcpuStartTime\tcpuStopTime\tsimTimeDuration\tsimDate"

    for virtualPlatform in ("Simics", "Qemu"):
        for benchmark in Benchmarks:
            for case in cases[virtualPlatform]:
                triggerMethod, printf, trace = case
                for optLevel in ("0", "1", "2", "3"):
                    binFilename = "../bin/VPI-case-study-%(virtualPlatform)s-%(benchmark)s-trig_%(triggerMethod)s-pf_%(printf)s-trace_%(trace)s-O%(optLevel)s.elf" % locals()

                    if trace == "GCC":
                        extraCaseStudyCompileArgs = "-finstrument-functions"
                    else:
                        extraCaseStudyCompileArgs = ""

                    linkerScript = linkerScripts[virtualPlatform]
                    logFilename = "../temp/" + os.path.basename(binFilename)[:-4] + ".log"

                    # Skip test cases already run (case of crash due to compile problem
                    #if os.path.exists(binFilename):
                    #    continue

                    # Compile test program
                    compile(locals())

                    # Simulate test program N times
                    if MUST_SIMULATE and optLevel == "2":
                        for i in xrange(N_TRIALS):
                            simulate(locals())

    binariesResultsFile.close()
    simResultsFile.close()
"""
../src/VPI-case-study.c: In function 'main':
../src/VPI-case-study.c:179:6: warning: unused variable 'flag'
../src/VPI-case-study.c:188:3: warning: 'VPI_temp_trigger' is used uninitialized in this function
../src/VPI-case-study.c:195:3: warning: 'VPI_temp_trigger' is used uninitialized in this function
../src/VPI-case-study.c:202:3: warning: 'VPI_temp_trigger' is used uninitialized in this function
'Finished building: ../src/VPI-case-study.c'
' '
'Building file: ../src/vpi.c'
'Invoking: Sourcery G++ C Compiler'
powerpc-eabi-gcc -DVPI_TRIGGER_METHOD_GDB -O3 -Wall -c -fmessage-length=0 -fno-common -MMD -MP -MF"src/vpi.d" -MT"src/vpi.d" -mcpu=7400 -te600 -o"src/vpi.o" "../src/vpi.c"
'Finished building: ../src/vpi.c'
' '
'Building target: VPI-case-study'
'Invoking: Sourcery G++ C Linker'
powerpc-eabi-gcc -te600 -Xlinker -Map="VPI-case-study.map" -T qemu-hosted.ld -mcpu=7400 -te600 -o"VPI-case-study" "@objs.rsp" "@user_objs.rsp" "@libs.rsp"
'Finished building target: VPI-case-study'
' '
cs-make --no-print-directory post-build
powerpc-eabi-size "VPI-case-study"
"""