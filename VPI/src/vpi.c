/*
 * vpi.c
 *
 * Source file for external VPI interception methods
 * 
 * Created on: 30/11/2010
 * Author: Tennessee Carmel-Veilleux (tennessee.carmelveilleux@gmail.com)
 * Revision: $Rev$
 * 
 * Copyright 2010 Tennessee Carmel-Veilleux and Ecole de technologie supérieure
 * 
 * Description: 
 * Source file for external VPI interception methods, such as GDB breakpoint
 * interception. Not required unless a global variable needs to be used.
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
#ifndef VPI_TRIGGER_METHOD_NONE
#include "vpi.h"
#endif

#ifdef VPI_TRIGGER_METHOD_GDB
/* Force the existence of a single global variable for
 * watching and add a marker string to be able to find it
 * by memory search of the program image.
 */

void VPIvpiVPI_trigger_dummy(int dummy)
{
	__asm__ __volatile__ (".data\n\t"
		 ".balign 8\n\t"
		 ".globl VPIvpiVPI_trigger\n"
		 "VPIvpiVPI_trigger:\n\t"
		 ".long 0\n\t"
		 ".asciz \"VPIvpiVPIvpiVPIvpiVPIvp\"\n\t"
		 ".previous\n\t ":::);
}
#endif
