import sys
import re


"""
Prints usage of the application
"""
def printUsage():
    print("Usage of the application: ")
    print()
    print("Application for converting 2D L-systems to PovRay (.pov) file for visualization")
    print("Arguments:")
    print("-in filePath  - path to input file (required)")
    print("-out filePath - path to output file, if not given, file will be named as input file_out.pov")
    print("-h print usage of the appliaction")
    print()
    print("Input file format:")
    print("Input file should contain L-system logic, number of iterations, angle, starting axiom and rules")
    print("each on the separate line, key first, value second, separated by ':'")
    print("Parser is case sensitive.")
    print("Example")
    print("iterations:6")
    print("angle:30")
    print("axiom:DH")
    print("rules:D=DF:H=FFFF[++++L][----P]H:L=F[--F][++F]L:P=F[--F][++F]P")
    print("Accepted characters are alphabetic characters as axioms, +/- as turning 'angle' degrees (+ left, - right)")
    print("[] representing subsegment")


"""
For the given opened file checks that it contains all needed information about the L-system
and returns this information for usage in a tuple
"""
def parseFile(fileName):
    iterations = 0
    angle = 0
    axiom = ""
    rules = {}
    with open(fileName) as file:
        for line in file:
            lineAttributes = line.rstrip().split(":")
            key = lineAttributes[0]
            if key == "iterations":
                iterations = int(lineAttributes[1])
            elif key == "angle":
                angle = int(lineAttributes[1])
            elif key == "axiom":
                axiom = lineAttributes[1]
            elif key == "rules":
                for i in range(1, len(lineAttributes)):
                    rule = lineAttributes[i].split("=")
                    if len(rule) != 2:
                        return None
                    rules[rule[0]] = rule[1]
            else:
                print("ERROR: Invalid input file format")
                return None
    return iterations, angle, axiom, rules


"""
For given string of axioms, rules and number of iterations returns axiom after the number of iterations
"""
def iterateSystem(iterations, axioms, rules):
    for _ in range(iterations):
        newAxiom = ""
        for axiom in axioms:
            if axiom in rules:
                newAxiom += rules[axiom]
            else:
                newAxiom += axiom
        axioms = newAxiom
    return axioms


"""
For given axioms, angle and input file will create output file that can be run by PovRay
and visualizes given L-system after given number of iterations
"""
def createPovRayFile(angle, axioms, fileName, outFileName):
    if outFileName is None:
        out = fileName.split(".")[0] + "_out.pov"
    else:
        out = outFileName
    
    file = open(out, "w")
    file.write('#include "colors.inc"\n')
    file.write("background { color White }\n")
    file.write("#declare Angle = " + str(angle) + ";\n")
    # declaring basic Stick for the model
    file.write("#declare Stick = cylinder {\n")
    file.write("    <0, 0, 0>,\n") # coords of the center of one end
    file.write("    <0, 2, 0>\n")  # coords of the center of other end
    file.write("    0.5\n")  # radius
    file.write("    texture {\n")
    file.write("        pigment { colour Green }\n")
    file.write("    }\n")
    file.write("}\n")
    # end of Stick
    axioms = defineSegments(file, angle, axioms)
    count = defineSegment(file, axioms, angle, "tree")
    # setting camera
    file.write("camera {\n")
    file.write("    location <0, " + str(count) + ", -10>\n")
    file.write("    look_at <0, " + str(count) + ", 0>\n")
    file.write("    angle 0\n")
    file.write("}\n")
    file.write("\nobject { tree rotate y*0 translate z*" + str(count*2) +" }\n")
    file.close()


"""
Given string that does not contaion '[' / ']' and open output file
will write declaration of that segment in PovRay language
"""
def defineSegment(file, string, angle, segmentName):
    actualAngle = 0
    file.write("#declare " + segmentName + " = object {\n")
    index = 0
    count = 0
    axiom = string[index]
    file.write("    union {\n")
    while axiom == "+" or axiom == "-":
        if axiom == "+":
            actualAngle += angle
        else:
            actualAngle -= angle
        index += 1
        axiom = string[index]
    while index < len(string):
        axiom = string[index]
        if axiom != "s":
            file.write("    object { Stick translate y*2*" + str(count) + " }\n")
            index += 1
            count += 1
        else:
            file.write("    object { " + string[index:index+6] + \
                       " translate y*2*" + str(count) + " }\n")
            index += 6
        #count += 1
    file.write("    rotate <0, 0, " + str(actualAngle) + "> } }\n")
    file.write("\n")
    return count
            

"""
For opened output file and string of axiom will each segment closed by [] be replaced by segment name and declared
into the output file
"""
def defineSegments(file, angle, axioms):
    match = re.match(r"^.*\[(.*?)\].*$", axioms)
    segmentNumber = 0
    while match != None:
        segmentName = "seg" + str(segmentNumber).zfill(3)
        axioms = axioms.replace("[" + match.group(1) + "]", segmentName)
        defineSegment(file, match.group(1), angle, segmentName)
        segmentNumber += 1
        match = re.match(r"^.*\[(.*?)\].*$", axioms)
        #print(axioms)
    return axioms


def main():
    argvLen = len(sys.argv)
    if argvLen == 0:
        print("Invalid number of arguments (0)")
        return
    inFile = None
    outFile = None
    print(sys.argv)
    for i in range(argvLen):
        arg = sys.argv[i]
        if arg == "-in" and i+1 < argvLen:
            inFile = sys.argv[i+1]
        elif arg == "-out" and i+1 < argvLen:
            outFile = sys.argv[i+1]
        elif arg == "-h":
            printUsage()
            return
    if inFile is None:
        print("ERROR: Input file not given")
        printUsage()
        return
    fileArguments = parseFile(inFile)
    if fileArguments is None:
        return
    iterations, angle, axioms, rules = fileArguments
    axioms = iterateSystem(iterations, axioms, rules)
    createPovRayFile(angle, axioms, inFile, outFile)
    print("Ended successfully")
    return

main()
