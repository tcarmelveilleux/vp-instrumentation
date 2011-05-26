"""
Case study data analysis script for the VPI framework.

Created on: December 30, 2010
Author: Tennessee Carmel-Veilleux (tcv -at- ro.boto.ca)
Revision: $Id: caseStudyAnalysis.py 237 2011-01-31 21:11:20Z veilleux $

Description:
Case study data analysis script for the VPI framework.

License (BSD):
Copyright 2010 Tennessee Carmel-Veilleux and
Ecole de technologie superieure (University of Quebec).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
    * Neither the name of Tennessee Carmel-Veilleux or Ecole de
Technologie Superieure (ETRS) nor the names of its contributors may be
used to endorse or promote products derived from this software without
specific prior written permission.

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

import matplotlib as plt
plt.use("WXAgg")
from matplotlib import rc
#rc('font',**{'family':'serif','sans-serif':['Times']})
rc('font',**{'family':'serif', 'serif':['Times New Roman']})
#rc('font',**{'family':'serif','serif':['Times'], 'sans-serif':["Helvetica"]})
#rc('text', usetex=True)
from pylab import *
import csv
import re

def get_test_context(binFilename):
    match = re.search("VPI-case-study-([A-Za-z0-9_]*)-([A-Za-z0-9_]*)-trig_([A-Za-z0-9_]*)-pf_([A-Za-z0-9_]*)(-pc_([A-Za-z0-9_]*))?(-trace_([A-Za-z0-9_]*))?-O([A-Za-z0-9_]*)", binFilename, re.MULTILINE)
    if match:
        result = {}
        result["virtualPlatform"] = match.group(1)
        result["benchmark"] = match.group(2)
        result["triggerMethod"] = match.group(3)
        result["printf"] = match.group(4)
        result["trace"] = match.group(8)
        result["putc"] = "NONE"
        result["optLevel"] = match.group(9)
        return result
    else:
        raise ValueError("### Error parsing binFilename=%s" % binFilename)

def parse_results(filename):
    # Results set is a dictionnary of lists. The binFilename of a test
    # uniquely identifies a tests's context. The results set is keyed
    # by binFilename. For each dict entry, a list of all results for
    # that key is provided. Each result is itself a dictionary of the
    # values keyed by column name.
    #
    # Ex: { "binFilename1" : [{"column1" : "value1", "column2" : "value3", "column3" : "value3"},
    #                         {"column1" : "value1", "column2" : "value3", "column3" : "value3"},
    #                         {"column1" : "value1", "column2" : "value3", "column3" : "value3"}],
    #       "binFilename2" : [{"column1" : "value1", "column2" : "value3", "column3" : "value3"},
    #                         {"column1" : "value1", "column2" : "value3", "column3" : "value3"},
    #                         {"column1" : "value1", "column2" : "value3", "column3" : "value3"}]}
    resultsSet = {}

    # Open a TSV reader on the simulation results file
    inFile = file(filename, "r")
    reader = csv.DictReader(inFile, dialect = csv.excel_tab)

    # Load data from the results file
    for row in reader:
        # Create the list for a result set the first time around
        if not row["binFilename"] in resultsSet:
            resultsSet[row["binFilename"]] = []

        # Build a test result entry from the current row
        testResult = {}
        for key, value in row.iteritems():
            if key != "binFilename":
                testResult[key] = value

        # Store the current row of results in the proper bin
        resultsSet[row["binFilename"]].append(testResult)

    inFile.close()

    return resultsSet

def filter_sim_results(simResultsSet):
    """
    Steps:
      1- Replace "cpuStartTime" and "cpuStopTime" key with "cpuTime" key.
         Actual cpuTime is 12 times the value measured (since we are using
         TBL on e600 which runs at 1/4 of MPX Bus which is 1/3 of CPU CLK)
      2- Replace value of "simTimeDuration" with its float equivalent
      3- Sort lists of results by "simTimeDuration"
    """
    #newSimResultsSet = {}
    for key, results in simResultsSet.iteritems():
        for result in results:
            # Step 1- Replace "cpuStartTime" and "cpuStopTime" key with "cpuTime" key
            result["cpuTime"] = (long(result.pop("cpuStopTime")) - long(result.pop("cpuStartTime"))) * 12
            # Step 2- Replace value of "simTimeDuration" with its float equivalent
            result["simTimeDuration"] = float(result["simTimeDuration"])

        # Step 3- Sort lists of results by "simTimeDuration"
        results.sort(key = lambda item : item["simTimeDuration"])

    return simResultsSet
    #return newSimResultsSet

def delete_outliers(values):
    valuesMean = mean(values)
    valuesDev = std(values)

    # Outliers are found to be the points more than +/- 3.0 standard
    # deviations from the mean
    set1 = values >= (valuesMean - (3.0 * valuesDev))
    set2 = values <= (valuesMean + (3.0 * valuesDev))
    newValues = values[find(logical_and(set1, set2))]

    """
    NOT CURRENTLY USED:
    The outliers are found by using the algorithm at:

    http://rfd.uoregon.edu/files/rfd/StatisticalResources/outl.txt

    The Python implementation is derived from http://www.gisnotes.com/wordpress/2007/11/removing-point-outliers/.

    valuesMed = median(newValues)
    valuesDev = newValues - valuesMed
    valuesMedOfDev = median(abs(valuesDev))
    final = abs(valuesDev) / valuesMedOfDev
    print final
    """
    return newValues

def calculate_sim_results_stats(simResultsSet):
    """
    Calculate the statistics of the simulation results

    For each binFilename, we calculate the min, max, average and stddev of simTimeDuration.
    We also store the cpuTime in the new results set.

    Outliers are removed. The outliers are found by checking for all points outside
    3 standard deviations of the mean.
    """
    print simResultsSet
    simResultsStats = {}
    for key, results in simResultsSet.iteritems():
        simResultsStats[key] = {}

        # Get list of all sim time durations
        simTimeDurations = array([item["simTimeDuration"] for item in results], float32())
        simTimeDurations = delete_outliers(simTimeDurations)
        cpuTimes = array([item["cpuTime"] for item in results], int32())
        simResultsStats[key]["simTimeDurations"] = simTimeDurations
        simResultsStats[key]["min"] = min(simTimeDurations)
        simResultsStats[key]["max"] = max(simTimeDurations)
        simResultsStats[key]["average"] = mean(simTimeDurations)
        simResultsStats[key]["stddev"] = std(simTimeDurations)
        simResultsStats[key]["cpuTime"] = mean(cpuTimes)

    # Find the minimum average value for use in normalization
    minSimTimeAverage = min([value["average"] for key, value in simResultsStats.iteritems()])

    # Find normalized values of dataset and recalculate mean and standard error
    for key, results in simResultsSet.iteritems():
        # Normalize sim time durations
        simTimeDurations = simResultsStats[key]["simTimeDurations"] / minSimTimeAverage

        simResultsStats[key]["averageNorm"] = mean(simTimeDurations)
        simResultsStats[key]["stddevNorm"] = std(simTimeDurations)

    return simResultsStats

def keep_sets(simResults, keyIndexFunc, keepFunc = None, **kwargs):
    newResults = {}
    for key, results in simResults.iteritems():
        # Get key index dictionary from key
        keyIndex = keyIndexFunc(key)

        if keepFunc:
            # keepFunc is a function that returns True if the item must
            # be kept.
            keepItem = keepFunc(keyIndex)
        else:
            # Each kwarg is a keyName = keepValues. If the key's
            # key index does not have each keyName equal to any of
            # the keepValues, reject the key.
            keepItem = True

            for keepKey, keepValues in kwargs.iteritems():
                if not keepValues: continue

                if keyIndex[keepKey] not in keepValues:
                    keepItem = False
                    break

        if keepItem:
            newResults[key] = results

    return newResults

def exclude_gdb_vpi(keyIndex):
    print keyIndex
    if keyIndex["triggerMethod"] == "GDB" and ("VPI" in (keyIndex["printf"],  keyIndex["putc"])):
        return False
    else:
        return True

def plot_sim_times(simResultsStats, ax, showLegend):
    """
    Plot simulation times in increasing order of normalized run time.

    Style of the chart is modified from the BSD-licensed example at:
    http://matplotlib.sourceforge.net/examples/api/barchart_demo.html
    as accessed on Dec 31, 2010.
    """
    ax.set_yscale("log", nonposy='clip')
    baseIndex = 0

    def autolabel(rects):
        # Attach mean time label to each column
        for newIdx, newRect in enumerate(rects):
            height = newRect.get_height()
            heightStr = '%.3f' % height
            if len(heightStr) > 5:
                heightStr = heightStr[0:5]
            ax.text(newRect.get_x() + newRect.get_width()/2.,
                    height-(0.25*height),
                    heightStr,
                    ha='center', va='top', size = 5)
            #ax.text(newRect.get_x() + newRect.get_width()/2.,
            #        1.05 * (simTimesMeans[newIdx] + simTimesStd[newIdx]),
            #        '%.3fs' % simTimesMeans[newIdx],
            #        ha='center', va='bottom', size = "xx-small")

    labels = []
    rects = []

    for idx, color in zip(range(len(simResultsStats)), ["w", "0.8"]):
        N = len(simResultsStats[idx])
        keys = simResultsStats[idx].keys()
        simTimesMeans = array([simResultsStats[idx][key]["average"] for key in keys])
        simTimesMin = array([simResultsStats[idx][key]["min"] for key in keys])
        simTimesMax = array([simResultsStats[idx][key]["max"] for key in keys])
        simTimesStd = [simResultsStats[idx][key]["stddev"] for key in keys]
        simTimesMeansNorm = [simResultsStats[idx][key]["averageNorm"] for key in keys]
        simTimesStdNorm = [simResultsStats[idx][key]["stddevNorm"] for key in keys]

        # Sort by simTimesMeans
        group = list(zip(keys, simTimesMeans, simTimesStd, simTimesMeansNorm, simTimesStdNorm, simTimesMin, simTimesMax))
        group.sort(key = lambda item: item[1])
        keys, simTimesMeans, simTimesStd, simTimesMeansNorm, simTimesStdNorm , simTimesMin, simTimesMax = zip(*group)

        ind = arange(N) + baseIndex  # the x locations for the groups
        width = 1.0                  # the width of the bars

        # Plot bars and save artists
        bars = ax.bar(ind + (width / 2.0), simTimesMeans, width, color=color, error_kw = {"ecolor": "k", "linewidth" : 0.5}, yerr=(3.0 * array(simTimesStd)))
        rects.append(bars)

        # Shift for next set
        baseIndex += len(bars)

        # Label bars
        for key in keys:
            print key, simResultsStats[idx][key]["average"]
            equiv = {"NONE": "None", "MAGIC": "Internal", "GDB" : "External", "C" : "Full-code", "VPI" : "VPI", "SEMI" : "Stub-call"}
            context = get_test_context(key)
            if context["triggerMethod"] == "NONE" and context["printf"] == "NONE":
                labels.append("Base")
            elif context["printf"] in ["C", "SEMI"]:
                labels.append("%s" % (equiv[context["printf"]]))
            else:
                
                labels.append("%s %s" % (equiv[context["triggerMethod"]], equiv[context["printf"]]))

        autolabel(bars)

    # Add styling
    ax.set_ylabel('Simulation time (seconds)', size = "xx-small")
    #ax.set_title('Simulation run times for QURT benchmark')
    ax.set_xticks(arange(len(simResultsStats[0]) + len(simResultsStats[1])) + width)
    ax.set_ylim(bottom=0.1)
    ax.yaxis.grid(which = "both", linewidth = 0.4)
    ax.set_axisbelow(True)

    #ax.xaxis.set_major_locator(IndexLocator(1.0,0.0))
    #ax.xaxis.set_minor_locator(IndexLocator(1.0,0.5))

    #ax.xaxis.set_major_formatter(NullFormatter())
    #ax.xaxis.set_minor_formatter(FixedFormatter(labels))
    ax.set_xticklabels( labels, size = 5, ha = "right", rotation = 45 )

    for tick in ax.get_xticklines():
        print repr(tick.get_data())
    #for tick in ax.xaxis.get_minor_ticks():
    #    tick.tick1line.set_markersize(0)
    #    tick.tick2line.set_markersize(0)
        #tick.label1.set_horizontalalignment('center')

    formatter = FixedFormatter(["0.1","1","10","100"])
    #formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(formatter)

    if showLegend:
        ax.legend( (rects[0][0],rects[1][0]), ('Simics', 'QEMU'), loc = "upper left", prop = {"size" : "x-small"} )

    # Fix sizes
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize("xx-small")

    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize("xx-small")

def keep_main_cases(keyIndex):
    if keyIndex["printf"] == "NONE":
        if keyIndex["triggerMethod"] == "NONE":
            return True
        else:
            return False
    else:
        return True

def exclude_none_none(keyIndex):
    return not (keyIndex["printf"] == "NONE" and keyIndex["triggerMethod"] == "NONE")


def plot_cpu_times(simResultsSets, ax):
    """
    Plot CPU times in increasing order of normalized run time.

    Style of the chart is modified from the BSD-licensed example at:
    http://matplotlib.sourceforge.net/examples/api/barchart_demo.html
    as accessed on Dec 31, 2010.
    """

    def autolabel(bars):
        # Attach mean time label to each column
        for idx, rect in enumerate(bars):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2.,
                    1.01 * height,
                    '%d' % height,
                    ha='center', va='bottom', size = "xx-small")

    patterns = ""
    rects = []

    for optInd, optLevel, hatch, color in zip(range(4), ("0", "1", "2", "3"), (".","\\\\", "//", "x"), ("w", "w", "w", "w")):
        tempSimResultsSets = keep_sets(simResultsSets, get_test_context, keepFunc = keep_main_cases)
        simResultsStats = calculate_sim_results_stats(keep_sets(tempSimResultsSets, get_test_context, optLevel = [optLevel]))

        # Get base case
        simResultNone = keep_sets(simResultsStats, get_test_context, printf = "NONE", triggerMethod = "NONE").values()[0]["cpuTime"]

        # Delete NONE NONE case
        simResultsStats = keep_sets(simResultsStats, get_test_context, keepFunc = exclude_none_none)

        ax.hold(True)

        N = len(simResultsStats)

        keys = simResultsStats.keys()
        cpuTimes = [simResultsStats[key]["cpuTime"] for key in keys]
        simTimesMeans = [simResultsStats[key]["average"] for key in keys]

        # Sort by simTimesMeans
        group = list(zip(keys, simTimesMeans, cpuTimes))
        group.sort(key = lambda item: item[1])
        keys, simTimesMeans, cpuTimes = zip(*group)
        print "optLevel = %s" % optLevel, cpuTimes

        ind = arange(N)  # the x locations for the groups
        width = 0.25      # the width of the bars

        bars = ax.bar((1.25*ind) + (optInd * width), cpuTimes - simResultNone, width, color=color, hatch=hatch)
        rects.append(bars)
        autolabel(bars)

    # Add labels and titles
    ax.yaxis.grid(which = "both")
    ax.set_axisbelow(True)
    ax.set_ylabel('Simulation CPU cycles', size = "small")
    ax.set_xticks((0.5,1.75))

    labels = []
    for key in keys:
        context = get_test_context(key)
        labels.append("%s" % (context["triggerMethod"]))

    ax.set_xticklabels( labels, size = "medium" )

    # Add legend
    ax.legend( (rects[0][0], rects[1][0], rects[2][0], rects[3][0]) , ('-O0', '-O1', '-O2', '-O3'), prop = {"size" : "small"})

    # Fix sizes
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize("x-small")
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize("x-small")

def analyze_binaries_sizes(binResultsSet):
    # Keep only -O2 results
    binResultsSet = keep_sets(binResultsSet, get_test_context, optLevel = ["2"])

    # Extract data lists for each analyzed variable from results set
    keys = binResultsSet.keys()
    for key in keys:
        print key
    textSizes = array([binResultsSet[key][0]["textSize"] for key in keys], int32())
    dataSizes = array([binResultsSet[key][0]["dataSize"] for key in keys], int32())
    rodataSizes = array([binResultsSet[key][0]["rodataSize"] for key in keys], int32())
    bssSizes = array([binResultsSet[key][0]["bssSize"] for key in keys], int32())

    # Sort by textSize
    results = list(zip(keys, textSizes, dataSizes, rodataSizes, bssSizes))
    results.sort(key = lambda item: item[1])

    print "VP\tTrigger\tprintf()\t.text\t.data\t.bss\t.rodata\ttotal"

    #keys, textSizes, dataSizes, rodataSizes, bssSizes = zip(*group)
    baseCase = results[0]

    for idx, result in enumerate(results):
        key = result[0]

        # For all results but the base case, use relative values
        if idx != 0:
            resultValues = array(result[1:]) - array(baseCase[1:])
        else:
            resultValues = array(result[1:])

        textSize, dataSize, rodataSize, bssSize = tuple(resultValues)

        # Build results line: |case name | .text size | .data size | .bss size | .rodata size| total
        resultLine = []
        context = get_test_context(key)

        if idx == 0:
            sizeFormat = "%d"
        else:
            sizeFormat = "%+d"

        resultLine.append("%s" % context["virtualPlatform"])
        resultLine.append("%s" % context["triggerMethod"])
        resultLine.append("%s" % context["printf"])
        resultLine.append(sizeFormat % textSize)
        resultLine.append(sizeFormat % dataSize)
        resultLine.append(sizeFormat % bssSize)
        resultLine.append(sizeFormat % rodataSize)
        resultLine.append(sizeFormat % (textSize + dataSize + bssSize + rodataSize))
        print "\t".join(resultLine)

def plot_all_sim_times(simResultsSimics, simResultsQemu, filename):
    rc('xtick',direction = 'out')

    def keep_printf_vpi(keyIndex):
        if keyIndex["putc"] == "VPI" or keyIndex["optLevel"] != "2":
            return False
        else:
            return True

    fig = plt.figure(figsize = (3.2,2.5), dpi=200)
    fig.subplots_adjust(left=0.125, right = 0.975, top = 0.95)
    fig.hold(True)
    ax = fig.add_subplot(111)

    tempSimResultsSimics = keep_sets(simResultsSimics, get_test_context, keepFunc = keep_printf_vpi)
    # XXX: Hack for one case:
    if not simResultsQemu:
        tempSimResultsQemu = keep_sets(simResultsSimics, get_test_context, keepFunc = keep_printf_vpi)
        showLegend = False
    else:
        tempSimResultsQemu = keep_sets(simResultsQemu, get_test_context, keepFunc = keep_printf_vpi)
        showLegend = True
    
    simResultsStats = (calculate_sim_results_stats(tempSimResultsSimics), calculate_sim_results_stats(tempSimResultsQemu))
    plot_sim_times(simResultsStats, ax, showLegend)
        # plot_sim_times(keep_sets(simResultsStats, get_test_context, keepFunc = exclude_gdb_vpi), axes[virtualPlatform])

    #fig.suptitle('Simulation times for printf() scenario', size = "small", y = 0.99)
    #fig.autofmt_xdate(rotation = 90)
    fig.subplots_adjust(bottom = 0.25)
    if filename:
        fig.savefig("../Paper/Figures/simTimes.pdf", dpi=600)
    plt.show()

def plot_all_cpu_times(simResultsSet):
    fig = plt.figure(figsize = (3.2,3.2))
    fig.subplots_adjust(left=0.2, right = 0.95)
    fig.hold(True)
    axes = {"Simics" : fig.add_subplot(111)}

    for virtualPlatform in ("Simics", ):
        tempSimResultsSet = keep_sets(simResultsSet, get_test_context, virtualPlatform = [virtualPlatform], putc = ["NONE"])
        plot_cpu_times(tempSimResultsSet, axes[virtualPlatform])
        # plot_sim_times(keep_sets(simResultsStats, get_test_context, keepFunc = exclude_gdb_vpi), axes[virtualPlatform])

    fig.suptitle('Simulation CPU cycles increase', size = "small")
    fig.savefig("../Paper/Figures/cpuTimes.pdf", dpi=600)
    plt.show()


if __name__ == "__main__":
     #runTimesSet = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults_simics_only_50.tsv")
     # runTimesSimics = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults_all_runtimes_O0-O3.tsv")
     runTimesSimics = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults_all_runtimes.tsv")
     runTimesSimics = filter_sim_results(runTimesSimics)
     runTimesQemu = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults_all_runtimes_qemu.tsv")
     runTimesQemu = filter_sim_results(runTimesQemu)
     plot_all_sim_times(runTimesSimics, runTimesQemu, "../Paper/Figures/simTimes.pdf")

     runTimesSimics = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults.tsv")
     runTimesSimics = filter_sim_results(runTimesSimics)
     plot_all_sim_times(runTimesSimics, None, None)
     
     #cpuTimesSet = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\simResults_all_runtimes_O0-O3_old.tsv")
     #cpuTimesSet = filter_sim_results(cpuTimesSet)
     #plot_all_cpu_times(cpuTimesSet)

     #binResultsSet = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\binaries_simics_and_qemu.tsv")
     binResultsSet = parse_results(r"C:\Users\veilleux\Desktop\Schoolwork\Maitrise\AREXIMAS\(THESIS) Debugging\CaseStudy\temp\binaries_all_runtimes.tsv")
     analyze_binaries_sizes(binResultsSet)