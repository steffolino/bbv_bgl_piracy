#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_comprehensive_player_stats():
    """
    Comprehensive player statistics crawler using statistik.do endpoints
    Extracts individual player data across multiple seasons and leagues
    """
    
    print("🏀 COMPREHENSIVE PLAYER STATISTICS CRAWLER")
    print("Extracting individual player stats across seasons and leagues")
    
    # Known liga_ids from previous testing
    target_leagues = [
        {'liga_id': '1701', 'name': 'Bezirksliga Herren', 'has_litzendorf': True},
        {'liga_id': '250', 'name': 'Liga 250', 'has_litzendorf': False},
        {'liga_id': '3340', 'name': 'Senioren Ü45', 'has_litzendorf': False},
        {'liga_id': '263', 'name': 'Senioren Ü40 (männlich)', 'has_litzendorf': False},
        {'liga_id': '8025', 'name': 'Senioreninnen Ü40', 'has_litzendorf': False},
        {'liga_id': '261', 'name': 'Senioren Ü35', 'has_litzendorf': False},
        {'liga_id': '256', 'name': 'Bezirkspokal Herren', 'has_litzendorf': False},
        {'liga_id': '248', 'name': 'Bezirksliga Damen A', 'has_litzendorf': False}
    ]
    
    # Player statistics endpoints
    stat_endpoints = [
        {
            'name': 'Best Scorers',
            'reqCode': 'statBesteWerferArchiv',
            'description': 'Top scoring players (points per game)'
        },
        {
            'name': 'Best Free Throw Shooters', 
            'reqCode': 'statBesteFreiWerferArchiv',
            'description': 'Top free throw percentage players'
        },
        {
            'name': 'Best 3-Point Shooters',
            'reqCode': 'statBeste3erWerferArchiv', 
            'description': 'Top 3-point shooters (3-pointers per game)'
        }
    ]
    
    # Target seasons 
    target_seasons = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_player_data = []
    comprehensive_summary = {
        'seasons_processed': {},
        'leagues_processed': {},
        'total_players': 0,
        'litzendorf_players': 0,
        'stat_categories': {}
    }
    
    # Process each season
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        season_players = []
        season_summary = {'leagues': {}, 'total_players': 0, 'litzendorf_players': 0}
        
        # Process each league
        for league in target_leagues:
            liga_id = league['liga_id']
            league_name = league['name']
            
            print(f"  🏀 {league_name} (ID: {liga_id})")
            league_players = []
            
            # Process each stat endpoint
            for endpoint in stat_endpoints:
                stat_name = endpoint['name']
                req_code = endpoint['reqCode']
                
                print(f"    📊 {stat_name}")
                
                # Build URL
                url = f"https://www.basketball-bund.net/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season}&_top=-1"
                
                try:
                    response = session.get(url, timeout=30)
                    
                    if response.status_code == 200 and len(response.text) > 10000:
                        # Parse players
                        config = {
                            'stat_type': req_code,
                            'stat_name': stat_name,
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'season': season
                        }
                        players = parse_player_statistics(response.text, config)
                        
                        if players:
                            league_players.extend(players)
                            
                            # Check for Litzendorf players
                            litzendorf_players = [p for p in players if p.get('is_litzendorf')]
                            
                            if litzendorf_players:
                                print(f"      ✅ {len(players)} players (🌟 {len(litzendorf_players)} Litzendorf)")
                                for lp in litzendorf_players[:3]:  # Show first 3
                                    full_name = f"{lp.get('first_name', '')} {lp.get('last_name', '')}".strip()
                                    stat_value = lp.get('primary_stat_value', 'N/A')
                                    stat_label = lp.get('primary_stat_label', 'stat')
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
                time.sleep(random.uniform(0.5, 1.5))
            
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
            
            time.sleep(random.uniform(1, 2))
        
        # Season summary
        if season_players:
            all_player_data.extend(season_players)
            season_litzendorf = len([p for p in season_players if p.get('is_litzendorf')])
            
            season_summary['total_players'] = len(season_players)
            season_summary['litzendorf_players'] = season_litzendorf
            comprehensive_summary['seasons_processed'][season] = season_summary
            
            save_season_player_data(season, season_players, season_summary)
            
            litz_indicator = f" (🌟 {season_litzendorf} Litzendorf)" if season_litzendorf > 0 else ""
            print(f"  📊 Season {season}: {len(season_players)} total players{litz_indicator}")
        else:
            print(f"  ❌ Season {season}: No data")
        
        time.sleep(random.uniform(2, 4))
    
    # Final comprehensive summary
    if all_player_data:
        comprehensive_summary['total_players'] = len(all_player_data)
        comprehensive_summary['litzendorf_players'] = len([p for p in all_player_data if p.get('is_litzendorf')])
        
        # Stat category breakdown
        for endpoint in stat_endpoints:
            stat_players = [p for p in all_player_data if p.get('stat_type') == endpoint['reqCode']]
            comprehensive_summary['stat_categories'][endpoint['reqCode']] = {
                'name': endpoint['name'],
                'total_players': len(stat_players),
                'litzendorf_players': len([p for p in stat_players if p.get('is_litzendorf')])
            }
        
        save_comprehensive_player_data(all_player_data, comprehensive_summary)
        update_frontend_with_player_data(all_player_data, comprehensive_summary)
    
    print(f"\n🎯 COMPREHENSIVE PLAYER STATS CRAWL COMPLETE!")
    print(f"📊 Total players extracted: {comprehensive_summary['total_players']:,}")
    print(f"🌟 Total Litzendorf players: {comprehensive_summary['litzendorf_players']}")
    print(f"📅 Seasons processed: {list(comprehensive_summary['seasons_processed'].keys())}")
    
    # Final breakdown
    for season, summary in comprehensive_summary['seasons_processed'].items():
        litz_count = summary['litzendorf_players']
        litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
        print(f"  {season}: {summary['total_players']} players{litz_indicator}")

