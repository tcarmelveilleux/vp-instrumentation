/*
 * vpi.h
 *
 * Main VPI implementation header.
 * 
 * Created on: 30/11/2010
 * Author: Tennessee Carmel-Veilleux (tennessee.carmelveilleux@gmail.com)
 * Revision: $Rev$
 * 
 * Copyright 2010 Tennessee Carmel-Veilleux and Ecole de technologie supérieure
 * 
 * Description: 
 * Main VPI implementation header for VPI prototype.
 *
 * TODO: Add more documentation
 * 
 * Copyright (c) 2010, Tennessee Carmel-Veilleux and
 * Ecole de technologie superieure. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are 
 * met:
 * 
 *     * Redistributions of source code must retain the above copyright 
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above 
 * copyright notice, this list of conditions and the following disclaimer 
 * in the documentation and/or other materials provided with the 
 * distribution.
 *     * Neither the name of Ecole de technollogie superieure nor the names of 
 * its contributors may be used to endorse or promote products derived from this 
 * software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */

#define __STR(x) #x
#define TO_STR(x) __STR(x)

#define VPI_TRIGGER_METHOD_MAGIC

/* IDs from 0-9 are reserved */
#define VPI_VP_PRINTF_ID 10
#define VPI_VP_PUTC_ID 11
#define VPI_VP_TRACE_ID 12
#define VPI_VP_TIMING_ID 13
#define VPI_VP_FOPEN 14
#define VPI_VP_FCLOSE 15
#define VPI_VP_FREAD 16
#define VPI_VP_FWRITE 17
/* Currently unimplemented */
#define VPI_VP_FPRINTF_ID 18

/**************** PPC 32-bits implementation ******************/
#if defined(__PPC__)

#if defined(VPI_TRIGGER_METHOD_GDB)
extern unsigned long VPIvpiVPI_trigger;

#define VPI_TRIGGER "addis %[TEMP_TRIGGER],0,VPIvpiVPI_trigger@ha; stw %[TEMP_TRIGGER],VPIvpiVPI_trigger@l(%[TEMP_TRIGGER]); b 2f\n\t"

#define VPI_NOP_CLOBBER
#define VPI_NOP_CLOBBER_SEPARATOR

#define VPI_FORCED_OUTPUT
#define VPI_FORCED_OUTPUT_SEPARATOR

#define VPI_FORCED_INPUT [TEMP_TRIGGER] "b" (VPI_temp_trigger)
#define VPI_FORCED_INPUT_SEPARATOR ,

#define VPI_EXTRA_BLOCK_VAR unsigned long VPI_temp_trigger;

#elif defined(VPI_TRIGGER_METHOD_MAGIC)
#define VPI_TRIGGER "rlwimi 0,0,0,0,9; b 2f\n\t"

#define VPI_NOP_CLOBBER
#define VPI_NOP_CLOBBER_SEPARATOR

#define VPI_FORCED_OUTPUT
#define VPI_FORCED_OUTPUT_SEPARATOR

#define VPI_FORCED_INPUT
#define VPI_FORCED_INPUT_SEPARATOR

#define VPI_EXTRA_BLOCK_VAR
#else
#error No method defined for VPI trigger (VPI_TRIGGER_METHOD_*)
#endif /* defined(VPI_TRIGGER_METHOD_*) */

#define VPI_DUMMY_RETURN

/* "res" = constraint for register or stable memory reference */
#define VPI_OUT_CONSTRAINT "=res"
#define VPI_IN_CONSTRAINT "res"
#define VPI_FLOAT_IN_CONSTRAINT "fes"
#define VPI_DOUBLE_IN_CONSTRAINT "des"

#define INSERT_VPI_CONST(placeholder_id) \
        ".long    %"TO_STR(placeholder_id)"\n\t"

#define INSERT_VPI_ALTERNATE_VAR(placeholder_id) \
    ".balign 4\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"0\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"1\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"2\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"3\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"4\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"5\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"6\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"7\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"8\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"9\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"10\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"11\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"12\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"13\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"14\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"15\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"16\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"17\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"18\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"19\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"20\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"21\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"22\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"23\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"24\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"25\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"26\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"27\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"28\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"29\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"30\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    ".ifc \"%"TO_STR(placeholder_id)"\",\"31\"\n\t" \
    ".long 0\n\t" \
    ".else\n\t" \
    "stw%X"TO_STR(placeholder_id)" 0,%"TO_STR(placeholder_id)"\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t" \
    ".endif\n\t"

