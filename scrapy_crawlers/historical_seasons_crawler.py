#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_historical_seasons():
    """
    Crawl historical seasons from 2003-2024 using the Action=106 endpoint
    Perfect for your Basketball Reference-inspired frontend!
    """
    
    print("🏀 HISTORICAL SEASONS CRAWLER (2003-2024)")
    print("Using Action=106 endpoint for comprehensive multi-season data")
    print("Building Basketball Reference-style dataset!")
    
    # Target seasons from 2003 to 2024 (excluding your complete 2018)
    target_seasons = list(range(2003, 2025))
    target_seasons.remove(2018)  # You already have complete 2018 data
    
    print(f"📅 Target seasons: {len(target_seasons)} seasons ({min(target_seasons)}-{max(target_seasons)})")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    all_seasons_data = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📊 CRAWLING SEASON {season}")
        
        season_data = crawl_season_data(session, season)
        
        if season_data:
            all_seasons_data.extend(season_data)
            
            # Calculate summary
            season_summary[season] = {
                'total_players': len(season_data),
                'unique_teams': len(set(p.get('team') for p in season_data if p.get('team'))),
                'unique_leagues': len(set(p.get('liga_id') for p in season_data if p.get('liga_id'))),
                'oberfranken_players': len([p for p in season_data if 'oberfranken' in str(p.get('bezirk', '')).lower()]),
                'litzendorf_players': len([p for p in season_data if 'litzendorf' in str(p.get('team', '')).lower()])
            }
            
            print(f"  ✅ Season {season}: {len(season_data)} players")
            print(f"    Teams: {season_summary[season]['unique_teams']}")
            print(f"    Oberfranken: {season_summary[season]['oberfranken_players']}")
            print(f"    Litzendorf: {season_summary[season]['litzendorf_players']}")
            
            # Save individual season
            save_individual_season(season, season_data)
        else:
            print(f"  ❌ Season {season}: No data found")
        
        # Rate limiting between seasons
        time.sleep(random.uniform(2, 4))
    
    # Save comprehensive multi-season dataset
    save_comprehensive_historical_data(all_seasons_data, season_summary)
    
    print(f"\n🎯 HISTORICAL CRAWL COMPLETE!")
    print(f"📊 Total seasons crawled: {len(season_summary)}")
    print(f"👤 Total players: {len(all_seasons_data)}")
    print(f"📈 Data span: {min(season_summary.keys()) if season_summary else 'None'}-{max(season_summary.keys()) if season_summary else 'None'}")

def crawl_season_data(session, season):
    """
    Crawl data for a specific season using Action=106 endpoint
    """
    
    # Form data based on your findings
    form_data = {
        'Action': '106',
        'Verband': '2',  # Bayern
        'saison_id': str(season),
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',  # Senioren
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '5',  # Oberfranken (based on your data)
        'cbKreisFilter': '0',
        'spieltyp_id': '1',
        'search': ''
    }
    
    try:
        print(f"  🔍 Requesting season {season} data...")
        
        # POST request to get season data
        response = session.post(
            'https://www.basketball-bund.net/index.jsp',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"    ✅ Got response ({len(response.text):,} chars)")
            
            # Parse the response
            season_players = parse_season_response(response.text, season)
            
            if season_players:
                print(f"    📊 Extracted {len(season_players)} players")
                return season_players
            else:
                print(f"    ❌ No players found in response")
                return []
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"    💥 Error: {str(e)[:100]}")
        return []

def parse_season_response(html_content, season):
    """
    Parse the Action=106 response to extract player data
    """
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Look for different table patterns in Action=106 response
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if table contains player/team data
            if is_player_data_table(table):
                table_players = extract_players_from_table(table, season)
                players.extend(table_players)
        
        # Also look for specific patterns that might contain league/team info
        league_data = extract_league_information(soup, season)
        
        # If we found league data but no individual players, create team records
        if league_data and not players:
            players = create_team_records_from_leagues(league_data, season)
        
        return players
        
    except Exception as e:
        print(f"      ❌ Parse error: {str(e)[:100]}")
        return []

def is_player_data_table(table):
    """
    Check if table contains player or team data
    """
    
    try:
        # Look at table headers and content
        headers = table.find_all(['th', 'td'])
        header_text = ' '.join([h.get_text().lower() for h in headers[:10]])
        
        # Check for basketball-related indicators
        basketball_indicators = [
            'liga', 'mannschaft', 'team', 'verein', 'spieler', 'punkte',
            'basketball', 'saison', 'tabelle', 'spiel'
        ]
        
        return any(indicator in header_text for indicator in basketball_indicators)
        
    except:
        return False

