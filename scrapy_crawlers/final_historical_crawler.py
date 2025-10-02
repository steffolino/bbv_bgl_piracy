#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

def crawl_historical_team_data():
    """
    Final working historical crawler using corrected parser
    Extracts team standings data from Action=107 league pages
    """
    
    print("🏀 HISTORICAL TEAM DATA CRAWLER")
    print("Using known liga_ids to extract team standings across seasons")
    
    # Known liga_ids from your 2010 Oberfranken example
    known_liga_ids = [
        {'liga_id': '3340', 'name': 'Senioren Ü45'},
        {'liga_id': '263', 'name': 'Senioren Ü40 (männlich)'},
        {'liga_id': '8025', 'name': 'Senioreninnen Ü40'},
        {'liga_id': '261', 'name': 'Senioren Ü35'},
        {'liga_id': '1701', 'name': 'Bezirksliga Herren'},
        {'liga_id': '256', 'name': 'Bezirkspokal Herren'},
        {'liga_id': '248', 'name': 'Bezirksliga Damen A'},
        {'liga_id': '2659', 'name': 'Bezirksliga Damen B'},
        {'liga_id': '6964', 'name': 'Bezirksliga Damen Meisterschaft'},
        {'liga_id': '697', 'name': 'Bezirkspokal Damen'}
    ]
    
    # Target seasons
    target_seasons = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_team_data = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        season_teams = []
        working_leagues = []
        
        for liga_info in known_liga_ids:
            liga_id = liga_info['liga_id']
            league_name = liga_info['name']
            
            print(f"  🏀 {league_name} (ID: {liga_id})")
            
            # Direct Action=107 URL
            url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season}'
            
            teams = crawl_league_teams(session, url, liga_id, league_name, season)
            if teams:
                season_teams.extend(teams)
                working_leagues.append(liga_info)
                
                # Check for Litzendorf teams
                litzendorf_teams = [t for t in teams if 'litzendorf' in t['team'].lower()]
                if litzendorf_teams:
                    print(f"    ✅ {len(teams)} teams (🌟 {len(litzendorf_teams)} Litzendorf)")
                    for lt in litzendorf_teams:
                        print(f"      🏆 {lt['team']} - Rank {lt['rank']}, {lt.get('points', 'N/A')} pts")
                else:
                    print(f"    ✅ {len(teams)} teams")
            else:
                print(f"    ❌ No teams")
            
            # Rate limiting
            time.sleep(random.uniform(1, 2))
        
        # Save season results
        if season_teams:
            all_team_data.extend(season_teams)
            season_summary[season] = {
                'total_teams': len(season_teams),
                'working_leagues': len(working_leagues),
                'league_names': [lg['name'] for lg in working_leagues],
                'litzendorf_teams': len([t for t in season_teams if 'litzendorf' in t['team'].lower()])
            }
            
            save_season_data(season, season_teams, working_leagues)
            print(f"  📊 Season {season}: {len(season_teams)} teams from {len(working_leagues)} leagues")
        else:
            print(f"  ❌ Season {season}: No data found")
        
        time.sleep(random.uniform(2, 3))
    
    # Save comprehensive results
    if all_team_data:
        save_comprehensive_data(all_team_data, season_summary)
        update_frontend_data(all_team_data, list(season_summary.keys()))
    
    print(f"\n🎯 HISTORICAL TEAM DATA CRAWL COMPLETE!")
    print(f"📊 Total teams: {len(all_team_data)}")
    print(f"📅 Successful seasons: {list(season_summary.keys())}")
    
    # Summary by season
    for season, summary in season_summary.items():
        litz_count = summary['litzendorf_teams']
        litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
        print(f"  {season}: {summary['total_teams']} teams, {summary['working_leagues']} leagues{litz_indicator}")

def crawl_league_teams(session, url, liga_id, league_name, season):
    """
    Crawl team standings from Action=107 league page
    """
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        # Quick check for meaningful content
        if len(response.text) < 10000:
            return []
        
        # Parse teams from response
        soup = BeautifulSoup(response.text, 'html.parser')
        teams = extract_teams_from_action_107(soup, liga_id, league_name, season)
        
        return teams
        
    except Exception as e:
        print(f"      💥 Error: {str(e)[:50]}")
        return []

