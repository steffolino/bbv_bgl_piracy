#!/usr/bin/env python3
"""
Extract league IDs and team names from basketball-bund export
Then use these to crawl real player data from the federation API
"""
import re
import requests
import json
from datetime import datetime
import sqlite3

def extract_league_info(file_path):
    """Extract real league IDs and team names from the export"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract league IDs
    league_pattern = r'Liganr\.: (\d+)\)'
    league_ids = re.findall(league_pattern, content)
    
    # Extract league names with IDs
    league_name_pattern = r'(.+?)\s+\(.*?Liganr\.: (\d+)\)'
    league_info = re.findall(league_name_pattern, content)
    
    # Extract team names from matches and tables
    teams = set()
    
    # From match results like "SV Gundelsheim - DJK Don Bosco Bamberg 2 81 : 77"
    match_pattern = r'(\d+)\s+(.+?)\s+-\s+(.+?)\s+(\d+)\s+:\s+(\d+)'
    matches = re.findall(match_pattern, content)
    
    for match in matches:
        home_team = match[1].strip()
        away_team = match[2].strip()
        teams.add(home_team)
        teams.add(away_team)
    
    # From table entries like "1. ATS Kulmbach 0 / 0 / 0 0 0 : 0"
    table_pattern = r'\d+\.\s+([A-Za-z0-9\s\.\-/]+?)\s+\d+\s+/\s+\d+\s+/\s+\d+'
    table_teams = re.findall(table_pattern, content)
    for team in table_teams:
        teams.add(team.strip())
    
    return {
        'league_ids': list(set(league_ids)),
        'league_info': league_info,
        'teams': list(teams)
    }

def crawl_league_data(league_id):
    """Crawl real data from basketball federation API using league ID"""
    base_url = "https://www.basketball-bund.net"
    
    # Try different API endpoints
    endpoints = [
        f"/webservice/proxy.php?action=getMatchesInLeague&ligaID={league_id}",
        f"/webservice/proxy.php?action=getTeamsInLeague&ligaID={league_id}",
        f"/webservice/proxy.php?action=getStandings&ligaID={league_id}",
        f"/liga-spielplan/{league_id}/",
        f"/liga-tabelle/{league_id}/",
        f"/liga-statistiken/{league_id}/"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"🔍 Trying: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Success: {endpoint}")
                
                # Try to parse as JSON first
                try:
                    data = response.json()
                    results[endpoint] = data
                    print(f"   📊 JSON data: {len(str(data))} chars")
                except:
                    # HTML response
                    results[endpoint] = response.text[:500] + "..." if len(response.text) > 500 else response.text
                    print(f"   📄 HTML data: {len(response.text)} chars")
            else:
                print(f"❌ Failed: {endpoint} - Status {response.status_code}")
                
        except Exception as e:
            print(f"💥 Error on {endpoint}: {str(e)}")
    
    return results

def save_real_data(data, output_file):
    """Save the real federation data"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'source': 'basketball-bund.net federation API',
            'data': data
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    file_path = r"c:\Users\StretzS\Downloads\ligaErgExtended (1).txt"
    
    print("🏀 EXTRACTING REAL LEAGUE INFO FROM BASKETBALL-BUND EXPORT")
    print("=" * 60)
    
    # Extract league info from export
    info = extract_league_info(file_path)
    
    print(f"📋 Found {len(info['league_ids'])} League IDs:")
    for i, league_id in enumerate(info['league_ids']):
        print(f"   {i+1:2d}. League ID: {league_id}")
    
    print(f"\n🏟️ Found {len(info['teams'])} Real Teams:")
    for i, team in enumerate(sorted(info['teams'])[:20]):  # Show first 20
        print(f"   {i+1:2d}. {team}")
    if len(info['teams']) > 20:
        print(f"   ... and {len(info['teams']) - 20} more teams")
    
    print(f"\n📊 League Details:")
    for name, league_id in info['league_info']:
        print(f"   • {name.strip()} (ID: {league_id})")
    
    # Now crawl real data using these IDs
    print(f"\n🕷️ CRAWLING REAL DATA FROM BASKETBALL FEDERATION API")
    print("=" * 60)
    
    all_data = {}
    
    # Try a few key leagues first
    key_leagues = info['league_ids'][:5]  # First 5 leagues
    
    for league_id in key_leagues:
        print(f"\n🎯 Crawling League ID: {league_id}")
        league_data = crawl_league_data(league_id)
        if league_data:
            all_data[league_id] = league_data
            print(f"   ✅ Got data from {len(league_data)} endpoints")
        else:
            print(f"   ❌ No data found")
    
    # Save results
    output_file = "real_federation_data.json"
    save_real_data({
        'extracted_info': info,
        'crawled_data': all_data
    }, output_file)
    
    print(f"\n💾 SAVED REAL DATA TO: {output_file}")
    print(f"📊 Total leagues crawled: {len(all_data)}")
    print(f"🏟️ Total teams found: {len(info['teams'])}")
