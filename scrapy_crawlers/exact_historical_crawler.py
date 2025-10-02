#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_historical_seasons_exact():
    """
    Crawl historical seasons using your EXACT working POST parameters
    Perfect for Basketball Reference frontend with 20+ years of data!
    """
    
    print("🏀 HISTORICAL SEASONS CRAWLER (2003-2024)")
    print("Using YOUR EXACT working POST parameters from Action=106")
    print("Building comprehensive Basketball Reference dataset!")
    
    # Target seasons from 2003 to 2024 (excluding your complete 2018)
    target_seasons = list(range(2003, 2025))
    if 2018 in target_seasons:
        target_seasons.remove(2018)  # You already have 2018
    
    print(f"📅 Target seasons: {len(target_seasons)} seasons")
    print(f"🎯 Range: {min(target_seasons)}-{max(target_seasons)}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.basketball-bund.net',
        'Referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
    })
    
    all_data = []
    season_summary = {}
    successful_seasons = []
    
    for season in target_seasons:
        print(f"\n📊 CRAWLING SEASON {season}")
        
        # Your EXACT working POST data - only changing the season
        post_data = {
            'Action': '106',
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',
            'cbKreisFilter': '0'
        }
        
        season_data = crawl_season_with_exact_params(session, season, post_data)
        
        if season_data:
            all_data.extend(season_data)
            successful_seasons.append(season)
            
            # Calculate summary
            season_summary[season] = analyze_season_data(season_data, season)
            
            print(f"  ✅ Season {season}: {len(season_data)} records")
            print(f"    Leagues: {season_summary[season]['unique_leagues']}")
            print(f"    Teams: {season_summary[season]['unique_teams']}")
            print(f"    Litzendorf: {season_summary[season]['litzendorf_records']}")
            
            # Save individual season
            save_season_file(season, season_data)
        else:
            print(f"  ❌ Season {season}: No data")
        
        # Rate limiting
        time.sleep(random.uniform(3, 6))
    
    # Save comprehensive dataset
    if all_data:
        save_comprehensive_dataset(all_data, season_summary, successful_seasons)
    
    print(f"\n🎯 CRAWL COMPLETE!")
    print(f"✅ Successful seasons: {successful_seasons}")
    print(f"📊 Total records: {len(all_data)}")
    print(f"📅 Coverage: {len(successful_seasons)} seasons")

def crawl_season_with_exact_params(session, season, post_data):
    """
    Crawl season data using exact POST parameters
    """
    
    try:
        print(f"  🔍 POST request for season {season}...")
        
        response = session.post(
            'https://www.basketball-bund.net/index.jsp?Action=106',
            data=post_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"    ✅ Response: {len(response.text):,} chars")
            
            # Save raw response for debugging
            save_raw_response(season, response.text)
            
            # Parse response
            parsed_data = parse_action_106_response(response.text, season)
            
            if parsed_data:
                print(f"    📊 Parsed: {len(parsed_data)} records")
                return parsed_data
            else:
                print(f"    ❌ No parseable data found")
                return []
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"    💥 Error: {str(e)[:100]}")
        return []

def save_raw_response(season, html_content):
    """
    Save raw HTML response for debugging/analysis
    """
    
    filename = f"action_106_response_{season}.html"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"    💾 Raw HTML: {filename}")
    except:
        pass

def parse_action_106_response(html_content, season):
    """
    Parse Action=106 response to extract basketball data
    """
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        data_records = []
        
        print(f"    🔍 Parsing HTML response...")
        
        # Look for multiple data patterns
        
        # 1. Table-based data
        tables = soup.find_all('table')
        for table_idx, table in enumerate(tables):
            if is_basketball_table(table):
                print(f"      📋 Found basketball table {table_idx + 1}")
                table_data = extract_table_data(table, season, f"table_{table_idx}")
                data_records.extend(table_data)
        
        # 2. List-based data
        lists = soup.find_all(['ul', 'ol'])
        for list_idx, list_elem in enumerate(lists):
            if is_basketball_list(list_elem):
                print(f"      📝 Found basketball list {list_idx + 1}")
                list_data = extract_list_data(list_elem, season, f"list_{list_idx}")
                data_records.extend(list_data)
        
        # 3. Link-based data (leagues, teams)
        links = soup.find_all('a', href=True)
        basketball_links = []
        for link in links:
            if is_basketball_link(link):
                basketball_links.append(link)
        
        if basketball_links:
            print(f"      🔗 Found {len(basketball_links)} basketball links")
            link_data = extract_link_data(basketball_links, season)
            data_records.extend(link_data)
        
        # 4. Text content analysis
        text_data = extract_text_patterns(soup, season)
        if text_data:
            print(f"      📄 Found {len(text_data)} text patterns")
            data_records.extend(text_data)
        
        print(f"    📊 Total extracted: {len(data_records)} records")
        return data_records
        
    except Exception as e:
        print(f"    ❌ Parse error: {str(e)[:100]}")
        return []

