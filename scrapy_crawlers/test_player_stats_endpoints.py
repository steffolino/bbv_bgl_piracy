#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def test_player_stats_endpoints():
    """
    Test the new player statistics endpoints discovered by user
    These should give us individual player data instead of team standings
    """
    
    print("🏀 TESTING PLAYER STATISTICS ENDPOINTS")
    print("Testing liga_id=250, saison_id=2010")
    
    # The three player stats endpoints
    endpoints = [
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
            'description': 'Top 3-point percentage players'
        }
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_player_data = []
    
    for endpoint in endpoints:
        print(f"\n📊 {endpoint['name']} ({endpoint['reqCode']})")
        print(f"   {endpoint['description']}")
        
        # Build URL
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint['reqCode']}&liga_id=250&saison_id=2010&_top=-1"
        print(f"   🔗 {url}")
        
        try:
            response = session.get(url, timeout=30)
            print(f"   📥 Status: {response.status_code}")
            print(f"   📏 Size: {len(response.text):,} chars")
            
            if response.status_code == 200:
                # Quick content check
                if 'Keine Einträge gefunden' in response.text:
                    print("   ❌ No entries found")
                elif len(response.text) < 5000:
                    print("   ⚠️  Small response - might be empty")
                else:
                    print("   ✅ Substantial content found")
                    
                    # Save raw response for analysis
                    filename = f"player_stats_{endpoint['reqCode']}_250_2010.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"   💾 Saved: {filename}")
                    
                    # Try to parse players
                    players = parse_player_stats(response.text, endpoint, 250, 2010)
                    if players:
                        print(f"   🏀 Found {len(players)} players!")
                        
                        # Show sample players
                        for i, player in enumerate(players[:3]):
                            name = player.get('name', 'Unknown')
                            team = player.get('team', 'Unknown')
                            stat = player.get('primary_stat', 'N/A')
                            print(f"      {i+1}. {name} ({team}) - {stat}")
                        
                        if len(players) > 3:
                            print(f"      ... and {len(players)-3} more")
                        
                        all_player_data.extend(players)
                        
                        # Check for Litzendorf players
                        litzendorf_players = [p for p in players if 'litzendorf' in str(p.get('team', '')).lower()]
                        if litzendorf_players:
                            print(f"   🌟 {len(litzendorf_players)} Litzendorf players found!")
                            for lp in litzendorf_players:
                                print(f"      🏆 {lp.get('name')} - {lp.get('primary_stat')}")
                    else:
                        print("   ❌ No players parsed")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        time.sleep(2)  # Rate limiting
    
    # Summary
    print(f"\n🎯 PLAYER STATS TEST COMPLETE")
    print(f"📊 Total players found: {len(all_player_data)}")
    
    if all_player_data:
        # Save combined results
        save_player_stats_data(all_player_data, endpoints)
        
        # Show breakdown by endpoint
        for endpoint in endpoints:
            endpoint_players = [p for p in all_player_data if p.get('stat_type') == endpoint['reqCode']]
            litz_count = len([p for p in endpoint_players if 'litzendorf' in str(p.get('team', '')).lower()])
            litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
            print(f"  {endpoint['name']}: {len(endpoint_players)} players{litz_indicator}")
    
    return all_player_data

def parse_player_stats(html_content, endpoint, liga_id, season):
    """
    Parse individual player statistics from basketball-bund.net stats pages
    """
    
    players = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for tables with player data
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        # Look for sportItem cells (same pattern as team data)
        sport_item_cells = table.find_all('td', class_=lambda x: x and 'sportItem' in x)
        
        if not sport_item_cells:
            continue
        
        # Process rows
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            row_cells = row.find_all('td', class_=lambda x: x and 'sportItem' in x)
            
            if len(row_cells) < 3:  # Need at least rank, name, team
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in row_cells]
            
            # Basic player data structure
            if len(cell_texts) >= 3:
                player = {
                    'rank': cell_texts[0] if len(cell_texts) > 0 else '',
                    'name': cell_texts[1] if len(cell_texts) > 1 else '',
                    'team': cell_texts[2] if len(cell_texts) > 2 else '',
                    'season_id': season,
                    'liga_id': str(liga_id),
                    'stat_type': endpoint['reqCode'],
                    'stat_category': endpoint['name'],
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'statistik.do player stats',
                    'extracted_at': datetime.now().isoformat(),
                    'raw_data': cell_texts
                }
                
                # Extract primary statistic (usually in 4th column)
                if len(cell_texts) > 3:
                    player['primary_stat'] = cell_texts[3]
                
                # Extract additional stats
                if len(cell_texts) > 4:
                    player['secondary_stat'] = cell_texts[4]
                if len(cell_texts) > 5:
                    player['games_played'] = cell_texts[5]
                
                # Check for Litzendorf
                if 'litzendorf' in player['team'].lower():
                    player['is_litzendorf'] = True
                
                # Skip empty names
                if player['name'] and len(player['name']) > 1 and not player['name'].isdigit():
                    players.append(player)
    
    return players

def save_player_stats_data(players, endpoints):
    """Save player statistics data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'player_stats_liga250_2010_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'statistik.do player statistics',
        'liga_id': '250',
        'season_id': 2010,
        'endpoints_tested': endpoints,
        'total_players': len(players),
        'litzendorf_players': [p for p in players if p.get('is_litzendorf')],
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Player stats saved: {filename}")
    print(f"🌟 Litzendorf players: {len(data['litzendorf_players'])}")

if __name__ == "__main__":
    test_player_stats_endpoints()
