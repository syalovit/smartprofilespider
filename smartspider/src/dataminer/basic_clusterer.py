'''
Created on Dec 23, 2014

@author: Eloise
'''

from db.file_based import readSeedIndex
from transport.linkedin import LINKEDIN

def main():
    idx = readSeedIndex(LINKEDIN)
    