#define INSERT_VPI_VAR(placeholder_id) \
        ".asciz \"%"TO_STR(placeholder_id)"\"\n\t" \
        INSERT_VPI_ALTERNATE_VAR(placeholder_id)

#define VPI_RODATA_SECTION ".section .rodata,\"a\",@progbits\n"

#define VPI_NO_CLOB_SEPARATOR

#define VPI_MIN_ALIGNMENT 4

/**************** ARM implementation ******************/
#elif defined(__arm__)

/*
 *     * R0–R15 and r0–r15
    * c0–c15 coprocessor registers
    * p0–p15 coprocessor registers
    * a1-a4 scratch registers, synonymous with r0-r3
    * v1-v8 variable registers, synonymous with r4-r11
    * s0-s32 Vector Floating Point (VFP) single precision registers
    * d0-d16 VFP double precision registers
    * fpsid VFP system ID register
    * fpscr VFP status and control register
    * fpexc VFP exception register
    * sb and SB stack base, synonymous with r9
    * sl and SL stack base, synonymous with r10
    * fp and FP frame pointer, synonymous with r11
    * ip and IP intra-procedure call scratch register, synonymous with r12
    * sp and SP stack pointer, synonymous with r13
    * lr and LR link register, synonymous with r14
    * pc and PC program counter, synonymous with r15
 *
 */
#define VPI_NOP "orreq r8,r8,r8\n\t"
#define VPI_NOP_CLOBBER
#define VPI_NOP_CLOBBER_SEPARATOR

#define VPI_BRANCH "b        2f\n\t"

#define VPI_FORCED_OUTPUT
#define VPI_FORCED_OUTPUT_SEPARATOR

#define VPI_FORCED_INPUT
#define VPI_FORCED_INPUT_SEPARATOR

#define VPI_DUMMY_RETURN

#define VPI_OUT_CONSTRAINT "=rm"
#define VPI_IN_CONSTRAINT "rm"

#define INSERT_VPI_CONST(placeholder_id) \
        ".long    %"TO_STR(placeholder_id)"\n\t"

#define INSERT_VPI_ALTERNATE_VAR(placeholder_id)

#define VPI_RODATA_SECTION ".section .rodata,\"a\",@progbits\n"

#define VPI_NO_CLOB_SEPARATOR

#define VPI_MIN_ALIGNMENT 4

/**************** IA32 implementation ******************/
#elif defined(__i386__)
#define VPI_NOP "cpuid\n\t"
#define VPI_NOP_CLOBBER "ecx", "edx", "ebx"
#define VPI_NOP_CLOBBER_SEPARATOR ,

#define VPI_BRANCH "jmp      2f\n\t"

#define VPI_FORCED_OUTPUT "=a"(dummy_eax)
#define VPI_FORCED_OUTPUT_SEPARATOR ,

#define VPI_FORCED_INPUT "a" (0x4711 | ((unsigned)(9) << 16))
#define VPI_FORCED_INPUT_SEPARATOR ,

#define VPI_DUMMY_RETURN int dummy_eax;

#define VPI_OUT_CONSTRAINT "=rm"
#define VPI_IN_CONSTRAINT "rm"

#define INSERT_VPI_CONST(placeholder_id) \
        "movl   %"TO_STR(placeholder_id)", %%eax\n\t"

#define VPI_RODATA_SECTION ".section .rdata,\"dr\"\n"

#define VPI_NO_CLOB_SEPARATOR :

#define VPI_MIN_ALIGNMENT 4
#else
#error unsupported platform. Please provide magic NOP in vpi.h
#endif

