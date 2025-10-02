#!/usr/bin/env python3
"""
🔥🔥🔥 BEAST RESUME CRAWLER - CONTINUING THE RAMPAGE! 🔥🔥🔥
Resume the beast from season 2006!
"""

import requests
import time
import csv
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

class BeastResumeCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.stats = {
            'start_time': datetime.now(),
            'seasons_crawled': 0,
            'leagues_found': 0,
            'players_collected': 0,
            'bg_litzendorf_found': 0,
            'anomalies': []
        }
        
        # Setup logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'BEAST_RESUME_{timestamp}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Authentication cookies
        self.session.cookies.update({
            'SESSION': 'YTFhZGEyMGItMzMyZi00NzE1LWJmNGItNGQwNTFiODJhZjhk',
            'cookieconsent_status': 'allow',
            'JSESSIONID': '16BEC2ABAC94A6CA3F62DBE2F57D3B29.TC-BKA-WEB06-80'
        })
        
    def unleash_beast_resume(self):
        """Continue the beast from season 2006!"""
        print("🔥🔥🔥 BEAST RESUMING FROM SEASON 2006! 🔥🔥🔥")
        print("Previous progress: 3754 players from seasons 2003-2005")
        print("Continuing with seasons 2006-2024...")
        
        self.logger.info("🔥🔥🔥 BEAST RESUMED! CONTINUING FROM 2006! 🔥🔥🔥")
        
        # Resume from 2006
        seasons = list(range(2006, 2025))
        all_players = []
        total_players = 3754  # Previous count
        
        for season_idx, season in enumerate(seasons):
            print(f"\\n🎯 BEAST ATTACKING SEASON {season} ({season_idx+4}/22)")
            print("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
            
            start_time = time.time()
            
            # Get leagues for this season
            leagues = self.get_season_leagues(season)
            if not leagues:
                self.logger.warning(f"⚠️ No leagues found for season {season}")
                continue
            
            season_players = 0
            season_bg_litzendorf = 0
            
            for idx, league in enumerate(leagues):
                print(f"  🔍 Liga {idx+1}/{len(leagues)}: {league['full_name']} (ID: {league['id']})")
                
                players = self.get_league_players(league['id'], season)
                
                # Check for BG Litzendorf
                bg_players = [p for p in players if 'litzendorf' in p.get('team', '').lower()]
                if bg_players:
                    print(f"    🎯 BG LITZENDORF: {len(bg_players)} players!")
                    season_bg_litzendorf += len(bg_players)
                
                # Add league metadata to each player
                for player in players:
                    player.update({
                        'season': season,
                        'liga_id': league['id'],
                        'spielklasse': league['spielklasse'],
                        'altersklasse': league['altersklasse'],
                        'geschlecht': league['geschlecht']
                    })
                
                all_players.extend(players)
                season_players += len(players)
                print(f"    ✅ {len(players)} players")
                
                # Brief pause
                time.sleep(0.2)
            
            # Season summary
            season_time = time.time() - start_time
            total_players += season_players
            
            print(f"\\n✅ Season {season} complete!")
            print(f"   Leagues: {len(leagues)}")
            print(f"   Players: {season_players}")
            print(f"   Time: {season_time:.1f}s")
            print(f"   TOTAL SO FAR: {total_players} players")
            
            remaining_seasons = len(seasons) - (season_idx + 1)
            if remaining_seasons > 0 and season_time > 0:
                eta_minutes = (remaining_seasons * season_time) / 60
                print(f"   ⏱️ ETA: {eta_minutes:.1f} minutes remaining")
            
            # Save progress every 3 seasons
            if (season_idx + 1) % 3 == 0 or season_idx == len(seasons) - 1:
                self.save_progress(all_players, f"SEASON_{season}")
                
            self.stats['seasons_crawled'] += 1
            self.stats['players_collected'] = len(all_players)
            self.stats['bg_litzendorf_found'] += season_bg_litzendorf
        
        # Final save
        self.save_final_results(all_players, total_players)
        
    def get_season_leagues(self, season):
        """Get all Oberfranken leagues for a season"""
        self.logger.info(f"🎯 BEAST DISCOVERING SEASON {season}")
        
        # Step 1: Go to Action=100&Verband=2
        setup_url = f"https://www.basketball-bund.net/liga_tool/mannschaft/suche/ergebnis_aktuell.do?Action=100&Verband=2&Liga=0&Saison={season}&PageOffset=0"
        
        try:
            response = self.session.get(setup_url, timeout=10)
            if response.status_code != 200:
                return []
                
            # Step 2: Navigate to Action=106
            leagues_url = f"https://www.basketball-bund.net/liga_tool/mannschaft/suche/ergebnis_aktuell.do?Action=106&Verband=2&Saison={season}&cbBezirkFilter=5&PageOffset=0"
            
            leagues = []
            page = 1
            startrow = 0
            
            while True:
                url = f"{leagues_url}&startrow={startrow}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                page_leagues = self.parse_leagues_page(soup, season)
                
                if not page_leagues:
                    break
                    
                leagues.extend(page_leagues)
                self.logger.info(f"  Page {page}: {len(page_leagues)} leagues")
                
                # Check for next page
                next_startrow = self.get_next_startrow(soup)
                if next_startrow is None or next_startrow <= startrow:
                    break
                    
                startrow = next_startrow
                page += 1
                time.sleep(0.5)
            
            self.logger.info(f"✅ Season {season}: {len(leagues)} leagues")
            return leagues
            
        except Exception as e:
            self.logger.error(f"Error getting leagues for {season}: {e}")
            return []
    
    def parse_leagues_page(self, soup, season):
        """Parse leagues from a page"""
        leagues = []
        
        # Find the table
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 6:
                    try:
                        # Extract liga ID from link
                        link_cell = cells[5]  # Full name column
                        link = link_cell.find('a', href=True)
                        if not link:
                            continue
                            
                        href = link.get('href', '')
                        liga_match = re.search(r'Liga=(\d+)', href)
                        if not liga_match:
                            continue
                            
                        liga_id = liga_match.group(1)
                        
                        # Extract all metadata
                        spielklasse = cells[0].get_text(strip=True)
                        altersklasse = cells[1].get_text(strip=True)  
                        geschlecht = cells[2].get_text(strip=True)
                        bezirk = cells[3].get_text(strip=True)
                        kreis = cells[4].get_text(strip=True)
                        full_name = cells[5].get_text(strip=True)
                        
                        if bezirk.lower() == 'oberfranken' and spielklasse and full_name:
                            leagues.append({
                                'id': liga_id,
                                'season': season,
                                'spielklasse': spielklasse,
                                'altersklasse': altersklasse,
                                'geschlecht': geschlecht,
                                'bezirk': bezirk,
                                'kreis': kreis,
                                'full_name': full_name
                            })
                    except:
                        continue
        
        return leagues
    
    def get_next_startrow(self, soup):
        """Find next page"""
        for link in soup.find_all('a', href=True):
            match = re.search(r'startrow=(\d+)', link.get('href', ''))
            if match:
                return int(match.group(1))
        return None
    
    def get_league_players(self, liga_id, season):
        """Get all players from a league"""
        url = f"https://www.basketball-bund.net/liga_tool/statistik.do?Action=100&Liga={liga_id}&PageOffset=0&Saison={season}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Find all player tables
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                
                if len(rows) < 2:
                    continue
                    
                # Check if this looks like a player stats table
                header = rows[0]
                header_text = header.get_text()
                
                if any(keyword in header_text.lower() for keyword in ['name', 'spiele', 'punkte', 'rebounds']):
                    # Get team name from preceding content
                    team_name = "Unknown"
                    prev_elements = []
                    current = table.find_previous_sibling()
                    while current and len(prev_elements) < 5:
                        if hasattr(current, 'get_text'):
                            text = current.get_text(strip=True)
                            if text and len(text) > 5:
                                prev_elements.append(text)
                        current = current.find_previous_sibling()
                    
                    if prev_elements:
                        team_name = prev_elements[0]
                    
                    # Parse player rows
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 4:
                            try:
                                name = cells[0].get_text(strip=True)
                                if name and name not in ['Gesamt', 'Durchschnitt', '']:
                                    player_data = {
                                        'name': name,
                                        'team': team_name,
                                        'spiele': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                                        'punkte': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                        'punkte_pro_spiel': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                                    }
                                    
                                    # Additional stats if available
                                    if len(cells) > 4:
                                        player_data['rebounds'] = cells[4].get_text(strip=True)
                                    if len(cells) > 5:
                                        player_data['assists'] = cells[5].get_text(strip=True)
                                    
                                    players.append(player_data)
                            except:
                                continue
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error getting players for liga {liga_id}: {e}")
            return []
    
    def save_progress(self, all_players, suffix="PROGRESS"):
        """Save progress during beast run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_file = f'BEAST_RESUME_{suffix}_{timestamp}.csv'
        if all_players:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
        
        # Save stats
        stats_file = f'BEAST_RESUME_STATS_{suffix}_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            current_stats = self.stats.copy()
            current_stats['total_players'] = len(all_players)
            current_stats['current_time'] = datetime.now().isoformat()
            json.dump(current_stats, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"💾 Progress saved: {len(all_players)} players")
    
    def save_final_results(self, all_players, total_players):
        """Save final beast results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Final CSV
        csv_file = f'BEAST_RESUME_FINAL_{timestamp}.csv'
        if all_players:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
        
        # Final stats
        self.stats['end_time'] = datetime.now()
        self.stats['total_runtime'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        self.stats['final_player_count'] = len(all_players)
        
        stats_file = f'BEAST_RESUME_FINAL_STATS_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\\n🔥🔥🔥 BEAST RESUME COMPLETE! 🔥🔥🔥")
        print(f"✅ Total players collected (resume portion): {len(all_players)}")
        print(f"✅ Grand total (including previous): {total_players + len(all_players)}")
        print(f"✅ Runtime: {self.stats['total_runtime']:.1f} seconds")
        print(f"✅ Files saved: {csv_file}, {stats_file}")

if __name__ == "__main__":
    beast = BeastResumeCrawler()
    beast.unleash_beast_resume()
