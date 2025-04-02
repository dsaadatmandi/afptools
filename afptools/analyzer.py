"""
AFP File Analyzer Module - Analyzes AFP files and provides detailed information.
"""

import os
import struct
from typing import Dict, List, Any, Optional, Tuple

from afptools.parser import AFPStructuredField


# Known AFP structured field type codes (in hex)
AFP_TYPES = {
    # Document level
    "d3a8a8": "BDT (Begin Document)",
    "d3a9a8": "EDT (End Document)",
    
    # Page level
    "d3a8af": "BPG (Begin Page)",
    "d3a9af": "EPG (End Page)",
    
    # Resource level
    "d3a8c6": "BRG (Begin Resource Group)",
    "d3a9c6": "ERG (End Resource Group)",
    
    # Other common types
    "d3a8c9": "BOG (Begin Object)",
    "d3a9c9": "EOG (End Object)",
    "d3a8a7": "BMM (Begin Mixed Mode)",
    "d3a9a7": "EMM (End Mixed Mode)",
    "d3a8fb": "BPT (Begin Presentation Text)",
    "d3a9fb": "EPT (End Presentation Text)",
    "d3a8df": "BDI (Begin Document Index)",
    "d3a9df": "EDI (End Document Index)",
}


def analyze_afp_file(file_path: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Analyze an AFP file and return detailed information.
    
    Args:
        file_path: Path to the AFP file
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary with analysis results
    """
    result = {
        "file_path": file_path,
        "file_size": 0,
        "is_afp": False,
        "field_count": 0,
        "page_count": 0,
        "fields": [],
        "errors": [],
        "warnings": []
    }
    
    if verbose:
        print(f"Analyzing AFP file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        result["errors"].append(f"File not found: {file_path}")
        return result
    
    # Get file size
    file_size = os.path.getsize(file_path)
    result["file_size"] = file_size
    
    if verbose:
        print(f"File size: {file_size} bytes")
    
    try:
        # Read the entire file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        if verbose:
            print(f"Read {len(data)} bytes from file")
            print(f"First 16 bytes (hex): {data[:16].hex()}")
        
        # Try different parsing strategies
        result.update(try_parse_standard_afp(data, verbose))
        
        # If standard parsing didn't work, try alternative formats
        if not result["is_afp"] and result["field_count"] == 0:
            result.update(try_parse_alternative_formats(data, verbose))
        
        # Final determination
        if result["field_count"] > 0:
            if result["is_afp"]:
                if verbose:
                    print("File appears to be a standard AFP file")
            else:
                if verbose:
                    print("File appears to be a non-standard AFP-like file")
                result["warnings"].append("Non-standard AFP format detected")
        else:
            if verbose:
                print("File does not appear to be an AFP file")
            result["errors"].append("Not a recognized AFP format")
        
    except Exception as e:
        result["errors"].append(f"Error analyzing file: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
    
    return result


def try_parse_standard_afp(data: bytes, verbose: bool = False) -> Dict[str, Any]:
    """
    Try to parse the file as a standard AFP file.
    
    Args:
        data: File data
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary with parsing results
    """
    result = {
        "is_afp": False,
        "field_count": 0,
        "page_count": 0,
        "fields": [],
        "errors": [],
        "warnings": []
    }
    
    if verbose:
        print("\nTrying standard AFP parsing...")
    
    # Parse structured fields
    offset = 0
    field_count = 0
    page_count = 0
    
    while offset < len(data):
        # Check if we have at least 5 bytes (minimum for a structured field)
        if offset + 5 > len(data):
            if verbose:
                print(f"Reached end of file at offset {offset}")
            break
        
        try:
            # Get the length of the next structured field (first 2 bytes)
            field_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            # Sanity check on field length
            if field_length < 5 or field_length > 32767:
                if verbose:
                    print(f"Invalid field length {field_length} at offset {offset}")
                result["warnings"].append(f"Invalid field length {field_length} at offset {offset}")
                offset += 1
                continue
            
            # Check if we have enough data for the complete field
            if offset + field_length > len(data):
                if verbose:
                    print(f"Incomplete field at offset {offset}, length {field_length}")
                result["warnings"].append(f"Incomplete field at offset {offset}, length {field_length}")
                break
            
            # Get the type code (next 3 bytes)
            type_code = data[offset+2:offset+5]
            type_hex = type_code.hex()
            
            # Check if it's a known AFP type
            type_name = AFP_TYPES.get(type_hex, "Unknown")
            
            # Store field info
            field_info = {
                "offset": offset,
                "length": field_length,
                "type_code": type_hex,
                "type_name": type_name
            }
            
            if verbose and (field_count < 10 or field_count % 1000 == 0):
                print(f"Field {field_count}: offset={offset}, length={field_length}, type={type_hex} ({type_name})")
            
            # Check for page markers
            if type_hex == "d3a8af":  # BPG
                page_count += 1
                field_info["is_page_start"] = True
                if verbose and page_count <= 5:
                    print(f"Page {page_count} starts at field {field_count}, offset {offset}")
            
            # Add to fields list (limit to first 100 for memory reasons)
            if len(result["fields"]) < 100:
                result["fields"].append(field_info)
            
            # Move to the next field
            offset += field_length
            field_count += 1
            
            # If we found at least one valid AFP field, mark as AFP
            if type_hex in AFP_TYPES:
                result["is_afp"] = True
            
        except Exception as e:
            if verbose:
                print(f"Error parsing field at offset {offset}: {str(e)}")
            result["errors"].append(f"Error at offset {offset}: {str(e)}")
            offset += 1  # Try to recover by skipping this byte
    
    result["field_count"] = field_count
    result["page_count"] = page_count
    
    if verbose:
        print(f"Standard parsing found {field_count} fields and {page_count} pages")
    
    return result


def try_parse_alternative_formats(data: bytes, verbose: bool = False) -> Dict[str, Any]:
    """
    Try to parse the file using alternative AFP-like formats.
    
    Args:
        data: File data
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary with parsing results
    """
    result = {
        "is_afp": False,
        "field_count": 0,
        "page_count": 0,
        "fields": [],
        "errors": [],
        "warnings": []
    }
    
    if verbose:
        print("\nTrying alternative AFP formats...")
    
    # Look for common AFP signatures
    signatures = [
        (b'\x5a\x00', "MODCA"),
        (b'\xd3\xa8\xa8', "BDT"),
        (b'\xd3\xa8\xaf', "BPG")
    ]
    
    for sig, name in signatures:
        positions = find_all(data, sig)
        if positions:
            if verbose:
                print(f"Found {name} signature at offsets: {positions[:5]}")
            
            # Try parsing from each signature position
            for pos in positions[:5]:  # Try first 5 positions
                if verbose:
                    print(f"Trying to parse from {name} signature at offset {pos}")
                
                # Try to parse from this position
                sub_result = try_parse_from_offset(data, pos, verbose)
                
                # If we found fields, use this result
                if sub_result["field_count"] > result["field_count"]:
                    result = sub_result
                    if verbose:
                        print(f"Found better parsing result: {sub_result['field_count']} fields")
    
    return result


def try_parse_from_offset(data: bytes, start_offset: int, verbose: bool = False) -> Dict[str, Any]:
    """
    Try to parse the file starting from a specific offset.
    
    Args:
        data: File data
        start_offset: Offset to start parsing from
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary with parsing results
    """
    result = {
        "is_afp": False,
        "field_count": 0,
        "page_count": 0,
        "fields": [],
        "errors": [],
        "warnings": []
    }
    
    # Parse structured fields
    offset = start_offset
    field_count = 0
    page_count = 0
    
    while offset < len(data):
        # Check if we have at least 5 bytes (minimum for a structured field)
        if offset + 5 > len(data):
            break
        
        try:
            # Get the length of the next structured field (first 2 bytes)
            field_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            # Sanity check on field length
            if field_length < 5 or field_length > 32767:
                offset += 1
                continue
            
            # Check if we have enough data for the complete field
            if offset + field_length > len(data):
                break
            
            # Get the type code (next 3 bytes)
            type_code = data[offset+2:offset+5]
            type_hex = type_code.hex()
            
            # Check if it's a known AFP type
            if type_hex in AFP_TYPES:
                field_count += 1
                
                # Check for page markers
                if type_hex == "d3a8af":  # BPG
                    page_count += 1
                
                # If we found a valid AFP field, mark as AFP
                result["is_afp"] = True
            
            # Move to the next field
            offset += field_length
            
        except Exception:
            offset += 1  # Try to recover by skipping this byte
    
    result["field_count"] = field_count
    result["page_count"] = page_count
    
    if verbose and field_count > 0:
        print(f"Alternative parsing from offset {start_offset} found {field_count} fields and {page_count} pages")
    
    return result


def find_all(data: bytes, sub: bytes) -> List[int]:
    """
    Find all occurrences of a subsequence in data.
    
    Args:
        data: Data to search in
        sub: Subsequence to find
        
    Returns:
        List of positions where the subsequence was found
    """
    positions = []
    start = 0
    
    while True:
        start = data.find(sub, start)
        if start == -1:
            break
        positions.append(start)
        start += 1
    
    return positions


def format_analysis_report(analysis: Dict[str, Any]) -> str:
    """
    Format a human-readable report of the AFP file analysis.
    
    Args:
        analysis: Analysis results from analyze_afp_file
        
    Returns:
        Formatted report as a string
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"AFP File Analysis Report: {analysis['file_path']}")
    lines.append("=" * 60)
    
    lines.append(f"\nFile size: {analysis['file_size']} bytes")
    
    if analysis["errors"]:
        lines.append("\nErrors:")
        for error in analysis["errors"]:
            lines.append(f"  - {error}")
    
    if analysis["warnings"]:
        lines.append("\nWarnings:")
        for warning in analysis["warnings"]:
            lines.append(f"  - {warning}")
    
    lines.append(f"\nAFP Format: {'Standard' if analysis['is_afp'] else 'Non-standard or not AFP'}")
    lines.append(f"Total fields: {analysis['field_count']}")
    lines.append(f"Total pages: {analysis['page_count']}")
    
    if analysis["fields"]:
        lines.append("\nFirst fields:")
        for i, field in enumerate(analysis["fields"][:10]):
            lines.append(f"  {i}: offset={field['offset']}, length={field['length']}, type={field['type_code']} ({field['type_name']})")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)
