"""
Simple regexp-driven text substitution function to
extract data from lists of lines using regexps

By Tennessee Carmel-Veilleux (veilleux -at- tentech.ca)
Version 1.1

This code is in the public domain. For more info:
http://www.tentech.ca/index.php/the-extract_lines-text-extraction-module-for-python

History
-------
10/28/2009: Initial version 1.0 release
11/21/2009: Version 1.1 (Tennessee Carmel-Veilleux)
            * added "removeStart" parameter
            * documented more exemples
"""
import re

def extract_lines(lines, startPat, endPat, extractPat, subPat, removeStart = True):
    """
    Extract all lines matching "extractPat" between the first line
    matching "startPat" and the first line matching "endPat".
    
    * The function returns a list of lines for which the "subPat" has been
      applied as a substitution pattern on the matching group from the
      "extractPat".
    * It is possible for "endPat" and "extractPat" to be the same.
    * "subPat" can be a function which can receive a Match object, or
      a regexp. See Python library reference for re.sub().
    * "extractPat" will be applied
    * Substitution is not done on the matching group of startPat
    * If "removeStart" is True (the default), the matching portion of the 
      start pattern will be removed from the first line before matching
      of "extractPat" begins. Otherwise ("removeStart" is False), the
      extractPat can be applied even on the portion of the first line
      containing the extractPattern.
    
    -----
    - Test the extraction of a std_logic_vector
    >>> lines = ['CONSTANT filter_in_force : filter_in_table :=',
    ...     '(',
    ...     ' to_stdlogicvector(bit_vector\\'(X"123"))(11 DOWNTO 0),',
    ...     ' to_stdlogicvector(bit_vector\\'(X"9ab"))(11 DOWNTO 0),',
    ...     ' to_stdlogicvector(bit_vector\\'(X"cde"))(11 DOWNTO 0),',
    ...     ' to_stdlogicvector(bit_vector\\'(X"FFF"))(11 DOWNTO 0));']
    >>> newLines = extract_lines(lines,
    ...     "filter_in_table :=", # Find table declaration
    ...     "[)];", # End on line with ");"
    ...     '.*X"([0-9a-fA-F]+)".*', # Extract hex values
    ...     r"0x\\1") # Replace with 0x + hex value extracted
    >>>
    ... i = 0
    >>> for line in newLines:
    ...     print "%d: %s" % (i, line)
    ...     i = i+1
    ...
    0: 0x123
    1: 0x9ab
    2: 0xcde
    3: 0xFFF
    >>>
    
    """

    # Local copy of lines for extracting
    localLines = lines[:]
    
    # Reinitialize state machine
    done = False
    state = "look_for_start"
    
    # Compile necessary regexps
    startMatcher = re.compile(startPat)
    endMatcher = re.compile(endPat)
    extractMatcher = re.compile(extractPat)
    crlfMatcher = re.compile("[\n\r]")
    
    # Result list
    resultLines = []
    
    while (len(localLines) <> 0) and (not done):
        line = localLines.pop(0)
        
        # Waiting for the startPat to occur
        if state == "look_for_start":
            # Immediately switch to extracting upon startMatcher local match
            startMatch = startMatcher.search(line)
            if startMatch:
                state = "extract_lines"
                
                if not removeStart:
                    # Reinsert start line altogether if specified
                    localLines.insert(0, line)
                else:
                    # Reinsert start line with startMatch removed if anything is left
                    if not len(line[startMatch.end():].strip()) == 0:
                        localLines.insert(0, line[startMatch.end():])
        elif state == "extract_lines":
            if extractMatcher.search(line):
                # On extract match, apply substition and store
                newLine = extractMatcher.sub(subPat, line)
                newLine = crlfMatcher.sub("", newLine)
                resultLines.append(newLine)
            
            if endMatcher.search(line):
                # Terminate extraction
                done = True
        else:
            raise RuntimeError("Invalid State Reached !")
    
    return resultLines
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
