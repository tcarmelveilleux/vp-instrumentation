/*
 * vpi-case-study.c
 *
 * Main VPI Case study code
 * 
 * Created on: 30/11/2010
 * Author: Tennessee Carmel-Veilleux (tennessee.carmelveilleux@gmail.com)
 * Revision: $Rev$
 * 
 * Copyright 2010 Tennessee Carmel-Veilleux and Ecole de technologie supérieure
 * 
 * Description: 
 * Main VPI case study code
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
#include <stdint.h>
#include <stdio.h>

#if !defined(VPI_TRIGGER_METHOD_NONE)
#include "vpi.h"

#if defined(TRACE_VPI) || defined(TRACE_GCC)
#undef vp_gcc_inst_trace
#define vp_gcc_inst_trace(trace_item, this_fn, filename, line_num) \
        START_VPI_BLOCK(VPI_VP_TRACE_ID, 4, 0, 0) \
        INSERT_VPI_CONST([TRACE_ITEM]) \
        INSERT_VPI_CONST([THIS_FN]) \
        INSERT_VPI_CONST([FILENAME]) \
        INSERT_VPI_CONST([LINE_NUM]) \
        END_VPI_BLOCK_NO_RET_NO_CLOB([TRACE_ITEM] "i" (trace_item), [THIS_FN] "i" (this_fn), [LINE_NUM] "i" (line_num), [FILENAME] "i" (filename))
#else
#undef vp_gcc_inst_trace
#define vp_gcc_inst_trace(trace_item, this_fn, filename, line_num)
#endif
#else
#undef vp_gcc_inst_trace
#define vp_gcc_inst_trace(trace_item, this_fn, filename, line_num)
#endif

#if defined(TRACE_VPI)
#define vp_gcc_inst_trace_inline(trace_item, this_fn, filename, line_num) vp_gcc_inst_trace(trace_item, this_fn, filename, line_num)
#else
#define vp_gcc_inst_trace_inline(trace_item, this_fn, filename, line_num)
#endif

/* Two levels of macro to permit macro expansion within stringification (GNU C Preprocessor sec 3.4) */
#define stringify(s)    tostring(s)
#define tostring(s) #s

#ifdef PLATFORM_Qemu
#define KERNEL_MSR 0x00002040UL
#else
#define KERNEL_MSR 0x00002070UL
#endif

#define mtmsr(value)    asm volatile("isync; sync; mtmsr %0; isync; sync;" : : "r" (value) : "memory")
#define mftbu()     ({uint32_t rval; asm volatile("mftbu %0" : "=r" (rval)); rval;})
#define mttbu(value)    asm volatile("mttbu %0" : : "r" (value) : "memory")
#define mftb()     ({uint32_t rval; asm volatile("mftb %0" : "=r" (rval)); rval;})
#define mttbl(value)    asm volatile("mttbl %0" : : "r" (value) : "memory")

#define mtspr(sprn, value)    asm volatile("mtspr " stringify(sprn) ",%0" : : "r" (value) : "memory")
#define HID0    1008

unsigned long CASE_STUDY_START_TIME;
unsigned long CASE_STUDY_STOP_TIME;

static void init_console(void)
{
	freopen ("/dev/ttyS0", "w", stdout);
	setvbuf (stdout, (char *) NULL, _IONBF, 0);
}

int open (const char *filename, int flags, int mode)
{
	return 42;
}

int my_write (int fd, const void *buf, size_t count)
{
#if 0
        char *p = (char *)buf;
	size_t my_count = count;

	while (my_count--)
	{
	    vp_putc(*p++);
	}
#endif
	/* Dummy write */
	return count;
}

#ifdef BENCHMARK_QURT

void my_printf(char *format_str, double x11, double x12, double x21, double x22)
{
#if !defined(VPI_TRIGGER_METHOD_NONE)
    vp_printf4f("Roots: x1 = (%.6f%+.6fj) x2 = (%.6f%+.6fj)\n", x11, x12, x21, x22);
#endif
}

