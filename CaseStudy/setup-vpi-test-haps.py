import vpi
import vpiFuncs

class PpcSimicsDebuggerInterface(vpi.SimicsDebuggerInterface, vpi.PpcSimicsRegisterAccessor,
                                 vpi.PpcApplicationBinaryInterface):
    def __init__(self, cpuInstance):
        vpi.SimicsDebuggerInterface.__init__(self, cpuInstance)
        vpi.PpcSimicsRegisterAccessor.__init__(self)
        vpi.PpcApplicationBinaryInterface.__init__(self)

class PpcSimicsVpiInterface(vpi.PpcVpiInterface, vpi.PpcSimicsVpiTriggerMethod):
    def __init__(self, debuggerInterface):
        vpi.PpcVpiInterface.__init__(self, debuggerInterface)
        vpi.PpcSimicsVpiTriggerMethod.__init__(self)

def vpi_magic_callback(cpuInstance):
    global vpiInterfaces

    # Instantiate the debugger and VPI interfaces the first time we get a magic callback on
    # a particular CPU instance.
    if not vpiInterfaces.has_key(cpuInstance):
        debuggerInterface = PpcSimicsDebuggerInterface(cpuInstance)
        vpiInterface = PpcSimicsVpiInterface(debuggerInterface)
        for func in vpiFuncs.functions:
            vpiInterface.register(func)

        vpiInterfaces[cpuInstance] = vpiInterface

    # Process the VPI in the current debugger context
    vpiInterface = vpiInterfaces[cpuInstance]
    vpiInterface.process()

def magic_hap_callback(user_arg, cpuInstance, magic_inst_num):
    # Call the registered callback if it exists
    if magic_callbacks.has_key(magic_inst_num):
        magic_callbacks[magic_inst_num](cpuInstance)
    else:
        SIM_break_simulation("No handler for magic breakpoint id=%d" % magic_inst_num)

# Magic callback handler table. Each dictionnary key should
# be the magic instruction number and the value should be the
# handler function to call.
magic_callbacks = { 9: vpi_magic_callback }

# Add the hap callback for magic instructions
SIM_hap_add_callback("Core_Magic_Instruction", magic_hap_callback, None)
vpiInterfaces = {}