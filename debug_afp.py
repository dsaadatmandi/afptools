#!/usr/bin/env python3
"""
Debug script for AFP file parsing.
"""

import sys
import os
import time
import struct
from typing import List, Optional

# Import our AFP parser
from afptools.parser import AFPParser, AFPStructuredField


def debug_parse_afp(file_path: str) -> None:
    """
    Parse an AFP file with detailed debugging output.
    
    Args:
        file_path: Path to the AFP file
    """
    print(f"Debugging AFP file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    try:
        # Open the file and read the first few bytes
        with open(file_path, 'rb') as f:
            header = f.read(16)  # Read first 16 bytes
        
        print(f"File header (hex): {header.hex()}")
        
        # Try to parse the first structured field
        if len(header) >= 5:
            length = struct.unpack('>H', header[0:2])[0]
            type_code = header[2:5]
            print(f"First field length: {length}")
            print(f"First field type code (hex): {type_code.hex()}")
            
            # Check if it's a known type
            known_types = {
                AFPStructuredField.BDT: "BDT (Begin Document)",
                AFPStructuredField.EDT: "EDT (End Document)",
                AFPStructuredField.BPG: "BPG (Begin Page)",
                AFPStructuredField.EPG: "EPG (End Page)",
                AFPStructuredField.BRG: "BRG (Begin Resource Group)",
                AFPStructuredField.ERG: "ERG (End Resource Group)"
            }
            
            if type_code in known_types:
                print(f"First field type: {known_types[type_code]}")
            else:
                print(f"First field type: Unknown")
        
        # Now try to parse the whole file with progress updates
        print("\nParsing file...")
        start_time = time.time()
        
        # Create parser
        parser = AFPParser(file_path)
        
        # Open file and read in chunks to track progress
        with open(file_path, 'rb') as f:
            data = f.read()
        
        print(f"Read {len(data)} bytes from file")
        
        # Parse structured fields with progress tracking
        offset = 0
        field_count = 0
        last_progress = 0
        
        while offset < len(data):
            # Print progress every 10%
            progress = int(offset * 100 / len(data))
            if progress >= last_progress + 10:
                print(f"Parsing: {progress}% complete ({field_count} fields)")
                last_progress = progress
            
            # Check if we have at least 2 bytes for the length
            if offset + 2 > len(data):
                print(f"Reached end of file at offset {offset}")
                break
            
            # Get the length of the next structured field
            try:
                field_length = struct.unpack('>H', data[offset:offset+2])[0]
                
                # Sanity check on field length
                if field_length < 5 or field_length > 32767:
                    print(f"Warning: Invalid field length {field_length} at offset {offset}")
                    # Try to recover by skipping this byte
                    offset += 1
                    continue
                
                # Check if we have enough data for the complete field
                if offset + field_length > len(data):
                    print(f"Warning: Incomplete field at offset {offset}, length {field_length}")
                    break
                
                # Get the type code
                type_code = data[offset+2:offset+5]
                
                # Print info about this field
                if field_count < 10 or field_count % 1000 == 0:
                    type_name = known_types.get(type_code, "Unknown")
                    print(f"Field {field_count}: offset={offset}, length={field_length}, type={type_code.hex()} ({type_name})")
                
                # Move to the next field
                offset += field_length
                field_count += 1
                
            except Exception as e:
                print(f"Error parsing field at offset {offset}: {str(e)}")
                offset += 1  # Try to recover by skipping this byte
        
        end_time = time.time()
        print(f"\nParsing completed in {end_time - start_time:.2f} seconds")
        print(f"Total fields found: {field_count}")
        
        # Now try to identify pages
        print("\nIdentifying pages...")
        page_count = 0
        
        for i in range(field_count):
            if i < len(parser.fields) and parser.fields[i].type_code == AFPStructuredField.BPG:
                page_count += 1
                if page_count <= 5:  # Show details for first 5 pages
                    print(f"Page {page_count} starts at field index {i}")
        
        print(f"Total pages found: {page_count}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <afp_file>")
        sys.exit(1)
    
    debug_parse_afp(sys.argv[1])
