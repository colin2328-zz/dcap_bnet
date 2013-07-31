'''Demonstration of a possible task file

Author: Alexander Waldin
'''

import argparse
import os

parser = argparse.ArgumentParser(description='Demo Task')
parser.add_argument('dataDirectory',type=str)
parser.add_argument('resultsDirectory',type=str)
args = parser.parse_args()
print 'running demo script'


print 'loading transferred data from ', args.dataDirectory
dataHandle = open(os.path.join(args.dataDirectory,'demotext.txt'),'r')
text = dataHandle.readlines()
dataHandle.close()
print text
resultHandle = open(os.path.join(args.resultsDirectory,'demoresult.txt'),'w')
resultHandle.writelines(text)
resultHandle.close()
print 'client done running demo script'