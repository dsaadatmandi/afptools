"""
Utility functions for AFP Tools.
"""

from typing import List, Tuple


def parse_page_range(range_str: str, total_pages: int) -> List[int]:
    """
    Parse a page range string into a list of page numbers.
    
    Supports formats:
    - Single pages: "5"
    - Ranges: "1:3" (pages 1-3)
    - Open-ended ranges: "7:" (page 7 to end)
    - Combinations: "1:3, 5, 7:"
    
    Args:
        range_str: String containing page ranges
        total_pages: Total number of pages in the document
        
    Returns:
        List of 0-indexed page numbers
    """
    if not range_str.strip():
        raise ValueError("Page range cannot be empty")
    
    result = []
    
    # Split by commas
    parts = [p.strip() for p in range_str.split(',')]
    
    for part in parts:
        if not part:
            continue
        
        # Check if it's a range (contains ':')
        if ':' in part:
            start_str, end_str = part.split(':', 1)
            
            # Parse start (default to 1 if empty)
            start = int(start_str) if start_str.strip() else 1
            
            # Parse end (default to total_pages if empty)
            end = int(end_str) if end_str.strip() else total_pages
            
            # Validate range
            if start < 1:
                raise ValueError(f"Page numbers must be >= 1, got {start}")
            if end > total_pages:
                raise ValueError(f"End page {end} exceeds total pages {total_pages}")
            if start > end:
                raise ValueError(f"Start page {start} cannot be greater than end page {end}")
            
            # Add pages to result (convert to 0-indexed)
            result.extend(range(start - 1, end))
        else:
            # Single page
            page = int(part)
            
            # Validate page number
            if page < 1:
                raise ValueError(f"Page numbers must be >= 1, got {page}")
            if page > total_pages:
                raise ValueError(f"Page {page} exceeds total pages {total_pages}")
            
            # Add to result (convert to 0-indexed)
            result.append(page - 1)
    
    # Remove duplicates and sort
    return sorted(set(result))


def validate_afp_structure(fields: List) -> bool:
    """
    Perform basic validation of AFP structure.
    
    Args:
        fields: List of AFPStructuredField objects
        
    Returns:
        True if structure appears valid, False otherwise
    """
    # Import here to avoid circular imports
    from afptools.parser import AFPStructuredField
    
    # Check if we have at least one field
    if not fields:
        return False
    
    # Check if we have a Begin Document
    has_bdt = any(field.type_code == AFPStructuredField.BDT for field in fields)
    
    # Check if we have an End Document
    has_edt = any(field.type_code == AFPStructuredField.EDT for field in fields)
    
    # Check if we have at least one Begin Page
    has_bpg = any(field.type_code == AFPStructuredField.BPG for field in fields)
    
    # Basic validation: should have BDT, EDT, and at least one BPG
    return has_bdt and has_edt and has_bpg
