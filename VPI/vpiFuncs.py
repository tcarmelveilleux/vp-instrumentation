#!/usr/bin/python
# -*- coding: cp1252 -*-
"""
VPI functions (VPIFs) implementation for VPI prototype

Created on: 25/05/2011
Author: Tennessee Carmel-Veilleux (tennessee.carmelveilleux@gmail.com)
Revision: $Rev$

Copyright 2011 Tennessee Carmel-Veilleux and Ecole de technologie supérieure

Description: 
Implementation of VPI functions

TODO: Add more documentation

Copyright (c) 2011, Tennessee Carmel-Veilleux and
Ecole de technologie superieure. All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are 
met:

    * Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above 
copyright notice, this list of conditions and the following disclaimer 
in the documentation and/or other materials provided with the 
distribution.
    * Neither the name of Ecole de technollogie superieure nor the names of 
its contributors may be used to endorse or promote products derived from this 
software without specific prior written permission.

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

import vpi
import re
import struct
import sys

VPI_VP_PRINTF_ID = 10
VPI_VP_PUTC_ID = 11
VPI_VP_TRACE_ID = 12
VPI_VP_TIMING_ID = 13

class vp_printf(vpi.VpiFunction):
    def __init__(self, id):
        vpi.VpiFunction.__init__(self, id)
        self.placeholdersCache = {}
        self.validator = re.compile(r"%(%|(([-0+]*)([1-9][0-9]*)?(\.(([1-9][0-9]*)?|0))?([diouxXeEfFgGcs]|(ld)|(lx)|(lX))))", re.MULTILINE)

    def process(self, vpiInterface, payload):
        funcId, dataTableAddr, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors = payload

        #print payload
        if (nConsts != 1) or (nOutVars != 0) or (nInVars > 15):
            # Ignore wrong values
            return

        # Cache placeHolders on first occurence
        if dataTableAddr in self.placeholdersCache:
            formatStr, placeHolders = self.placeholdersCache[dataTableAddr]
        else:
            # First constant is format string address
            formatStr = vpiInterface.debuggerInterface.read_string_variable(consts[0], 256)

            # Extract all placeholders
            placeHolders = []
            for match in self.validator.finditer(formatStr):
                # Skip literal percent sign
                if match.group(0) != "%%":
                    # Group 8 is type
                    placeHolders.append(match.group(8))

            # Cache placeholders
            self.placeholdersCache[dataTableAddr] = (formatStr, placeHolders)

        # Extract values
        values = []

        # Eliminate needless input variables
        if len(placeHolders) > nInVars:
            placeHolders = placeHolders[0:nInVars]

        # Read all values from accessors, depending on format specifier
        for idx, placeHolder in enumerate(placeHolders):
            isLong = False
            # Check for long
            if placeHolder[0] == "l":
                isLong = True

            # Handle floats
            if placeHolder[-1] in 'eEfFgG':
                value = inVarAccessors[idx].read_n_bytes_variable(8)
                values.append(vpiInterface.debuggerInterface.get_double_from_longlong(value))
            # Handle integers
            elif placeHolder[-1] in 'diouxX':
                nBytes = 4 if (not isLong) else 8
                value = inVarAccessors[idx].read_n_bytes_variable(nBytes)

                # Handle signed ints
                if placeHolder[-1] in 'di':
                    values.append(vpiInterface.debuggerInterface.to_signed(value, nBytes))
                else:
                    values.append(value)
            # Handle chars
            elif placeHolder[-1] == 'c':
                value = inVarAccessors[idx].read_n_bytes_variable(1)
                values.append(chr(value))
            # Handle strings (max length: 256
            elif placeHolder[-1] == 's':
                # FIXME: Add "read_pointer" in ABI class
                address = inVarAccessors[idx].read_n_bytes_variable(4)
                #print inVarAccessors[idx]
                #print "0x%x" % address
                value = vpiInterface.debuggerInterface.read_string_variable(address, 256)
                values.append(value)
            # Other (unknown) cases:
            else:
                values.append(0)

        # Actually print result
        sys.stdout.write(formatStr % tuple(values))
        #sys.stdout.write((("[%s] " % vpiInterface.debuggerInterface.cpu.name) + formatStr) % tuple(values))

class vp_putc(vpi.VpiFunction):
    def __init__(self, id):
        vpi.VpiFunction.__init__(self, id)

    def process(self, vpiInterface, payload):
        funcId, dataTableAddr, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors = payload

        #print payload
        if (nConsts != 0) or (nOutVars != 0) or (nInVars != 1):
            return

        #print inVarAccessors[0]
        sys.stdout.write(chr(inVarAccessors[0].read_n_bytes_variable(1)))

def trace_process_func_enterexit(vpiInterface, dataTableAddr, traceItem, consts, inVarAccessors):
    data = [traceItem,
            vpiInterface.debuggerInterface.read_string_variable(consts[1], 256),
            vpiInterface.debuggerInterface.read_string_variable(consts[2], 256) +
            ":%d" % consts[3],
            "%x" % vpiInterface.debuggerInterface.get_reg("lr")]
    print "### TRACE\t" + "\t".join(data)

def trace_process_cyg_profile(vpiInterface, dataTableAddr, traceItem, consts, inVarAccessors):
    data = [traceItem,
            "0x%x" % inVarAccessors[0].read_n_bytes_variable(4),
            "0x%x" % inVarAccessors[1].read_n_bytes_variable(4),
            "%x" % vpiInterface.debuggerInterface.get_reg("lr")]
    print "### TRACE\t" + "\t".join(data)

class vp_trace(vpi.VpiFunction):
    def __init__(self, id):
        vpi.VpiFunction.__init__(self, id)
        self.handlers = {"FUNC_ENTER" : trace_process_func_enterexit,
                         "FUNC_EXIT" : trace_process_func_enterexit,
                         "CYG_PROFILE_FUNC_ENTER" : trace_process_cyg_profile,
                         "CYG_PROFILE_FUNC_EXIT" : trace_process_cyg_profile}
        self.traceEventsCache = {}

    def process(self, vpiInterface, payload):
        funcId, dataTableAddr, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors = payload

        # Validate parameters
        if (nConsts < 1) or (nOutVars != 0):
            return

        # Handle caching for the trace event description
        if dataTableAddr in self.traceEventsCache:
            traceEvent = self.traceEventsCache[dataTableAddr]
        else:
            traceEvent = vpiInterface.debuggerInterface.read_string_variable(consts[0], 256)
            self.traceEventsCache[dataTableAddr] = traceEvent

        # Run the correct handler for the trace event if it exists
        if traceEvent in self.handlers:
            self.handlers[traceEvent](vpiInterface, dataTableAddr, traceItem, consts, inVarAccessors)
        else:
            # TODO: Add a default handler
            pass

class vp_timing(vpi.VpiFunction):
    def __init__(self, id):
        vpi.VpiFunction.__init__(self, id)
        self.timestamps = {}
        self.timingIdentifiersCache = {}

    def process(self, vpiInterface, payload):
        funcId, dataTableAddr, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors = payload

        # Validate parameter numbers
        if (nConsts < 2) or (nOutVars != 0):
            return

        if nConsts == 2:
            # Handle caching for the timing identifiers if it is static
            if dataTableAddr in self.timingIdentifiersCache:
                identifier = self.timingIdentifiersCache[dataTableAddr]
            else:
                identifier = vpiInterface.debuggerInterface.read_string_variable(consts[1], 256)
                self.timingIdentifiersCache[dataTableAddr] = identifier
        elif (nConsts == 3) and (nInVars == 1):
            # Handle dynamic identifiers
            identifier = vpiInterface.debuggerInterface.read_string_variable(consts[1], 256)
            subIdType = vpiInterface.debuggerInterface.read_string_variable(consts[2], 256)
            if subIdType == "char *":
                subId = inVarAccessors[0].read_string_variable(256)
            elif subIdType == "int":
                # FIXME: Read native length
                subId = "%d" % inVarAccessors[0].read_n_bytes_variable(4)
            elif subIdType == "hex":
                subId = "0x%08x" % inVarAccessors[0].read_n_bytes_variable(4)
            else:
                # Wrong format: silently ignore and exit
                return

            # Build extended identifier
            identifier = identifier + "@" + subId
        else:
            # Wrong format: silently ignore and exit
            return

        # Handle the timing operating
        subfunction = consts[0]
        if subfunction == 0:
            # Subfunction 0: Beging timing
            self.timestamps[identifier] = vpiInterface.debuggerInterface.get_timestamp()
        elif subfunction == 1:
            # Subfunction 1: End timing (display delta since last start)
            end = vpiInterface.debuggerInterface.get_timestamp()

            if identifier in self.timestamps:
                # Timing was started: we have the time
                start = self.timestamps[identifier]
            else:
                # Timing never started; use nil difference and record this as a start
                start = end
                self.timestamps[identifier] = end

            delta = (end - start)
            print "### TIMING\t%s\t%d\t%d\t%d" % (identifier, start, end, delta)
        else:
            # Unknown subfunction
            return

class vp_fopen(vpi.VpiFunction):
    def __init__(self, id):
        vpi.VpiFunction.__init__(self, id)

    def process(self, vpiInterface, payload):
        # Obtain contents of payload
        funcId, dataTableAddr,
        nConsts, nInVars, nOutVars,
        consts, inVarAccessors, outVarAccessors = payload

        # Access parameters from payload table
        filename = inVarAccessors[0].read_string_variable()
        mode = inVarAccessors[1].read_string_variable()

        # Open the file and save the descriptor
        handle = open(filename, mode)
        global handlePool
        handlePool.append(handle)

        # Return an opaque file descriptor from the function
        retval = long(len(handlePool))
        outVarAccessors[0].write_nbytes_variable(retval, 4)

#class vp_fclose(vpi.VpiFunction):
#    def __init__(self, id):
#        vpi.VpiFunction.__init__(self, id)
#
#    def process(self, vpiInterface, payload):
#        # Obtain contents of payload
#        funcId, dataTableAddr,
#        nConsts, nInVars, nOutVars,
#        consts, inVarAccessors, outVarAccessors = payload
#
#        # Access parameters from payload table
#        handle = inVarAccessors[0].read_nbytes_variable(4)
#
#        # Open the file and save the descriptor
#
#        global handlePool
#        handlePool.append(handle)
#
#        # Return an opaque file descriptor from the function
#        retval = long(len(handlePool))
#        outVarAccessors[0].write_nbytes_variable(retval, 4)

functions = [vp_printf(id = VPI_VP_PRINTF_ID),
             vp_putc(id = VPI_VP_PUTC_ID),
             vp_trace(id = VPI_VP_TRACE_ID),
             vp_timing(id = VPI_VP_TIMING_ID)]