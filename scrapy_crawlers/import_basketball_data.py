#!/usr/bin/env python3
"""
🏀 BASKETBALL DATA IMPORT SCRIPT 🏀
Import our massive crawled dataset into the Prisma database

This script processes our 8,944+ player CSV files and imports them
into the proper database structure for basketball-reference.com style frontend.
"""

import csv
import sqlite3
import json
import os
from datetime import datetime
from collections import defaultdict
import hashlib

class BasketballDataImporter:
    def __init__(self, db_path="../../league_cache.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Statistics tracking
        self.stats = {
            'players_imported': 0,
            'teams_imported': 0,
            'leagues_imported': 0,
            'season_stats_imported': 0,
            'duplicates_skipped': 0,
            'errors': []
        }
        
        # Data normalization maps
        self.team_aliases = {}
        self.player_aliases = {}
        
    def setup_database(self):
        """Create missing tables if needed"""
        print("🔧 Setting up database schema...")
        
        # Note: Prisma should have already created the tables
        # This is just a backup check
        
        cursor = self.conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('players', 'teams', 'seasons', 'season_stats', 'leagues')
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found existing tables: {existing_tables}")
        
        if not existing_tables:
            print("⚠️ No Prisma tables found. Run 'npx prisma db push' first!")
            return False
            
        return True
    
    def normalize_team_name(self, team_name):
        """Normalize team names for consistency"""
        if not team_name or team_name.strip() == "":
            return "Unknown Team"
            
        # Remove common prefixes/suffixes
        team = team_name.strip()
        
        # Handle special cases
        if team.lower() in ['bg litzendorf', 'basketball litzendorf']:
            return "BG Litzendorf"
        elif team.lower().startswith('bbc '):
            return team.replace('bbc ', 'BBC ')
        elif team.lower().startswith('tsv '):
            return team.replace('tsv ', 'TSV ')
        elif team.lower().startswith('fc '):
            return team.replace('fc ', 'FC ')
            
        return team
    
    def normalize_player_name(self, first_name, last_name):
        """Normalize player names"""
        if not first_name and not last_name:
            return "Unknown Player"
            
        # Clean up the names
        first = (first_name or "").strip()
        last = (last_name or "").strip()
        
        # Handle cases where names might be in wrong fields
        if not first and last:
            return last
        elif first and not last:
            return first
        else:
            return f"{first} {last}".strip()
    
    def generate_id(self, entity_type, *args):
        """Generate consistent IDs based on content"""
        content = f"{entity_type}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()
    
    def import_csv_file(self, csv_file_path):
        """Import a single CSV file"""
        print(f"📂 Importing {csv_file_path}...")
        
        if not os.path.exists(csv_file_path):
            print(f"❌ File not found: {csv_file_path}")
            return
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                # Detect CSV structure
                sample = f.read(1024)
                f.seek(0)
                
                # Try to detect delimiter
                dialect = csv.Sniffer().sniff(sample, delimiters=',;|')
                
                reader = csv.DictReader(f, delimiter=dialect.delimiter)
                
                # Process each row
                for row_num, row in enumerate(reader, 1):
                    try:
                        self.process_player_row(row)
                    except Exception as e:
                        error_msg = f"Error processing row {row_num}: {e}"
                        print(f"⚠️ {error_msg}")
                        self.stats['errors'].append(error_msg)
                        
                        if len(self.stats['errors']) > 50:  # Limit error logging
                            print("🛑 Too many errors, stopping...")
                            break
                            
        except Exception as e:
            error_msg = f"Error reading file {csv_file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
    
    def process_player_row(self, row):
        """Process a single player row from CSV"""
        
        # Extract data based on available columns
        # Handle different CSV formats from our crawling
        
        # Try different possible column names
        player_name = (
            row.get('name') or 
            f"{row.get('firstname', '')} {row.get('lastname', '')}".strip() or
            row.get('player_name') or
            "Unknown Player"
        )
        
        team_name = self.normalize_team_name(
            row.get('team') or row.get('team_name') or "Unknown Team"
        )
        
        season = row.get('season') or row.get('year') or "2024"  # Default season
        
        # Stats
        points = self.safe_int(row.get('points') or row.get('pts'), 0)
        games = self.safe_int(row.get('games') or row.get('g'), 0)
        
        # League info
        liga_id = row.get('liga_id') or row.get('league_id') or "unknown"
        spielklasse = row.get('spielklasse') or row.get('league_name') or "Unknown"
        altersklasse = row.get('altersklasse') or ""
        geschlecht = row.get('geschlecht') or ""
        bezirk = row.get('bezirk') or "Unknown"
        
        # Generate consistent IDs
        player_id = self.generate_id("player", player_name.lower())
        team_id = self.generate_id("team", team_name.lower())
        season_id = f"{season}"
        
        # Insert/update entities
        self.upsert_player(player_id, player_name)
        self.upsert_team(team_id, team_name)
        self.upsert_season(season_id, int(season))
        self.upsert_league(liga_id, season_id, spielklasse, bezirk)
        self.upsert_season_stat(player_id, season_id, points, games, team_id)
        
    def safe_int(self, value, default=0):
        """Safely convert to int"""
        try:
            if value is None or value == "":
                return default
            return int(float(str(value).replace(',', '')))
        except:
            return default
    
    def upsert_player(self, player_id, name):
        """Insert or update player"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO players (id, name) 
            VALUES (?, ?)
        """, (player_id, name))
        
        if cursor.rowcount > 0:
            self.stats['players_imported'] += 1
    
    def upsert_team(self, team_id, name):
        """Insert or update team"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO teams (id, name) 
            VALUES (?, ?)
        """, (team_id, name))
        
        if cursor.rowcount > 0:
            self.stats['teams_imported'] += 1
    
    def upsert_season(self, season_id, year):
        """Insert or update season"""
        cursor = self.conn.cursor()
        
        # For now, use a default liga_id since seasons are linked to leagues
        cursor.execute("""
            INSERT OR IGNORE INTO seasons (seasonId, year, ligaId) 
            VALUES (?, ?, ?)
        """, (season_id, year, "default"))
        
    def upsert_league(self, liga_id, season_id, name, region):
        """Insert or update league"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO leagues (ligaId, seasonId, name, region, source, scraped_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (liga_id, season_id, name, region, "beast_crawler", datetime.now()))
        
        if cursor.rowcount > 0:
            self.stats['leagues_imported'] += 1
    
    def upsert_season_stat(self, player_id, season_id, points, games, team_id=None):
        """Insert or update season statistics"""
        cursor = self.conn.cursor()
        
        # Calculate points per game
        ppg = round(points / games, 1) if games > 0 else 0.0
        
        stat_id = self.generate_id("stat", player_id, season_id)
        
        cursor.execute("""
            INSERT OR REPLACE INTO season_stats 
            (id, playerId, seasonId, pts, g, pts_g) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (stat_id, player_id, season_id, points, games, ppg))
        
        if cursor.rowcount > 0:
            self.stats['season_stats_imported'] += 1
    
    def import_all_csv_files(self):
        """Import all available CSV files"""
        print("🏀 Starting massive basketball data import!")
        
        # List of our CSV files to import
        csv_files = [
            "oberfranken_all_players_20251002_141033.csv",  # 8,944 players
            "BEAST_OBERFRANKEN_SEASON_2005_20251002_144710.csv",  # 3,754 players with metadata
            "oberfranken_players_robust_2018_20251002_142152.csv",  # 2018 season
            "copy_2018_successful_method.csv",
            "sample_export.csv"
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                self.import_csv_file(csv_file)
            else:
                print(f"⚠️ File not found: {csv_file}")
        
        # Commit all changes
        self.conn.commit()
        
        # Print summary
        self.print_import_summary()
    
    def print_import_summary(self):
        """Print import statistics"""
        print("\\n🏆 IMPORT COMPLETE!")
        print("=" * 50)
        print(f"✅ Players imported: {self.stats['players_imported']}")
        print(f"✅ Teams imported: {self.stats['teams_imported']}")
        print(f"✅ Leagues imported: {self.stats['leagues_imported']}")
        print(f"✅ Season stats imported: {self.stats['season_stats_imported']}")
        print(f"⚠️ Errors encountered: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\\n🔍 Sample errors:")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")
        
        # Verify data
        self.verify_import()
    
    def verify_import(self):
        """Verify the imported data"""
        print("\\n🔍 Verifying imported data...")
        
        cursor = self.conn.cursor()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM players")
        player_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM season_stats")
        stats_count = cursor.fetchone()[0]
        
        print(f"📊 Database contains:")
        print(f"   Players: {player_count}")
        print(f"   Teams: {team_count}")
        print(f"   Season Stats: {stats_count}")
        
        # Sample players
        cursor.execute("SELECT name FROM players LIMIT 5")
        sample_players = [row[0] for row in cursor.fetchall()]
        print(f"   Sample players: {sample_players}")
        
        # Sample teams
        cursor.execute("SELECT name FROM teams LIMIT 5")
        sample_teams = [row[0] for row in cursor.fetchall()]
        print(f"   Sample teams: {sample_teams}")
        
        # Check for BG Litzendorf
        cursor.execute("SELECT COUNT(*) FROM players p JOIN season_stats s ON p.id = s.playerId JOIN teams t ON t.name LIKE '%litzendorf%'")
        bg_litzendorf_count = cursor.fetchone()[0]
        print(f"🎯 BG Litzendorf related records: {bg_litzendorf_count}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__ == "__main__":
    print("🏀🔥 BASKETBALL DATA IMPORT - UNLEASHING THE DATASET! 🔥🏀")
    
    importer = BasketballDataImporter()
    
    if not importer.setup_database():
        print("❌ Database setup failed!")
        exit(1)
    
    try:
        importer.import_all_csv_files()
    except KeyboardInterrupt:
        print("\\n🛑 Import interrupted by user")
    except Exception as e:
        print(f"❌ Import failed: {e}")
    finally:
        importer.close()
    
    print("\\n🎉 Ready for basketball-reference.com style frontend!")