def is_basketball_table(table):
    """Check if table contains basketball data"""
    try:
        table_text = table.get_text().lower()
        basketball_keywords = [
            'liga', 'mannschaft', 'team', 'verein', 'basketball',
            'saison', 'tabelle', 'spiel', 'punkte', 'oberfranken'
        ]
        return any(keyword in table_text for keyword in basketball_keywords)
    except:
        return False

def extract_table_data(table, season, source_id):
    """Extract data from basketball table"""
    data = []
    try:
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                record = {
                    'season_id': season,
                    'source_type': 'table',
                    'source_id': source_id,
                    'row_index': row_idx,
                    'extracted_at': datetime.now().isoformat(),
                    'raw_cells': cell_texts
                }
                
                # Try to identify data structure
                if len(cell_texts) >= 1 and cell_texts[0] and len(cell_texts[0]) > 2:
                    record['primary_text'] = cell_texts[0]
                    
                    # Check for team names
                    if any(keyword in cell_texts[0].lower() for keyword in ['bg', 'tv', 'sv', 'fc', 'tus', 'djk']):
                        record['likely_team'] = cell_texts[0]
                    
                    # Check for Litzendorf
                    if 'litzendorf' in cell_texts[0].lower():
                        record['is_litzendorf'] = True
                
                if len(cell_texts) >= 2:
                    record['secondary_text'] = cell_texts[1]
                
                data.append(record)
    except Exception as e:
        print(f"        ❌ Table extraction error: {str(e)[:50]}")
    
    return data

def is_basketball_list(list_elem):
    """Check if list contains basketball data"""
    try:
        list_text = list_elem.get_text().lower()
        return any(keyword in list_text for keyword in ['liga', 'team', 'basketball', 'oberfranken'])
    except:
        return False

def extract_list_data(list_elem, season, source_id):
    """Extract data from basketball list"""
    data = []
    try:
        items = list_elem.find_all('li')
        for item_idx, item in enumerate(items):
            item_text = item.get_text(strip=True)
            if item_text and len(item_text) > 2:
                record = {
                    'season_id': season,
                    'source_type': 'list',
                    'source_id': source_id,
                    'item_index': item_idx,
                    'text_content': item_text,
                    'extracted_at': datetime.now().isoformat()
                }
                
                if 'litzendorf' in item_text.lower():
                    record['is_litzendorf'] = True
                
                data.append(record)
    except Exception as e:
        print(f"        ❌ List extraction error: {str(e)[:50]}")
    
    return data

def is_basketball_link(link):
    """Check if link is basketball-related"""
    try:
        href = link.get('href', '').lower()
        text = link.get_text(strip=True).lower()
        
        # Check href for basketball patterns
        href_indicators = ['liga', 'team', 'competition', 'saison', 'basketball']
        text_indicators = ['liga', 'mannschaft', 'oberfranken', 'litzendorf']
        
        return (any(indicator in href for indicator in href_indicators) or
                any(indicator in text for indicator in text_indicators))
    except:
        return False

def extract_link_data(links, season):
    """Extract data from basketball links"""
    data = []
    for link_idx, link in enumerate(links):
        try:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if text and len(text) > 2:
                record = {
                    'season_id': season,
                    'source_type': 'link',
                    'link_index': link_idx,
                    'link_text': text,
                    'link_href': href,
                    'extracted_at': datetime.now().isoformat()
                }
                
                if 'litzendorf' in text.lower():
                    record['is_litzendorf'] = True
                
                data.append(record)
        except:
            continue
    
    return data

def extract_text_patterns(soup, season):
    """Extract basketball data from text patterns"""
    data = []
    try:
        # Look for structured text content
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text(strip=True)
            if (text and 20 <= len(text) <= 200 and 
                any(keyword in text.lower() for keyword in ['liga', 'oberfranken', 'basketball', 'litzendorf'])):
                
                record = {
                    'season_id': season,
                    'source_type': 'text_pattern',
                    'text_content': text,
                    'extracted_at': datetime.now().isoformat()
                }
                
                if 'litzendorf' in text.lower():
                    record['is_litzendorf'] = True
                
                data.append(record)
    except:
        pass
    
    return data

