# AFP Tools

Testing Claude assisted development.

A Python package for working with AFP (Advanced Function Presentation) files.

## Features

- Extract specific pages from AFP files while preserving resource sections
- Support for flexible page range syntax (e.g., "1:3, 5, 7:")
- Basic validation to ensure output files are valid

## Installation

### From Source

```bash
git clone https://github.com/user/afptools.git
cd afptools
pip install -e .
```

### Using pip (once published)

```bash
pip install afptools
```

## Usage

### Command Line Interface

#### Extract Pages

Extract specific pages from an AFP file:

```bash
afptools extract input.afp output.afp "1:3, 5, 7:"
```

This extracts:
- Pages 1-3
- Page 5
- Page 7 to the end of the document

### Page Range Syntax

The page range syntax supports:

- Single pages: `5` (just page 5)
- Ranges: `1:3` (pages 1, 2, and 3)
- Open-ended ranges: `7:` (page 7 to the end)
- Combinations: `1:3, 5, 7:` (pages 1-3, page 5, and page 7 to the end)

## Python API

You can also use AFP Tools as a Python library:

```python
from afptools.parser import AFPParser
from afptools.operations import extract_pages
from afptools.utils import parse_page_range

# Parse the AFP file
parser = AFPParser("input.afp")
parser.parse()

# Get total number of pages
total_pages = parser.get_total_pages()

# Parse page range
page_numbers = parse_page_range("1:3, 5, 7:", total_pages)

# Extract pages
extract_pages(parser, page_numbers, "output.afp")
```

## AFP File Structure

AFP (Advanced Function Presentation) is an architecture-based print stream format developed by IBM. It consists of structured fields, including:

- BDT (Begin Document)
- EDT (End Document)
- BPG (Begin Page)
- EPG (End Page)
- BRG (Begin Resource Group)
- ERG (End Resource Group)

This tool preserves the resource sections at the beginning of the file to ensure the output file remains valid and can be properly rendered.

## License

MIT License