def parse_player_statistics(html_content, config):
    """
    Parse individual player statistics from statistik.do responses
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
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'comprehensive statistik.do crawler',
                    'extracted_at': datetime.now().isoformat(),
                    'raw_data': cell_texts
                }
                
                # Add stat-specific labels with CORRECTED column mapping
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
                    player['primary_stat_label'] = '3PG'  # 3-Pointers Per Game, NOT percentage!
                
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

def save_season_player_data(season, players, summary):
    """Save individual season player data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'comprehensive_players_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'extraction_method': 'comprehensive statistik.do player crawler',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'litzendorf_players': [p for p in players if p.get('is_litzendorf')],
        'season_summary': summary,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Season file: {filename}")

def save_comprehensive_player_data(all_players, summary):
    """Save comprehensive multi-season player dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'comprehensive_players_all_seasons_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'comprehensive statistik.do player crawler',
        'total_players': len(all_players),
        'comprehensive_summary': summary,
        'litzendorf_players': [p for p in all_players if p.get('is_litzendorf')],
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")
    print(f"🌟 Total Litzendorf players: {len(data['litzendorf_players'])}")

def update_frontend_with_player_data(historical_players, summary):
    """Update frontend data with comprehensive historical player statistics"""
    try:
        # Load existing 2018 data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Convert historical player data to frontend format
        frontend_players = []
        for player in historical_players:
            frontend_player = {
                'name': player['full_name'],
                'team': player['team'],
                'season_id': player['season_id'],
                'league': player['league_name'],
                'liga_id': player['liga_id'],
                'stat_category': player['stat_category'],
                'stat_type': player['stat_type'],
                'primary_stat': player.get('primary_stat_value'),
                'primary_stat_label': player.get('primary_stat_label'),
                'endpoint': 'statistik.do_player_stats',
                'source': 'comprehensive_player_crawler',
                'extracted_at': player['extracted_at'],
                'data_type': 'individual_player_statistics'
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
            'source': 'Combined 2018 players + Comprehensive historical player stats',
            'total_records': len(all_data),
            'original_2018_records': len(existing_players),
            'historical_player_records': len(frontend_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'litzendorf_players_total': len([p for p in all_data if p.get('is_litzendorf')]),
            'comprehensive_summary': summary,
            'players': all_data
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data:")
        print(f"   👥 {len(existing_players):,} original 2018 records")
        print(f"   🏀 {len(frontend_players):,} historical player records")
        print(f"   🌟 {updated_data['litzendorf_players_total']} total Litzendorf players")
        print(f"   📅 Coverage: {min(all_seasons)}-{max(all_seasons)} ({len(all_seasons)} seasons)")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_comprehensive_player_stats()
