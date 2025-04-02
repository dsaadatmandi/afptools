"""
Command-line interface for AFP Tools.
"""

import argparse
import sys
from typing import List, Optional

from afptools.parser import AFPParser
from afptools.operations import extract_pages
from afptools.utils import parse_page_range
from afptools.analyzer import analyze_afp_file, format_analysis_report


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description='AFP file manipulation tools',
        prog='afptools'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Extract pages command
    extract_parser = subparsers.add_parser('extract', help='Extract pages from AFP file')
    extract_parser.add_argument('input', help='Input AFP file path')
    extract_parser.add_argument('output', help='Output AFP file path')
    extract_parser.add_argument('pages', help='Page range (e.g., "1:3, 5, 7:")')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze AFP file structure')
    analyze_parser.add_argument('input', help='Input AFP file path')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # If no command specified, show help
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    # Execute appropriate command
    if parsed_args.command == 'extract':
        return execute_extract(parsed_args.input, parsed_args.output, parsed_args.pages)
    elif parsed_args.command == 'analyze':
        return execute_analyze(parsed_args.input, parsed_args.verbose)
    
    # Unknown command
    print(f"Unknown command: {parsed_args.command}")
    return 1


def execute_extract(input_path: str, output_path: str, page_range: str) -> int:
    """
    Execute the extract pages command.
    
    Args:
        input_path: Path to the input AFP file
        output_path: Path where the output AFP file will be written
        page_range: Page range string (e.g., "1:3, 5, 7:")
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse the AFP file
        print(f"Parsing AFP file: {input_path}")
        parser = AFPParser(input_path)
        parser.parse()
        
        # Get total number of pages
        total_pages = parser.get_total_pages()
        print(f"Total pages in document: {total_pages}")
        
        # Parse page range
        print(f"Parsing page range: {page_range}")
        page_numbers = parse_page_range(page_range, total_pages)
        print(f"Selected pages: {[p+1 for p in page_numbers]}")  # Convert back to 1-indexed for display
        
        # Extract pages
        print(f"Extracting pages to: {output_path}")
        success = extract_pages(parser, page_numbers, output_path)
        
        if success:
            print(f"Successfully extracted {len(page_numbers)} pages to {output_path}")
            return 0
        else:
            print("Failed to extract pages")
            return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


def execute_analyze(input_path: str, verbose: bool = False) -> int:
    """
    Execute the analyze command.
    
    Args:
        input_path: Path to the input AFP file
        verbose: Whether to show verbose output
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Analyze the AFP file
        analysis = analyze_afp_file(input_path, verbose)
        
        # Print the analysis report
        print(format_analysis_report(analysis))
        
        # Return success if we could analyze the file, even if it's not a standard AFP
        if analysis["errors"]:
            return 1
        return 0
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
