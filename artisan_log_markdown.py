#!/usr/bin/env python3

import sys
import argparse
import ast
from datetime import datetime
import os

def parse_artisan_log(file_path):
    """
    Parse an Artisan log file and extract roast information.
    """
    roast_data = {
        'title': '',
        'file': '',
        'date': '',
        'organization': '',
        'operator': '',
        'beans': '',
        'machine': '',
        'roasting_notes': '',
        'cupping_notes': ''
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Extract the file name
    roast_data['file'] = os.path.basename(file_path)
    
    # Parse the Python dictionary
    try:
        data = ast.literal_eval(content)
    except Exception as e:
        print(f"Error parsing file content: {e}")
        sys.exit(1)
    
    # Extract information
    roast_data['title'] = data.get('title', '')
    roast_data['organization'] = data.get('organization', '')
    roast_data['operator'] = data.get('operator', '')
    roast_data['beans'] = data.get('beans', '')
    roast_data['machine'] = data.get('roastertype', '')
    roast_data['roasting_notes'] = data.get('roastingnotes', '')
    roast_data['cupping_notes'] = data.get('cuppingnotes', '')
    
    # Format date from roastisodate and roasttime
    roast_date = data.get('roastisodate', '')
    roast_time = data.get('roasttime', '')
    if roast_date and roast_time:
        # Convert to datetime and adjust format
        try:
            # Parse the time string
            time_obj = datetime.strptime(roast_time, '%H:%M:%S')
            formatted_time = time_obj.strftime('%H:%M')
            roast_data['date'] = f"{roast_date} {formatted_time}"
        except ValueError:
            roast_data['date'] = f"{roast_date} {roast_time}"
    else:
        roast_data['date'] = roast_date or roast_time
    
    return roast_data

def format_as_markdown(roast_data):
    """
    Format the roast data as markdown.
    """
    markdown = []
    
    # Title
    if roast_data['title']:
        markdown.append(f"# {roast_data['title']}")
    else:
        markdown.append("# Roast Report")
    
    # Metadata
    if roast_data['file']:
        markdown.append(f"- File: {roast_data['file']}")
    
    if roast_data['date']:
        markdown.append(f"- Date: {roast_data['date']}")
    
    if roast_data['organization']:
        markdown.append(f"- Organization: {roast_data['organization']}")
    
    if roast_data['operator']:
        markdown.append(f"- Operator: {roast_data['operator']}")
    
    markdown.append("")  # Blank line
    
    # Beans section
    if roast_data['beans']:
        markdown.append("## Beans")
        # Split beans by newlines and add each line
        bean_lines = roast_data['beans'].split('\\n')
        for line in bean_lines:
            # Handle escaped characters
            line = line.replace('\\xe3', 'ã')
            markdown.append(line)
        markdown.append("")  # Blank line
    
    # Machine section
    if roast_data['machine']:
        markdown.append("## Machine")
        markdown.append(f"Model: {roast_data['machine']}")
        markdown.append("")  # Blank line
    
    # Roasting Notes section
    if roast_data['roasting_notes']:
        markdown.append("## Roasting Notes")
        # Handle escaped newlines
        notes = roast_data['roasting_notes'].replace('\\n', '\n')
        markdown.append(notes)
        markdown.append("")  # Blank line
    
    # Cupping Notes section
    if roast_data['cupping_notes']:
        markdown.append("## Cupping Notes")
        markdown.append(roast_data['cupping_notes'])
        markdown.append("")  # Blank line
    
    markdown.append("---")
    return "\n".join(markdown)

def main():
    parser = argparse.ArgumentParser(description="Extract roast information from an Artisan log and output as markdown")
    parser.add_argument("input_file", help="Path to the Artisan log file (.alog)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Parse the log file
    roast_data = parse_artisan_log(args.input_file)
    
    # Format as markdown
    markdown_output = format_as_markdown(roast_data)
    
    # Output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            print(f"Markdown output written to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            sys.exit(1)
    else:
        print(markdown_output)

if __name__ == "__main__":
    main()
