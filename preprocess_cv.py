#!/usr/bin/env python3
"""
Preprocess moderncv LaTeX to standard LaTeX for pandoc conversion
"""

import re
import sys
from collections import defaultdict

def parse_bibfile(bibfile):
    """Parse BibTeX file and return entries grouped by type"""
    entries_by_type = defaultdict(list)
    
    try:
        with open(bibfile, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return entries_by_type
    
    # Find all entries
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1).lower()
        cite_key = match.group(2).strip()
        fields_str = match.group(3)
        
        # Parse fields
        fields = {}
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
        for field_match in re.finditer(field_pattern, fields_str):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value
        
        entries_by_type[entry_type].append({
            'key': cite_key,
            'type': entry_type,
            'fields': fields
        })
    
    return entries_by_type

def format_bibliography_entry(entry, number=None):
    """Format a single bibliography entry as markdown"""
    fields = entry['fields']
    
    # Get author
    author = fields.get('author', 'Unknown')
    # Bold "Dunne" in author list
    author = re.sub(r'\bDunne\b', r'**Dunne**', author)
    
    # Get year
    year = fields.get('year', '')
    
    # Get title
    title = fields.get('title', '')
    
    # Build citation based on type
    if entry['type'] == 'article':
        journal = fields.get('journal', '')
        volume = fields.get('volume', '')
        pages = fields.get('pages', '')
        doi = fields.get('doi', '')
        
        citation = f"{author} ({year}). {title}. *{journal}*"
        if volume:
            citation += f", {volume}"
        if pages:
            citation += f", {pages}"
        if doi:
            citation += f". DOI: [{doi}](https://doi.org/{doi})"
        citation += "."
        
    elif entry['type'] == 'incollection':
        booktitle = fields.get('booktitle', '')
        editor = fields.get('editor', '')
        publisher = fields.get('publisher', '')
        
        citation = f"{author} ({year}). {title}. In "
        if editor:
            citation += f"{editor} (Ed.), "
        citation += f"*{booktitle}*"
        if publisher:
            citation += f". {publisher}"
        citation += "."
        
    elif entry['type'] == 'inproceedings':
        booktitle = fields.get('booktitle', '')
        location = fields.get('address', '')
        
        citation = f"{author} ({year}). {title}. *{booktitle}*"
        if location:
            citation += f", {location}"
        citation += "."
        
    else:  # misc and others
        note = fields.get('note', '')
        howpublished = fields.get('howpublished', '')
        
        citation = f"{author} ({year}). {title}"
        if note:
            citation += f". {note}"
        if howpublished:
            citation += f". {howpublished}"
        citation += "."
    
    # Add number prefix if provided
    if number is not None:
        citation = f"{number}. {citation}"
    
    return citation

def sort_entries_by_year(entries):
    """Sort bibliography entries by year descending"""
    return sorted(entries, key=lambda x: x['fields'].get('year', '0000'), reverse=True)

def find_balanced_braces(text, start_pos):
    """Find the end position of a balanced brace group starting at start_pos"""
    if text[start_pos] != '{':
        return -1
    
    count = 0
    i = start_pos
    while i < len(text):
        if text[i] == '{' and (i == 0 or text[i-1] != '\\'):
            count += 1
        elif text[i] == '}' and (i == 0 or text[i-1] != '\\'):
            count -= 1
            if count == 0:
                return i
        i += 1
    return -1

def extract_args(text, num_args):
    """Extract num_args balanced brace arguments from text"""
    args = []
    pos = 0
    
    for _ in range(num_args):
        # Skip whitespace
        while pos < len(text) and text[pos] in ' \n\t':
            pos += 1
        
        if pos >= len(text) or text[pos] != '{':
            args.append('')
            continue
        
        end = find_balanced_braces(text, pos)
        if end == -1:
            args.append('')
            break
        
        args.append(text[pos+1:end])
        pos = end + 1
    
    return args

