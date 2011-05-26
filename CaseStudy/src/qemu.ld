/* Linker script for QEMU Simulator
 *
 * Version: Sourcery G++ 2010.09-53
 * Support: https://support.codesourcery.com/GNUToolchain/
 *
 * Copyright (c) 2007, 2008, 2009, 2010 CodeSourcery, Inc.
 *
 * The authors hereby grant permission to use, copy, modify, distribute,
 * and license this software and its documentation for any purpose, provided
 * that existing copyright notices are retained in all copies and that this
 * notice is included verbatim in any distributions.  No written agreement,
 * license, or royalty fee is required for any of the authorized uses.
 * Modifications to this software may be copyrighted by their authors
 * and need not follow the licensing terms described here, provided that
 * the new terms are clearly indicated on the first page of each file where
 * they apply.
 */
OUTPUT_ARCH(powerpc)
ENTRY(__cs3_reset)
SEARCH_DIR(.)
GROUP(-lgcc -lc -lcs3 -lcs3unhosted)

MEMORY
{
  ram (rwx) : ORIGIN = 0x10000000, LENGTH = 144M
}

/* These force the linker to search for particular symbols from
 * the start of the link process and thus ensure the user's
 * overrides are picked up
 */
EXTERN(__cs3_reset __cs3_reset_qemu)
EXTERN(__cs3_start_asm __cs3_start_asm_qemu)
EXTERN(__cs3_start_c main __cs3_stack __cs3_heap_end)

/* Provide fall-back values */
PROVIDE(__cs3_heap_start = _end);
PROVIDE(__cs3_heap_end = __cs3_region_start_ram + __cs3_region_size_ram);
PROVIDE(__cs3_region_num = (__cs3_regions_end - __cs3_regions) / 20);
/* The startup code knows to inherit the provided stack.  */
PROVIDE (__cs3_stack = 0);

