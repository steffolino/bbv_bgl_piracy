#!/usr/bin/env python3
"""
🧪 TEST SPECIFIC LEAGUE 47955 🧪
Test the known current season league ID
"""

import requests
import json
from datetime import datetime

def test_league_47955():
    """Test the specific league ID 47955"""
    print("🧪 TESTING LEAGUE 47955")
    print("=" * 50)
    
    # Set up session with cookies
    cookies = {
        "__cmpcc": "1",
        "__cmpconsentx47082": "CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA",
        "SESSION": "NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh",
        "_cc_id": "b616c325dc88e1ae505ba80bd46882fe"
    }
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    # Test the specific league
    league_id = 47955
    url = f"https://www.basketball-bund.net/rest/competition/actual/id/{league_id}"
    
    print(f"🔍 Testing URL: {url}")
    print(f"🍪 Using authentication cookies")
    print()
    
    try:
        response = session.get(url, timeout=15)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Extract key information
                league_name = data.get('name', 'Unknown')
                season_info = data.get('season', {})
                season_name = season_info.get('name', 'Unknown') if season_info else 'Unknown'
                
                teams = data.get('teams', [])
                matches = data.get('matches', [])
                table = data.get('table', [])
                
                print("✅ SUCCESS! League data retrieved")
                print("=" * 50)
                print(f"🏀 League: {league_name}")
                print(f"📅 Season: {season_name}")
                print(f"👥 Teams: {len(teams)}")
                print(f"🎯 Matches: {len(matches)}")
                print(f"📊 Table entries: {len(table)}")
                
                # Show team names
                if teams:
                    print("\\n🏀 TEAMS:")
                    for i, team in enumerate(teams[:10], 1):  # Show first 10
                        team_name = team.get('name', 'Unknown')
                        print(f"   {i:2d}. {team_name}")
                    if len(teams) > 10:
                        print(f"   ... and {len(teams) - 10} more teams")
                
                # Show recent matches
                if matches:
                    print("\\n🎯 RECENT MATCHES:")
                    recent_matches = sorted(matches, key=lambda x: x.get('date', ''), reverse=True)[:5]
                    for match in recent_matches:
                        home_team = match.get('homeTeam', {}).get('name', 'Unknown')
                        away_team = match.get('awayTeam', {}).get('name', 'Unknown')
                        date = match.get('date', '')[:10]  # Just the date part
                        home_score = match.get('homeScore', '')
                        away_score = match.get('awayScore', '')
                        status = match.get('status', '')
                        
                        if home_score is not None and away_score is not None:
                            score = f"{home_score}:{away_score}"
                        else:
                            score = "vs"
                        
                        print(f"   📅 {date}: {home_team} {score} {away_team} ({status})")
                
                # Show current standings
                if table:
                    print("\\n📊 CURRENT STANDINGS (Top 5):")
                    for i, entry in enumerate(table[:5], 1):
                        team_name = entry.get('team', {}).get('name', 'Unknown')
                        games = entry.get('matchesPlayed', 0)
                        wins = entry.get('matchesWon', 0)
                        losses = entry.get('matchesLost', 0)
                        points_for = entry.get('pointsFor', 0)
                        points_against = entry.get('pointsAgainst', 0)
                        
                        print(f"   {i:2d}. {team_name:<25} {wins:2d}-{losses:2d} ({games:2d} games) {points_for:4d}:{points_against:4d}")
                
                # Save data for inspection
                filename = f"league_47955_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"\\n💾 Full data saved to: {filename}")
                print("\\n🎉 LEAGUE 47955 IS ACTIVE AND ACCESSIBLE!")
                print("✅ Ready for weekly data updates")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📝 Raw response: {response.text[:500]}...")
                return False
        
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"📝 Response: {response.text[:500]}...")
            return False
    
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def test_wam_data_endpoint():
    """Test the WAM data endpoint with the payload you provided"""
    print("\\n🌐 TESTING WAM DATA ENDPOINT")
    print("=" * 50)
    
    cookies = {
        "__cmpcc": "1",
        "SESSION": "NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh"
    }
    
    payload = {
        "token": 0,
        "verbandIds": [2],
        "gebietIds": ["5_"]
    }
    
    url = "https://www.basketball-bund.net/rest/wam/data"
    
    try:
        response = requests.post(url, json=payload, cookies=cookies, timeout=15)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ WAM endpoint accessible!")
            print(f"📊 Data size: {len(str(data))} characters")
            
            # Try to extract useful information
            if isinstance(data, dict):
                print("🔍 Data structure analysis:")
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"   • {key}: {len(value)} items")
                    else:
                        print(f"   • {key}: {type(value).__name__}")
            
            # Save for inspection
            filename = f"wam_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 WAM data saved to: {filename}")
            return True
        
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏀 CURRENT SEASON DATA VALIDATION")
    print("Testing specific league and endpoints...")
    print()
    
    # Test the specific league
    league_success = test_league_47955()
    
    # Test the WAM endpoint
    wam_success = test_wam_data_endpoint()
    
    print("\\n🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"🏀 League 47955: {'✅' if league_success else '❌'}")
    print(f"🌐 WAM Endpoint: {'✅' if wam_success else '❌'}")
    
    if league_success and wam_success:
        print("\\n🎉 ALL TESTS PASSED!")
        print("🚀 Ready to implement weekly basketball data updates")
        print("💡 Update the current_season_scraper.py with league ID 47955")
    else:
        print("\\n⚠️ Some tests failed - check authentication")