#if defined(PRINTF_VPI)
#define EXPERIMENTAL_PRINTF vp_printf4f("Roots: x1 = (%.6f%+.6fj) x2 = (%.6f%+.6fj)\n", x1[0], x1[1], x2[0], x2[1])
#elif defined(PRINTF_C)
#define EXPERIMENTAL_PRINTF printf("Roots: x1 = (%.6f%+.6fj) x2 = (%.6f%+.6fj)\n", x1[0], x1[1], x2[0], x2[1])
#elif defined(PRINTF_SEMI)
#define EXPERIMENTAL_PRINTF my_printf("Roots: x1 = (%.6f%+.6fj) x2 = (%.6f%+.6fj)\n", x1[0], x1[1], x2[0], x2[1])
#else
#define EXPERIMENTAL_PRINTF
#endif
#endif


#if 0
volatile long long x;

__inline__ void test_asm(int a, int b)
{
	int c, d, e, f, i, j, k, l;
	char stringvar[] = "roboto";
	float w = 123.4f;

	l = 23;

	stringvar[0] = 'c';

	for (i = 0; i < 10; i++)
	{
		stringvar[0] = '0' + i;
		c = a;
		d = b;
		e = f = j = k = i;
		x = (long long)i << (32 + i - 1);
		/*vp_test_in3_out4("HELLO", x, l, j, a, x, l, i); */
		vp_printf4("Hello world 0x%016lx, %d, %s, %f\n", x, i, stringvar, (double)w);
		/*printf("Hello world 0x%016llx, %d, %s, %f\n", x, i, stringvar, w); */
	}
}

int main(void)
{
	test_asm(1,2);
	return 0;
}

#endif

#ifdef BENCHMARK_QURT
/*************************************************************************/
/*                                                                       */
/*   SNU-RT Benchmark Suite for Worst Case Timing Analysis               */
/*   =====================================================               */
/*                              Collected and Modified by S.-S. Lim      */
/*                                           sslim@archi.snu.ac.kr       */
/*                                         Real-Time Research Group      */
/*                                        Seoul National University      */
/*                                                                       */
/*                                                                       */
/*        < Features > - restrictions for our experimental environment   */
/*                                                                       */
/*          1. Completely structured.                                    */
/*               - There are no unconditional jumps.                     */
/*               - There are no exit from loop bodies.                   */
/*                 (There are no 'break' or 'return' in loop bodies)     */
/*          2. No 'switch' statements.                                   */
/*          3. No 'do..while' statements.                                */
/*          4. Expressions are restricted.                               */
/*               - There are no multiple expressions joined by 'or',     */
/*                'and' operations.                                      */
/*          5. No library calls.                                         */
/*               - All the functions needed are implemented in the       */
/*                 source file.                                          */
/*                                                                       */
/*                                                                       */
/*************************************************************************/
/*                                                                       */
/*  FILE: qurt.c                                                         */
/*  SOURCE : Turbo C Programming for Engineering by Hyun Soo Ahn         */
/*                                                                       */
/*  DESCRIPTION :                                                        */
/*                                                                       */
/*     Root computation of quadratic equations.                          */
/*     The real and imaginary parts of the solution are stored in the    */
/*     array x1[] and x2[].                                              */
/*                                                                       */
/*  REMARK :                                                             */
/*                                                                       */
/*  EXECUTION TIME :                                                     */
/*                                                                       */
/*                                                                       */
/*************************************************************************/

/*
 ** Benchmark Suite for Real-Time Applications, by Sung-Soo Lim
 **
 **    III-7. qurt.c : the root computation of a quadratic equation
 **                 (from the book C Programming for EEs by Hyun Soon Ahn)
 */
static double a[3], x1[2], x2[2];
static int flag;

static int qurt(void);
static double sqrt(double val);
static double fabs(double n);

#ifndef TRACE_NONE
#define __cyg_profile(name) \
    START_VPI_BLOCK(VPI_VP_TRACE_ID, 1, 2, 0) \
    INSERT_VPI_CONST([TRACE_ITEM]) \
    INSERT_2_VPI_INPUTS \
    END_VPI_BLOCK_NO_RET_NO_CLOB([TRACE_ITEM] "i" (name), [IN0] "r" (this_fn), [IN1] "r" (call_site))
#else
#define __cyg_profile(name)
#endif

void __attribute__((no_instrument_function)) __cyg_profile_func_enter (void *this_fn, void *call_site)
{
    /* __cyg_profile("CYG_PROFILE_FUNC_ENTER"); */
    vp_gcc_inst_trace("FUNC_ENTER", "GENERIC", __FILE__, __LINE__);
}

void __attribute__((no_instrument_function)) __cyg_profile_func_exit (void *this_fn, void *call_site)
{
    /*__cyg_profile("CYG_PROFILE_FUNC_EXIT");*/
    vp_gcc_inst_trace("FUNC_EXIT", "GENERIC", __FILE__, __LINE__);
}

