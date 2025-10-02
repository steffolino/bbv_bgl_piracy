#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
import random
import re

class OberfrankenLeagueDiscovery:
    """Systematic discovery of ALL leagues in Bezirk Oberfranken across all seasons"""
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.bezirk_oberfranken = 5  # Bezirk filter for Oberfranken
        self.cache_file = "oberfranken_leagues_cache.json"
        self.successful_urls_file = "successful_basketball_urls.json"
        
        # Load existing cache to avoid re-crawling
        self.leagues_cache = self.load_cache()
        self.successful_urls = self.load_successful_urls()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Referer': 'https://www.basketball-bund.net/',
        })
    
    def load_cache(self):
        """Load existing league cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                print(f"📦 Loaded cache: {len(cache.get('leagues', []))} leagues from {len(cache.get('seasons', []))} seasons")
                return cache
            except:
                print("⚠️  Cache file corrupted, starting fresh")
        return {'seasons': {}, 'leagues': [], 'last_updated': None}
    
    def load_successful_urls(self):
        """Load successful URL database"""
        if os.path.exists(self.successful_urls_file):
            try:
                with open(self.successful_urls_file, 'r', encoding='utf-8') as f:
                    urls = json.load(f)
                print(f"🔗 Loaded {len(urls.get('working_urls', []))} successful URLs")
                return urls
            except:
                print("⚠️  Successful URLs file corrupted, starting fresh")
        return {'working_urls': [], 'failed_urls': [], 'last_tested': None}
    
    def save_cache(self):
        """Save league cache"""
        self.leagues_cache['last_updated'] = datetime.now().isoformat()
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.leagues_cache, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved cache: {len(self.leagues_cache.get('leagues', []))} leagues")
    
    def save_successful_urls(self):
        """Save successful URLs database"""
        self.successful_urls['last_tested'] = datetime.now().isoformat()
        with open(self.successful_urls_file, 'w', encoding='utf-8') as f:
            json.dump(self.successful_urls, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(self.successful_urls.get('working_urls', []))} working URLs")
    
    def discover_all_oberfranken_leagues(self, start_season=2003, end_season=2024, test_mode=False):
        """Discover ALL leagues in Oberfranken across all seasons"""
        
        print("🎯 DISCOVERING ALL OBERFRANKEN LEAGUES")
        print(f"📅 Seasons: {start_season} to {end_season}")
        print(f"🏀 Target: Bezirk Oberfranken (filter=5)")
        if test_mode:
            print("🧪 TEST MODE: Single season (2018) for validation")
            start_season = end_season = 2018
        
        seasons_to_test = list(range(start_season, end_season + 1))
        total_leagues_found = 0
        
        for saison_id in seasons_to_test:
            print(f"\n📅 SEASON {saison_id} ({saison_id}/{saison_id+1})")
            
            # Check cache first
            season_key = str(saison_id)
            if season_key in self.leagues_cache.get('seasons', {}):
                cached_leagues = self.leagues_cache['seasons'][season_key]
                print(f"   📦 Found {len(cached_leagues)} leagues in cache")
                total_leagues_found += len(cached_leagues)
                continue
            
            # Discover leagues for this season
            leagues = self.discover_leagues_for_season(saison_id)
            
            if leagues:
                # Save to cache
                if 'seasons' not in self.leagues_cache:
                    self.leagues_cache['seasons'] = {}
                self.leagues_cache['seasons'][season_key] = leagues
                
                # Add to master league list
                for league in leagues:
                    if league not in self.leagues_cache.get('leagues', []):
                        self.leagues_cache.setdefault('leagues', []).append(league)
                
                total_leagues_found += len(leagues)
                print(f"   ✅ Discovered {len(leagues)} new leagues")
                
                # Test a sample of URLs to validate
                self.test_sample_urls(leagues[:3])  # Test first 3 leagues
                
            else:
                print(f"   ❌ No leagues found for season {saison_id}")
            
            # Save progress regularly
            self.save_cache()
            self.save_successful_urls()
            
            # Rate limiting
            time.sleep(random.uniform(2, 4))
        
        print(f"\n🎯 DISCOVERY COMPLETE:")
        print(f"   📊 {total_leagues_found} total leagues found")
        print(f"   📅 {len(self.leagues_cache.get('seasons', {}))} seasons covered")
        print(f"   🔗 {len(self.successful_urls.get('working_urls', []))} working URLs validated")
        
        return self.leagues_cache
    
    def discover_leagues_for_season(self, saison_id):
        """Discover all leagues in Oberfranken for a specific season"""
        
        # Try multiple discovery approaches
        approaches = [
            self.discover_via_action_106,  # Main discovery page
            self.discover_via_direct_enumeration,  # Direct ID testing
        ]
        
        all_leagues = []
        
        for approach in approaches:
            try:
                leagues = approach(saison_id)
                for league in leagues:
                    # Avoid duplicates
                    if not any(l.get('liga_id') == league.get('liga_id') for l in all_leagues):
                        all_leagues.append(league)
            except Exception as e:
                print(f"      ⚠️  Approach failed: {e}")
        
        return all_leagues
    
    def discover_via_action_106(self, saison_id):
        """Discover leagues using Action=106 form with all possible filters"""
        
        print(f"   🔍 Method 1: Action=106 discovery")
        
        # Try different filter combinations for Oberfranken
        filter_combinations = [
            {'cbSpielklasseFilter': '0', 'cbAltersklasseFilter': '-3'},  # All levels, Senioren
            {'cbSpielklasseFilter': '0', 'cbAltersklasseFilter': '0'},   # All levels, All ages
            {'cbSpielklasseFilter': '1', 'cbAltersklasseFilter': '-3'},  # 1. Liga, Senioren
            {'cbSpielklasseFilter': '2', 'cbAltersklasseFilter': '-3'},  # 2. Liga, Senioren
            {'cbSpielklasseFilter': '3', 'cbAltersklasseFilter': '-3'},  # Bezirksliga, Senioren
        ]
        
        all_leagues = []
        
        for filters in filter_combinations:
            params = {
                'Action': '106',
                'viewid': '',
                'saison_id': saison_id,
                'cbBezirkFilter': self.bezirk_oberfranken,  # Oberfranken
                'cbKreisFilter': '0',
                'cbGeschlechtFilter': '0',  # All genders
                **filters
            }
            
            try:
                url = f"{self.base_url}/index.jsp"
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    leagues = self.parse_discovery_page(response.text, saison_id, params)
                    
                    for league in leagues:
                        # Avoid duplicates
                        if not any(l.get('liga_id') == league.get('liga_id') for l in all_leagues):
                            all_leagues.append(league)
                            
                    if leagues:
                        print(f"      ✅ Found {len(leagues)} leagues with filter {filters}")
                else:
                    print(f"      ❌ HTTP {response.status_code} for filter {filters}")
                    
            except Exception as e:
                print(f"      ⚠️  Error with filter {filters}: {e}")
            
            time.sleep(1)  # Rate limiting
        
        return all_leagues
    
    def discover_via_direct_enumeration(self, saison_id):
        """Discover leagues by testing liga_id ranges directly"""
        
        print(f"   🔢 Method 2: Direct ID enumeration")
        
        # Test liga_id ranges that are likely for Oberfranken
        # Based on the known working ID 26212, test nearby ranges
        id_ranges = [
            range(26000, 26300),  # Around known working ID
            range(25000, 25300),  # Slightly lower
            range(27000, 27300),  # Slightly higher
        ]
        
        discovered_leagues = []
        tested_count = 0
        
        for id_range in id_ranges:
            for liga_id in id_range:
                # Quick test: try team statistics URL
                test_url = f"{self.base_url}/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}"
                
                # Skip if we've already tested this URL
                if test_url in [url['url'] for url in self.successful_urls.get('working_urls', [])]:
                    continue
                if test_url in [url['url'] for url in self.successful_urls.get('failed_urls', [])]:
                    continue
                
                try:
                    response = self.session.get(test_url, timeout=10)
                    tested_count += 1
                    
                    if response.status_code == 200:
                        # Check if it contains Oberfranken data
                        if self.is_oberfranken_league(response.text):
                            league_info = self.extract_league_from_stats_page(response.text, liga_id, saison_id)
                            if league_info:
                                discovered_leagues.append(league_info)
                                
                                # Save as working URL
                                self.successful_urls.setdefault('working_urls', []).append({
                                    'url': test_url,
                                    'liga_id': liga_id,
                                    'saison_id': saison_id,
                                    'tested_at': datetime.now().isoformat(),
                                    'response_status': 200
                                })
                                
                                print(f"      ✅ Found league {liga_id}: {league_info.get('league_name', 'Unknown')}")
                        else:
                            # Save as failed URL
                            self.successful_urls.setdefault('failed_urls', []).append({
                                'url': test_url,
                                'tested_at': datetime.now().isoformat(),
                                'reason': 'Not Oberfranken'
                            })
                    
                    # Rate limiting and progress
                    if tested_count % 10 == 0:
                        print(f"      🔍 Tested {tested_count} IDs, found {len(discovered_leagues)} leagues")
                        time.sleep(1)
                    
                    if tested_count >= 50:  # Limit for testing
                        break
                        
                except Exception as e:
                    continue
            
            if tested_count >= 50:
                break
        
        print(f"      📊 Enumeration complete: {len(discovered_leagues)} leagues from {tested_count} tests")
        return discovered_leagues
    
    def parse_discovery_page(self, html_content, saison_id, params):
        """Parse Action=106 discovery page for league links"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            leagues = []
            
            # Look for links with liga_id parameters
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                
                # Extract liga_id from various link patterns
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = int(liga_id_match.group(1))
                    
                    # Get league name from link text or surrounding context
                    league_name = link.get_text(strip=True)
                    
                    # Skip empty or very short names
                    if league_name and len(league_name) > 3:
                        leagues.append({
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'saison_id': saison_id,
                            'season_display': f"{saison_id}/{saison_id+1}",
                            'discovery_method': 'Action=106',
                            'discovery_params': params,
                            'source_link': href,
                            'discovered_at': datetime.now().isoformat()
                        })
            
            # Remove duplicates based on liga_id
            unique_leagues = {}
            for league in leagues:
                liga_id = league['liga_id']
                if liga_id not in unique_leagues:
                    unique_leagues[liga_id] = league
            
            return list(unique_leagues.values())
            
        except Exception as e:
            print(f"      Error parsing discovery page: {e}")
            return []
    
    def is_oberfranken_league(self, html_content):
        """Check if HTML content indicates this is an Oberfranken league"""
        
        text = html_content.lower()
        oberfranken_indicators = [
            'oberfranken',
            'coburg',
            'bamberg',
            'bayreuth',
            'kronach',
            'lichtenfels',
            'forchheim',
            'kulmbach'
        ]
        
        return any(indicator in text for indicator in oberfranken_indicators)
    
    def extract_league_from_stats_page(self, html_content, liga_id, saison_id):
        """Extract league information from statistics page"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for title elements
            title_elements = soup.find_all(['td', 'div'], class_=lambda x: x and 'title' in x.lower())
            
            for element in title_elements:
                text = element.get_text(strip=True)
                
                if 'saison' in text.lower() and 'oberfranken' in text.lower():
                    # Extract league name
                    league_match = re.search(r'.*?saison:\s*\d{4}/\d{4}\)\s*-\s*(.+)', text, re.IGNORECASE)
                    if league_match:
                        league_name = league_match.group(1).strip()
                    else:
                        league_name = text.split('-')[-1].strip()
                    
                    return {
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'season_display': f"{saison_id}/{saison_id+1}",
                        'discovery_method': 'Direct enumeration',
                        'full_title': text,
                        'discovered_at': datetime.now().isoformat()
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def test_sample_urls(self, leagues):
        """Test sample URLs to validate league data availability"""
        
        if not leagues:
            return
        
        print(f"   🧪 Testing {len(leagues)} sample URLs...")
        
        for league in leagues[:3]:  # Test first 3
            liga_id = league.get('liga_id')
            saison_id = league.get('saison_id')
            
            # Test multiple endpoints
            test_urls = [
                f"{self.base_url}/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}",
                f"{self.base_url}/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
            ]
            
            for url in test_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200 and len(response.text) > 5000:  # Has substantial content
                        # Add to successful URLs
                        success_entry = {
                            'url': url,
                            'liga_id': liga_id,
                            'saison_id': saison_id,
                            'league_name': league.get('league_name'),
                            'tested_at': datetime.now().isoformat(),
                            'response_status': 200,
                            'content_length': len(response.text)
                        }
                        
                        # Avoid duplicates
                        if not any(u.get('url') == url for u in self.successful_urls.get('working_urls', [])):
                            self.successful_urls.setdefault('working_urls', []).append(success_entry)
                        
                        print(f"      ✅ {url} - Working ({len(response.text)} chars)")
                        break  # One working URL per league is enough for validation
                        
                except Exception as e:
                    continue

if __name__ == "__main__":
    discoverer = OberfrankenLeagueDiscovery()
    
    # Start with test mode for single season
    print("🧪 Starting with TEST MODE (Season 2018) to validate approach")
    cache = discoverer.discover_all_oberfranken_leagues(test_mode=True)
    
    print("\n" + "="*50)
    print("Test complete! To run full discovery (2003-2024), run:")
    print("discoverer.discover_all_oberfranken_leagues(start_season=2003, end_season=2024)")
