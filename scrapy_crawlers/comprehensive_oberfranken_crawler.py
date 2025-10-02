#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

def crawl_all_oberfranken_leagues():
    """
    Comprehensive crawler for ALL leagues in Bezirk Oberfranken across ALL seasons
    1. Discover all liga_ids in Oberfranken (cbBezirkFilter=5)
    2. Extract player statistics from all leagues 
    3. Cover all seasons 2010-2024
    4. Get all 3 stat categories per player
    """
    
    print("🏀 COMPREHENSIVE OBERFRANKEN BASKETBALL CRAWLER")
    print("Discovering and crawling ALL leagues in Bezirk Oberfranken across ALL seasons (2003-2024)")
    print("📅 Coverage: 21 years of basketball history! (2003-2017, 2019-2024)")
    
    # Target seasons - ALL available from 2003 onwards (21 years, missing 2018)
    target_seasons = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    # Player statistics endpoints
    stat_endpoints = [
        {
            'name': 'Best Scorers',
            'reqCode': 'statBesteWerferArchiv',
            'description': 'Top scoring players (points per game)',
            'stat_label': 'PPG'
        },
        {
            'name': 'Best Free Throw Shooters', 
            'reqCode': 'statBesteFreiWerferArchiv',
            'description': 'Top free throw percentage players',
            'stat_label': 'FT%'
        },
        {
            'name': 'Best 3-Point Shooters',
            'reqCode': 'statBeste3erWerferArchiv', 
            'description': 'Top 3-point shooters (3-pointers per game)',
            'stat_label': '3PG'
        }
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_player_data = []
    comprehensive_summary = {
        'seasons_processed': {},
        'leagues_discovered': {},
        'total_players': 0,
        'litzendorf_players': 0,
        'oberfranken_coverage': True
    }
    
    # Discover all leagues in Oberfranken for each season
    print(f"\n🔍 PHASE 1: DISCOVERING ALL OBERFRANKEN LEAGUES")
    all_discovered_leagues = {}
    
    for season in target_seasons:
        print(f"\n📅 DISCOVERING LEAGUES FOR SEASON {season}")
        
        # Use Action=106 to discover leagues in Oberfranken
        discovered_leagues = discover_oberfranken_leagues(session, season)
        
        if discovered_leagues:
            all_discovered_leagues[season] = discovered_leagues
            print(f"  ✅ Found {len(discovered_leagues)} leagues in Oberfranken for {season}")
            
            # Show sample leagues
            for i, league in enumerate(discovered_leagues[:5]):
                liga_id = league.get('liga_id', 'Unknown')
                name = league.get('name', 'Unknown')
                print(f"    {i+1}. {name} (ID: {liga_id})")
            
            if len(discovered_leagues) > 5:
                print(f"    ... and {len(discovered_leagues)-5} more leagues")
        else:
            print(f"  ❌ No leagues found for {season}")
        
        time.sleep(random.uniform(1, 2))
    
    # Save discovered leagues
    save_discovered_leagues(all_discovered_leagues)
    
    # Phase 2: Extract player statistics from all discovered leagues
    print(f"\n🏀 PHASE 2: EXTRACTING PLAYER STATISTICS")
    
    total_leagues_to_process = sum(len(leagues) for leagues in all_discovered_leagues.values())
    processed_leagues = 0
    
    for season in target_seasons:
        if season not in all_discovered_leagues:
            continue
            
        print(f"\n📅 SEASON {season}")
        season_players = []
        season_leagues = all_discovered_leagues[season]
        
        for league in season_leagues:
            liga_id = league.get('liga_id')
            league_name = league.get('name', f'Liga {liga_id}')
            
            processed_leagues += 1
            print(f"  🏀 {league_name} (ID: {liga_id}) [{processed_leagues}/{total_leagues_to_process}]")
            
            league_players = []
            
            # Extract player stats for all 3 categories
            for endpoint in stat_endpoints:
                stat_name = endpoint['name']
                req_code = endpoint['reqCode']
                stat_label = endpoint['stat_label']
                
                print(f"    📊 {stat_name}")
                
                try:
                    # Build statistik.do URL
                    url = f"https://www.basketball-bund.net/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season}&_top=-1"
                    
                    response = session.get(url, timeout=30)
                    
                    if response.status_code == 200 and len(response.text) > 10000:
                        # Parse players
                        config = {
                            'stat_type': req_code,
                            'stat_name': stat_name,
                            'stat_label': stat_label,
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'season': season
                        }
                        players = parse_oberfranken_player_stats(response.text, config)
                        
                        if players:
                            league_players.extend(players)
                            
                            # Check for Litzendorf players
                            litzendorf_players = [p for p in players if p.get('is_litzendorf')]
                            
                            if litzendorf_players:
                                print(f"      ✅ {len(players)} players (🌟 {len(litzendorf_players)} Litzendorf)")
                                # Show first Litzendorf player
                                lp = litzendorf_players[0]
                                full_name = f"{lp.get('first_name', '')} {lp.get('last_name', '')}".strip()
                                stat_value = lp.get('primary_stat_value', 'N/A')
                                print(f"        🏆 {full_name} - {stat_value} {stat_label}")
                            else:
                                print(f"      ✅ {len(players)} players")
                        else:
                            print(f"      ❌ No players")
                    else:
                        print(f"      ❌ No data (status: {response.status_code})")
                        
                except Exception as e:
                    print(f"      💥 Error: {str(e)[:50]}")
                
                # Rate limiting
                time.sleep(random.uniform(0.3, 0.8))
            
            # League summary
            if league_players:
                season_players.extend(league_players)
                litzendorf_count = len([p for p in league_players if p.get('is_litzendorf')])
                
                litz_indicator = f" (🌟 {litzendorf_count} Litzendorf)" if litzendorf_count > 0 else ""
                print(f"    📈 League total: {len(league_players)} players{litz_indicator}")
            
            time.sleep(random.uniform(0.5, 1.5))
        
        # Season summary
        if season_players:
            all_player_data.extend(season_players)
            season_litzendorf = len([p for p in season_players if p.get('is_litzendorf')])
            
            comprehensive_summary['seasons_processed'][season] = {
                'total_players': len(season_players),
                'litzendorf_players': season_litzendorf,
                'leagues_processed': len(season_leagues)
            }
            
            save_season_oberfranken_data(season, season_players, season_leagues)
            
            litz_indicator = f" (🌟 {season_litzendorf} Litzendorf)" if season_litzendorf > 0 else ""
            print(f"  📊 Season {season}: {len(season_players)} total players{litz_indicator}")
        else:
            print(f"  ❌ Season {season}: No data")
        
        time.sleep(random.uniform(1, 3))
    
    # Final comprehensive results
    if all_player_data:
        comprehensive_summary['total_players'] = len(all_player_data)
        comprehensive_summary['litzendorf_players'] = len([p for p in all_player_data if p.get('is_litzendorf')])
        comprehensive_summary['leagues_discovered'] = all_discovered_leagues
        
        save_comprehensive_oberfranken_data(all_player_data, comprehensive_summary)
        update_frontend_with_oberfranken_data(all_player_data, comprehensive_summary)
    
    print(f"\n🎯 COMPREHENSIVE OBERFRANKEN CRAWL COMPLETE!")
    print(f"📊 Total players extracted: {comprehensive_summary['total_players']:,}")
    print(f"🌟 Total Litzendorf players: {comprehensive_summary['litzendorf_players']}")
    print(f"📅 Seasons processed: {list(comprehensive_summary['seasons_processed'].keys())}")
    print(f"🏀 Total leagues discovered: {sum(len(leagues) for leagues in all_discovered_leagues.values())}")
    
    # Final breakdown
    for season, summary in comprehensive_summary['seasons_processed'].items():
        litz_count = summary['litzendorf_players']
        league_count = summary['leagues_processed']
        litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
        print(f"  {season}: {summary['total_players']} players, {league_count} leagues{litz_indicator}")

def discover_oberfranken_leagues(session, season):
    """
    Discover all liga_ids in Bezirk Oberfranken for a given season
    Uses Action=106 with the exact POST parameters from user's working request
    """
    
    discovered_leagues = []
    
    try:
        # Action=106 URL for Oberfranken league discovery
        url = 'https://www.basketball-bund.net/index.jsp'
        
        # POST data with EXACT parameters from user's working request
        post_data = {
            'Action': '106',
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',  # Senioren (all ages)
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        response = session.post(url, data=post_data, timeout=30)
        
        if response.status_code == 200 and len(response.text) > 10000:
            # Parse league links from response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for links with Action=107 and liga_id
            links = soup.find_all('a', href=re.compile(r'Action=107.*liga_id='))
            
            for link in links:
                href = link.get('href', '')
                
                # Extract liga_id from href
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = liga_id_match.group(1)
                    
                    # Get league name from link text
                    league_name = link.get_text(strip=True)
                    
                    if liga_id and league_name:
                        discovered_leagues.append({
                            'liga_id': liga_id,
                            'name': league_name,
                            'season': season,
                            'bezirk': 'Oberfranken',
                            'discovery_method': 'Action=106 exact POST parameters'
                        })
        
        # Remove duplicates
        seen = set()
        unique_leagues = []
        for league in discovered_leagues:
            key = (league['liga_id'], league['name'])
            if key not in seen:
                seen.add(key)
                unique_leagues.append(league)
        
        return unique_leagues
        
    except Exception as e:
        print(f"    💥 Discovery error: {str(e)[:50]}")
        return []

def parse_oberfranken_player_stats(html_content, config):
    """
    Parse player statistics from Oberfranken leagues with corrected column mapping
    """
    
    players = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for tables with player data
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        # Look for sportItem cells
        sport_item_cells = table.find_all('td', class_=lambda x: x and 'sportItem' in x)
        
        if not sport_item_cells:
            continue
        
        # Process rows
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            row_cells = row.find_all('td', class_=lambda x: x and 'sportItem' in x)
            
            if len(row_cells) < 7:  # Need all 7 columns
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in row_cells]
            
            # Parse with correct column mapping: Rank, LastName, FirstName, Team, Stat1, Stat2, Stat3
            if len(cell_texts) >= 7:
                player = {
                    'rank': cell_texts[0],
                    'last_name': cell_texts[1], 
                    'first_name': cell_texts[2],
                    'team': cell_texts[3],
                    'stat_value_1': cell_texts[4],
                    'stat_value_2': cell_texts[5], 
                    'stat_value_3': cell_texts[6],
                    'season_id': config['season'],
                    'liga_id': config['liga_id'],
                    'league_name': config['league_name'],
                    'stat_type': config['stat_type'],
                    'stat_category': config['stat_name'],
                    'bezirk': 'Oberfranken',
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'comprehensive Oberfranken player crawler',
                    'extracted_at': datetime.now().isoformat(),
                    'raw_data': cell_texts
                }
                
                # Add stat-specific labels with corrected mapping
                if config['stat_type'] == 'statBesteWerferArchiv':
                    # Punkte | Spiele | Schnitt (PPG)
                    player['total_points'] = cell_texts[4]
                    player['games_played'] = cell_texts[5]
                    player['points_per_game'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = 'PPG'
                    
                elif config['stat_type'] == 'statBesteFreiWerferArchiv':
                    # Freiwürfe (attempted) | Treffer (made) | Quote (%)
                    player['ft_attempted'] = cell_texts[4] 
                    player['ft_made'] = cell_texts[5]
                    player['ft_percentage'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = 'FT%'
                    
                elif config['stat_type'] == 'statBeste3erWerferArchiv':
                    # 3-er (made) | Spiele (games) | Schnitt (per game)
                    player['three_point_made'] = cell_texts[4]
                    player['games_played'] = cell_texts[5] 
                    player['three_point_per_game'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = '3PG'  # 3-Pointers Per Game!
                
                # Full name
                player['full_name'] = f"{player['first_name']} {player['last_name']}".strip()
                
                # Check for Litzendorf (multiple variations)
                team_lower = player['team'].lower()
                if any(term in team_lower for term in ['litzendorf', 'bg litzendorf', 'bgl']):
                    player['is_litzendorf'] = True
                    player['team_type'] = 'BG Litzendorf'
                
                # Skip invalid data
                if (player['last_name'] and 
                    len(player['last_name']) > 1 and 
                    not player['last_name'].isdigit() and
                    player['team'] and
                    len(player['team']) > 1):
                    
                    players.append(player)
    
    return players

def save_discovered_leagues(all_discovered_leagues):
    """Save discovered leagues data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'oberfranken_discovered_leagues_{timestamp}.json'
    
    data = {
        'discovery_timestamp': datetime.now().isoformat(),
        'discovery_method': 'Action=106 cbBezirkFilter=5 Oberfranken',
        'total_seasons': len(all_discovered_leagues),
        'total_leagues': sum(len(leagues) for leagues in all_discovered_leagues.values()),
        'leagues_by_season': all_discovered_leagues
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Discovered leagues saved: {filename}")
    print(f"🏀 Total leagues found: {data['total_leagues']} across {data['total_seasons']} seasons")

def save_season_oberfranken_data(season, players, leagues):
    """Save individual season Oberfranken data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'oberfranken_players_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'bezirk': 'Oberfranken',
        'extraction_method': 'comprehensive Oberfranken player crawler',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'total_leagues': len(leagues),
        'litzendorf_players': [p for p in players if p.get('is_litzendorf')],
        'leagues_processed': leagues,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Season file: {filename}")

def save_comprehensive_oberfranken_data(all_players, summary):
    """Save comprehensive Oberfranken dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'oberfranken_comprehensive_players_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'comprehensive Oberfranken player crawler',
        'bezirk': 'Oberfranken',
        'total_players': len(all_players),
        'comprehensive_summary': summary,
        'litzendorf_players': [p for p in all_players if p.get('is_litzendorf')],
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive Oberfranken file: {filename}")
    print(f"🌟 Total Litzendorf players: {len(data['litzendorf_players'])}")

def update_frontend_with_oberfranken_data(historical_players, summary):
    """Update frontend data with comprehensive Oberfranken player statistics"""
    try:
        # Load existing data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Convert Oberfranken player data to frontend format
        frontend_players = []
        for player in historical_players:
            frontend_player = {
                'name': player['full_name'],
                'team': player['team'],
                'season_id': player['season_id'],
                'league': player['league_name'],
                'liga_id': player['liga_id'],
                'bezirk': 'Oberfranken',
                'stat_category': player['stat_category'],
                'stat_type': player['stat_type'],
                'primary_stat': player.get('primary_stat_value'),
                'primary_stat_label': player.get('primary_stat_label'),
                'endpoint': 'statistik.do_oberfranken_comprehensive',
                'source': 'oberfranken_comprehensive_crawler',
                'extracted_at': player['extracted_at'],
                'data_type': 'oberfranken_player_statistics'
            }
            
            # Add specific stats
            if player.get('points_per_game'):
                frontend_player['points_per_game'] = player['points_per_game']
                frontend_player['total_points'] = player.get('total_points')
                frontend_player['games_played'] = player.get('games_played')
            
            if player.get('ft_percentage'):
                frontend_player['ft_percentage'] = player['ft_percentage']
                frontend_player['ft_made'] = player.get('ft_made')
                frontend_player['ft_attempted'] = player.get('ft_attempted')
            
            if player.get('three_point_per_game'):
                frontend_player['three_point_per_game'] = player['three_point_per_game']
                frontend_player['three_point_made'] = player.get('three_point_made')
                frontend_player['games_played_3p'] = player.get('games_played')
            
            # Litzendorf flag
            if player.get('is_litzendorf'):
                frontend_player['is_litzendorf'] = True
                frontend_player['team_type'] = 'BG Litzendorf'
            
            frontend_players.append(frontend_player)
        
        # Combine datasets
        all_data = existing_players + frontend_players
        all_seasons = sorted(list(set([2018] + list(summary['seasons_processed'].keys()))))
        
        # Update frontend file
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 players + Comprehensive Oberfranken player stats',
            'total_records': len(all_data),
            'original_records': len(existing_players),
            'oberfranken_records': len(frontend_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'bezirk_coverage': 'Oberfranken (comprehensive)',
            'litzendorf_players_total': len([p for p in all_data if p.get('is_litzendorf')]),
            'oberfranken_summary': summary,
            'players': all_data
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data with comprehensive Oberfranken coverage:")
        print(f"   👥 {len(existing_players):,} original records")
        print(f"   🏀 {len(frontend_players):,} Oberfranken player records")
        print(f"   🌟 {updated_data['litzendorf_players_total']} total Litzendorf players")
        print(f"   📅 Coverage: {min(all_seasons)}-{max(all_seasons)} ({len(all_seasons)} seasons)")
        print(f"   🏀 Leagues: {sum(len(leagues) for leagues in summary['leagues_discovered'].values())} total")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_all_oberfranken_leagues()
