from bs4 import BeautifulSoup
import re

# Read the form page
with open('debug_form_page.html', 'r', encoding='utf-8') as f:
    form_html = f.read()

soup = BeautifulSoup(form_html, 'html.parser')

# Find the form and examine its structure
form = soup.find('form')
if form:
    print('📋 FORM ANALYSIS:')
    print('Action:', form.get('action', 'No action'))
    print('Method:', form.get('method', 'GET'))
    print()
    
    # Find all form fields
    inputs = form.find_all(['input', 'select', 'textarea', 'button'])
    print('Form fields:')
    for inp in inputs:
        field_type = inp.get('type', inp.name)
        field_name = inp.get('name', 'No name')
        field_value = inp.get('value', '')
        
        print(f'  - {field_type}: {field_name} = "{field_value}"')
        
        # For select elements, show first few options
        if inp.name == 'select':
            options = inp.find_all('option')
            if options:
                print(f'    Options ({len(options)}):')
                for opt in options[:3]:
                    opt_value = opt.get('value', '')
                    opt_text = opt.get_text(strip=True)
                    print(f'      * {opt_value}: {opt_text}')
                if len(options) > 3:
                    print(f'      ... and {len(options) - 3} more')
        print()

# Look for hidden inputs or CSRF tokens
hidden_inputs = soup.find_all('input', {'type': 'hidden'})
print(f'🔒 Found {len(hidden_inputs)} hidden inputs:')
for hidden in hidden_inputs:
    name = hidden.get('name', 'No name')
    value = hidden.get('value', '')
    print(f'  - {name}: {value}')

# Check if form has a submit button
submit_buttons = soup.find_all(['input', 'button'], {'type': ['submit', 'button']})
print(f'\n🔘 Found {len(submit_buttons)} submit buttons:')
for btn in submit_buttons:
    name = btn.get('name', 'No name')
    value = btn.get('value', '')
    text = btn.get_text(strip=True)
    print(f'  - {name}: {value} ("{text}")')

print('\n🔍 LOOKING FOR ARCHIVE DATA IN FORM PAGE:')
# Look for any existing archive data in tables
tables = soup.find_all('table')
print(f'Found {len(tables)} tables in the form page')

# Check if any tables contain league data
league_indicators = ['liga', 'Liga', 'Bezirk', 'Oberfranken', 'Kreisliga', 'Bezirksliga']
for i, table in enumerate(tables):
    table_text = table.get_text()
    found_indicators = [indicator for indicator in league_indicators if indicator in table_text]
    if found_indicators:
        print(f'  Table {i+1} contains: {found_indicators}')
        # Show first few rows
        rows = table.find_all('tr')[:3]
        for j, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            print(f'    Row {j+1}: {cell_texts[:5]}')  # First 5 cells

print('\n✅ Analysis complete!')
