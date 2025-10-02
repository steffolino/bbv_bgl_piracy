#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

class DistrictDiscovery:
    """
    Discover Bezirk (district) and Kreis IDs for Oberfranken
    This is key to getting your 2003-2024 data working!
    """
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net/index.jsp"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
    
    def discover_districts_and_kreise(self):
        """
        Discover all available Bezirke and Kreise to find Oberfranken
        """
        
        print("🔍 DISCOVERING DISTRICTS AND KREISE")
        print("Finding Oberfranken IDs for 2003-2024 historical data")
        
        # Step 1: Get the form with all filter options
        districts_kreise = self.get_filter_options()
        
        # Step 2: Test different combinations to find Oberfranken data
        if districts_kreise:
            self.test_oberfranken_combinations(districts_kreise)
        
        return districts_kreise
    
    def get_filter_options(self):
        """
        Get all available filter options from the Action=106 form
        """
        
        print("\n📋 Getting filter options...")
        
        try:
            # Make initial request to get form with all options
            response = self.session.get(
                f"{self.base_url}?Action=106",
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all select options
                filters = {
                    'seasons': self.extract_select_options(soup, 'saison_id'),
                    'spielklassen': self.extract_select_options(soup, 'cbSpielklasseFilter'),
                    'altersklassen': self.extract_select_options(soup, 'cbAltersklasseFilter'),
                    'geschlecht': self.extract_select_options(soup, 'cbGeschlechtFilter'),
                    'bezirke': self.extract_select_options(soup, 'cbBezirkFilter'),
                    'kreise': self.extract_select_options(soup, 'cbKreisFilter')
                }
                
                print(f"✅ Extracted filter options:")
                for filter_name, options in filters.items():
                    print(f"  {filter_name}: {len(options)} options")
                    if filter_name in ['bezirke', 'kreise']:
                        print(f"    {options}")
                
                # Save for analysis
                with open('filter_options.json', 'w', encoding='utf-8') as f:
                    json.dump(filters, f, indent=2, ensure_ascii=False)
                
                return filters
                
            else:
                print(f"❌ HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting filter options: {e}")
            return None
    
    def extract_select_options(self, soup, select_name):
        """
        Extract all options from a select element
        """
        
        options = []
        
        try:
            select_elem = soup.find('select', {'name': select_name})
            if select_elem:
                option_elems = select_elem.find_all('option')
                
                for option in option_elems:
                    value = option.get('value', '')
                    text = option.get_text(strip=True)
                    
                    if value and text:
                        options.append({
                            'value': value,
                            'text': text
                        })
            
        except Exception as e:
            print(f"    Error extracting {select_name}: {e}")
        
        return options
    
    def test_oberfranken_combinations(self, filters):
        """
        Test different combinations to find Oberfranken data
        """
        
        print(f"\n🎯 TESTING COMBINATIONS FOR OBERFRANKEN")
        
        # Test with different districts/kreise
        bezirke = filters.get('bezirke', [])
        kreise = filters.get('kreise', [])
        
        print(f"Available Bezirke: {len(bezirke)}")
        print(f"Available Kreise: {len(kreise)}")
        
        # If we have empty filter lists, try making requests to populate them
        if not bezirke or not kreise:
            print("🔄 Trying to get populated filter lists...")
            self.try_populate_filters()
        
        # Test some basic combinations for 2018 (known working year)
        test_combinations = [
            # Test all districts with Senioren
            {'saison_id': '2018', 'cbBezirkFilter': '0', 'cbAltersklasseFilter': '1750'},
            # Test different age groups
            {'saison_id': '2018', 'cbBezirkFilter': '0', 'cbAltersklasseFilter': '-3'},  # All Senioren
            {'saison_id': '2018', 'cbBezirkFilter': '0', 'cbAltersklasseFilter': '0'},   # All ages
        ]
        
        for i, params in enumerate(test_combinations, 1):
            print(f"\n  Test {i}: {params}")
            result = self.test_filter_combination(params)
            
            if result and result.get('total_results', 0) > 0:
                print(f"    ✅ Found {result['total_results']} results!")
                
                # Save successful combination
                with open(f'successful_combination_{i}.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'params': params,
                        'result': result
                    }, f, indent=2, ensure_ascii=False)
            else:
                print(f"    ❌ No results")
            
            time.sleep(1)  # Rate limiting
    
    def try_populate_filters(self):
        """
        Try different requests to populate the filter dropdowns
        """
        
        print("🔄 Attempting to populate filter dropdowns...")
        
        # Try different initial parameters that might populate the filters
        test_params = [
            {'Action': '106'},
            {'Action': '106', 'saison_id': '2018'},
            {'Action': '106', 'saison_id': '2018', 'cbAltersklasseFilter': '1750'},
        ]
        
        for params in test_params:
            try:
                response = self.session.post(self.base_url, data=params, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if we now have populated filter options
                    bezirke = self.extract_select_options(soup, 'cbBezirkFilter')
                    kreise = self.extract_select_options(soup, 'cbKreisFilter')
                    
                    if bezirke or kreise:
                        print(f"  ✅ Found populated filters: {len(bezirke)} bezirke, {len(kreise)} kreise")
                        
                        # Save populated filters
                        with open('populated_filters.json', 'w', encoding='utf-8') as f:
                            json.dump({
                                'bezirke': bezirke,
                                'kreise': kreise,
                                'params_used': params
                            }, f, indent=2, ensure_ascii=False)
                        
                        return {'bezirke': bezirke, 'kreise': kreise}
                
            except Exception as e:
                print(f"    Error with {params}: {e}")
                continue
        
        return None
    
    def test_filter_combination(self, params):
        """
        Test a specific filter combination
        """
        
        # Default parameters
        default_params = {
            'Action': '106',
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '1750',  # Senioren
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '0',
            'cbKreisFilter': '0'
        }
        
        # Merge with test parameters
        test_params = {**default_params, **params}
        
        try:
            response = self.session.post(
                self.base_url,
                data=test_params,
                timeout=15
            )
            
            if response.status_code == 200:
                # Parse response to count results
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for result count
                result_count = self.extract_result_count(soup)
                
                # Look for data tables
                data_tables = self.find_data_tables(soup)
                
                return {
                    'total_results': result_count,
                    'data_tables': len(data_tables),
                    'response_size': len(response.text)
                }
            
            return None
            
        except Exception as e:
            print(f"      Error: {e}")
            return None
    
    def extract_result_count(self, soup):
        """
        Extract the total number of results from the page
        """
        
        try:
            # Look for result count text like "Seite 1 / 5 (123 Treffer insgesamt)"
            nav_text = soup.find_all(text=re.compile(r'\d+\s+Treffer'))
            
            for text in nav_text:
                match = re.search(r'(\d+)\s+Treffer', text)
                if match:
                    return int(match.group(1))
            
            # Alternative: look for table rows (excluding headers)
            sport_view_tables = soup.find_all('table', class_='sportView')
            total_rows = 0
            
            for table in sport_view_tables:
                rows = table.find_all('tr')
                # Exclude header rows
                data_rows = [r for r in rows if not r.find('th')]
                total_rows += len(data_rows)
            
            return total_rows
            
        except:
            return 0
    
    def find_data_tables(self, soup):
        """
        Find tables that contain actual data (not just filters)
        """
        
        data_tables = []
        
        try:
            # Look for sportView tables with actual content
            sport_view_tables = soup.find_all('table', class_='sportView')
            
            for table in sport_view_tables:
                # Check if table has data rows (not just headers/filters)
                rows = table.find_all('tr')
                data_rows = []
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # At least 3 columns
                        # Check if it's not a filter row
                        cell_texts = [c.get_text(strip=True) for c in cells]
                        if not any('select' in str(cell) for cell in cells):
                            data_rows.append(cell_texts)
                
                if data_rows:
                    data_tables.append({
                        'rows': len(data_rows),
                        'sample_row': data_rows[0] if data_rows else None
                    })
        
        except:
            pass
        
        return data_tables

def main():
    """
    Main function to discover Oberfranken districts
    """
    
    print("🏀 OBERFRANKEN DISTRICT DISCOVERY")
    print("Finding the right parameters for 2003-2024 historical data")
    
    discovery = DistrictDiscovery()
    results = discovery.discover_districts_and_kreise()
    
    if results:
        print(f"\n🎯 DISCOVERY COMPLETE!")
        print(f"Check the generated JSON files for successful combinations")
    else:
        print(f"\n❌ Discovery failed - manual parameter adjustment needed")

if __name__ == "__main__":
    main()