def analyze_season_data(season_data, season):
    """Analyze season data and create summary"""
    
    summary = {
        'total_records': len(season_data),
        'unique_teams': 0,
        'unique_leagues': 0,
        'litzendorf_records': 0,
        'data_types': {},
        'has_oberfranken': False
    }
    
    teams = set()
    leagues = set()
    
    for record in season_data:
        # Count data types
        source_type = record.get('source_type', 'unknown')
        summary['data_types'][source_type] = summary['data_types'].get(source_type, 0) + 1
        
        # Check for Litzendorf
        if record.get('is_litzendorf') or any(
            'litzendorf' in str(value).lower() 
            for value in record.values() 
            if isinstance(value, str)
        ):
            summary['litzendorf_records'] += 1
        
        # Check for Oberfranken
        if any(
            'oberfranken' in str(value).lower() 
            for value in record.values() 
            if isinstance(value, str)
        ):
            summary['has_oberfranken'] = True
        
        # Extract team names
        if record.get('likely_team'):
            teams.add(record['likely_team'])
        
        # Extract potential league info
        for key, value in record.items():
            if isinstance(value, str) and 'liga' in value.lower():
                leagues.add(value)
    
    summary['unique_teams'] = len(teams)
    summary['unique_leagues'] = len(leagues)
    
    return summary

def save_season_file(season, season_data):
    """Save individual season file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'season_{season}_action106_{timestamp}.json'
    
    season_file = {
        'season': season,
        'extraction_method': 'Action=106 POST',
        'extraction_timestamp': datetime.now().isoformat(),
        'total_records': len(season_data),
        'data': season_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(season_file, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_dataset(all_data, season_summary, successful_seasons):
    """Save comprehensive multi-season dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    comprehensive_data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Action=106 Historical Crawl',
        'source_url': 'https://www.basketball-bund.net/index.jsp?Action=106',
        'seasons_crawled': successful_seasons,
        'total_seasons': len(successful_seasons),
        'total_records': len(all_data),
        'data_span': f"{min(successful_seasons)}-{max(successful_seasons)}" if successful_seasons else "None",
        'season_summary': season_summary,
        'records': all_data
    }
    
    # Save main comprehensive file
    main_file = f'comprehensive_basketball_history_{timestamp}.json'
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive dataset: {main_file}")
    print(f"📊 {len(all_data):,} records across {len(successful_seasons)} seasons")
    
    # Try to update frontend data
    try:
        # Load existing frontend data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Convert historical records to player-like format for frontend
        frontend_records = convert_to_frontend_format(all_data)
        
        # Combine with existing
        combined_data = existing_players + frontend_records
        
        # Update frontend file
        updated_frontend_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 statistik.do + historical Action=106 data',
            'seasons_available': sorted(list(set([2018] + successful_seasons))),
            'total_players': len(combined_data),
            'total_seasons': len(set([2018] + successful_seasons)),
            'historical_seasons': successful_seasons,
            'players': combined_data
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_frontend_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data: {len(combined_data):,} total records")
        print(f"📅 Seasons: {min(set([2018] + successful_seasons))}-{max(set([2018] + successful_seasons))}")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")
        print(f"💾 Historical data saved separately")
    
    print(f"\n🚀 BASKETBALL REFERENCE FRONTEND READY!")
    print(f"📈 Multi-decade dataset spanning {len(set([2018] + successful_seasons))} seasons")

def convert_to_frontend_format(historical_records):
    """Convert historical records to frontend-compatible format"""
    frontend_records = []
    
    for record in historical_records:
        # Create a frontend-compatible record
        frontend_record = {
            'season_id': record.get('season_id'),
            'source': 'Action=106',
            'extracted_at': record.get('extracted_at'),
            'name': record.get('primary_text', 'Unknown'),
            'team': record.get('likely_team', record.get('primary_text', 'Unknown')),
            'endpoint': 'Action=106',
            'historical_data': True
        }
        
        # Add any additional data we found
        if record.get('is_litzendorf'):
            frontend_record['is_litzendorf'] = True
        
        frontend_records.append(frontend_record)
    
    return frontend_records

if __name__ == "__main__":
    crawl_historical_seasons_exact()
