#!/usr/bin/env python3
"""
🏀 VENUE & CONTACT DATA SCRAPER 🏀
Extract REAL venue addresses and team contacts from BBV Oberfranken

Sources:
- https://ofr.bbv-online.de/Hallen.htm (venue addresses)
- https://ofr.bbv-online.de/Spielbetrieb.htm (team contacts & leagues)
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import sqlite3

def scrape_venues():
    """Extract venue data from Hallen.htm"""
    print("🏛️ Scraping venue data...")
    
    url = "https://ofr.bbv-online.de/Hallen.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    venues = []
    
    # Find all venue entries
    # Pattern: [CODE] Venue Name, Street, Postal Code City
    venue_pattern = r'\[([A-Z\-0-9]+)\]\s*([^,]+),\s*([^,]+),\s*(\d{5})\s*([^,\n]+)'
    
    # Extract text content
    text = soup.get_text()
    
    for match in re.finditer(venue_pattern, text):
        code, name, street, postal, city = match.groups()
        
        # Clean up venue name
        name = name.strip()
        street = street.strip()
        city = city.strip()
        
        venue = {
            'code': code,
            'name': name,
            'street': street,
            'postal_code': postal,
            'city': city,
            'full_address': f"{street}, {postal} {city}",
            'google_maps_url': f"http://maps.google.de/maps?f=q&hl=de&geocode=&q={street},{postal}%20{city}".replace(' ', '%20')
        }
        
        venues.append(venue)
        print(f"  📍 {code}: {name} in {city}")
    
    print(f"✅ Found {len(venues)} venues")
    return venues

def scrape_team_contacts():
    """Extract team contact data from Spielbetrieb.htm"""
    print("📞 Scraping team contacts...")
    
    url = "https://ofr.bbv-online.de/Spielbetrieb.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    teams = []
    
    # Extract text content
    text = soup.get_text()
    
    # Pattern for team entries:
    # LIGA Team Name Contact Name email phone
    team_pattern = r'([A-Z0-9]+)\s+([^A-Z\n]+?)\s+([A-Z][a-zA-Z\s]+?)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s+([\d\s,/+()-]+)'
    
    current_league = None
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        
        # Detect league headers
        if line in ['BOH', 'BLH', 'BLDA', 'BODA', 'BLDB', 'BODB', 'BKH', 'KLHA', 'KLHB', 'BPH', 'BPD', 'U20M', 'U18MA', 'U18MB', 'U18WA']:
            current_league = line
            continue
        
        # Try to extract team data
        # Simplified pattern for team entries
        parts = line.split()
        if len(parts) >= 4 and '@' in line:
            # Find email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
            if email_match:
                email = email_match.group(1)
                
                # Extract team name (before contact name)
                email_pos = line.find(email)
                before_email = line[:email_pos].strip()
                
                # Split to get team and contact
                parts_before = before_email.split()
                if len(parts_before) >= 2:
                    # Team is usually the first few words
                    team_name = ' '.join(parts_before[:-2]) if len(parts_before) > 2 else parts_before[0]
                    contact_name = ' '.join(parts_before[-2:]) if len(parts_before) > 1 else ""
                    
                    # Extract phone after email
                    after_email = line[email_pos + len(email):].strip()
                    phone = after_email.split()[0] if after_email else ""
                    
                    team = {
                        'league': current_league,
                        'team_name': team_name.strip(),
                        'contact_name': contact_name.strip(),
                        'email': email,
                        'phone': phone,
                        'season': '2025/26'
                    }
                    
                    teams.append(team)
                    print(f"  🏀 {current_league}: {team_name} ({contact_name})")
    
    print(f"✅ Found {len(teams)} team contacts")
    return teams

def save_venue_data(venues, teams):
    """Save venue and team data to database and files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to JSON files
    venues_file = f"oberfranken_venues_{timestamp}.json"
    teams_file = f"oberfranken_teams_{timestamp}.json"
    
    with open(venues_file, 'w', encoding='utf-8') as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)
    
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(venues)} venues to {venues_file}")
    print(f"💾 Saved {len(teams)} teams to {teams_file}")
    
    # Try to save to database
    try:
        db_path = "../league_cache.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create venues table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                id TEXT PRIMARY KEY,
                code TEXT UNIQUE,
                name TEXT,
                street TEXT,
                postal_code TEXT,
                city TEXT,
                full_address TEXT,
                google_maps_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create team_contacts table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_contacts (
                id TEXT PRIMARY KEY,
                league TEXT,
                team_name TEXT,
                contact_name TEXT,
                email TEXT,
                phone TEXT,
                season TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert venues
        for venue in venues:
            venue_id = f"venue_{venue['code'].lower()}"
            cursor.execute("""
                INSERT OR REPLACE INTO venues 
                (id, code, name, street, postal_code, city, full_address, google_maps_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                venue_id, venue['code'], venue['name'], venue['street'],
                venue['postal_code'], venue['city'], venue['full_address'],
                venue['google_maps_url']
            ))
        
        # Insert team contacts
        for team in teams:
            team_id = f"contact_{team['league']}_{team['team_name'].lower().replace(' ', '_')}"
            cursor.execute("""
                INSERT OR REPLACE INTO team_contacts 
                (id, league, team_name, contact_name, email, phone, season)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id, team['league'], team['team_name'], team['contact_name'],
                team['email'], team['phone'], team['season']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved to database: {len(venues)} venues, {len(teams)} team contacts")
        
    except Exception as e:
        print(f"⚠️ Database save failed: {e}")
    
    return venues_file, teams_file

def analyze_venue_coverage():
    """Analyze which teams have venue data"""
    print("\\n📊 VENUE COVERAGE ANALYSIS")
    print("=" * 50)
    
    # Key venues for major teams
    major_venues = {
        'BA-AR': 'Brose Arena Bamberg - BBC Bayreuth home venue',
        'BT-OH': 'Oberfrankenhalle - Major Bayreuth venue',
        'LIT-VS': 'Litzendorf School - BG Litzendorf',
        'STR-BCH': 'Basketball Center Hauptsmoor - Strullendorf',
        'CO-HUK': 'HUK Coburg Arena - BBC Coburg',
        'HIR-RA': 'Regnitzarena - Hirschaid venue'
    }
    
    for code, description in major_venues.items():
        print(f"🏟️ {code}: {description}")
    
    print("\\n🎯 This data enables:")
    print("- Venue directory with addresses")
    print("- Team contact management")
    print("- Google Maps integration")
    print("- League structure analysis")
    print("- Contact database for admin")

def main():
    """Main scraper function"""
    print("🏀 BBV OBERFRANKEN DATA SCRAPER")
    print("=" * 50)
    print("Extracting REAL venue and contact data...")
    print()
    
    # Scrape data
    venues = scrape_venues()
    teams = scrape_team_contacts()
    
    # Save data
    venues_file, teams_file = save_venue_data(venues, teams)
    
    # Analysis
    analyze_venue_coverage()
    
    print("\\n🎉 SCRAPING COMPLETE!")
    print("=" * 50)
    print(f"📍 Venues: {len(venues)} locations with full addresses")
    print(f"📞 Teams: {len(teams)} contacts across all leagues")
    print(f"💾 Files: {venues_file}, {teams_file}")
    print("\\n🚀 Ready to enhance Vereine system with real venue data!")

if __name__ == "__main__":
    main()
