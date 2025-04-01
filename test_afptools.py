#!/usr/bin/env python3
"""
Test script for AFP Tools.

This script demonstrates how to use the AFP Tools package.
It doesn't actually run since we don't have a sample AFP file,
but it shows the expected usage pattern.
"""

from afptools.parser import AFPParser
from afptools.operations import extract_pages
from afptools.utils import parse_page_range


def main():
    """
    Demonstrate AFP Tools usage.
    """
    # Sample file paths (these don't exist)
    input_path = "sample.afp"
    output_path = "output.afp"
    page_range = "1:3, 5, 7:"
    
    print(f"Parsing AFP file: {input_path}")
    print("(This is just a demonstration - no actual file is being processed)")
    
    # In a real scenario, you would do:
    # parser = AFPParser(input_path)
    # parser.parse()
    # total_pages = parser.get_total_pages()
    # page_numbers = parse_page_range(page_range, total_pages)
    # extract_pages(parser, page_numbers, output_path)
    
    print("\nExample code for using AFP Tools:")
    print("""
    from afptools.parser import AFPParser
    from afptools.operations import extract_pages
    from afptools.utils import parse_page_range
    
    # Parse the AFP file
    parser = AFPParser("input.afp")
    parser.parse()
    
    # Get total number of pages
    total_pages = parser.get_total_pages()
    print(f"Total pages: {total_pages}")
    
    # Parse page range
    page_range = "1:3, 5, 7:"
    page_numbers = parse_page_range(page_range, total_pages)
    print(f"Selected pages: {[p+1 for p in page_numbers]}")
    
    # Extract pages
    extract_pages(parser, page_numbers, "output.afp")
    print("Pages extracted successfully!")
    """)
    
    print("\nCommand-line usage:")
    print("afptools extract input.afp output.afp \"1:3, 5, 7:\"")


if __name__ == "__main__":
    main()