static inline int qurt(void) {
	double d, w1, w2;

	vp_gcc_inst_trace_inline("FUNC_ENTER", "QURT", __FILE__, __LINE__);

	if (a[0] == 0.0)
	{
	    vp_gcc_inst_trace_inline("FUNC_EXIT", "QURT", __FILE__, __LINE__);
	    return (999);
	}
	d = a[1] * a[1] - 4 * a[0] * a[2];
	w1 = 2.0 * a[0];
	w2 = sqrt(fabs(d));
	if (d > 0.0) {
		flag = 1;
		x1[0] = (-a[1] + w2) / w1;
		x1[1] = 0.0;
		x2[0] = (-a[1] - w2) / w1;
		x2[1] = 0.0;
		vp_gcc_inst_trace_inline("FUNC_EXIT", "QURT", __FILE__, __LINE__);
		return (0);
	} else if (d == 0.0) {
		flag = 0;
		x1[0] = -a[1] / w1;
		x1[1] = 0.0;
		x2[0] = x1[0];
		x2[1] = 0.0;
		vp_gcc_inst_trace_inline("FUNC_EXIT", "QURT", __FILE__, __LINE__);
		return (0);
	} else {
		flag = -1;
		w2 /= w1;
		x1[0] = -a[1] / w1;
		x1[1] = w2;
		x2[0] = x1[0];
		x2[1] = -w2;
		vp_gcc_inst_trace_inline("FUNC_EXIT", "QURT", __FILE__, __LINE__);
		return (0);
	}
}

static inline double fabs(double n) {
	double f;

	vp_gcc_inst_trace_inline("FUNC_ENTER", "FABS", __FILE__, __LINE__);

	if (n >= 0)
		f = n;
	else
		f = -n;

	vp_gcc_inst_trace_inline("FUNC_EXIT", "FABS", __FILE__, __LINE__);
	return f;
}

static inline double sqrt(double val) {
	double x = val / 10;

	double dx;

	double diff;
	double min_tol = 0.00001;

	int i, flag;

	vp_gcc_inst_trace_inline("FUNC_ENTER", "SQRT", __FILE__, __LINE__);

	flag = 0;
	if (val == 0)
		x = 0;
	else {
		for (i = 1; i < 20; i++) {
			if (!flag) {
				dx = (val - (x * x)) / (2.0 * x);
				x = x + dx;
				diff = val - (x * x);
				if (fabs(diff) <= min_tol)
					flag = 1;
			} else
				x = x;
		}
	}

	vp_gcc_inst_trace_inline("FUNC_EXIT", "SQRT", __FILE__, __LINE__);
	return (x);
}

int main(void) {
	int i,j;

	vp_gcc_inst_trace_inline("FUNC_ENTER", "MAIN", __FILE__, __LINE__);

	mtmsr(KERNEL_MSR);
	mttbu(0UL);
	mttbl(0UL);
        mtspr(HID0, (1UL << 26));

        init_console();

	CASE_STUDY_START_TIME = mftb();

	for (i = 0; i < 100; i++)
	{
		for (j = 0; j < 100; j++)
		{
			a[0] = (double)(j+1);
			a[1] = -3.0;
			a[2] = 2.0;

			qurt();
		}
		EXPERIMENTAL_PRINTF;
	}

	for (i = 0; i < 100; i++)
	{
		for (j = 0; j < 100; j++)
		{
			a[0] = (double)(j+1);
			a[1] = -2.0;
			a[2] = 1.0;

			qurt();
		}
		EXPERIMENTAL_PRINTF;
	}

	for (i = 0; i < 100; i++)
	{
		for (j = 0; j < 100; j++)
		{
			a[0] = (double)(j+1);
			a[1] = -4.0;
			a[2] = 8.0;

			qurt();
		}
		EXPERIMENTAL_PRINTF;
	}

	vp_gcc_inst_trace_inline("FUNC_EXIT", "MAIN", __FILE__, __LINE__);

	CASE_STUDY_STOP_TIME = mftb();

#ifdef PLATFORM_Qemu
	printf("###### CASE_STUDY1 ######\t%lu\t%lu\n",CASE_STUDY_START_TIME, CASE_STUDY_STOP_TIME);
#else

#endif
	return 0;
}
#endif
