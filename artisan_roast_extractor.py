#!/usr/bin/env python3

import sys
import argparse
import re
from datetime import datetime

def parse_artisan_log(file_path):
    """
    Parse an Artisan log file and extract roast information.
    """
    roast_data = {
        'title': '',
        'date': '',
        'beans': '',
        'roast_level': '',
        'duration': '',
        'temperature': '',
        'notes': [],
        'events': []
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
    
    # Extract basic information using regex patterns
    # These patterns might need adjustment based on actual file format
    title_match = re.search(r'Title:\s*(.*)', content, re.IGNORECASE)
    if title_match:
        roast_data['title'] = title_match.group(1).strip()
    
    date_match = re.search(r'Date:\s*(.*)', content, re.IGNORECASE)
    if date_match:
        roast_data['date'] = date_match.group(1).strip()
    
    beans_match = re.search(r'Beans?:\s*(.*)', content, re.IGNORECASE)
    if beans_match:
        roast_data['beans'] = beans_match.group(1).strip()
    
    roast_level_match = re.search(r'Roast\s*Level:\s*(.*)', content, re.IGNORECASE)
    if roast_level_match:
        roast_data['roast_level'] = roast_level_match.group(1).strip()
    
    duration_match = re.search(r'Duration:\s*(.*)', content, re.IGNORECASE)
    if duration_match:
        roast_data['duration'] = duration_match.group(1).strip()
    
    temp_match = re.search(r'Temp(?:erature)?:\s*(.*)', content, re.IGNORECASE)
    if temp_match:
        roast_data['temperature'] = temp_match.group(1).strip()
    
    # Extract notes (lines starting with - or *)
    notes_matches = re.findall(r'[-*]\s*(.*)', content)
    roast_data['notes'] = [note.strip() for note in notes_matches]
    
    # Extract events (timestamped entries)
    event_matches = re.findall(r'(\d+:\d+:\d+)\s*(.*)', content)
    roast_data['events'] = [(time, event.strip()) for time, event in event_matches]
    
    # If no title was found, create one from beans and date
    if not roast_data['title'] and (roast_data['beans'] or roast_data['date']):
        bean_info = roast_data['beans'] if roast_data['beans'] else 'Unknown Beans'
        date_info = roast_data['date'] if roast_data['date'] else datetime.now().strftime('%Y-%m-%d')
        roast_data['title'] = f"{bean_info} - {date_info}"
    
    return roast_data

def format_as_markdown(roast_data):
    """
    Format the roast data as markdown.
    """
    markdown = []
    
    # Title
    if roast_data['title']:
        markdown.append(f"# {roast_data['title']}\n")
    else:
        markdown.append("# Roast Report\n")
    
    # Metadata table
    markdown.append("| Attribute | Value |")
    markdown.append("|----------|-------|")
    
    if roast_data['date']:
        markdown.append(f"| Date | {roast_data['date']} |")
    
    if roast_data['beans']:
        markdown.append(f"| Beans | {roast_data['beans']} |")
    
    if roast_data['roast_level']:
        markdown.append(f"| Roast Level | {roast_data['roast_level']} |")
    
    if roast_data['duration']:
        markdown.append(f"| Duration | {roast_data['duration']} |")
    
    if roast_data['temperature']:
        markdown.append(f"| Temperature | {roast_data['temperature']} |")
    
    markdown.append("")
    
    # Events timeline
    if roast_data['events']:
        markdown.append("## Roast Timeline\n")
        for time, event in roast_data['events']:
            markdown.append(f"- **{time}**: {event}")
        markdown.append("")
    
    # Notes
    if roast_data['notes']:
        markdown.append("## Tasting Notes\n")
        for note in roast_data['notes']:
            markdown.append(f"- {note}")
        markdown.append("")
    
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