SECTIONS
{
  .text :
  {
    CREATE_OBJECT_SYMBOLS
    __cs3_region_start_ram = .;
    _ftext = .;
    *(.cs3.region-head.ram)
    ASSERT (. == __cs3_region_start_ram, ".cs3.region-head.ram not permitted");

    PROVIDE(__cs3_reset = __cs3_reset_qemu);
    *(.cs3.reset)
    __cs3_start_asm_qemu = DEFINED(__cs3_start_asm) ? __cs3_start_asm : __cs3_start_asm_qemu;

    *(.text.cs3.init)
    *(.text .text.* .gnu.linkonce.t.*)

    . = ALIGN(0x4);
    KEEP (*crtbegin.o(.jcr))
    KEEP (*(EXCLUDE_FILE (*crtend.o) .jcr))
    KEEP (*crtend.o(.jcr))

    . = ALIGN(0x4);
    *(.gcc_except_table .gcc_except_table.*)
  } >ram
  .eh_frame_hdr : ALIGN (4)
  {
    KEEP (*(.eh_frame_hdr))
  } >ram
  .eh_frame : ALIGN (4)
  {
    KEEP (*(.eh_frame))
  } >ram
  .rodata : ALIGN (4)
  {
    *(.rodata .rodata.* .gnu.linkonce.r.*)
    *(.rodata1)

    . = ALIGN(4);
    KEEP(*(.init))

    . = ALIGN(4);
    __preinit_array_start = .;
    KEEP (*(.preinit_array))
    __preinit_array_end = .;

    . = ALIGN(4);
    __init_array_start = .;
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array))
    __init_array_end = .;

    . = ALIGN(4);
    KEEP(*(.fini))

    . = ALIGN(4);
    __fini_array_start = .;
    KEEP (*(.fini_array))
    KEEP (*(SORT(.fini_array.*)))
    __fini_array_end = .;

    *(.lit)

    . = ALIGN(4);
    __cs3_regions = .;
    LONG (0)
    LONG (__cs3_region_init_sdata2)
    LONG (__cs3_region_start_sdata2)
    LONG (__cs3_region_init_size_sdata2)
    LONG (__cs3_region_zero_size_sdata2)
    LONG (0)
    LONG (__cs3_region_init_ram)
    LONG (__cs3_region_start_ram)
    LONG (__cs3_region_init_size_ram)
    LONG (__cs3_region_zero_size_ram)
    __cs3_regions_end = .;
    . = ALIGN (8);
    _etext = .;
  } >ram

  ASSERT (!(__cs3_region_init_sdata2 & 7), "__cs3_region_init_sdata2 not aligned")
  ASSERT (!(__cs3_region_start_sdata2 & 7), "__cs3_region_start_sdata2 not aligned")
  ASSERT (!(__cs3_region_init_size_sdata2 & 7), "__cs3_region_init_size_sdata2 not aligned")
  ASSERT (!(__cs3_region_zero_size_sdata2 & 7), "__cs3_region_zero_size_sdata2 not aligned")
  ASSERT (!(__cs3_region_init_ram & 7), "__cs3_region_init_ram not aligned")
  ASSERT (!(__cs3_region_start_ram & 7), "__cs3_region_start_ram not aligned")
  ASSERT (!(__cs3_region_init_size_ram & 7), "__cs3_region_init_size_ram not aligned")
  ASSERT (!(__cs3_region_zero_size_ram & 7), "__cs3_region_zero_size_ram not aligned")
  .sdata2 : ALIGN (8)
  {
    __cs3_region_start_sdata2 = .;
    *(.cs3.region-head.sdata2)
    *(.sdata2 .sdata2.*)
    . = ALIGN (8);
  } >ram
  .sbss2 :
  {
    *(.sbss2 .sbss2.*)
    . = ALIGN (8);
  } >ram
  __cs3_region_init_sdata2 = LOADADDR (.sdata2);
  __cs3_region_init_size_sdata2 = LOADADDR (.sbss2) - LOADADDR (.sdata2);
  __cs3_region_zero_size_sdata2 = SIZEOF(.sbss2);

  .data : ALIGN (8)
  {
    *(.got.plt) *(.got)
    *(.shdata)
    *(.data .data.* .gnu.linkonce.d.*)
    *(.data1 .data1.*)
    *(.got1)
    *(.got2)
    *(.sdata .sdata.*)

    . = ALIGN(0x4);
    KEEP (*ecrti.o(.ctors))
    KEEP (*crtbegin.o(.ctors))
    KEEP (*(EXCLUDE_FILE (*crtend.o *ecrtn.o) .ctors))
    KEEP (*(SORT(.ctors.*)))
    KEEP (*crtend.o(.ctors))
    KEEP (*ecrtn.o(.ctors))

    . = ALIGN(0x4);
    KEEP (*ecrti.o(.dtors))
    KEEP (*crtbegin.o(.dtors))
    KEEP (*(EXCLUDE_FILE (*crtend.o *ecrtn.o) .dtors))
    KEEP (*(SORT(.dtors.*)))
    KEEP (*crtend.o(.dtors))
    KEEP (*ecrtn.o(.dtors))
    . = ALIGN (8);
    *(.ram)
    . = ALIGN (8);
    _edata = .;
  } >ram
  .bss : ALIGN (8)
  {
    *(.sbss .sbss.*)
    *(.scommon)
    *(.dynbss)
    *(.bss .bss.* .gnu.linkonce.b.*)
    *(COMMON)
    . = ALIGN (8);
    *(.ram.b .bss.ram)
    . = ALIGN (8);
    _end = .;
    __end = .;
  } >ram
  __cs3_region_init_ram = __cs3_region_start_ram;
  __cs3_region_init_size_ram = _edata - __cs3_region_start_ram;
  __cs3_region_zero_size_ram = _end - _edata;
  /* Default to 1M of heap */
  __cs3_region_size_ram = ALIGN (1024) - __cs3_region_start_ram + 1M;

  .stab 0 (NOLOAD) : { *(.stab) }
  .stabstr 0 (NOLOAD) : { *(.stabstr) }
  /* DWARF debug sections.
   * Symbols in the DWARF debugging sections are relative to
   * the beginning of the section so we begin them at 0.
   */
  /* DWARF 1 */
  .debug          0 : { *(.debug) }
  .line           0 : { *(.line) }
  /* GNU DWARF 1 extensions */
  .debug_srcinfo  0 : { *(.debug_srcinfo) }
  .debug_sfnames  0 : { *(.debug_sfnames) }
  /* DWARF 1.1 and DWARF 2 */
  .debug_aranges  0 : { *(.debug_aranges) }
  .debug_pubnames 0 : { *(.debug_pubnames) }
  /* DWARF 2 */
  .debug_info     0 : { *(.debug_info .gnu.linkonce.wi.*) }
  .debug_abbrev   0 : { *(.debug_abbrev) }
  .debug_line     0 : { *(.debug_line) }
  .debug_frame    0 : { *(.debug_frame) }
  .debug_str      0 : { *(.debug_str) }
  .debug_loc      0 : { *(.debug_loc) }
  .debug_macinfo  0 : { *(.debug_macinfo) }
  /* DWARF 2.1 */
  .debug_ranges   0 : { *(.debug_ranges) }
  /* SGI/MIPS DWARF 2 extensions */
  .debug_weaknames 0 : { *(.debug_weaknames) }
  .debug_funcnames 0 : { *(.debug_funcnames) }
  .debug_typenames 0 : { *(.debug_typenames) }
  .debug_varnames  0 : { *(.debug_varnames) }
}
/* checksum: 20525f746a505935e6579a530 */
