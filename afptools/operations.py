"""
Operations for AFP file manipulation.
"""

import os
from typing import List

from afptools.parser import AFPParser, AFPStructuredField
from afptools.utils import validate_afp_structure


def extract_pages(parser: AFPParser, page_numbers: List[int], output_path: str) -> bool:
    """
    Extract specified pages from an AFP file.
    
    Args:
        parser: Initialized and parsed AFPParser instance
        page_numbers: List of 0-indexed page numbers to extract
        output_path: Path where the output AFP file will be written
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If the file cannot be processed or if no pages were found
    """
    # Check if the file has any pages
    if not parser.page_indices:
        raise ValueError("No pages found in the AFP file. The file may not be a valid AFP file or may not contain any pages.")
    
    # Check if any of the requested pages are valid
    valid_pages = [p for p in page_numbers if p < len(parser.page_indices)]
    if not valid_pages:
        raise ValueError(f"None of the requested pages ({page_numbers}) are valid. The file has {len(parser.page_indices)} pages.")
    
    # If some pages are invalid, print a warning
    if len(valid_pages) < len(page_numbers):
        invalid_pages = [p for p in page_numbers if p >= len(parser.page_indices)]
        print(f"Warning: Skipping invalid pages: {[p+1 for p in invalid_pages]} (file has {len(parser.page_indices)} pages)")
    
    # Get all fields from the resource section
    resource_fields = parser.fields[:parser.resource_end_index]
    
    # Get fields for each specified page
    page_fields = []
    for page_num in valid_pages:
        start_idx = parser.page_indices[page_num]
        
        # Find end index (start of next page or end of file)
        if page_num + 1 < len(parser.page_indices):
            end_idx = parser.page_indices[page_num + 1]
        else:
            # For the last page, find the next EDT (End Document) or use the end of file
            end_idx = len(parser.fields)
            for i in range(start_idx + 1, len(parser.fields)):
                if parser.fields[i].type_code == AFPStructuredField.EDT:
                    end_idx = i
                    break
        
        # Add all fields for this page
        page_fields.extend(parser.fields[start_idx:end_idx])
    
    # If we have an EDT (End Document) in the original file, make sure we include it
    has_edt = False
    for field in page_fields:
        if field.type_code == AFPStructuredField.EDT:
            has_edt = True
            break
    
    if not has_edt and parser.fields:
        # Look for EDT in the original file
        for field in reversed(parser.fields):
            if field.type_code == AFPStructuredField.EDT:
                page_fields.append(field)
                break
    
    # Combine resource fields and page fields
    output_fields = resource_fields + page_fields
    
    # Validate the structure
    if not validate_afp_structure(output_fields):
        print("Warning: Generated AFP file structure may not be valid")
    
    # Write the output file
    return write_afp_file(output_fields, output_path)


def write_afp_file(fields: List[AFPStructuredField], output_path: str) -> bool:
    """
    Write structured fields to an AFP file.
    
    Args:
        fields: List of AFPStructuredField objects
        output_path: Path where the output AFP file will be written
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for field in fields:
                f.write(field.to_bytes())
        
        return True
    except Exception as e:
        print(f"Error writing AFP file: {str(e)}")
        return False
