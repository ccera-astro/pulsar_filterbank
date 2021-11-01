#!/usr/bin/env python2
import os
import sys
import time
import xml.etree.ElementTree as ET

def find_block(root, tag, name):
    foundblock = None
    for block in root.iter("block"):
        key = block.find("key")
        #
        # Block type is correct, also match on "id"
        #
        if (key.text == tag):
            for param in block.findall("param"):
                ky = param.find("key")
                val = param.find("value")
                if (ky.text == "id" and val.text == name):
                    foundblock = block
                    break
        if (foundblock != None):
            break
    return foundblock

def update_block(root, tag, name, subdict):
    block = find_block(root, tag, name)
    if (block != None):
        for param in block.findall("param"):
            ky = param.find("key")
            if (ky.text in subdict):
                newval = subdict[ky.text]
                val = param.find("value")
                val.text = newval

def update_connection(root, source, sink, insub):
    for conn in root.iter("connection"):
        source_key = conn.find("source_block_id")
        sink_key = conn.find("sink_block_id")
        if (source_key.text == source and sink_key.text == sink):
            source_key.text = insub

def delete_connection(root, source, sink):
    for conn in root.iter("connection"):
        source_key = conn.find("source_block_id")
        sink_key = conn.find("sink_block_id")
        if (source_key.text == source and sink_key.text == sink):
            root.remove(conn)

def delete_block(root, tag, name):
	block = find_block(root, tag, name)
	if (block != None):
		root.remove(block)


tree = ET.parse(sys.argv[1])
fp = open(sys.argv[1])
lines = fp.readlines()
header = lines[0] + lines[1]
fp.close()
root = tree.getroot()
fp = open(sys.argv[3], "r")
lines = fp.readlines()
for line in lines:
    line = line.replace("(", "(root, ", 1)
    print(line)
    eval(line)
fp.close()

fp = open(sys.argv[2], "w")
fp.write(header)

tree.write(fp)
fp.close()
