import requests
from bs4 import BeautifulSoup

# Check the main archive page for forms
test_url = 'https://www.basketball-bund.net/index.jsp?Action=106'

print('🔍 Analyzing archive page forms...')
try:
    response = requests.get(test_url, timeout=10)
    print('Status:', response.status_code)
    print('Content length:', len(response.text), 'characters')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all forms
    forms = soup.find_all('form')
    print('Found', len(forms), 'forms on the page')
    
    for i, form in enumerate(forms):
        print(f'\n📋 Form {i+1}:')
        action = form.get('action', 'No action')
        method = form.get('method', 'GET')
        print(f'  Action: {action}')
        print(f'  Method: {method}')
        
        # Find all input fields
        inputs = form.find_all(['input', 'select', 'textarea'])
        print(f'  Input fields ({len(inputs)}):')
        
        for inp in inputs:
            inp_type = inp.get('type', inp.name)
            inp_name = inp.get('name', 'No name')
            inp_value = inp.get('value', '')
            print(f'    - {inp_type}: {inp_name} = "{inp_value}"')
            
            # For select elements, show options
            if inp.name == 'select':
                options = inp.find_all('option')
                if options:
                    print(f'      Options ({len(options)}):')
                    for opt in options[:10]:  # First 10 options
                        opt_value = opt.get('value', '')
                        opt_text = opt.get_text(strip=True)
                        print(f'        * {opt_value}: {opt_text}')
                    if len(options) > 10:
                        print(f'        ... and {len(options) - 10} more')

except Exception as e:
    print('Error:', str(e))
