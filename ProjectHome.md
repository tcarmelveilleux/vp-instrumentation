# Introduction #
This project is the central hub for dissemination of the "VPI" (Virtual Platform Instrumentation) framework as described by Tennessee Carmel-Veilleux, Jean-François Boland and Guy Bois in a conference article presented at the 2011 IEEE International Symposium on Rapid System Prototyping.

The VPI framework can be used to implement semihosting, profiling, tracing and other instrumentation use cases on existing virtual platforms and ISSes with better performance than existing approaches.

Our Python implementation is directly usable under any ISS with GDB support. It also supports the Simics virtual platform.

# Implementations #
We currently have a complete implementation supporting the PowerPC architecture and several virtual platforms. More support is to come with external involvement. Don't hesitate to contact the project members if you want to participate :)

## Supported architectures ##
  * PowerPC (full)
  * x86 (work-in-progress)
  * ARM (work-in-progress)

## Supported virtual platforms ##
  * Generic (any with GDB support)
  * Wind River Simics 4.0+
  * Qemu

# Availability #
Source code for the VPI implementation (trunk/VPI) as well as our case study (trunk/CaseStudy) are available.

  * The file "trunk/CaseStudy/src/VPI-case-study.c" has examples of VPI in use.
  * The file "trunk/VPI/include/vpi.h" is the main VPI implementation header for use in C code.
  * The files "trunk/VPI/vpi.py" and "trunk/VPI/vpiFuncs.py" are the VPII and VPIFs  implementations, respectively, as described in the paper.

# References #
Full reference to the paper on IEEE Xplore and the PowerPoint presentation from the conference will come after the proceedings appear.

In the meantime:
> Carmel-Veilleux, Tennessee, Jean François Boland and Guy Bois: A Novel Low-Overhead Flexible Instrumentation Framework for Virtual Platforms. In Proc. 22nd IEEE International Symposium on Rapid System Prototyping, May 2011, Karlsruhe, Germany.