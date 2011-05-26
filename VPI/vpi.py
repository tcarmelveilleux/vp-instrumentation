#!/usr/bin/python
# -*- coding: cp1252 -*-
"""
Main implementation for VPI prototype

Created on: 25/05/2011
Author: Tennessee Carmel-Veilleux (tennessee.carmelveilleux@gmail.com)
Revision: $Rev$

Copyright 2011 Tennessee Carmel-Veilleux and Ecole de technologie supérieure

Description: 
Implementation of all aspects of the VPI prototype except VPI functions.

TODO: Separate this into multiple classes and add more documentation

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

import re
import struct

VPI_TRIGGER_METHOD_GDB = 0
VPI_TRIGGER_METHOD_MAGIC = 1

class DebuggerInterface:
    def __init__(self, inferior):
        """
        Default constructor. Inferior argument is ignored.

        Args: - inferior: ignored
        """
        pass

    def eval_expr(self, expression):
        """
        Evaluate the symbolic "expression" specified in the debugger and
        returns a string of the resulting value
        """
        return None

    def read_mem(self, startAddress, endAddress = None):
        """
        Read bytes from memory.

        Args: - startAddress: starting address of read
              - endAddress: end address of read or None if a single byte is
                            desired.
        Returns: a single integer (if endAddress == None) or a list of integers
                 with values equal to the bytes read in order.
        """
        if not endAddress or (endAddress < startAddress):
            return 0
        else:
            return [0] * ((endAddress - startAddress) + 1)

    def write_mem(self, startAddress, buffer):
        """
        Write bytes to memory.

        Args: - startAddress: starting address of write
              - buffer: buffer of bytes to write

        Returns: nothing
        """
        if not buffer:
            return
        else:
            pass

    def read_n_bytes_variable(self, address, nBytes):
        """
        Read a value from memory, in the configured byte order, with
        nBytes bytes (ie: 4 for 32 bits, 8 for 64 bits).

        Args: - address: first byte address for the value.

        Returns: a long with the nBytes bytes unsigned value read.
        """
        data = self.read_mem(address, address+(nBytes - 1))
        data = self.get_adapted_endian(data)

        """
        if not self.isBigEndian:
            # Copy the data before reversing
            data = data[:]
            data.reverse()
        """
        retValue = long(0)
        for idx in xrange(nBytes):
            retValue |= long(data[idx]) << (8 * (nBytes - idx - 1))

        return retValue

    def write_n_bytes_variable(self, address, nBytes, value):
        """
        Write an "nBytes" bytes value to memory, in the configured byte order.
        For example, a 32 bits value would have nBytes = 4.

        Args: - address: address of first byte where to start writing
              - nBytes: number of bytes to write
              - value: long (unsigned) to write

        Returns: nothing
        """
        data = [int((value >> (8 * (bBytes - idx - 1))) & 0xff) for idx in xrange(nBytes)]

        """
        if not self.isBigEndian:
            # Copy the data before reversing
            data = data[:]
            data.reverse()
        """
        data = self.get_adapted_endian(data)

        self.write_mem(address, data)

    def read_string_variable(self, startAddress, maxLen):
        """
        Read a null-terminated string from memory. The string is built until
        a null is read or the length of the string reaches "maxLen".

        Args: - startAddress: address of first byte of the string in memory.
              - maxLen: maximum length for the string.

        Returns: a Python string with the value read, excluding null terminator
                 if applicable.
        """
        count = 0
        done = False
        chars = []
        currAddr = startAddress

        while count < maxLen and not done:
            character = self.read_mem(currAddr)

            # If char is not null, append to string, otherwise terminate
            if character != 0:
                chars.append(chr(character))
            else:
                done = True

            currAddr += 1

        return "".join(chars)

    def get_reg(self, name):
        """
        Get the value of the machine register specified by name.

        Args: - name: name of the register to read

        Returns: a long with the unsigned value of the register
        """
        return None

    def get_fpu_reg(self, name):
        """
        Get the value of the FPU register specified by name.

        Args: - name: name of the FPU register to read

        Returns: a long with the unsigned raw value of the register
        """
        return None

    def set_reg(self, name, value):
        """
        Set the value of the machine register specified by name.

        Args: - name: name of the register to read
              - value: value to set in the register (must fit in the register)

        Returns: a long with the unsigned value of the register
        """
        return None

    def get_pc(self):
        """
        Get the current program counter value.

        Returns: a long with the unsigned value of the PC.
        """
        return long(0)

    def get_timestamp(self):
        """
        Get a high-resolution timestamp of the interception point hit

        Returns: a long with the timestamp
        """
        return long(0)

class SimicsDebuggerInterface(DebuggerInterface):
    def __init__(self, cpu):
        """
        Constructor for a SimicsDebuggerInterface.

        Args: - cpu: instance of the CPU configuration object from which to
                     read data.
        """
        DebuggerInterface.__init__(self, cpu)
        self.cpu = cpu

        # Get reference to symbol evaluator
        import simics
        self.eval_sym = simics.SIM_get_class_interface("symtable", "symtable").eval_sym

        # Get memory object from processor
        self.mem = cpu.iface.processor_info.get_physical_memory().memory

    def eval_expr(self, expression):
        return self.eval_sym(self.cpu, expression, [], 'v')

    def read_mem(self, startAddress, endAddress = None):
        if not endAddress or (endAddress < startAddress):
            return self.mem[startAddress]
        else:
            return self.mem[[startAddress, endAddress]]

    def get_reg(self, name):
        # Use a mix-in class to get that behavior
        return self.get_internal_register(self.cpu, name)

    def get_fpu_reg(self, name):
        # Use a mix-in class to get that behavior (CPU-specific)
        return self.get_internal_register(self.cpu, name)

    def set_reg(self, name, value):
        # Use a mix-in class to get that behavior
        return self.set_internal_register(self.cpu, name, value)

    def get_pc(self):
        return self.get_reg("pc")

    def get_timestamp(self):
        return long(self.cpu.cycles)

class GdbDebuggerInterface(DebuggerInterface):
    def __init__(self, inferior):
        DebuggerInterface.__init__(self, inferior)
        self.inferior = inferior

        # Get a reference to the parse_and_eval function of GDB
        import gdb
        self.parse_and_eval = gdb.parse_and_eval
        self.execute = gdb.execute

        self.rawFloatRegExp = re.compile(r"raw ")

    def eval_expr(self, expression):
        return self.parse_and_eval(expression)

    def read_mem(self, startAddress, endAddress = None):
        if not endAddress or (endAddress < startAddress):
            data = self.inferior.read_memory(startAddress, 1)
            return ord(data[0])
        else:
            data = self.inferior.read_memory(startAddress, (endAddress - startAddress) + 1)
            return [ord(char) for char in data[:]]

    def get_reg(self, name):
        # FIXME: Only valid for 32 bits !!!
        return long(self.eval_expr("(unsigned long)$" + name))

    def get_fpu_reg(self, name):
        # HACK: Remarshals double value back to IEEE format because GDB does not easily provide raw value to Python
        # FIXME: Find a way to get raw value, perhaps by parsing the result of "info all-registers $f1" or "info float $f1"
        return long(struct.unpack(">q",struct.pack(">d",float(self.eval_expr("$" + name))))[0])

    def set_reg(self, name, value):
        # TODO: Implement this
        raise RuntimeError("How to do that in GDB ???")
        #return self.eval_expr("(unsigned long)$" + name)

    def get_pc(self):
        return self.get_reg("pc")



class PpcSimicsRegisterAccessor:
    def __init__(self):
        pass

    def get_internal_register(self, cpu, name):
        """
        Get the value of a target register by name
        """
        if name[0] == "r" and name[1:].isdigit():
            # Handle GPRs in the GPR array
            return long(cpu.gprs[int(name[1:])])
        elif name[0] == "f" and name[1:].isdigit():
            # Handle FPRs in the FPR array
            return long(cpu.fprs[int(name[1:])])
        else:
            # Handle other named registers
            return long(getattr(cpu,name))

    def set_internal_register(self, cpu, name, value):
        """
        Set the value of a target register by name
        """
        if name[0] == "r" and name[1:].isdigit():
            # Handle GPRs in the GPR array
            cpu.gprs[int(name[1:])] = value
        elif name[0] == "f" and name[1:].isdigit():
            # Handle GPRs in the GPR array
            cpu.fprs[int(name[1:])] = value
        else:
            # Handle other named registers
            setattr(cpu,name,value)

class ApplicationBinaryInterface:
    def __init__(self):
        pass

    def is_64_bits(self):
        """
        Returns: True if this ABI is a 64 bits ABI.
        """
        return False

    def get_longlong_second_register(self, baseReg):
        """
        Get the second register name for a long long (64-bit) value given
        the first register name

        Args: - baseReg: String containing the name of the first (base) register
                         in a long long value.

        Returns: a string containing the register name of the second part of a
        long long, given the name of the first part
        """
        return None

    def get_longlong_from_regs(self, baseRegVal, otherRegVal):
        """
        - baseRegVal is base register
        - otherRegVal is the other register of the pair

        Returns a 64 bit long combining both values correctly according
        to the ABI.
        """
        return long(0)

    def get_regs_from_longlong(self, data):
        """
        Return a tuple (baseRegVal, otherRegVal) of values suitable to
        represent a longlong value in a register pair compatible with
        the ABI.

        Args: - data: sequence of 8 byte values in target order, to use
                      to build the two register values

        """
        return (0,0)

    def get_adapted_endian(self, data):
        """
        Return a sequence of bytes with endianness converted from VPI native (big-endian)
        to the ABI's endianness

        Args: - data: Sequence of bytes to adapt to the correct endianness before/after
                      conversion to/from a long value.

        Returns: an adapted sequence (copy)
        """
        return None

    def to_signed(self, value, nBytes):
        """
        Convert a hardware-format long (always unsigned absolute value) to a
        a signed Python long equivalent using the ABI's definition of negative
        values. In most cases, this just uses 2's complement representation.

        Args: - value: Python long value obtained from an accessor
              - nBytes: length of value in bytes

        Returns: a Python long representation of "value" with correct sign
        """
        # If sign bit is set, negate using 2's complement
        msb = long(1) << ((8 * nBytes) - 1)

        if (value & msb):
             value = -((value & (msb - 1)) + 1)

        return value

    def get_top_address(self):
        """
        Returns: a Python long with the machine's top effective address.
        """
        return 0xffffffffL

    def get_double_from_longlong(self, value):
        """
        Convert from a 64-bit longlong value (in unsigned Python long format)
        to a Python float, using C's double floating point representation.

        Args: - value: Python long value to convert (ie: read from memory or registers)

        Returns: a Python float with the value converted to a double-precision float
        """
        raise NotImplementedError()

class PpcApplicationBinaryInterface(ApplicationBinaryInterface):
    def __init__(self):
        ApplicationBinaryInterface.__init__(self)

    def is_64_bits(self):
        return False

    def get_longlong_second_register(self, baseReg):
        if baseReg[0] == "r" and baseReg[1:].isdigit():
            regNum = int(baseReg[1:]) + 1
            if regNum > 31:
                raise ValueError("Trying to read a 'long long' value with an invalid base register: 'r%d'" % (regNum - 1))
        else:
            raise ValueError("Cannot read a 'long long' value from base regiser '%s'" % baseReg)

        return "r%d" % regNum

    def get_longlong_from_regs(self, baseRegVal, otherRegVal):
        return (baseRegVal << 32) | otherRegVal

    def get_double_from_longlong(self, value):
        """
        Convert from a 64-bit longlong value (in unsigned Python long format)
        to a Python float, using C's double floating point representation.
        """
        nBytes = 8
        # Separate data into native byte-order char array
        data = [chr((value >> (8 * (nBytes - idx - 1))) & 0xff) for idx in xrange(nBytes)]
        doubleValue = struct.unpack('>d',''.join(data))[0]

        return doubleValue

    def get_regs_from_longlong(self, data):
        baseRegVal = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
        otherRegVal = (data[4] << 24) | (data[5] << 16) | (data[6] << 8) | data[7]
        return (baseRegVal, otherRegVal)

    def get_adapted_endian(self, data):
        newData = data[:]
        return newData

class VariableAccessor:
    def __init__(self, debuggerInterface):
        self.debuggerInterface = debuggerInterface

    def read_n_bytes_variable(self, nBytes):
        raise NotImplementedError()

    def write_n_bytes_variable(self, nBytes, value):
        raise NotImplementedError()

    def read_string_variable(self, maxLen):
        raise NotImplementedError()

class DummyAccessor(VariableAccessor):
    """
    Accessor that does mostly nothing for cases where
    we could not generate a better one (error...)
    """
    def __init__(self, debuggerInterface):
        self.debuggerInterface = debuggerInterface

    def read_n_bytes_variable(self, nBytes):
        return 0L

    def write_n_bytes_variable(self, nBytes, value):
        pass

    def read_string_variable(self, maxLen):
        return ""

class DirectMemoryAccessor(VariableAccessor):
    def __init__(self, debuggerInterface, address):
        VariableAccessor.__init__(self, debuggerInterface)
        self.address = address

    def read_n_bytes_variable(self, nBytes):
        return self.debuggerInterface.read_n_bytes_variable(self.address, nBytes)

    def write_n_bytes_variable(self, nBytes, value):
        self.debuggerInterface.write_n_bytes_variable(self.address, nBytes, value)

    def read_string_variable(self, maxLen):
        return self.debuggerInterface.read_string_variable(self.address, maxLen)

    def __repr__(self):
        return "DirectMemoryAccessor(address = 0x%lx)" % (long(self.address))

class RegisterAccessor(VariableAccessor):
    def __init__(self, debuggerInterface, baseReg, regSize = 4, isFloat = False):
        VariableAccessor.__init__(self, debuggerInterface)
        self.baseReg = baseReg
        self.regSize = regSize
        self.isFloat = isFloat

    def read_n_bytes_variable(self, nBytes):
        if nBytes <= 4:
            value = self.debuggerInterface.get_reg(self.baseReg)
        elif self.isFloat:
            value = self.debuggerInterface.get_fpu_reg(self.baseReg)
        elif nBytes <= 8 and self.regSize == 4:
            regValue1 = self.debuggerInterface.get_reg(self.baseReg)
            regValue2 = self.debuggerInterface.get_reg(self.debuggerInterface.get_longlong_second_register(self.baseReg))
            value = self.debuggerInterface.get_longlong_from_regs(regValue1, regValue2)
        elif nBytes <= 8 and self.regSize >= 8:
            value = self.debuggerInterface.get_reg(self.baseReg)
        else:
            raise TypeError("Cannot read values larger than 8 bytes (requested %d with RegisterAccessor on baseReg=%s" % \
                            (nBytes, repr(self.baseReg)))

        # Mask-out unnecessary bits
        value = value & ((long(1) << (8 * nBytes)) - 1)

        return value

    def write_n_bytes_variable(self, nBytes, value):
        value = value & ((long(1) << (8 * nBytes)) - 1)

        if nBytes <= 4:
            self.debuggerInterface.set_reg(self.baseReg, value)
        elif nBytes <= 8:
            # Get other register to use
            otherReg = self.debuggerInterface.get_longlong_second_register(self.baseReg)

            # Separate data into native byte-order integer array
            data = [int((value >> (8 * (nBytes - idx - 1))) & 0xff) for idx in xrange(nBytes)]

            # Pad high-order bytes
            if nBytes != 8:
                padded = [0] * (8 - nBytes)
                padded.extend(data)
                data = padded

            # Adapt from big-endian to target endian
            data = self.debuggerInterface.get_adapted_endian(data)

            # Compute register pair contents and write them
            baseRegVal, otherRegVal = self.debuggerInterface.get_regs_from_longlong(data)
            self.debuggerInterface.set_reg(self.baseReg, baseRegVal)
            self.debuggerInterface.set_reg(otherReg, otherRegVal)
        else:
            raise TypeError("Cannot write values larger than 8 bytes (requested %d with RegisterAccessor on baseReg=%s" % \
                            (nBytes, repr(self.baseReg)))

    def read_string_variable(self, maxLen):
        address = self.debuggerInterface.get_reg(self.baseReg)
        return self.debuggerInterface.read_string_variable(address, maxLen)

    def __repr__(self):
        return "RegisterAccessor(baseReg = %s)" % (repr(self.baseReg))

class SymbolicMemoryAccessor(VariableAccessor):
    def __init__(self, debuggerInterface, symbol):
        VariableAccessor.__init__(self, debuggerInterface)
        # Cache symbol address
        self.symbol = symbol
        self.address = debuggerInterface.eval_expr("(unsigned long)&%s", symbol)

    def read_n_bytes_variable(self, nBytes):
        return self.debuggerInterface.read_n_bytes_variable(self.address, nBytes)

    def write_n_bytes_variable(self, nBytes, value):
        self.debuggerInterface.write_n_bytes_variable(self.address, nBytes, value)

    def read_string_variable(self, maxLen):
        return self.debuggerInterface.read_string_variable(self.address, maxLen)

    def __repr__(self):
        return "SymbolicMemoryAccessor(symbol = '%s' = 0x%lx)" % (self.symbol, long(self.address))

class VpiTriggerMethod:
    """
    Mix-in class for VpiInterface that provides methods to help find the payload
    data table address base on the triggering mecanism.

    Depends on features provided by ApplicationBinaryInterface and VpiInterface.
    """
    def __init__(self):
        pass

    def get_trigger_length(self):
        """
        Returns the length of the trigger block.
        """
        raise NotImplementedError()

    def get_branch_pattern(self):
        """
        Returns the pattern of the unconditional branch instruction that is part
        of the trigger (and which remains constant), which allows us to "re-fix"
        our position to find the payload data table address from
        DebuggerInterface.get_data_table_addr().

        Returns: a sequence of byte values representing trigger instruction pattern.
                 The data table address should follow the pattern directly. Values
                 which are None are ignored in the pattern.
        """
        raise NotImplementedError()

    def get_trigger_search_start_address(self, pc):
        raise NotImplementedError()

class PpcGdbVpiTriggerMethod(VpiTriggerMethod):
    def __init__(self):
        VpiTriggerMethod.__init__(self)

    def get_trigger_length(self):
        # lis ... : 4 bytes
        # stw ... : 4 bytes
        # b 2f == b +8 : 4 bytes
        return 12

    def get_trigger_pattern(self):
        # "b +8" is 0x48000008
        return [0x48,0x00,0x00,0x08]

    def get_trigger_search_start_address(self, pc):
        return pc - 16

    def get_trigger_search_length(self):
        return 32

class PpcSimicsVpiTriggerMethod(VpiTriggerMethod):
    def __init__(self):
        VpiTriggerMethod.__init__(self)

    def get_trigger_length(self):
        # rlwimi .... : 4 bytes
        # b 2f == b +8 : 4 bytes
        return 8

    def get_trigger_pattern(self):
        # "b +8" is 0x48000008
        return [0x48,0x00,0x00,0x08]

    def get_trigger_search_start_address(self, pc):
        return pc

    def get_trigger_search_length(self):
        return 16


class VpiInterface:
    def __init__(self, debuggerInterface):
        """
        Args: - debuggerInterface: DebuggerInterface instance to use for data accesses
        """
        self.debuggerInterface = debuggerInterface
        self.payloadCache = {}
        self.dataTableAddrCache = {}
        self.functions = {}

    def get_vpi_next_var(self, varsAddr):
        """
        Read the next variable descriptor at the provided address in a payload
        table and return the accessor for it.

        Args: - varsAddr: pointer to start of payload variable entry
        Returns: a tuple of (incremented varsAddr, variable source accessor)
        """
        raise NotImplementedError()

    def accessor_factory(self, refString):
        """
        Return an accessor class instance based on the reference type
        used in the reference string. The accessor instance can then
        be used at runtime to access data on dynamically computed sources.

        Args: - refString: reference string obtained from VPI variables table

        Returns: a VariableAccessor instance
        """
        for match in self.regOffsetRegExp.finditer(refString):
            return RegisterOffsetMemoryAccessor()

    # TODO: Rename this "register_function" or something similar
    def register(self, vpiFunction):
        """
        Register a VPI function for processing when encountered.

        Args: - vpiFunction: Instance of the VpiFunction class
        """
        self.functions[vpiFunction.get_func_id()] = vpiFunction

    def find_data_table_addr(self, pc):
        """
        Return the address of the data table that can be found just after
        the unconditional branch. To do so, we must search for the pattern
        of the unconditional branch in the vicinity of the PC in a
        platform-specific way (using data from the VpiTriggerMethod mix-in
        class). This is because different debuggers leave us with a different
        PC after the trigger is caught.

        Args: - pc: Program Counter on entry in VPI handler

        Returns: the address of the data table extracted from the code space
                 just after the trigger.
        """
        # Get pattern to search
        pattern = self.get_trigger_pattern()

        # Get block to search
        searchStartAddr = self.get_trigger_search_start_address(pc)
        searchLen = self.get_trigger_search_length()
        searchEndAddr = searchStartAddr + searchLen - 1
        searchBlock = self.debuggerInterface.read_mem(searchStartAddr, searchEndAddr)

        found = False
        # Traverse block to find pattern
        for startIdx in xrange(searchLen - len(pattern) + 1):
            validCount = 0
            sameCount = 0
            for patternIdx in xrange(len(pattern)):
                if pattern[patternIdx]:
                    validCount += 1
                    # Find same elements from pattern in block
                    if searchBlock[startIdx + patternIdx] == pattern[patternIdx]:
                        sameCount += 1
            # Full match: OK
            if sameCount == validCount:
                found = True
                break

        if found:
            return self.debuggerInterface.read_n_bytes_variable(searchStartAddr + startIdx + len(pattern), 4)
        else:
            print "### [VPI] Did not find a trigger pattern between 0x%lx and 0x%lx" % (searchStartAddr, searchEndAddr)
            return None

    def get_data_table_addr(self):
        """
        Get data table address associated with this VPI trigger point
        if it is in cache. Otherwise, compute it.
        """
        pc = self.debuggerInterface.get_pc()

        if self.dataTableAddrCache.has_key(pc):
            dataTableAddr = self.dataTableAddrCache[pc]
        else:
            dataTableAddr = self.find_data_table_addr(pc)
            self.dataTableAddrCache[pc] = dataTableAddr

        return dataTableAddr

    def get_payload(self, dataTableAddr):
        """
        Extract the VPI's configuration elements from the VPI payload data table
        at the address specified in memory.

        - Args: dataTableAddr: Base address of the VPI payload data table

        Returns a tuple:
        (funcId, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors)
            with:
            - funcId: Identifier of VPI
            - dataTableAddr: Address of data table
            - nConsts: Number of constants
            - nInVars: Number of input variables
            - nOutVars: Number of output variables
            - consts: Sequence of constants, in table order
            - inVarAccessors: Sequence of accessors of input variables, in table order
            - outVarAccessors: Sequence of accessors of output variables, in table order
        extracted from the VPI payload data table at address "dataTableAddr".
        """
        # Get the spec word in the first word of the data table,
        # which contains the ID, number of constants and number of variables
        specWord = self.debuggerInterface.read_n_bytes_variable(dataTableAddr, 4)
        funcId = specWord & 0xffff
        nConsts = (specWord >> 16) & 0xf
        nInVars = (specWord >> 20) & 0xf
        nOutVars = (specWord >> 24) & 0xf

        # Get the values of all the constants
        constsBase = dataTableAddr + 4
        consts = []
        for idx in xrange(nConsts):
            # Get the next constant value
            newBase, constValue = self.get_vpi_const(constsBase)
            # Update reading address
            consts.append(constValue)
            constsBase = newBase

        # Get accessors to all of the input variables references
        inVarsBase = constsBase
        inVarAccessors = []
        for idx in xrange(nInVars):
            # Get the next variable reference specifier
            newBase, valRefString = self.get_vpi_next_var(inVarsBase)

            # Obtain a dynamic VariableAccessor for the variable
            inVarAccessors.append(self.accessor_factory(valRefString))

            # Update reading address
            inVarsBase = newBase

        # Get accessors to all of the output variables references
        outVarsBase = inVarsBase
        outVarAccessors = []
        for idx in xrange(nOutVars):
            # Get the next variable reference specifier
            newBase, valRefString = self.get_vpi_next_var(outVarsBase)

            # Obtain a dynamic VariableAccessor for the variable
            outVarAccessors.append(self.accessor_factory(valRefString))

            # Update reading address
            outVarsBase = newBase

        return (funcId, dataTableAddr, nConsts, nInVars, nOutVars, consts, inVarAccessors, outVarAccessors)

    def process(self):
        """
        Process a VPI that was just encountered in the current debugger context.

        This involves reading the VPI payload data table to identify the VPI function
        to call and obtain its parameters. If the VPI function's ID is registered in
        this VpiInterface instance (through the register() method), the function will
        be processed using the registered handler.
        """
        pc = self.debuggerInterface.get_pc()
        #print "process, pc = 0x%x" % self.debuggerInterface.get_pc()

        # 1- Get the address of the data table (PC + headerLen)
        dataTableAddr = self.get_data_table_addr()

        #print "dataTableAddr = 0x%lx" % dataTableAddr
        # Skip processing if payload data table was not found
        if not dataTableAddr:
            return

        # 2- Get the payload data from the cache, building the cache entry if it
        #    is absent.
        if not self.payloadCache.has_key(dataTableAddr):
            payload = self.get_payload(dataTableAddr)
            self.payloadCache[dataTableAddr] = payload
        else:
            payload = self.payloadCache[dataTableAddr]

        # 3- Get the VPI id
        funcId = payload[0]

        # 4- Process the function if it is registered
        if self.functions.has_key(funcId):
            self.functions[funcId].process(self, payload)
        else:
            print "### [VPI] Function id=%d has been called at PC = 0x%lx, but is not registered" % \
                (funcId, pc)

class X86VpiInterface(VpiInterface):
    def __init__(self, debuggerInterface):
        VpiInterface.__init__(self, debuggerInterface)

    def get_vpi_header_length(self):
        # cpuid = 0x0f 0xa2
        # jmp 2f = 0xeb 0x09
        return 4

    def get_vpi_const(self, address):
        # Consts are saved in a "movl Immed32, %eax" instruction to prevent
        # assembler error. Opcode: 0xb8 + 4 bytes of immediate value
        value = self.debuggerInterface.read_n_bytes_variable(address + 1, 4)
        return (address + 5, value)

class PpcVpiInterface(VpiInterface):
    def __init__(self, debuggerInterface):
        VpiInterface.__init__(self, debuggerInterface)
        # Regexp to extract a PPC-style register+offset reference (ie: "128(31)" for r31+128)
        self.regOffsetRegExp = re.compile(r"^(-?\d+)\(([0-9]|[12][0-9]|3[01])\)$")
        self.regIndexedRegExp = re.compile("^([0-9]|[12][0-9]|3[01]),([0-9]|[12][0-9]|3[01])$")
        self.registerRegExp = re.compile(r"^([0-9]|[12][0-9]|3[01])$")
        self.fpuRegisterRegExp = re.compile(r"^f([0-9]|[12][0-9]|3[01])$")
        self.symbolRegExp = re.compile(r"^([a-zA-Z_$][a-zA-Z0-9_$]*)$")

    def get_vpi_const(self, address):
        # Consts are stored directly as 32-bits values
        value = self.debuggerInterface.read_n_bytes_variable(address , 4)
        return (address + 4, value)

    def accessor_factory(self, refString):
        # None means an error occured in trying to get the refstring so
        # we generate a dummy accessor.
        if not refString:
            return DummyAccessor(self.debuggerInterface)

        # Check for register + offset case first
        for match in self.regOffsetRegExp.finditer(refString):
            return self.PpcRegisterOffsetMemoryAccessor(self.debuggerInterface,
                                                        baseReg = ("r%s" % match.group(2)),
                                                        offset = long(match.group(1)) )

        # Check for register-direct next
        for match in self.registerRegExp.finditer(refString):
            return RegisterAccessor(self.debuggerInterface,
                                    baseReg = ("r%s" % match.group(1)))

        # Check for FPU register-direct next
        for match in self.fpuRegisterRegExp.finditer(refString):
            return RegisterAccessor(self.debuggerInterface,
                                    baseReg = ("f%s" % match.group(1)), regSize = 8, isFloat = True)

        # Check for indexed reg + reg next
        for match in self.regIndexedRegExp.finditer(refString):
            return self.PpcRegisterOffsetMemoryAccessor(self.debuggerInterface,
                                                        baseReg = ("r%s" % match.group(1)),
                                                        offset = ("r%s" % match.group(2)) )

        # Check for symbolic next
        for match in self.symbolRegExp.finditer(refString):
            return SymbolicMemoryAccessor(self.debuggerInterface,
                                          symbol = (match.group(1)))

        # If we got here, the reference string was invalid
        raise ValueError("Invalid reference string: '%s'", refString)

    def _get_refstring_from_stw(self, instWord):
        """
        Returns a reference string disassembled from an "stw" or "stwx"
        instruction. This is needed because some "register+offset" references
        output by the compiler use local symbols instead of constants for the
        offsets (ie: .L312@l(8) instead of -452(8)). Thoses references cannot
        be computed, even with the symbol table. We use an "stw 0,Offset(Base)"
        instruction in the payload data table to obtain the final,
        linker-relocated value indirectly. We then synthesize a reference
        string through disassembly of the instruction. The "stwx" case is
        handled this way also, to prevent the compiler from generating invalid
        references in some cases when the "%X" modifier is not included in the
        stw.

        Args: - instWord: Instruction word for "stw 0,Offset(Base)" or
                          stwx 0,rA,rB obtained from the payload data table.

        Returns: a reference string usable with self.accessor_factory()
        """
        # stw rS,d(rA) format is:
        # (inst & 0xfc000000) == 0x90000000
        # (inst & 0x03e00000) >> 21 == rS
        # (inst & 0x001f0000) >> 16 == rA
        # (inst & 0x0000ffff) == d

        # stwx rS,rA,rB format is:
        # (inst & 0xfc000000) == 0x7c000000
        # (inst & 0x03e00000) >> 21 == rS
        # (inst & 0x001f0000) >> 16 == rA
        # (inst & 0x0000f800) >> 11 == rb
        # (inst & 0x000007ff) == 0x12e

        # Check whether we have the right instruction (stw 0,d(rA))
        if not ((instWord & 0xffe00000L) == 0x90000000L) and not ((instWord & 0xffe00000L) == 0x7c000000L):
            print "### [VPI] Wrong instruction in PPC alternate source (not stw 0,d(rA) or stwx 0,rA,rB). Instruction: 0x%08x." % instWord
            return None

        # Extract base register (rA)
        baseReg = (instWord & 0x001f0000L) >> 16

        # Handle either cases of stw or stwx
        if (instWord & 0xffe00000L) == 0x90000000L:
            # === Case of stw 0,d(rA)
            # Extract displacement and sign-extend
            d = self.debuggerInterface.to_signed((instWord & 0x0000ffffL), 2)

            # Return a reference string representing the base+offset found in the instruction
            return "%d(%d)" % (d, baseReg)
        else:
            # === Case of stwx 0,rA,rB
            offsetReg = (instWord & 0x0000f800L) >> 11
            # Return a reference string representing the baseReg+offsetReg found in the instruction
            return "%d,%d" % (baseReg, offsetReg)

    def get_vpi_next_var(self, varsAddr):
        varValue = []
        done = False

        # Read a null terminated-string byte by byte for the "main"
        # refString.
        while not done:
            char = self.debuggerInterface.read_mem(varsAddr)
            if char != 0:
                varValue.append(chr(char))
            else:
                done = True

            varsAddr += 1

            # Var specs should not be larger than 32 chars...
            if len(varValue) > 32: done = True

        # Align to 4 bytes to read the alternate representation
        varsAddr = (varsAddr + 3) & (~3L)

        # Read alternate representation and replace refstring if it
        # is available. See _get_refstring_from_str for more info about
        # PPC alternate representation.
        alternateInst = self.debuggerInterface.read_n_bytes_variable(varsAddr, 4)
        if alternateInst != 0L:
            # Alternate present: use it
            refString = self._get_refstring_from_stw(alternateInst)
        else:
            # Default case with no alternate representation: use loaded string
            refString = "".join(varValue)

        # Skip past alternate instruction
        varsAddr += 4
        return (varsAddr, refString)

    class PpcRegisterOffsetMemoryAccessor(VariableAccessor):
        """
        Specific accessor for PowerPC basereg + offset ("d(rA)") or
        baseReg + offsetReg ("rA, rB") addressing modes.
        """
        def __init__(self, debuggerInterface, baseReg, offset):
            VariableAccessor.__init__(self, debuggerInterface)
            self.baseReg = baseReg
            self.offset = offset
            # Handle the case of offset being a string instead of a long (indexed
            # addressing mode instead of base+offset).
            if type(offset) == type("r1"):
                self.isIndexed = True
            else:
                self.isIndexed = False

        def _adjust_address(self, address):
            """
            Handle roll-over from top of address space (ie: 0x00000000 - 512 =
            0xfffffe00).

            Args: - address: address to adjust

            Returns: the provided address, adjusted to take in account roll-over if
                     it occured.
            """
            if address < 0L:
                return self.debuggerInterface.get_top_address() + 1 + address
            else:
                return address

        def _get_address(self):
            """
            Obtain the effective address from the d(rA) or rA,rB values, according
            to the rules of the load and store instructions on the PPC.

            Returns: the effective address to use for further operations
            """
            if self.baseReg != "r0":
                if not self.isIndexed:
                    # Normal case of d(rA): read register and add offset
                    address = self._adjust_address(self.debuggerInterface.get_reg(self.baseReg) + self.offset)
                else:
                    # Normal case of rA,rB: read both registers and add
                    address = self._adjust_address(self.debuggerInterface.get_reg(self.baseReg) + \
                                                   self.debuggerInterface.get_reg(self.offset))
            else:
                if not self.isIndexed:
                    # Case of d(r0): just use the offset
                    address = self._adjust_address(self.offset)
                else:
                    # Case of r0,rB: just use rB
                    address = self._adjust_address(self.debuggerInterface.get_reg(self.offset))

            return address

        def read_n_bytes_variable(self, nBytes):
            address = self._get_address()
            return self.debuggerInterface.read_n_bytes_variable(address, nBytes)

        def write_n_bytes_variable(self, nBytes, value):
            address = self._get_address()
            self.debuggerInterface.write_n_bytes_variable(address, nBytes, value)

        def read_string_variable(self, maxLen):
            address = self._get_address()
            return self.debuggerInterface.read_string_variable(address, maxLen)

        def __repr__(self):
            return "PpcRegisterOffsetMemoryAccessor(baseReg = %s, offset = %s)" % (repr(self.baseReg), repr(self.offset))

class VpiFunction:
    def __init__(self, id):
        self.id = id

    def get_func_id(self):
        return self.id

    def process(self, vpiInterface, payload):
        pass