def extract_personal_info(content):
    """Extract personal information from moderncv commands"""
    info = {}
    
    # Extract name
    name_match = re.search(r'\\name\{([^}]*)\}\{([^}]*)\}', content)
    if name_match:
        info['firstname'] = name_match.group(1)
        info['lastname'] = name_match.group(2)
    
    # Extract photo
    photo_match = re.search(r'\\photo(?:\[[^\]]*\])*\{([^}]*)\}', content)
    if photo_match:
        info['photo'] = photo_match.group(1)
    
    # Extract address
    addr_match = re.search(r'\\address\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', content)
    if addr_match:
        info['address1'] = addr_match.group(1)
        info['address2'] = addr_match.group(2)
        info['address3'] = addr_match.group(3)
    
    # Extract phone
    phone_match = re.search(r'\\phone\[[^\]]*\]\{([^}]*)\}', content)
    if phone_match:
        info['phone'] = phone_match.group(1)
    
    # Extract email
    email_match = re.search(r'\\email\{([^}]*)\}', content)
    if email_match:
        info['email'] = email_match.group(1)
    
    # Extract extra info
    extra_match = re.search(r'\\extrainfo\{([^}]*)\}', content)
    if extra_match:
        info['extrainfo'] = extra_match.group(1)
    
    # Extract social links
    info['socials'] = []
    for social_match in re.finditer(r'\\social\[([^\]]*)\]\{([^}]*)\}', content):
        social_type = social_match.group(1)
        social_value = social_match.group(2)
        info['socials'].append((social_type, social_value))
    
    return info

def format_header_html(info):
    """Format personal info as HTML header - no indentation to avoid pandoc treating it as code"""
    # Add Font Awesome CDN link
    html = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">\n'
    html += '<div class="cv-header">\n'
    
    # Photo
    if info.get('photo'):
        html += f'<div class="cv-photo"><img src="{info["photo"]}" alt="Photo"></div>\n'
    
    html += '<div class="cv-header-content">\n'
    
    # Name
    if info.get('firstname') or info.get('lastname'):
        html += f'<h1 class="cv-name">{info.get("firstname", "")} {info.get("lastname", "")}</h1>\n'
    
    # Address
    if info.get('address1'):
        html += '<div class="cv-contact">\n'
        html += f'<div>{info.get("address1", "")}</div>\n'
        if info.get('address2'):
            html += f'<div>{info.get("address2", "")}</div>\n'
        if info.get('address3'):
            html += f'<div>{info.get("address3", "")}</div>\n'
        html += '</div>\n'
    
    # Contact details
    html += '<div class="cv-details">\n'
    if info.get('phone'):
        html += f'<div class="cv-phone">{info["phone"]}</div>\n'
    if info.get('email'):
        html += f'<div class="cv-email"><a href="mailto:{info["email"]}">{info["email"]}</a></div>\n'
    if info.get('extrainfo'):
        extra_clean = info['extrainfo'].replace('\\\\', '<br>')
        html += f'<div class="cv-extra">{extra_clean}</div>\n'
    html += '</div>\n'
    
    # Social links
    if info.get('socials'):
        html += '<div class="cv-socials">\n'
        for social_type, social_value in info['socials']:
            if social_type == 'orcid':
                html += f'<div class="social-link"><a href="https://orcid.org/{social_value}"><i class="fab fa-orcid"></i> {social_value}</a></div>\n'
            elif social_type == 'github':
                html += f'<div class="social-link"><a href="https://github.com/{social_value}"><i class="fab fa-github"></i> {social_value}</a></div>\n'
            elif social_type == 'linkedin':
                html += f'<div class="social-link"><a href="https://linkedin.com/in/{social_value}"><i class="fab fa-linkedin"></i> {social_value}</a></div>\n'
        html += '</div>\n'
    
    html += '</div>\n'
    html += '</div>\n\n'
    html += '<hr class="cv-header-separator">\n\n'
    
    return html