#define START_VPI_BLOCK(id, n_consts, n_invars, n_outvars) \
        do { \
        	VPI_EXTRA_BLOCK_VAR \
            VPI_DUMMY_RETURN \
        __asm__ __volatile__ ( \
        VPI_TRIGGER \
        ".long    1f\n\t" \
        VPI_RODATA_SECTION \
        ".balign "TO_STR(VPI_MIN_ALIGNMENT)"\n\t" \
        "1:\n\t" \
        ".long    ("TO_STR(id)" & 0x00ffff) | (("TO_STR(n_consts)" & 0xf) << 16) | (("TO_STR(n_invars)" & 0xf) << 20) | (("TO_STR(n_outvars)" & 0xf) << 24)\n\t" \

#define START_VPI_BLOCK_RET1(id, n_consts, n_invars, n_outvars, type_outvar0, outvar01) \
        ({ \
            type_outvar0 outvar0; \
        	VPI_EXTRA_BLOCK_VAR \
            VPI_DUMMY_RETURN \
        __asm__ __volatile__ ( \
        VPI_TRIGGER \
        ".long    1f\n\t" \
        VPI_RODATA_SECTION \
        ".balign "TO_STR(VPI_MIN_ALIGNMENT)"\n\t" \
        "1:\n\t" \
        ".long    ("TO_STR(id)" & 0x00ffff) | (("TO_STR(n_consts)" & 0xf) << 16) | (("TO_STR(n_invars)" & 0xf) << 20) | (("TO_STR(n_outvars)" & 0xf) << 24)\n\t" \

#define INSERT_1_VPI_OUTPUTS \
    INSERT_VPI_VAR([OUT0])

#define INSERT_1_VPI_INPUTS \
    INSERT_VPI_VAR([IN0])

#define INSERT_2_VPI_INPUTS \
    INSERT_1_VPI_INPUTS \
    INSERT_VPI_VAR([IN1])

#define INSERT_3_VPI_INPUTS \
    INSERT_2_VPI_INPUTS \
    INSERT_VPI_VAR([IN2])

#define INSERT_4_VPI_INPUTS \
    INSERT_3_VPI_INPUTS \
    INSERT_VPI_VAR([IN3])

#define INSERT_5_VPI_INPUTS \
    INSERT_4_VPI_INPUTS \
    INSERT_VPI_VAR([IN4])

#define INSERT_6_VPI_INPUTS \
    INSERT_5_VPI_INPUTS \
    INSERT_VPI_VAR([IN5])

#define INSERT_7_VPI_INPUTS \
    INSERT_6_VPI_INPUTS \
    INSERT_VPI_VAR([IN6])

#define INSERT_8_VPI_INPUTS \
    INSERT_7_VPI_INPUTS \
    INSERT_VPI_VAR([IN7])

#define INSERT_9_VPI_INPUTS \
    INSERT_8_VPI_INPUTS \
    INSERT_VPI_VAR([IN8])

#define INSERT_10_VPI_INPUTS \
    INSERT_9_VPI_INPUTS \
    INSERT_VPI_VAR([IN9])

#define INSERT_11_VPI_INPUTS \
    INSERT_10_VPI_INPUTS \
    INSERT_VPI_VAR([IN10])

#define INSERT_12_VPI_INPUTS \
    INSERT_11_VPI_INPUTS \
    INSERT_VPI_VAR([IN11])

#define INSERT_13_VPI_INPUTS \
    INSERT_12_VPI_INPUTS \
    INSERT_VPI_VAR([IN12])

#define END_VPI_BLOCK_COMMON \
        ".balign  4\n\t" \
        ".text\n\t" \
        ".balign  4\n" \
        "2:\n"

#define END_VPI_BLOCK_NO_RET_NO_CLOB(...) \
        END_VPI_BLOCK_COMMON \
        : VPI_FORCED_OUTPUT : VPI_FORCED_INPUT VPI_FORCED_INPUT_SEPARATOR __VA_ARGS__ VPI_NO_CLOB_SEPARATOR VPI_NOP_CLOBBER); } while(0)

#define END_VPI_BLOCK_RET4_NO_CLOB(outvar0, outvar1, outvar2, outvar3, ...) \
        INSERT_VPI_VAR([OUT0]) \
        INSERT_VPI_VAR([OUT1]) \
        INSERT_VPI_VAR([OUT2]) \
        INSERT_VPI_VAR([OUT3]) \
        END_VPI_BLOCK_COMMON \
        : VPI_FORCED_OUTPUT VPI_FORCED_OUTPUT_SEPARATOR [OUT0] VPI_OUT_CONSTRAINT (outvar0), [OUT1] VPI_OUT_CONSTRAINT (outvar1), [OUT2] VPI_OUT_CONSTRAINT (outvar2), [OUT3] VPI_OUT_CONSTRAINT (outvar3) : VPI_FORCED_INPUT VPI_FORCED_INPUT_SEPARATOR __VA_ARGS__ VPI_NO_CLOB_SEPARATOR VPI_NOP_CLOBBER ); } while(0)

#define END_VPI_BLOCK_RET1_NO_CLOB(outvar0, ...) \
        INSERT_VPI_VAR([OUT0]) \
        END_VPI_BLOCK_COMMON \
        : VPI_FORCED_OUTPUT VPI_FORCED_OUTPUT_SEPARATOR [OUT0] VPI_OUT_CONSTRAINT (outvar0) : VPI_FORCED_INPUT VPI_FORCED_INPUT_SEPARATOR __VA_ARGS__ VPI_NO_CLOB_SEPARATOR VPI_NOP_CLOBBER ); outvar0; } )

