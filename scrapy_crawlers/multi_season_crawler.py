#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_multiple_seasons():
    """
    Systematically crawl multiple seasons using your proven 2018 methodology
    Perfect for your Basketball Reference-inspired frontend!
    """
    
    print("🏀 MULTI-SEASON BASKETBALL DATA CRAWLER")
    print("Building comprehensive dataset for your Basketball Reference frontend!")
    
    # Define seasons to crawl (excluding your completed ones)
    target_seasons = [2019, 2020, 2021, 2022, 2023]
    
    # Load your proven working leagues from 2018
    known_working_leagues = load_proven_leagues()
    
    print(f"📅 Target seasons: {target_seasons}")
    print(f"🎯 Testing {len(known_working_leagues)} proven league IDs")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    all_working_urls = []
    all_players = []
    season_summary = {}
    
    # Test each season with your proven league IDs
    for season in target_seasons:
        print(f"\n📊 CRAWLING SEASON {season}")
        season_urls = []
        season_players = []
        
        # Test all your proven league IDs for this season
        for i, league_id in enumerate(known_working_leagues, 1):
            print(f"  {i:3d}/{len(known_working_leagues)}: Testing Liga {league_id} for {season}...")
            
            working_urls = test_league_season(league_id, season, headers)
            if working_urls:
                print(f"      ✅ Found {len(working_urls)} endpoints")
                season_urls.extend(working_urls)
                
                # Extract players immediately
                for url_info in working_urls:
                    try:
                        response = requests.get(url_info['url'], headers=headers, timeout=15)
                        if response.status_code == 200:
                            players = extract_players_from_response(response.text, url_info)
                            season_players.extend(players)
                            print(f"        📊 +{len(players)} players from {url_info['endpoint']}")
                    except Exception as e:
                        print(f"        ❌ Error extracting: {e}")
                    
                    time.sleep(0.5)  # Rate limiting
            else:
                print(f"      ❌ No data")
            
            time.sleep(0.3)  # Rate limiting between leagues
        
        # Save season results
        if season_players:
            season_summary[season] = {
                'total_players': len(season_players),
                'unique_leagues': len(set(p.get('liga_id') for p in season_players)),
                'working_urls': len(season_urls),
                'teams': len(set(p.get('team') for p in season_players if p.get('team')))
            }
            
            all_working_urls.extend(season_urls)
            all_players.extend(season_players)
            
            # Save individual season file
            save_season_data(season, season_players, season_urls)
            
            print(f"  ✅ Season {season}: {len(season_players)} players from {len(set(p.get('liga_id') for p in season_players))} leagues")
        else:
            print(f"  ❌ Season {season}: No data found")
    
    # Save comprehensive multi-season dataset
    save_comprehensive_multi_season_data(all_players, all_working_urls, season_summary)
    
    print(f"\n🎯 MULTI-SEASON CRAWL COMPLETE!")
    print(f"📊 Total new players: {len(all_players)}")
    print(f"📅 Seasons with data: {list(season_summary.keys())}")
    print(f"🏀 Total working URLs: {len(all_working_urls)}")
    
    print(f"\n📈 SEASON BREAKDOWN:")
    for season, stats in season_summary.items():
        print(f"  {season}: {stats['total_players']:,} players, {stats['unique_leagues']} leagues, {stats['teams']} teams")
    
    print(f"\n🚀 Your Basketball Reference frontend now has multi-season data!")