def preprocess_moderncv(content, bibfile='my_publications.bib'):
    """Convert moderncv commands to Markdown with HTML header"""
    
    # Extract personal info before processing
    personal_info = extract_personal_info(content)
    
    # Parse bibliography
    bib_entries = parse_bibfile(bibfile)
    
    # Remove preamble - extract only document content
    doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
    if doc_match:
        content = doc_match.group(1)
    
    # Remove LaTeX comments early (before other processing)
    content = re.sub(r'%.*', '', content)
    
    # Format header
    header_html = format_header_html(personal_info)
    content = header_html + content
    
    # Remove all moderncv-specific commands
    content = re.sub(r'\\makecvtitle', '', content)
    content = re.sub(r'\\nocite\{\*\}', '', content)
    content = re.sub(r'\\vspace\{[^}]*\}', '', content)
    
    # Convert sections to collapsible HTML details/summary elements
    # First convert subsections (so they don't interfere with section conversion)
    content = re.sub(r'\\subsection\{([^}]*)\}', r'\n### \1\n', content)
    
    # Convert sections to details/summary - only first one (Summary) is open
    section_count = [0]  # Use list to allow modification in nested function
    def replace_section(match):
        section_name = match.group(1)
        section_count[0] += 1
        open_attr = ' open' if section_count[0] == 1 else ''
        return f'\n</details>\n\n<details{open_attr}>\n<summary>{section_name}</summary>\n\n'
    
    # Add sections
    content = re.sub(r'\\section\{([^}]*)\}', replace_section, content)
    
    # Close any open details at the end and remove the first closing tag (since we start with one)
    content = content.replace('\n</details>\n\n<details open>', '\n<details open>', 1)
    content += '\n</details>\n'
    
    # Replace \printbibliography commands with actual bibliography entries
    def replace_printbib(match):
        full_match = match.group(0)
        
        # Extract type filter if present
        type_match = re.search(r'type=(\w+)', full_match)
        if type_match:
            bib_type = type_match.group(1)
            entries = bib_entries.get(bib_type, [])
        else:
            # No filter, use all entries
            entries = []
            for type_list in bib_entries.values():
                entries.extend(type_list)
        
        if not entries:
            return ''
        
        # Sort by year
        entries = sort_entries_by_year(entries)
        
        # Format as numbered markdown list
        result = '\n'
        for i, entry in enumerate(entries, 1):
            result += format_bibliography_entry(entry, i) + '\n\n'
        
        return result
    
    content = re.sub(r'\\printbibliography\[[^\]]*\]', replace_printbib, content)
    content = re.sub(r'\\printbibliography', replace_printbib, content)
    
    # Remove bibliography section header formatting
    content = re.sub(r'\\noindent\\textbf\{([^}]*)\}', r'\n### \1\n', content)
    
    # Convert \cventry - find them one at a time
    pattern = r'\\cventry'
    result = []
    last_end = 0
    
    for match in re.finditer(pattern, content):
        result.append(content[last_end:match.start()])
        args = extract_args(content[match.end():], 6)
        
        year, title, org, location, grade, desc = args
        
        entry = f"**{year}**"
        if title:
            entry += f": **{title}**"
        if org:
            entry += f", *{org}*"
        if location:
            entry += f", {location}"
        if grade:
            entry += f" ({grade})"
        if desc:
            entry += f". {desc}"
        entry += "\n\n"
        
        result.append(entry)
        
        # Skip past all the arguments
        pos = match.end()
        for _ in range(6):
            while pos < len(content) and content[pos] in ' \n\t':
                pos += 1
            if pos < len(content) and content[pos] == '{':
                end = find_balanced_braces(content, pos)
                if end != -1:
                    pos = end + 1
        last_end = pos
    
    result.append(content[last_end:])
    content = ''.join(result)
    
    # Convert \cvline - use balanced brace extraction
    pattern = r'\\cvline'
    result = []
    last_end = 0
    
    for match in re.finditer(pattern, content):
        result.append(content[last_end:match.start()])
        args = extract_args(content[match.end():], 2)
        
        label, value = args
        
        if label:
            result.append(f"**{label}**: {value}\n\n")
        else:
            result.append(f"{value}\n\n")
        
        # Skip past both arguments
        pos = match.end()
        for _ in range(2):
            while pos < len(content) and content[pos] in ' \n\t':
                pos += 1
            if pos < len(content) and content[pos] == '{':
                end = find_balanced_braces(content, pos)
                if end != -1:
                    pos = end + 1
        last_end = pos
    
    result.append(content[last_end:])
    content = ''.join(result)
    
    # Convert \cvlistitem
    content = re.sub(r'\\cvlistitem\{([^}]*)\}', r'- \1\n', content)
    
    # Clean up remaining LaTeX commands
    content = re.sub(r'\\url\{([^}]*)\}', r'<\1>', content)
    content = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', content)
    content = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', content)
    
    return content

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 preprocess_cv.py input.tex output.md [bibfile.bib]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    bibfile = sys.argv[3] if len(sys.argv) > 3 else 'my_publications.bib'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    processed = preprocess_moderncv(content, bibfile)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed)
    
    print(f"Preprocessed {input_file} -> {output_file} (with {bibfile})")

if __name__ == '__main__':
    main()
