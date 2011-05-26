template = r"""
#define vp_printf%(numArgs)d(format_str, %(inArgs)s) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, %(numArgs)d, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_%(numArgs)d_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), %(blockArgs)s)
"""

for numArgs in range(1,11):
    inArgs = ", ".join(["invar%d" % idx for idx in range(numArgs)])
    blockArgs = ", ".join(["[IN%d] VPI_IN_CONSTRAINT (invar%d)" % (idx, idx) for idx in range(numArgs)])
    print template % locals(),
    