def load_proven_leagues():
    """Load league IDs that worked for 2018 season"""
    try:
        with open('oberfranken_working_urls.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract unique league IDs that worked for 2018
        league_ids = set()
        for url_info in data.get('working_urls', []):
            if url_info.get('saison_id') == 2018:
                league_ids.add(url_info.get('liga_id'))
        
        return sorted(list(league_ids))
    except:
        # Fallback to known working leagues from your analysis
        return [
            26162, 26163, 26164, 26165, 26166, 26167, 26168, 26169,
            26171, 26172, 26173, 26174, 26175, 26176, 26177, 26178,
            26179, 26182, 26188, 26189, 26190, 26191, 26192, 26194,
            26195, 26196, 26197, 26198, 26199, 26200, 26211, 26212,
            26214, 26216, 26218, 26219, 26220, 26221, 26222, 26225,
            26226, 26241, 26243, 26244, 26245, 26246, 26247, 26255,
            26256, 26257, 26258, 26259, 26260, 26261
        ]

def test_league_season(liga_id, saison_id, headers):
    """Test if a liga_id + saison_id combination has data"""
    
    test_urls = [
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteFreiWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBeste3erWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
    ]
    
    working_urls = []
    
    for url in test_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200 and has_player_data(response.text):
                endpoint = url.split('reqCode=')[1].split('&')[0]
                working_urls.append({
                    'url': url,
                    'liga_id': liga_id,
                    'saison_id': saison_id,
                    'endpoint': endpoint,
                    'tested_at': datetime.now().isoformat()
                })
        except:
            continue
    
    return working_urls

def has_player_data(html_content):
    """Check if the page actually contains player data"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        sportitem_rows = soup.find_all(['td', 'tr'], class_=lambda x: x and 'sportitem' in str(x).lower())
        text = html_content.lower()
        player_indicators = ['spieler', 'punkte', 'werfer']
        has_indicators = any(indicator in text for indicator in player_indicators)
        
        return len(sportitem_rows) > 5 or (has_indicators and 'basketball' in text)
    except:
        return False

def extract_players_from_response(html_content, url_info):
    """Extract players using your proven parser logic"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Find rows with sportItem classes (your proven method)
        all_rows = soup.find_all('tr')
        player_rows = []
        
        for row in all_rows:
            cells = row.find_all('td')
            has_sport_item = any('sportItem' in str(cell) for cell in cells)
            
            if has_sport_item and len(cells) >= 6:
                player_rows.append(row)
        
        # Parse each player row (your proven method)
        for row in player_rows:
            cells = row.find_all('td')
            
            try:
                cell_texts = []
                for cell in cells:
                    text = cell.get_text().replace('\u00a0', ' ').strip()
                    cell_texts.append(text)
                
                if len(cell_texts) >= 6:
                    player_data = {
                        'liga_id': url_info['liga_id'],
                        'season_id': url_info['saison_id'],
                        'endpoint': url_info['endpoint'],
                        'source_url': url_info['url'],
                        'extracted_at': datetime.now().isoformat(),
                    }
                    
                    # Parse columns (your proven structure)
                    try:
                        player_data['rank'] = int(cell_texts[0].rstrip('.'))
                    except:
                        pass
                    
                    player_data['surname'] = cell_texts[1]
                    player_data['first_name'] = cell_texts[2]
                    player_data['team'] = cell_texts[3]
                    
                    try:
                        player_data['points'] = int(cell_texts[4])
                    except:
                        player_data['points'] = 0
                    
                    try:
                        player_data['games'] = int(cell_texts[5])
                    except:
                        player_data['games'] = 0
                    
                    if len(cell_texts) >= 7:
                        try:
                            player_data['average'] = float(cell_texts[6].replace(',', '.'))
                        except:
                            pass
                    
                    # Create full name
                    if player_data['first_name'] and player_data['surname']:
                        player_data['name'] = f"{player_data['first_name']} {player_data['surname']}"
                    
                    # Only add valid players
                    if player_data.get('name') and player_data.get('team') and player_data.get('points', 0) > 0:
                        players.append(player_data)
                        
            except:
                continue
        
        return players
    except:
        return []

def save_season_data(season, players, working_urls):
    """Save individual season data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    season_data = {
        'season': season,
        'extraction_timestamp': datetime.now().isoformat(),
        'source': f'Multi-season crawl - Season {season}',
        'total_players': len(players),
        'unique_leagues': len(set(p.get('liga_id') for p in players)),
        'unique_teams': len(set(p.get('team') for p in players if p.get('team'))),
        'working_urls': working_urls,
        'players': players
    }
    
    filename = f'basketball_season_{season}_{timestamp}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(season_data, f, indent=2, ensure_ascii=False)
    
    print(f"      💾 Saved: {filename}")

def save_comprehensive_multi_season_data(all_players, all_working_urls, season_summary):
    """Save comprehensive multi-season dataset for your Basketball Reference frontend"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Frontend-ready data structure
    frontend_data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'source': 'Multi-season Basketball-Bund crawl for Basketball Reference frontend',
        'seasons_available': sorted(list(season_summary.keys())),
        'total_players': len(all_players),
        'total_leagues': len(set(p.get('liga_id') for p in all_players)),
        'total_teams': len(set(p.get('team') for p in all_players if p.get('team'))),
        'season_summary': season_summary,
        'players': all_players
    }
    
    # Save main file
    with open(f'multi_season_basketball_data_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    # Update frontend data file (combine with existing 2018 data)
    try:
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        combined_players = existing_players + all_players
        
        combined_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined multi-season basketball data',
            'seasons_available': sorted(list(set([2018] + list(season_summary.keys())))),
            'total_players': len(combined_players),
            'total_seasons': len(set([2018] + list(season_summary.keys()))),
            'players': combined_players
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated real_players_extracted.json with {len(all_players)} new players")
        print(f"📊 Total combined: {len(combined_players)} players across multiple seasons")
        
    except Exception as e:
        print(f"⚠️  Couldn't combine with existing data: {e}")
        print(f"💾 New data saved separately")
    
    # Save working URLs database
    urls_database = {
        'created_at': datetime.now().isoformat(),
        'total_working_urls': len(all_working_urls),
        'seasons_covered': sorted(list(season_summary.keys())),
        'working_urls': all_working_urls
    }
    
    with open(f'multi_season_working_urls_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(urls_database, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    crawl_multiple_seasons()
