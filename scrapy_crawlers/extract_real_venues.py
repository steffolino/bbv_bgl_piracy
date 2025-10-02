#!/usr/bin/env python3
"""
🏀 MANUAL VENUE & CONTACT EXTRACTOR 🏀
Extract venue and contact data from the fetched content
"""

import json
from datetime import datetime

def extract_venues():
    """Manually extract venues from the known data"""
    venues = [
        {
            'code': 'STE-ARH',
            'name': 'Adam Riese Halle',
            'street': 'St.-Georg-Str.',
            'postal_code': '96231',
            'city': 'Bad Staffelstein',
            'full_address': 'St.-Georg-Str., 96231 Bad Staffelstein'
        },
        {
            'code': 'BA-AR',
            'name': 'Brose Arena Bamberg',
            'street': 'Forchheimer Str. 15',
            'postal_code': '96050',
            'city': 'Bamberg',
            'full_address': 'Forchheimer Str. 15, 96050 Bamberg'
        },
        {
            'code': 'BA-DG',
            'name': 'Dientzenhofer-Gymnasium',
            'street': 'Feldkirchenstr. 22',
            'postal_code': '96052',
            'city': 'Bamberg',
            'full_address': 'Feldkirchenstr. 22, 96052 Bamberg'
        },
        {
            'code': 'BA-EG',
            'name': 'Eichendorff-Gymnasium',
            'street': 'Kloster-Langheim-Str. 10',
            'postal_code': '96050',
            'city': 'Bamberg',
            'full_address': 'Kloster-Langheim-Str. 10, 96050 Bamberg'
        },
        {
            'code': 'BA-ETA',
            'name': 'ETA-Hoffmann-Gymnasium',
            'street': 'Sternwartstr. 3',
            'postal_code': '96049',
            'city': 'Bamberg',
            'full_address': 'Sternwartstr. 3, 96049 Bamberg'
        },
        {
            'code': 'BA-FLG',
            'name': 'Franz-Ludwig-Gymnasium',
            'street': 'Franz-Ludwig-Str. 13',
            'postal_code': '96047',
            'city': 'Bamberg',
            'full_address': 'Franz-Ludwig-Str. 13, 96047 Bamberg'
        },
        {
            'code': 'BA-GEO',
            'name': 'Dreifachhalle am Georgendamm',
            'street': 'Georgendamm 2',
            'postal_code': '96047',
            'city': 'Bamberg',
            'full_address': 'Georgendamm 2, 96047 Bamberg'
        },
        {
            'code': 'BT-AS',
            'name': 'Altstadtschule',
            'street': 'Fantaisiestr. 11',
            'postal_code': '95445',
            'city': 'Bayreuth',
            'full_address': 'Fantaisiestr. 11, 95445 Bayreuth'
        },
        {
            'code': 'BT-OH',
            'name': 'Oberfrankenhalle',
            'street': 'Am Sportpark 1',
            'postal_code': '95448',
            'city': 'Bayreuth',
            'full_address': 'Am Sportpark 1, 95448 Bayreuth'
        },
        {
            'code': 'BT-SZ',
            'name': 'Sportzentrum',
            'street': 'Am Sportpark 3',
            'postal_code': '95448',
            'city': 'Bayreuth',
            'full_address': 'Am Sportpark 3, 95448 Bayreuth'
        },
        {
            'code': 'BIN-BH',
            'name': 'Bärenhalle',
            'street': 'Hirtenackerstr. 47',
            'postal_code': '95463',
            'city': 'Bindlach',
            'full_address': 'Hirtenackerstr. 47, 95463 Bindlach'
        },
        {
            'code': 'CO-ANG',
            'name': 'Angerhalle',
            'street': 'Karchestr. 4',
            'postal_code': '96450',
            'city': 'Coburg',
            'full_address': 'Karchestr. 4, 96450 Coburg'
        },
        {
            'code': 'CO-HUK',
            'name': 'HUK Coburg Arena',
            'street': 'Oudenaarder Str. 1',
            'postal_code': '96450',
            'city': 'Coburg',
            'full_address': 'Oudenaarder Str. 1, 96450 Coburg'
        },
        {
            'code': 'CO-PS',
            'name': 'Pestalozzi-Sporthalle',
            'street': 'Seidmannsdorfer Str. 74',
            'postal_code': '96450',
            'city': 'Coburg',
            'full_address': 'Seidmannsdorfer Str. 74, 96450 Coburg'
        },
        {
            'code': 'EBS-SH',
            'name': 'Stadthalle',
            'street': 'Georg-Wagner-Str. 14',
            'postal_code': '91320',
            'city': 'Ebermannstadt',
            'full_address': 'Georg-Wagner-Str. 14, 91320 Ebermannstadt'
        },
        {
            'code': 'FO-HER',
            'name': 'Herderhalle',
            'street': 'Ruhalmstraße',
            'postal_code': '91301',
            'city': 'Forchheim',
            'full_address': 'Ruhalmstraße, 91301 Forchheim'
        },
        {
            'code': 'HIR-RA',
            'name': 'Regnitzarena',
            'street': 'Georg-Kügel-Ring 3',
            'postal_code': '96114',
            'city': 'Hirschaid',
            'full_address': 'Georg-Kügel-Ring 3, 96114 Hirschaid'
        },
        {
            'code': 'HO-JH',
            'name': 'Jahnhalle',
            'street': 'Jahnstr. 5',
            'postal_code': '95030',
            'city': 'Hof',
            'full_address': 'Jahnstr. 5, 95030 Hof'
        },
        {
            'code': 'KC-SZ',
            'name': 'Dreifachturnhalle Schulzentrum',
            'street': 'Am Schulzentrum',
            'postal_code': '96317',
            'city': 'Kronach',
            'full_address': 'Am Schulzentrum, 96317 Kronach'
        },
        {
            'code': 'KU-CVG',
            'name': 'Caspar-Vischer-Gymnasium',
            'street': 'Christian-Pertsch-Str.',
            'postal_code': '95326',
            'city': 'Kulmbach',
            'full_address': 'Christian-Pertsch-Str., 95326 Kulmbach'
        },
        {
            'code': 'LIF-SZ',
            'name': 'Sportzentrum',
            'street': 'An der Friedenslinde',
            'postal_code': '96215',
            'city': 'Lichtenfels',
            'full_address': 'An der Friedenslinde, 96215 Lichtenfels'
        },
        {
            'code': 'LIT-GMS',
            'name': 'Grund- und Mittelschule Litzendorf',
            'street': 'Schulstr. 2',
            'postal_code': '96123',
            'city': 'Litzendorf',
            'full_address': 'Schulstr. 2, 96123 Litzendorf'
        },
        {
            'code': 'MEM-SH',
            'name': 'Seehofhalle',
            'street': 'Pödeldorfer Str. 20a',
            'postal_code': '96117',
            'city': 'Memmelsdorf',
            'full_address': 'Pödeldorfer Str. 20a, 96117 Memmelsdorf'
        },
        {
            'code': 'STR-BCH',
            'name': 'Basketball Center Hauptsmoor',
            'street': 'Hauptsmoorstr. 2',
            'postal_code': '96129',
            'city': 'Strullendorf',
            'full_address': 'Hauptsmoorstr. 2, 96129 Strullendorf'
        }
    ]
    
    # Add Google Maps URLs
    for venue in venues:
        venue['google_maps_url'] = f"https://maps.google.com/maps?q={venue['full_address'].replace(' ', '+')}"
    
    return venues

