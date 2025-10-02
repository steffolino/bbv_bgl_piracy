#!/usr/bin/env python3
"""
🏀 VEREINE MAPPING ANALYSIS 🏀
Analyze our REAL team data to create vereine (clubs) mapping

This script processes our crawled team data to:
1. Identify unique clubs/vereine from team names
2. Map teams to their parent organizations
3. Extract team numbers and categories
4. Prepare vereine database entries
"""

import csv
import re
import json
from collections import defaultdict, Counter
import os

class VereineAnalyzer:
    def __init__(self):
        self.teams_found = set()
        self.vereine_mapping = {}
        self.vereine_data = {}
        
        # Known vereine data from web research
        self.known_vereine_info = {
            'BG Litzendorf e.V.': {
                'website': 'https://bg-litzendorf.de/',
                'region': 'Oberfranken',
                'city': 'Litzendorf',
                'postal_code': '96215',
                'state': 'Bayern',
                'short_name': 'BG Litzendorf'
            },
            'BBC Bayreuth e.V.': {
                'website': 'https://bbc-bayreuth.de/',
                'region': 'Oberfranken',
                'city': 'Bayreuth',
                'state': 'Bayern',
                'short_name': 'BBC Bayreuth'
            },
            'TSV Breitengüßbach e.V.': {
                'region': 'Oberfranken',
                'city': 'Breitengüßbach',
                'state': 'Bayern',
                'short_name': 'TSV Breitengüßbach'
            },
            '1. FC Baunach e.V.': {
                'region': 'Oberfranken',
                'city': 'Baunach',
                'state': 'Bayern',
                'short_name': '1. FC Baunach'
            },
            'TS Lichtenfels e.V.': {
                'region': 'Oberfranken',
                'city': 'Lichtenfels',
                'state': 'Bayern',
                'short_name': 'TS Lichtenfels'
            }
        }
        
        # Patterns for extracting verein from team names
        self.verein_patterns = [
            (r'(BG\s+Litzendorf)', 'BG Litzendorf e.V.'),
            (r'(BBC\s+\w+)', lambda m: f"BBC {m.group(1).split()[-1]} e.V."),
            (r'(TSV\s+\w+)', lambda m: f"TSV {m.group(1).split()[-1]} e.V."),
            (r'(\d+\.\s*FC\s+\w+)', lambda m: f"{m.group(1)} e.V."),
            (r'(FC\s+\w+)', lambda m: f"FC {m.group(1).split()[-1]} e.V."),
            (r'(SpVgg\s+\w+)', lambda m: f"SpVgg {m.group(1).split()[-1]} e.V."),
            (r'(SV\s+\w+)', lambda m: f"SV {m.group(1).split()[-1]} e.V."),
            (r'(DJK\s+\w+)', lambda m: f"DJK {m.group(1).split()[-1]} e.V."),
            (r'(TS\s+\w+)', lambda m: f"TS {m.group(1).split()[-1]} e.V."),
            (r'(TTL\s+\w+)', lambda m: f"TTL {m.group(1).split()[-1]} e.V."),
            (r'(VfL\s+\w+)', lambda m: f"VfL {m.group(1).split()[-1]} e.V."),
            (r'(ATS\s+\w+)', lambda m: f"ATS {m.group(1).split()[-1]} e.V."),
            (r'(ATSV\s+\w+)', lambda m: f"ATSV {m.group(1).split()[-1]} e.V."),
            (r'(BSC\s+\w+)', lambda m: f"BSC {m.group(1).split()[-1]} e.V."),
        ]
    
    def extract_verein_info(self, team_name):
        """Extract verein information from team name"""
        if not team_name or team_name.strip() == "":
            return None
            
        team = team_name.strip()
        
        # Try each pattern
        for pattern, verein_template in self.verein_patterns:
            match = re.search(pattern, team, re.IGNORECASE)
            if match:
                if callable(verein_template):
                    verein_name = verein_template(match)
                else:
                    verein_name = verein_template
                
                # Extract team number (e.g., "BG Litzendorf 2" -> 2)
                team_number = self.extract_team_number(team)
                
                # Extract category/age group
                category = self.extract_category(team)
                
                return {
                    'verein_name': verein_name,
                    'team_name': team,
                    'team_number': team_number,
                    'category': category,
                    'short_name': match.group(1) if not callable(verein_template) else match.group(1)
                }
        
        return None
    
    def extract_team_number(self, team_name):
        """Extract team number from name like 'BG Litzendorf 2'"""
        match = re.search(r'\s+(\d+)$', team_name)
        return int(match.group(1)) if match else 1
    
    def extract_category(self, team_name):
        """Extract category/age group from team name"""
        team_lower = team_name.lower()
        
        # Age categories
        if 'u8' in team_lower or 'u 8' in team_lower:
            return 'U8'
        elif 'u10' in team_lower or 'u 10' in team_lower:
            return 'U10'
        elif 'u12' in team_lower or 'u 12' in team_lower:
            return 'U12'
        elif 'u14' in team_lower or 'u 14' in team_lower:
            return 'U14'
        elif 'u16' in team_lower or 'u 16' in team_lower:
            return 'U16'
        elif 'u18' in team_lower or 'u 18' in team_lower:
            return 'U18'
        elif 'u20' in team_lower or 'u 20' in team_lower:
            return 'U20'
        elif 'ü40' in team_lower or 'ü 40' in team_lower or 'senior' in team_lower:
            return 'Ü40'
        elif 'ü50' in team_lower or 'ü 50' in team_lower:
            return 'Ü50'
        elif 'herren' in team_lower or 'männlich' in team_lower:
            return 'Herren'
        elif 'damen' in team_lower or 'weiblich' in team_lower:
            return 'Damen'
        
        return 'Unbekannt'
    
    def analyze_csv_file(self, csv_file_path):
        """Analyze a CSV file for team names"""
        print(f"📂 Analyzing {csv_file_path}...")
        
        if not os.path.exists(csv_file_path):
            print(f"❌ File not found: {csv_file_path}")
            return
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                delimiter = ','
                if ';' in sample:
                    delimiter = ';'
                elif '|' in sample:
                    delimiter = '|'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row in reader:
                    # Try different possible team column names
                    team_name = (
                        row.get('team') or 
                        row.get('team_name') or 
                        row.get('Team') or
                        ""
                    )
                    
                    if team_name and team_name.strip():
                        self.teams_found.add(team_name.strip())
                        
        except Exception as e:
            print(f"⚠️ Error reading {csv_file_path}: {e}")
    
    def analyze_all_data(self):
        """Analyze all our CSV files"""
        print("🏀 Starting vereine analysis of REAL data!")
        
        # List of our CSV files
        csv_files = [
            "oberfranken_all_players_20251002_141033.csv",  # 8,944 players
            "BEAST_OBERFRANKEN_SEASON_2005_20251002_144710.csv",  # 3,754 players
            "oberfranken_players_robust_2018_20251002_142152.csv",
            "copy_2018_successful_method.csv",
            "sample_export.csv"
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                self.analyze_csv_file(csv_file)
        
        print(f"✅ Found {len(self.teams_found)} unique teams")
        
        # Process teams to extract vereine
        self.process_teams()
        
        # Generate reports
        self.generate_reports()
    
    def process_teams(self):
        """Process all teams to extract vereine information"""
        print("\\n🔍 Processing teams to extract vereine...")
        
        vereine_teams = defaultdict(list)
        unmatched_teams = []
        
        for team_name in sorted(self.teams_found):
            verein_info = self.extract_verein_info(team_name)
            
            if verein_info:
                verein_name = verein_info['verein_name']
                vereine_teams[verein_name].append(verein_info)
                
                # Store verein data
                if verein_name not in self.vereine_data:
                    self.vereine_data[verein_name] = {
                        'name': verein_name,
                        'short_name': verein_info['short_name'],
                        'teams': [],
                        'team_count': 0,
                        'categories': set(),
                        'team_numbers': set()
                    }
                    
                    # Add known info if available
                    if verein_name in self.known_vereine_info:
                        self.vereine_data[verein_name].update(self.known_vereine_info[verein_name])
                
                # Add team info
                self.vereine_data[verein_name]['teams'].append(verein_info)
                self.vereine_data[verein_name]['team_count'] += 1
                self.vereine_data[verein_name]['categories'].add(verein_info['category'])
                self.vereine_data[verein_name]['team_numbers'].add(verein_info['team_number'])
            else:
                unmatched_teams.append(team_name)
        
        print(f"✅ Mapped {len(vereine_teams)} vereine")
        print(f"⚠️ Unmatched teams: {len(unmatched_teams)}")
        
        # Store results
        self.vereine_teams = vereine_teams
        self.unmatched_teams = unmatched_teams
    
    def generate_reports(self):
        """Generate analysis reports"""
        print("\\n📊 VEREINE ANALYSIS REPORT")
        print("=" * 50)
        
        # Vereine summary
        print(f"\\n🏟️ DISCOVERED VEREINE: {len(self.vereine_data)}")
        for verein_name, data in sorted(self.vereine_data.items()):
            categories = sorted(data['categories'])
            team_numbers = sorted(data['team_numbers'])
            
            print(f"\\n📍 {verein_name}")
            print(f"   Teams: {data['team_count']}")
            print(f"   Categories: {', '.join(categories)}")
            print(f"   Team Numbers: {', '.join(map(str, team_numbers))}")
            
            if 'city' in data:
                print(f"   City: {data['city']}")
            if 'website' in data:
                print(f"   Website: {data['website']}")
            
            # Show some example teams
            example_teams = [t['team_name'] for t in data['teams'][:3]]
            if len(data['teams']) > 3:
                example_teams.append(f"... and {len(data['teams'])-3} more")
            print(f"   Example Teams: {', '.join(example_teams)}")
        
        # BG Litzendorf special analysis
        if 'BG Litzendorf e.V.' in self.vereine_data:
            bg_data = self.vereine_data['BG Litzendorf e.V.']
            print(f"\\n🌟 BG LITZENDORF SPECIAL ANALYSIS:")
            print(f"   Total Teams: {bg_data['team_count']}")
            print(f"   Categories: {', '.join(sorted(bg_data['categories']))}")
            print(f"   All Teams:")
            for team_info in bg_data['teams']:
                print(f"     - {team_info['team_name']} (#{team_info['team_number']}, {team_info['category']})")
        
        # Unmatched teams
        if self.unmatched_teams:
            print(f"\\n⚠️ UNMATCHED TEAMS ({len(self.unmatched_teams)}):")
            for team in self.unmatched_teams[:10]:  # Show first 10
                print(f"   - {team}")
            if len(self.unmatched_teams) > 10:
                print(f"   ... and {len(self.unmatched_teams)-10} more")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save analysis results to files"""
        timestamp = "20251002_vereine_analysis"
        
        # Save vereine mapping
        vereine_file = f"vereine_mapping_{timestamp}.json"
        with open(vereine_file, 'w', encoding='utf-8') as f:
            # Convert sets to lists for JSON serialization
            serializable_data = {}
            for verein, data in self.vereine_data.items():
                serializable_data[verein] = {
                    **data,
                    'categories': list(data['categories']),
                    'team_numbers': list(data['team_numbers'])
                }
            
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        # Save team list
        teams_file = f"all_teams_{timestamp}.txt"
        with open(teams_file, 'w', encoding='utf-8') as f:
            for team in sorted(self.teams_found):
                f.write(f"{team}\\n")
        
        # Save SQL for vereine creation
        sql_file = f"create_vereine_{timestamp}.sql"
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write("-- Generated SQL for creating vereine\\n\\n")
            
            for verein, data in self.vereine_data.items():
                f.write(f"INSERT INTO vereine (name, short_name, region, address_city, address_state, website) VALUES\\n")
                f.write(f"  ('{verein}', '{data.get('short_name', '')}', '{data.get('region', '')}', ")
                f.write(f"'{data.get('city', '')}', '{data.get('state', '')}', '{data.get('website', '')}');\\n\\n")
        
        print(f"\\n💾 Results saved:")
        print(f"   📄 {vereine_file} - Vereine mapping data")
        print(f"   📄 {teams_file} - All team names")
        print(f"   📄 {sql_file} - SQL for database creation")

if __name__ == "__main__":
    print("🏀🔍 VEREINE ANALYSIS - REAL DATA PROCESSING! 🔍🏀")
    
    analyzer = VereineAnalyzer()
    analyzer.analyze_all_data()
    
    print("\\n🎉 Vereine analysis complete!")
    print("Next steps:")
    print("1. Review the vereine mapping")
    print("2. Update Prisma database with vereine") 
    print("3. Link teams to their parent vereine")
    print("4. Create club pages in frontend")