def extract_players_from_table(table, season):
    """
    Extract player/team data from HTML table
    """
    
    players = []
    
    try:
        rows = table.find_all('tr')
        
        for row_idx, row in enumerate(rows[1:], 1):  # Skip header
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:  # Need at least some data
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Try to identify what kind of data this is
                player_data = {
                    'season_id': season,
                    'source': 'Action=106',
                    'extracted_at': datetime.now().isoformat(),
                    'row_index': row_idx
                }
                
                # Parse based on cell content patterns
                if len(cell_texts) >= 3:
                    # Could be: Team, Liga, Bezirk or Player, Team, Points, etc.
                    
                    # Check if first cell looks like a team name
                    if cell_texts[0] and len(cell_texts[0]) > 2 and not cell_texts[0].isdigit():
                        player_data['team'] = cell_texts[0]
                    
                    # Check if second cell looks like league info
                    if len(cell_texts) > 1 and ('liga' in cell_texts[1].lower() or cell_texts[1].isdigit()):
                        player_data['liga_info'] = cell_texts[1]
                    
                    # Check if third cell looks like region info
                    if len(cell_texts) > 2:
                        if 'franken' in cell_texts[2].lower() or 'bayern' in cell_texts[2].lower():
                            player_data['bezirk'] = cell_texts[2]
                        elif cell_texts[2].isdigit():
                            player_data['points'] = int(cell_texts[2])
                    
                    # Look for numeric data (points, games, etc.)
                    for i, cell_text in enumerate(cell_texts):
                        if cell_text.isdigit():
                            if i == 3:
                                player_data['games'] = int(cell_text)
                            elif i == 4:
                                player_data['wins'] = int(cell_text)
                            elif i == 5:
                                player_data['losses'] = int(cell_text)
                
                # Only add if we have meaningful data
                if player_data.get('team') and len(player_data) > 4:
                    players.append(player_data)
    
    except Exception as e:
        print(f"        ❌ Table extraction error: {str(e)[:50]}")
    
    return players

def extract_league_information(soup, season):
    """
    Extract league and competition information from the page
    """
    
    league_data = []
    
    try:
        # Look for league listings, competition info, etc.
        # This might be in different formats depending on the response
        
        # Look for links that might contain league IDs
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if 'liga' in href.lower() or 'competition' in href.lower():
                league_info = {
                    'season_id': season,
                    'link_text': link.get_text(strip=True),
                    'link_href': href,
                    'source': 'Action=106_links'
                }
                league_data.append(league_info)
        
        # Look for structured data in divs or spans
        for element in soup.find_all(['div', 'span', 'p']):
            text = element.get_text(strip=True)
            if ('liga' in text.lower() or 'oberfranken' in text.lower()) and len(text) < 200:
                league_info = {
                    'season_id': season,
                    'text_content': text,
                    'source': 'Action=106_text'
                }
                league_data.append(league_info)
    
    except Exception as e:
        print(f"        ❌ League extraction error: {str(e)[:50]}")
    
    return league_data

def create_team_records_from_leagues(league_data, season):
    """
    Create team records from league information when individual player data isn't available
    """
    
    teams = []
    
    for item in league_data:
        if item.get('link_text') and 'liga' not in item['link_text'].lower():
            # Might be a team name
            team_record = {
                'season_id': season,
                'team': item['link_text'],
                'source': 'Action=106_derived',
                'data_type': 'team_listing',
                'extracted_at': datetime.now().isoformat()
            }
            teams.append(team_record)
    
    return teams

def save_individual_season(season, season_data):
    """
    Save individual season data
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'historical_season_{season}_{timestamp}.json'
    
    season_file_data = {
        'season': season,
        'extraction_method': 'Action=106',
        'extraction_timestamp': datetime.now().isoformat(),
        'total_records': len(season_data),
        'data': season_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(season_file_data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_historical_data(all_data, season_summary):
    """
    Save comprehensive historical dataset for Basketball Reference frontend
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Comprehensive dataset
    comprehensive_data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Action=106 Historical Crawl',
        'source': 'basketball-bund.net Action=106 endpoint',
        'seasons_covered': sorted(list(season_summary.keys())),
        'total_seasons': len(season_summary),
        'total_records': len(all_data),
        'season_summary': season_summary,
        'data_span': f"{min(season_summary.keys()) if season_summary else 'None'}-{max(season_summary.keys()) if season_summary else 'None'}",
        'players': all_data
    }
    
    # Save main file
    main_filename = f'historical_basketball_data_{timestamp}.json'
    with open(main_filename, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved comprehensive data: {main_filename}")
    
    # Try to merge with existing data
    try:
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Combine data
        combined_players = existing_players + all_data
        
        # Update existing seasons list
        existing_seasons = existing_data.get('seasons_available', [2018])
        all_seasons = sorted(list(set(existing_seasons + list(season_summary.keys()))))
        
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined historical and existing basketball data',
            'seasons_available': all_seasons,
            'total_players': len(combined_players),
            'total_seasons': len(all_seasons),
            'historical_summary': season_summary,
            'players': combined_players
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated real_players_extracted.json")
        print(f"📊 Combined dataset: {len(combined_players):,} players across {len(all_seasons)} seasons")
        print(f"📅 Season coverage: {min(all_seasons)}-{max(all_seasons)}")
        
    except Exception as e:
        print(f"⚠️  Couldn't merge with existing data: {e}")
        print(f"💾 Historical data saved separately")
    
    print(f"\n🚀 Basketball Reference Frontend Ready!")
    print(f"📈 Multi-season dataset perfect for historical comparisons")
    print(f"🏀 Spans {len(season_summary)} seasons of basketball data")

if __name__ == "__main__":
    crawl_historical_seasons()