def extract_teams():
    """Manually extract current team data"""
    teams = [
        {
            'league': 'BOH',
            'team_name': '1. FC Baunach 2',
            'contact_name': 'Claus Meixner',
            'email': 'claus.meixner@freenet.de',
            'phone': '0175 4068543',
            'season': '2025/26'
        },
        {
            'league': 'BOH',
            'team_name': 'ATS Kulmbach',
            'contact_name': 'Tim Koths',
            'email': 'tim@kulmbach-basketball.de',
            'phone': '0151 15844897',
            'season': '2025/26'
        },
        {
            'league': 'BOH',
            'team_name': 'Bischberg Baskets',
            'contact_name': 'Moritz Biedermann',
            'email': 'moe-biedermann@gmx.de',
            'phone': '0163 6805483',
            'season': '2025/26'
        },
        {
            'league': 'BOH',
            'team_name': 'BSC Saas Bayreuth',
            'contact_name': 'Martin Schmidt',
            'email': 'schmidt.martin@gmail.com',
            'phone': '0176 47040526',
            'season': '2025/26'
        },
        {
            'league': 'BOH',
            'team_name': 'DJK Don Bosco Bamberg',
            'contact_name': 'DJK-Trainer H1',
            'email': 'H1.2526@DJK-Bamberg.de',
            'phone': '0951 9329568',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'BBC Bayreuth 3',
            'contact_name': 'Lukas Schultze',
            'email': 'lukas.schultze@young-heroes.de',
            'phone': '0178 2309158',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'BBC Coburg 2',
            'contact_name': 'Simon Hägele',
            'email': 'simon.haegele@bbc-coburg.com',
            'phone': '0176 84542633',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'BG Litzendorf',
            'contact_name': 'Florian Schmidt',
            'email': 'florian.4ontour@t-online.de',
            'phone': '0151 51330535',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'RSC Oberhaid',
            'contact_name': 'Dominik Christa',
            'email': 'dominikchrista@web.de',
            'phone': '09503 8769',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'SG TSG/Post SV Bamberg',
            'contact_name': 'Christian Lother',
            'email': 'djcee@vodafonemail.de',
            'phone': '0179 7039208',
            'season': '2025/26'
        },
        {
            'league': 'BLH',
            'team_name': 'SV Pettstadt 2',
            'contact_name': 'Nicat Nagiyev',
            'email': 'nicat.nagiyev@gmail.com',
            'phone': '0151 40380120',
            'season': '2025/26'
        },
        {
            'league': 'BODA',
            'team_name': 'SpVgg Rattelsdorf',
            'contact_name': 'Marco Dorsch',
            'email': 'dorsch.marco@hotmail.com',
            'phone': '0151 70614989',
            'season': '2025/26'
        },
        {
            'league': 'BODA',
            'team_name': 'SC Kemmern',
            'contact_name': 'Manuel Theobald',
            'email': 'manueltheobald84@gmail.com',
            'phone': '0173 92144335',
            'season': '2025/26'
        },
        {
            'league': 'BODA',
            'team_name': 'TSV Ludwigsstadt',
            'contact_name': 'Johanna Messer',
            'email': 'messerjohanna@gmail.com',
            'phone': '0151 56789123',
            'season': '2025/26'
        },
        {
            'league': 'BODB',
            'team_name': 'BBC Coburg',
            'contact_name': 'Christiane Stark',
            'email': 'christiane.stark@bbc-coburg.com',
            'phone': '09561 3548430',
            'season': '2025/26'
        },
        {
            'league': 'BODB',
            'team_name': 'MSG Kronach/Küps/Weismain',
            'contact_name': 'Meinhard Madinger',
            'email': 'm.madinger@web.de',
            'phone': '09261 2173',
            'season': '2025/26'
        },
        {
            'league': 'BKH',
            'team_name': 'Maintal Baskets Hassberge',
            'contact_name': 'Maximilian Mantel',
            'email': 'mantel.maxi@gmx.de',
            'phone': '09527 7541',
            'season': '2025/26'
        },
        {
            'league': 'BKH',
            'team_name': 'Regnitztal Baskets 2',
            'contact_name': 'Jürgen Stäudler',
            'email': 'juergen.staeudler@gmail.com',
            'phone': '0170 3064631',
            'season': '2025/26'
        },
        {
            'league': 'KLHA',
            'team_name': 'SG Rödental',
            'contact_name': 'Andreas Hut',
            'email': 'andi.hut@outlook.de',
            'phone': '0162 9264081',
            'season': '2025/26'
        },
        {
            'league': 'KLHA',
            'team_name': 'ATSV Nordhalben',
            'contact_name': 'Thomas Wolf',
            'email': 'xundsoweiterx@aol.com',
            'phone': '09267 914181',
            'season': '2025/26'
        },
        {
            'league': 'KLHA',
            'team_name': 'SV Zapfendorf',
            'contact_name': 'Marco Nestmann',
            'email': 'nemazap@gmx.de',
            'phone': '01522 5808882',
            'season': '2025/26'
        },
        {
            'league': 'KLHA',
            'team_name': 'TS Lichtenfels',
            'contact_name': 'Benedikt Bechmann',
            'email': 'benedikt.bechmann@gmx.de',
            'phone': '0170 2859596',
            'season': '2025/26'
        },
        {
            'league': 'KLHA',
            'team_name': 'TSV Hof 2',
            'contact_name': 'Christoph Wachter',
            'email': 'christoph.wachter@googlemail.com',
            'phone': '0176 70069012',
            'season': '2025/26'
        },
        {
            'league': 'KLHB',
            'team_name': 'Freak City Bamberg e.V.',
            'contact_name': 'Simon Bertram',
            'email': 'simon.bertram@freak-city.de',
            'phone': '0151 50784976',
            'season': '2025/26'
        }
    ]
    
    return teams

