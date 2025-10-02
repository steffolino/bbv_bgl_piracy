#!/usr/bin/env python3
"""
🔍 EXTRACT CURRENT LEAGUE IDS 🔍
Extract all current Oberfranken league IDs from WAM data
"""

import json

def extract_current_leagues():
    """Extract current season league IDs"""
    print("🔍 EXTRACTING CURRENT LEAGUE IDS")
    print("=" * 50)
    
    # Load the WAM data
    with open('wam_data_20251002_175441.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract leagues from ligaListe data
    liga_liste = data.get('data', {}).get('ligaListe', {})
    ligen = liga_liste.get('ligen', [])
    
    oberfranken_leagues = []
    
    for comp in ligen:
        bezirk_name = comp.get('bezirkName', '')
        if bezirk_name == 'Oberfranken':
            league_info = {
                'ligaId': comp.get('ligaId'),
                'liganame': comp.get('liganame', ''),
                'skName': comp.get('skName', ''),
                'geschlecht': comp.get('geschlecht', ''),
                'akName': comp.get('akName', ''),
                'seasonName': comp.get('seasonName', ''),
                'vorabliga': comp.get('vorabliga', False)
            }
            
            # Filter out preparation leagues
            if not league_info['vorabliga'] and league_info['ligaId']:
                oberfranken_leagues.append(league_info)
    
    # Sort by league ID
    oberfranken_leagues.sort(key=lambda x: x['ligaId'])
    
    print(f"✅ Found {len(oberfranken_leagues)} active Oberfranken leagues")
    print()
    
    # Display leagues
    print("🏀 CURRENT OBERFRANKEN LEAGUES (2025/26):")
    print("-" * 80)
    print(f"{'ID':<8} {'League Name':<35} {'Level':<15} {'Gender':<10}")
    print("-" * 80)
    
    for league in oberfranken_leagues:
        liga_id = league['ligaId']
        name = league['liganame'][:34]
        level = league['skName'][:14]
        gender = league['geschlecht'][:9]
        
        print(f"{liga_id:<8} {name:<35} {level:<15} {gender:<10}")
    
    # Extract just the IDs for the scraper
    league_ids = [league['ligaId'] for league in oberfranken_leagues]
    
    print()
    print("🎯 LEAGUE IDS FOR SCRAPER:")
    print(f"current_leagues = {league_ids}")
    
    # Save to file
    output = {
        'extraction_date': '2025-10-02',
        'source': 'WAM API Oberfranken',
        'total_leagues': len(oberfranken_leagues),
        'league_ids': league_ids,
        'detailed_leagues': oberfranken_leagues
    }
    
    with open('current_oberfranken_leagues_2025.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Detailed data saved to: current_oberfranken_leagues_2025.json")
    
    # Show some highlights
    men_leagues = [l for l in oberfranken_leagues if l['geschlecht'] == 'männlich']
    women_leagues = [l for l in oberfranken_leagues if l['geschlecht'] == 'weiblich']
    
    print()
    print("📊 LEAGUE BREAKDOWN:")
    print(f"   👨 Men's leagues: {len(men_leagues)}")
    print(f"   👩 Women's leagues: {len(women_leagues)}")
    
    # Show top levels
    bezirksoberliga = [l for l in oberfranken_leagues if 'Bezirksoberliga' in l['skName']]
    bezirksliga = [l for l in oberfranken_leagues if 'Bezirksliga' in l['skName']]
    kreisliga = [l for l in oberfranken_leagues if 'Kreisliga' in l['skName']]
    
    print(f"   🏆 Bezirksoberliga: {len(bezirksoberliga)}")
    print(f"   🥈 Bezirksliga: {len(bezirksliga)}")  
    print(f"   🥉 Kreisliga: {len(kreisliga)}")
    
    return league_ids

if __name__ == "__main__":
    league_ids = extract_current_leagues()
    
    print()
    print("🚀 READY FOR CURRENT SEASON SCRAPING!")
    print("Update current_season_scraper.py with these league IDs")
