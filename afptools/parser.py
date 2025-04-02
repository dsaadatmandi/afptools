"""
AFP Parser Module - Handles parsing of AFP structured fields.
"""

import struct
from typing import List, Tuple, Optional


class AFPStructuredField:
    """Represents a single AFP structured field."""
    
    # Common AFP structured field type codes
    BDT = b'\xd3\xa8\xa8'  # Begin Document
    EDT = b'\xd3\xa9\xa8'  # End Document
    BPG = b'\xd3\xa8\xaf'  # Begin Page
    EPG = b'\xd3\xa9\xaf'  # End Page
    BRG = b'\xd3\xa8\xc6'  # Begin Resource Group
    ERG = b'\xd3\xa9\xc6'  # End Resource Group
    
    def __init__(self, type_code: bytes, data: bytes):
        """
        Initialize a structured field.
        
        Args:
            type_code: 3-byte type code identifying the structured field
            data: The data portion of the structured field
        """
        self.type_code = type_code
        self.data = data
        self.length = len(data) + 5  # 5 bytes for header (length + type code)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['AFPStructuredField']:
        """
        Parse a structured field from bytes.
        
        Args:
            data: Bytes starting with a structured field
            
        Returns:
            An AFPStructuredField instance or None if parsing failed
        """
        if len(data) < 5:  # Minimum length for a valid structured field
            return None
        
        # First 2 bytes are the length (including these 2 bytes)
        length = struct.unpack('>H', data[0:2])[0]
        
        # Check if we have enough data
        if len(data) < length:
            return None
        
        # Next 3 bytes are the type code
        type_code = data[2:5]
        
        # Rest is the data
        field_data = data[5:length]
        
        return cls(type_code, field_data)
    
    def to_bytes(self) -> bytes:
        """
        Convert the structured field to bytes.
        
        Returns:
            Bytes representation of the structured field
        """
        # Calculate total length (2 bytes for length + 3 bytes for type code + data)
        total_length = 5 + len(self.data)
        
        # Pack the length as big-endian unsigned short
        length_bytes = struct.pack('>H', total_length)
        
        # Combine everything
        return length_bytes + self.type_code + self.data
    
    def __repr__(self) -> str:
        """String representation of the structured field."""
        type_hex = self.type_code.hex()
        return f"AFPStructuredField(type=0x{type_hex}, length={self.length})"


class AFPParser:
    """Parser for AFP files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the AFP parser.
        
        Args:
            file_path: Path to the AFP file
        """
        self.file_path = file_path
        self.fields: List[AFPStructuredField] = []
        self.resource_end_index = 0  # Index where resource section ends
        self.page_indices: List[int] = []  # Start indices for each page
    
    def parse(self) -> List[AFPStructuredField]:
        """
        Parse the AFP file into structured fields.
        
        Returns:
            List of structured fields
        
        Raises:
            ValueError: If the file cannot be parsed as a valid AFP file
        """
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            
            # Parse all structured fields
            offset = 0
            field_count = 0
            error_count = 0
            max_errors = 10  # Maximum number of errors before giving up
            
            while offset < len(data):
                # Check if we have at least 2 bytes for the length
                if offset + 2 > len(data):
                    break
                
                try:
                    # Get the length of the next structured field
                    field_length = struct.unpack('>H', data[offset:offset+2])[0]
                    
                    # Sanity check on field length
                    if field_length < 5 or field_length > 32767:
                        error_count += 1
                        if error_count > max_errors:
                            raise ValueError(f"Too many invalid field lengths, last at offset {offset}")
                        # Try to recover by skipping this byte
                        offset += 1
                        continue
                    
                    # Check if we have enough data for the complete field
                    if offset + field_length > len(data):
                        break
                    
                    # Parse the structured field
                    field_data = data[offset:offset+field_length]
                    field = AFPStructuredField.from_bytes(field_data)
                    
                    if field:
                        self.fields.append(field)
                        field_count += 1
                    
                    # Move to the next field
                    offset += field_length
                    
                except Exception as e:
                    error_count += 1
                    if error_count > max_errors:
                        raise ValueError(f"Too many errors parsing AFP file: {str(e)}")
                    # Try to recover by skipping this byte
                    offset += 1
            
            # Check if we found any valid fields
            if not self.fields:
                raise ValueError("No valid AFP structured fields found in the file")
            
            # Identify resource section and pages
            self.identify_resources()
            self.identify_pages()
            
            return self.fields
            
        except Exception as e:
            # If there was an error parsing the file, try to provide a helpful message
            if "No valid AFP structured fields" in str(e) or "Too many" in str(e):
                raise ValueError(f"This does not appear to be a valid AFP file: {str(e)}")
            else:
                raise ValueError(f"Error parsing AFP file: {str(e)}")
    
    def identify_resources(self) -> int:
        """
        Identify the resource section of the AFP file.
        
        Returns:
            Index where resource section ends
        """
        # Find the first BPG (Begin Page) field
        for i, field in enumerate(self.fields):
            if field.type_code == AFPStructuredField.BPG:
                self.resource_end_index = i
                return i
        
        # If no BPG found, assume all content is resources
        self.resource_end_index = len(self.fields)
        return self.resource_end_index
    
    def identify_pages(self) -> List[int]:
        """
        Identify page boundaries in the AFP file.
        
        Returns:
            List of indices where pages start
        """
        self.page_indices = []
        
        # Find all BPG (Begin Page) fields
        for i, field in enumerate(self.fields):
            if field.type_code == AFPStructuredField.BPG:
                self.page_indices.append(i)
        
        return self.page_indices
    
    def get_total_pages(self) -> int:
        """
        Get the total number of pages in the AFP file.
        
        Returns:
            Total number of pages
        """
        return len(self.page_indices)