/** === void vp_printfXX(const char *format_string, ... ===
 * Semihosted printf(const char *format_string, ...) implementation. This
 * outputs to the console in the VP.
 *
 * Use the version that has the correct number of inputs (ie: vp_printf4
 * for 4 inputs). A variadic version can be made, but then the
 * input constraints must be manually constructed in GCC assembler
 * syntax, which is not practical for most cases.
 */
#define vp_printf0(format_str) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 0, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str))


#define vp_printf1(format_str, invar0) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 1, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_1_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0))

#define vp_printf2(format_str, invar0, invar1) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 2, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_2_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1))

#define vp_printf3(format_str, invar0, invar1, invar2) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 3, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_3_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2))

#define vp_printf4(format_str, invar0, invar1, invar2, invar3) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 4, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_4_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3))

#define vp_printf5(format_str, invar0, invar1, invar2, invar3, invar4) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 5, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_5_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4))

#define vp_printf6(format_str, invar0, invar1, invar2, invar3, invar4, invar5) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 6, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_6_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4), [IN5] VPI_IN_CONSTRAINT (invar5))

#define vp_printf7(format_str, invar0, invar1, invar2, invar3, invar4, invar5, invar6) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 7, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_7_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4), [IN5] VPI_IN_CONSTRAINT (invar5), [IN6] VPI_IN_CONSTRAINT (invar6))

#define vp_printf8(format_str, invar0, invar1, invar2, invar3, invar4, invar5, invar6, invar7) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 8, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_8_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4), [IN5] VPI_IN_CONSTRAINT (invar5), [IN6] VPI_IN_CONSTRAINT (invar6), [IN7] VPI_IN_CONSTRAINT (invar7))

#define vp_printf9(format_str, invar0, invar1, invar2, invar3, invar4, invar5, invar6, invar7, invar8) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 9, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_9_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4), [IN5] VPI_IN_CONSTRAINT (invar5), [IN6] VPI_IN_CONSTRAINT (invar6), [IN7] VPI_IN_CONSTRAINT (invar7), [IN8] VPI_IN_CONSTRAINT (invar8))

#define vp_printf10(format_str, invar0, invar1, invar2, invar3, invar4, invar5, invar6, invar7, invar8, invar9) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 10, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        INSERT_10_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_IN_CONSTRAINT (invar0), [IN1] VPI_IN_CONSTRAINT (invar1), [IN2] VPI_IN_CONSTRAINT (invar2), [IN3] VPI_IN_CONSTRAINT (invar3), [IN4] VPI_IN_CONSTRAINT (invar4), [IN5] VPI_IN_CONSTRAINT (invar5), [IN6] VPI_IN_CONSTRAINT (invar6), [IN7] VPI_IN_CONSTRAINT (invar7), [IN8] VPI_IN_CONSTRAINT (invar8), [IN9] VPI_IN_CONSTRAINT (invar9))

/* This is an example of a printf with 4 inputs, all of which are doubles.
 *
 * The variable insertion is modified to prepend an "f" to the string
 * description emitted by INSERT_VPI_VAR(). This identifies the float
 * access so that the VPII can construct the correct accessor.
 *
 * Note the different constraint (VPI_DOUBLE_IN_CONSTRAINT) compared to the
 * vp_printfXX macros above, as well as the double cast so that floats are
 * also possible as inputs.
 */
