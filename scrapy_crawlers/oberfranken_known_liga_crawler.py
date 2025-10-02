#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

def crawl_oberfranken_with_known_liga_ids():
    """
    Comprehensive Oberfranken crawler using KNOWN WORKING liga_ids
    Skip the discovery phase and use liga_ids we know work from previous tests
    """
    
    print("🏀 COMPREHENSIVE OBERFRANKEN CRAWLER (KNOWN LIGA_IDS)")
    print("Using known working liga_ids to extract player statistics")
    print("📅 Coverage: 21 years of basketball history! (2003-2017, 2019-2024)")
    
    # Known working liga_ids from previous discoveries and tests
    known_liga_ids = [
        {'liga_id': '1701', 'name': 'Bezirksliga Herren', 'has_litzendorf': True},
        {'liga_id': '250', 'name': 'Liga 250', 'has_litzendorf': False},
        {'liga_id': '3340', 'name': 'Senioren Ü45', 'has_litzendorf': False},
        {'liga_id': '263', 'name': 'Senioren Ü40 (männlich)', 'has_litzendorf': False},
        {'liga_id': '8025', 'name': 'Senioreninnen Ü40', 'has_litzendorf': False},
        {'liga_id': '261', 'name': 'Senioren Ü35', 'has_litzendorf': False},
        {'liga_id': '256', 'name': 'Bezirkspokal Herren', 'has_litzendorf': False},
        {'liga_id': '248', 'name': 'Bezirksliga Damen A', 'has_litzendorf': False},
        {'liga_id': '2659', 'name': 'Bezirksliga Damen B', 'has_litzendorf': False},
        {'liga_id': '6964', 'name': 'Bezirksliga Damen Meisterschaft', 'has_litzendorf': False},
        {'liga_id': '697', 'name': 'Bezirkspokal Damen', 'has_litzendorf': False}
    ]
    
    # Target seasons 
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
        'leagues_processed': known_liga_ids,
        'total_players': 0,
        'litzendorf_players': 0,
        'method': 'known_liga_ids'
    }
    
    total_combinations = len(target_seasons) * len(known_liga_ids) * len(stat_endpoints)
    processed_combinations = 0
    
    # Process each season
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        season_players = []
        season_summary = {'leagues': {}, 'total_players': 0, 'litzendorf_players': 0}
        
        # Process each league
        for league in known_liga_ids:
            liga_id = league['liga_id']
            league_name = league['name']
            
            print(f"  🏀 {league_name} (ID: {liga_id})")
            league_players = []
            
            # Process each stat endpoint
            for endpoint in stat_endpoints:
                stat_name = endpoint['name']
                req_code = endpoint['reqCode']
                stat_label = endpoint['stat_label']
                
                processed_combinations += 1
                progress = f"[{processed_combinations}/{total_combinations}]"
                
                print(f"    📊 {stat_name} {progress}")
                
                try:
                    # Build statistik.do URL
                    url = f"https://www.basketball-bund.net/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season}&_top=-1"
                    
                    response = session.get(url, timeout=30)
                    
                    if response.status_code == 200 and len(response.text) > 10000:
                        # Quick check for data
                        if 'Keine Einträge gefunden' not in response.text:
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
                                print(f"      ❌ No players parsed")
                        else:
                            print(f"      ❌ No entries found")
                    else:
                        print(f"      ❌ No data (status: {response.status_code})")
                        
                except Exception as e:
                    print(f"      💥 Error: {str(e)[:50]}")
                
                # Rate limiting
                time.sleep(random.uniform(0.2, 0.6))
            
            # League summary
            if league_players:
                season_players.extend(league_players)
                litzendorf_count = len([p for p in league_players if p.get('is_litzendorf')])
                season_summary['leagues'][liga_id] = {
                    'name': league_name,
                    'total_players': len(league_players),
                    'litzendorf_players': litzendorf_count
                }
                
                litz_indicator = f" (🌟 {litzendorf_count} Litzendorf)" if litzendorf_count > 0 else ""
                print(f"    📈 League total: {len(league_players)} players{litz_indicator}")
            
            time.sleep(random.uniform(0.3, 0.8))
        
        # Season summary
        if season_players:
            all_player_data.extend(season_players)
            season_litzendorf = len([p for p in season_players if p.get('is_litzendorf')])
            
            season_summary['total_players'] = len(season_players)
            season_summary['litzendorf_players'] = season_litzendorf
            comprehensive_summary['seasons_processed'][season] = season_summary
            
            save_season_known_liga_data(season, season_players, season_summary)
            
            litz_indicator = f" (🌟 {season_litzendorf} Litzendorf)" if season_litzendorf > 0 else ""
            print(f"  📊 Season {season}: {len(season_players)} total players{litz_indicator}")
        else:
            print(f"  ❌ Season {season}: No data")
        
        time.sleep(random.uniform(0.5, 1.5))
    
    # Final comprehensive results
    if all_player_data:
        comprehensive_summary['total_players'] = len(all_player_data)
        comprehensive_summary['litzendorf_players'] = len([p for p in all_player_data if p.get('is_litzendorf')])
        
        save_comprehensive_known_liga_data(all_player_data, comprehensive_summary)
        update_frontend_with_known_liga_data(all_player_data, comprehensive_summary)
    
    print(f"\n🎯 COMPREHENSIVE OBERFRANKEN CRAWL COMPLETE!")
    print(f"📊 Total players extracted: {comprehensive_summary['total_players']:,}")
    print(f"🌟 Total Litzendorf players: {comprehensive_summary['litzendorf_players']}")
    print(f"📅 Seasons processed: {list(comprehensive_summary['seasons_processed'].keys())}")
    print(f"🏀 Leagues used: {len(known_liga_ids)}")
    
    # Final breakdown
    for season, summary in comprehensive_summary['seasons_processed'].items():
        litz_count = summary['litzendorf_players']
        league_count = len(summary['leagues'])
        litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
        print(f"  {season}: {summary['total_players']} players, {league_count} leagues{litz_indicator}")

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
                    'extraction_method': 'known_liga_ids Oberfranken crawler',
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

def save_season_known_liga_data(season, players, summary):
    """Save individual season data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'oberfranken_known_liga_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'bezirk': 'Oberfranken',
        'extraction_method': 'known_liga_ids crawler',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'litzendorf_players': [p for p in players if p.get('is_litzendorf')],
        'season_summary': summary,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Season file: {filename}")

def save_comprehensive_known_liga_data(all_players, summary):
    """Save comprehensive dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'oberfranken_comprehensive_known_liga_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'known_liga_ids Oberfranken crawler',
        'bezirk': 'Oberfranken',
        'coverage_years': '2003-2017, 2019-2024',
        'total_players': len(all_players),
        'comprehensive_summary': summary,
        'litzendorf_players': [p for p in all_players if p.get('is_litzendorf')],
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")
    print(f"🌟 Total Litzendorf players: {len(data['litzendorf_players'])}")

def update_frontend_with_known_liga_data(historical_players, summary):
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
                'endpoint': 'statistik.do_oberfranken_known_liga_comprehensive',
                'source': 'oberfranken_known_liga_crawler',
                'extracted_at': player['extracted_at'],
                'data_type': 'oberfranken_known_liga_statistics'
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
            'source': 'Combined 2018 players + Comprehensive Oberfranken known liga stats',
            'total_records': len(all_data),
            'original_records': len(existing_players),
            'oberfranken_records': len(frontend_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'bezirk_coverage': 'Oberfranken (known liga_ids)',
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
        print(f"   🏀 Known liga_ids used: {len(summary['leagues_processed'])}")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_oberfranken_with_known_liga_ids()