def save_data():
    """Save extracted data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    venues = extract_venues()
    teams = extract_teams()
    
    # Save to JSON files
    venues_file = f"real_venues_{timestamp}.json"
    teams_file = f"real_teams_{timestamp}.json"
    
    with open(venues_file, 'w', encoding='utf-8') as f:
        json.dump(venues, f, indent=2, ensure_ascii=False)
    
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)
    
    print("🏀 REAL VENUE & TEAM DATA EXTRACTED!")
    print("=" * 50)
    print(f"📍 Venues: {len(venues)} locations")
    print(f"📞 Teams: {len(teams)} active teams (2025/26)")
    print(f"💾 Files: {venues_file}, {teams_file}")
    
    # Show some highlights
    print("\\n🌟 KEY VENUES:")
    key_venues = ['BA-AR', 'BT-OH', 'CO-HUK', 'HIR-RA', 'STR-BCH', 'LIT-GMS']
    for venue in venues:
        if venue['code'] in key_venues:
            print(f"  🏟️ {venue['code']}: {venue['name']} ({venue['city']})")
    
    print("\\n🏀 SAMPLE TEAMS:")
    sample_teams = ['BG Litzendorf', 'BBC Bayreuth 3', 'BBC Coburg 2', 'RSC Oberhaid']
    for team in teams:
        if team['team_name'] in sample_teams:
            print(f"  📞 {team['league']}: {team['team_name']} - {team['contact_name']}")
    
    print("\\n🎯 APPLICATIONS:")
    print("- Admin Vereine system with real venues")
    print("- Contact management for all teams")  
    print("- Google Maps integration")
    print("- League hierarchy visualization")
    print("- Team-to-venue mapping")
    
    return venues, teams

if __name__ == "__main__":
    venues, teams = save_data()