def extract_teams_from_action_107(soup, liga_id, league_name, season):
    """
    Extract team standings data from Action=107 page using corrected parser
    """
    
    teams = []
    
    # Look for tables with sportItem cells
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        # Find cells with sportItem class
        sport_item_cells = table.find_all('td', class_=re.compile(r'sportItem'))
        
        if not sport_item_cells:
            continue
        
        # Group cells by rows to extract team data
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            row_cells = row.find_all('td', class_=re.compile(r'sportItem'))
            
            if len(row_cells) < 3:  # Need at least rank, name, some stats
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in row_cells]
            
            # Check if this looks like team data
            if len(cell_texts) >= 2 and cell_texts[1]:  # Has team name
                
                team = {
                    'rank': cell_texts[0] if len(cell_texts) > 0 else '',
                    'team': cell_texts[1] if len(cell_texts) > 1 else '',
                    'season_id': season,
                    'liga_id': str(liga_id),
                    'league_name': league_name,
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'Action=107 Team Standings',
                    'extracted_at': datetime.now().isoformat(),
                    'raw_data': cell_texts
                }
                
                # Extract games and points if available
                for i, value in enumerate(cell_texts[2:], 2):
                    if value and value.isdigit():
                        if 'games' not in team and i >= 3:
                            team['games'] = int(value)
                        elif 'points' not in team and i >= 4:
                            team['points'] = int(value)
                
                # Extract additional stats
                if len(cell_texts) > 5:
                    team['score_ratio'] = cell_texts[5] if len(cell_texts) > 5 else ''
                if len(cell_texts) > 6:
                    team['score_diff'] = cell_texts[6] if len(cell_texts) > 6 else ''
                
                # Check for Litzendorf
                if 'litzendorf' in team['team'].lower():
                    team['is_litzendorf'] = True
                    team['team_type'] = 'BG Litzendorf'
                
                # Skip empty team names or just numbers
                if (team['team'] and 
                    len(team['team']) > 1 and 
                    not team['team'].isdigit()):
                    
                    teams.append(team)
    
    return teams

def save_season_data(season, teams, working_leagues):
    """Save individual season team data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'historical_teams_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'method': 'Action=107 Team Standings',
        'timestamp': datetime.now().isoformat(),
        'total_teams': len(teams),
        'working_leagues': working_leagues,
        'litzendorf_teams': [t for t in teams if t.get('is_litzendorf')],
        'teams': teams
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_data(all_teams, season_summary):
    """Save comprehensive multi-season team dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'historical_teams_comprehensive_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Historical Action=107 Team Standings',
        'total_teams': len(all_teams),
        'seasons_crawled': list(season_summary.keys()),
        'season_summary': season_summary,
        'litzendorf_teams': [t for t in all_teams if t.get('is_litzendorf')],
        'teams': all_teams
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")
    print(f"🌟 Litzendorf teams found: {len(data['litzendorf_teams'])}")

def update_frontend_data(historical_teams, historical_seasons):
    """Update frontend data with historical team data"""
    try:
        # Load existing 2018 data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Convert team data to frontend format (treating teams as "players" for now)
        frontend_teams = []
        for team in historical_teams:
            frontend_team = {
                'name': team['team'],
                'team': team['team'],  # Same as name for teams
                'season_id': team['season_id'],
                'league': team['league_name'],
                'liga_id': team['liga_id'],
                'endpoint': 'Action=107_teams',
                'source': 'historical_team_standings',
                'extracted_at': team['extracted_at'],
                'rank': team.get('rank'),
                'games': team.get('games'),
                'points': team.get('points'),
                'data_type': 'team_standing'
            }
            
            # Add Litzendorf flag
            if team.get('is_litzendorf'):
                frontend_team['is_litzendorf'] = True
            
            frontend_teams.append(frontend_team)
        
        # Combine datasets
        all_data = existing_players + frontend_teams
        all_seasons = sorted(list(set([2018] + historical_seasons)))
        
        # Update frontend file
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 players + Historical team standings',
            'total_records': len(all_data),
            'player_records': len(existing_players),
            'team_records': len(frontend_teams),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'players': all_data  # Keeping same field name for compatibility
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data:")
        print(f"   👥 {len(existing_players):,} player records (2018)")
        print(f"   🏀 {len(frontend_teams):,} team records (historical)")
        print(f"   📅 Coverage: {min(all_seasons)}-{max(all_seasons)} ({len(all_seasons)} seasons)")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_historical_team_data()
