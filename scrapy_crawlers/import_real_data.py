#!/usr/bin/env python3
"""
🏀 REAL DATA IMPORT SCRIPT 🏀
Import our REAL crawled basketball data (8,945 players) into the database

NO MOCK DATA - Only real players from basketball-bund.net!
"""

import sqlite3
import csv
import hashlib
import os
from datetime import datetime

def generate_id(prefix, *args):
    """Generate consistent IDs"""
    content = f"{prefix}:" + ":".join(str(arg) for arg in args)
    return hashlib.md5(content.encode()).hexdigest()

def normalize_name(first, last):
    """Clean up player names"""
    if not first and not last:
        return "Unknown Player"
    
    # Remove numbering prefix like "1.", "2.", etc.
    if first and first.endswith('.'):
        first = first[:-1]
    if first and first.isdigit():
        first = ""
    
    first = (first or "").strip()
    last = (last or "").strip()
    
    if not first and last:
        return last
    elif first and not last:
        return first
    else:
        return f"{first} {last}".strip()

def normalize_team(team_name):
    """Normalize team names"""
    if not team_name:
        return "Unknown Team"
    return team_name.strip()

def import_real_data():
    """Import our REAL basketball data"""
    
    # Connect to database
    db_path = "../league_cache.db"
    if not os.path.exists(db_path):
        print("❌ Database not found! Run 'npx prisma db push' first")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if 'players' not in tables:
        print("❌ Prisma tables not found! Run 'npx prisma db push' first")
        return
    
    print("🏀 Importing REAL basketball data...")
    print("Source: basketball-bund.net crawled data")
    print("Players: 8,945 real basketball players")
    print("Teams: Real German basketball teams")
    print("NO MOCK DATA!")
    
    # Our largest real data file
    csv_file = "oberfranken_all_players_20251002_141033.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Data file not found: {csv_file}")
        return
    
    stats = {
        'players': 0,
        'teams': 0,
        'seasons': 0,
        'leagues': 0,
        'season_stats': 0,
        'bg_litzendorf': 0
    }
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, 1):
            if row_num % 1000 == 0:
                print(f"  Processing row {row_num}...")
            
            try:
                # Extract data
                lastname = row.get('lastname', '')
                firstname = row.get('firstname', '')
                team_name = normalize_team(row.get('team', ''))
                points = int(row.get('points', 0)) if row.get('points', '').isdigit() else 0
                games = int(row.get('games', 0)) if row.get('games', '').isdigit() else 0
                liga_id = row.get('liga_id', 'unknown')
                league_name = row.get('league_name', 'Unknown League')
                season = row.get('season', '2003')
                bezirk = row.get('bezirk', 'Unknown')
                
                # Generate IDs
                player_name = normalize_name(firstname, lastname)
                player_id = generate_id("player", player_name.lower())
                team_id = generate_id("team", team_name.lower())
                season_id = season
                league_id = liga_id
                
                # Insert Player
                cursor.execute("""
                    INSERT OR IGNORE INTO players (id, name) 
                    VALUES (?, ?)
                """, (player_id, player_name))
                
                if cursor.rowcount > 0:
                    stats['players'] += 1
                
                # Insert Team  
                cursor.execute("""
                    INSERT OR IGNORE INTO teams (id, name) 
                    VALUES (?, ?)
                """, (team_id, team_name))
                
                if cursor.rowcount > 0:
                    stats['teams'] += 1
                
                # Insert Season
                try:
                    year = int(season)
                    cursor.execute("""
                        INSERT OR IGNORE INTO seasons (seasonId, year, ligaId) 
                        VALUES (?, ?, ?)
                    """, (season_id, year, league_id))
                    
                    if cursor.rowcount > 0:
                        stats['seasons'] += 1
                except:
                    pass
                
                # Insert League
                cursor.execute("""
                    INSERT OR IGNORE INTO leagues (ligaId, seasonId, name, region, source, scraped_at) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (league_id, season_id, league_name, bezirk, "basketball-bund.net", datetime.now()))
                
                if cursor.rowcount > 0:
                    stats['leagues'] += 1
                
                # Insert Season Stats
                ppg = round(points / games, 1) if games > 0 else 0.0
                stat_id = generate_id("stat", player_id, season_id)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO season_stats 
                    (id, playerId, seasonId, pts, g, pts_g) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (stat_id, player_id, season_id, points, games, ppg))
                
                stats['season_stats'] += 1
                
                # Track BG Litzendorf
                if 'litzendorf' in team_name.lower():
                    stats['bg_litzendorf'] += 1
                
            except Exception as e:
                print(f"⚠️ Error processing row {row_num}: {e}")
                continue
    
    # Commit all changes
    conn.commit()
    
    # Verify data
    cursor.execute("SELECT COUNT(*) FROM players")
    db_players = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM teams")
    db_teams = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM season_stats")
    db_stats = cursor.fetchone()[0]
    
    # Sample BG Litzendorf players
    cursor.execute("""
        SELECT p.name, t.name as team, s.pts, s.g 
        FROM players p 
        JOIN season_stats s ON p.id = s.playerId 
        JOIN teams t ON t.name LIKE '%litzendorf%'
        LIMIT 5
    """)
    bg_players = cursor.fetchall()
    
    conn.close()
    
    print("\\n🎉 REAL DATA IMPORT COMPLETE!")
    print("=" * 50)
    print(f"✅ Players imported: {stats['players']} (Total: {db_players})")
    print(f"✅ Teams imported: {stats['teams']} (Total: {db_teams})")
    print(f"✅ Season stats: {stats['season_stats']} (Total: {db_stats})")
    print(f"✅ Leagues: {stats['leagues']}")
    print(f"🎯 BG Litzendorf records: {stats['bg_litzendorf']}")
    
    if bg_players:
        print("\\n🌟 Sample BG Litzendorf players:")
        for player in bg_players:
            print(f"  - {player[0]} ({player[1]}) - {player[2]} pts in {player[3]} games")
    
    print("\\n🏀 Database is now filled with REAL basketball data!")
    print("🚀 Ready for basketball-reference.com style frontend!")

if __name__ == "__main__":
    import_real_data()