#define vp_printf4f(format_str, invar0, invar1, invar2, invar3) \
        START_VPI_BLOCK(VPI_VP_PRINTF_ID, 1, 4, 0) \
        INSERT_VPI_CONST([FORMAT_STR]) \
        ".ascii \"f\"\n\t" \
        INSERT_VPI_VAR([IN0]) \
        ".ascii \"f\"\n\t" \
        INSERT_VPI_VAR([IN1]) \
        ".ascii \"f\"\n\t" \
        INSERT_VPI_VAR([IN2]) \
        ".ascii \"f\"\n\t" \
        INSERT_VPI_VAR([IN3]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([FORMAT_STR] "i" (format_str), [IN0] VPI_DOUBLE_IN_CONSTRAINT ((double)(invar0)), [IN1] VPI_DOUBLE_IN_CONSTRAINT ((double)(invar1)), [IN2] VPI_DOUBLE_IN_CONSTRAINT ((double)(invar2)), [IN3] VPI_DOUBLE_IN_CONSTRAINT ((double)(invar3)))

/** === void vp_putc(char c) ===
 * Semihosted putc(char c) implementation
 */
#define vp_putc(invar0) \
        START_VPI_BLOCK(VPI_VP_PUTC_ID, 0, 1, 0) \
        INSERT_1_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([IN0] VPI_IN_CONSTRAINT (invar0))

/** === void vp_trace(const char *trace_event, const char *this_fn, const char *filename, const int line_num) ===
 * Emits a tracing message on the VP's console. The trace event description in "trace_event"
 * is used to match an event handler in the VPIF's handler dictionnary. The even handler can
 * then print the correct tracing data from the information provided, or record further data.
 * The name of the function in which the trace call is inserted should be in "this_fn",
 * although it can be an arbitrary string. Same goes for the "filename" and "line_num"
 * arguments.
 *
 * ex: The following traces a "FUNC_ENTER" event in the my_strcmp() function, with
 *     current file and line information. This assumes the trace call is made
 *     within the "my_strcmp()" function.
 *
 *     vp_trace("FUNC_ENTER", "my_strcmp", __FILE__, __LINE__)
 *
 *     The definition of the built-in "FUNC_ENTER" handler is as follows:
 *
 *     def trace_process_func_enterexit(vpiInterface, dataTableAddr, traceItem, consts, inVarAccessors):
 *         data = [traceItem,
 *                 vpiInterface.debuggerInterface.read_string_variable(consts[1], 256),
 *                 vpiInterface.debuggerInterface.read_string_variable(consts[2], 256) +
 *                 ":%d" % consts[3],
 *                 "%x" % vpiInterface.debuggerInterface.get_reg("lr")]
 *         print "### TRACE\t" + "\t".join(data)
 *
 *     It could be re-registered by doing:
 *
 *     import vpiFuncs
 *     vpiFuncs.vp_trace.handlers["FUNC_ENTER"] = trace_process_func_enterexit
 *
 *     Look at the source code of vpiFuncs.py for more information.
 */
#define vp_trace(trace_event, this_fn, filename, line_num) \
        START_VPI_BLOCK(VPI_VP_TRACE_ID, 4, 0, 0) \
        INSERT_VPI_CONST([TRACE_EVENT]) \
        INSERT_VPI_CONST([THIS_FN]) \
        INSERT_VPI_CONST([FILENAME]) \
        INSERT_VPI_CONST([LINE_NUM]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([TRACE_EVENT] "i" (trace_event), [THIS_FN] "i" (this_fn), [LINE_NUM] "i" (line_num), [FILENAME] "i" (filename))

/** === void vp_timing_begin(const char *identifier) ===
 * Begin hi-resolution performance timing on the virtual
 * performance timer whose name is in the "identifier" string
 *
 * Ex: vp_timing_begin("CONTEXT_SWITCH");
 *     ... context switch code to time;
 *     vp_timing_end("CONTEXT_SWITCH");
 *
 * When vp_timing_end() is reached, a timing message will appear
 * on the console listing the time difference between the last
 * vp_timing_begin() and the current vp_timing_end(). The message
 * is printed by the VPI library, in a format easy to extract from
 * logs.
 */
#define vp_timing_begin(identifier, subidentifier) \
        START_VPI_BLOCK(VPI_VP_TIMING_ID, 2, 1, 0) \
        INSERT_VPI_CONST([SUBFUNCTION_ID]) \
        INSERT_VPI_CONST([IDENTIFIER]) \
        INSERT_VPI_VAR([SUBIDENTIFIER]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([SUBFUNCTION_ID] "i" (0), [IDENTIFIER] "i" (identifier), [SUBIDENTIFIER] VPI_IN_CONSTRAINT (sub_id))

/** === void vp_timing_end(const char *identifier) ===
 * End hi-resolution performance timing on the virtual
 * performance timer whose name is in the "identifier" string.
 * See example in vp_timing_begin comment above.
 */
#define vp_timing_end(identifier) \
        START_VPI_BLOCK(VPI_VP_TIMING_ID, 2, 1, 0) \
        INSERT_VPI_CONST([SUBFUNCTION_ID]) \
        INSERT_VPI_CONST([IDENTIFIER]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([SUBFUNCTION_ID] "i" (1), [IDENTIFIER] "i" (identifier))

/** === void vp_timing_extended_begin(const char *identifier, const char *sub_id_type, void *sub_id) ===
 * Same as vp_timing_begin(), except that an arbitrary data item of specified "sub_id_type"
 * (one of "char *", "int" or "hex") will be appended to the identifier dynamically.
 *
 * Must be matched with a vp_timing_extended_end().
 *
 * This allows for the timing of multiple similar events, like context switches of different
 * tasks, using a dynamic element to differentiate them.
 *
 * Example:
 * vp_timing_extended_begin("CONTEXT_SWITCH", "char *", (void *)(&task->name));
 * ... context switch code to time
 * vp_timing_extended_end("CONTEXT_SWITCH", "char *", (void *)(&task->name));
 *
 * Assuming task->name is "myTask", the identifier in the log would be:
 * "CONTEXT_SWITCH@myTask"
 *
 */
#define vp_timing_extended_begin(identifier, sub_id_type, sub_id) \
        START_VPI_BLOCK(VPI_VP_TIMING_ID, 3, 1, 0) \
        INSERT_VPI_CONST([SUBFUNCTION_ID]) \
        INSERT_VPI_CONST([IDENTIFIER]) \
        INSERT_VPI_CONST([SUB_ID_TYPE]) \
        INSERT_VPI_VAR([SUB_ID]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([SUBFUNCTION_ID] "i" (0), [IDENTIFIER] "i" (identifier), [SUB_ID_TYPE] "i" (sub_id_type), [SUB_ID] VPI_IN_CONSTRAINT (sub_id))

/** === void vp_timing_extended_end(const char *identifier, const char *sub_id_type, void *sub_id) ===
 * See vp_timing_extended_end above.
 */
#define vp_timing_extended_end(identifier, sub_id_type, sub_id) \
        START_VPI_BLOCK(VPI_VP_TIMING_ID, 3, 1, 0) \
        INSERT_VPI_CONST([SUBFUNCTION_ID]) \
        INSERT_VPI_CONST([IDENTIFIER]) \
        INSERT_VPI_CONST([SUB_ID_TYPE]) \
        INSERT_VPI_VAR([SUB_ID]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([SUBFUNCTION_ID] "i" (1), [IDENTIFIER] "i" (identifier), [SUB_ID_TYPE] "i" (sub_id_type), [SUB_ID] VPI_IN_CONSTRAINT (sub_id))

/** === FILE *vp_fopen(char *fname, char *mode) ===
 */
#define vp_fopen(fname, mode) \
        START_VPI_BLOCK_RET1(VPI_VP_FOPEN_ID, 0, 2, 1, int, retval ) \
        INSERT_1_VPI_OUTPUTS \
        INSERT_2_VPI_INPUTS \
        END_VPI_BLOCK_RET1_NO_CLOB(retval, [IN0] VPI_IN_CONSTRAINT (fname), [IN1] VPI_IN_CONSTRAINT (mode))

/** === void vp_fclose(FILE *descriptor) ===
 */
#define vp_fclose(descriptor) \
        START_VPI_BLOCK(VPI_VP_FCLOSE_ID, 0, 1, 0 ) \
        INSERT_1_VPI_INPUTS \
        END_VPI_BLOCK_NO_RET_NO_CLOB([IN0] VPI_IN_CONSTRAINT (descriptor))
        
/** === int vp_fread(void *ptr, int size, int count, FILE *descriptor) ===
 */
#define vp_fread(ptr, size, count, descriptor) \
        START_VPI_BLOCK_RET1(VPI_VP_FREAD_ID, 0, 4, 1, int, retval ) \
        INSERT_1_VPI_OUTPUTS \
        INSERT_4_VPI_INPUTS \
        END_VPI_BLOCK_RET1_NO_CLOB(retval, [IN0] VPI_IN_CONSTRAINT (ptr), [IN1] VPI_IN_CONSTRAINT (size), [IN2] VPI_IN_CONSTRAINT (count), [IN3] VPI_IN_CONSTRAINT (descriptor))

/** === int vp_fwrite(void *ptr, int size, int count, FILE *descriptor) ===
 */
#define vp_fwrite(ptr, size, count, descriptor) \
        START_VPI_BLOCK_RET1(VPI_VP_FWRITE_ID, 0, 4, 1, int, retval ) \
        INSERT_1_VPI_OUTPUTS \
        INSERT_4_VPI_INPUTS \
        END_VPI_BLOCK_RET1_NO_CLOB(retval, [IN0] VPI_IN_CONSTRAINT (ptr), [IN1] VPI_IN_CONSTRAINT (size), [IN2] VPI_IN_CONSTRAINT (count), [IN3] VPI_IN_CONSTRAINT (descriptor))

