import os
from subprocess import PIPE, Popen
import sys

# Return RAM information (unit=kb) in a list                                        
# Index 0: total RAM                                                                
# Index 1: used RAM                                                                 
# Index 2: free RAM

def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])
print(getRAMinfo())

# Return % of CPU used by user as a character string                                
def getCPUuse():
    return(str(os.popen("top -n3 -o %CPU | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

os.popen("top -n 3 -o %CPU | awk '{print $2}'").readline().strip())
print(getCPUuse())
