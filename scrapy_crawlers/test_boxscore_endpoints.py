import requests
import json
import time
from urllib.parse import urljoin

def test_boxscore_endpoints():
    """Test various basketball-bund.net endpoints for player statistics"""
    
    base_url = "https://www.basketball-bund.net"
    
    # Sample match IDs from our database
    test_match_ids = [2738771, 2738776, 2733859, 2738765, 2738778]
    test_league_id = 49749  # From our database
    
    print("=== TESTING BASKETBALL-BUND.NET BOXSCORE ENDPOINTS ===")
    print()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8'
    }
    
    # Test different potential endpoints
    endpoint_patterns = [
        "/games/{match_id}/boxscore",
        "/games/{match_id}/statistics", 
        "/games/{match_id}/players",
        "/matches/{match_id}/boxscore",
        "/matches/{match_id}/statistics",
        "/api/games/{match_id}/boxscore",
        "/api/matches/{match_id}/statistics",
        "/leagues/{league_id}/statistics"
    ]
    
    for pattern in endpoint_patterns:
        print(f"Testing pattern: {pattern}")
        
        if "{match_id}" in pattern:
            # Test with first match ID
            test_id = test_match_ids[0]
            url = base_url + pattern.format(match_id=test_id)
        elif "{league_id}" in pattern:
            url = base_url + pattern.format(league_id=test_league_id)
        else:
            continue
            
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"  Content-Type: {content_type}")
                print(f"  Content Length: {len(response.text)}")
                
                # Check if response contains player data indicators
                text = response.text.lower()
                player_indicators = ['player', 'spieler', 'punkte', 'rebounds', 'assists', 'boxscore']
                found_indicators = [ind for ind in player_indicators if ind in text]
                
                if found_indicators:
                    print(f"  🎯 FOUND PLAYER DATA INDICATORS: {found_indicators}")
                    
                    # Save sample for analysis
                    with open(f'boxscore_sample_{test_id}.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"  💾 Saved sample to boxscore_sample_{test_id}.html")
                else:
                    print(f"  ❌ No player data indicators found")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        print()
        time.sleep(1)  # Be nice to the server
    
    print("=== CONCLUSION ===")
    print("Need to check if individual match pages have embedded player statistics")
    print("or if there are different URL patterns for accessing boxscore data")

if __name__ == "__main__":
    test_boxscore_endpoints()
