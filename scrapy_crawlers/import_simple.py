"""
🏀 BASKETBALL DATA IMPORT - SIMPLIFIED VERSION 🏀
Import player statistics directly into the existing database structure
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

def import_csv_to_database():
    """Import basketball data from CSV files into the existing database"""
    
    # Database connection
    db_path = "../league_cache.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🏀🔥 BASKETBALL DATA IMPORT - SIMPLIFIED VERSION 🔥🏀")
        print(f"📁 Connected to database: {os.path.abspath(db_path)}")
        
        # CSV files to import
        csv_files = [
            "oberfranken_all_players_20251002_141033.csv",  # 8,944 players
            "BEAST_OBERFRANKEN_SEASON_2005_20251002_144710.csv",  # 3,754 players with metadata
            "sample_export.csv"
        ]
        
        total_imported = 0
        
        for csv_file in csv_files:
            if not os.path.exists(csv_file):
                print(f"⚠️ Skipping {csv_file} - file not found")
                continue
                
            print(f"\n📊 Processing {csv_file}...")
            
            try:
                # Read CSV
                df = pd.read_csv(csv_file)
                print(f"   📈 Found {len(df)} rows")
                print(f"   📋 Columns: {list(df.columns)}")
                
                # Import players into current_player_stats table
                imported_count = import_player_stats(cursor, df, csv_file)
                total_imported += imported_count
                
                print(f"   ✅ Imported {imported_count} player records")
                
            except Exception as e:
                print(f"   ❌ Error processing {csv_file}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print(f"\n🎉 IMPORT COMPLETE!")
        print(f"📊 Total records imported: {total_imported}")
        print("✅ Ready for basketball-reference.com style frontend!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def import_player_stats(cursor, df, source_file):
    """Import player statistics into current_player_stats table"""
    
    imported = 0
    
    for idx, row in df.iterrows():
        try:
            # Map the correct columns based on actual CSV structure
            if 'lastname' in df.columns:
                # oberfranken_all_players format: lastname=rank, firstname=lastname, team=firstname, points=team, games=points
                rank = str(row.get('lastname', '')).replace('.', '').strip()
                last_name = str(row.get('firstname', '')).strip()
                first_name = str(row.get('team', '')).strip()
                team_name = str(row.get('points', 'Unknown Team')).strip()
                points_total = int(row.get('games', 0)) if pd.notna(row.get('games')) else 0
                league_id = int(row.get('liga_id', 0)) if pd.notna(row.get('liga_id')) else 0
                season = str(row.get('season', '2003')).strip()
                league_name = str(row.get('league_name', 'Unknown League')).strip()
                
                # Construct full player name
                player_name = f"{first_name} {last_name}".strip()
                games_played = 1  # Assume 1 game since we don't have games data
                
            elif 'Name' in df.columns:
                # Different format
                player_name = str(row.get('Name', 'Unknown')).strip()
                team_name = str(row.get('Team', 'Unknown Team')).strip()
                points_total = int(row.get('Points', 0)) if pd.notna(row.get('Points')) else 0
                games_played = int(row.get('Games', 1)) if pd.notna(row.get('Games')) else 1
                league_id = 1000  # Default
                season = '2024/25'
                league_name = 'Unknown League'
                
            else:
                # sample_export format or other
                player_name = f"{row.get('first_name', '')} {row.get('surname', '')}".strip()
                team_name = str(row.get('team', 'Unknown Team')).strip()
                points_total = int(row.get('points', 0)) if pd.notna(row.get('points')) else 0
                games_played = int(row.get('games', 1)) if pd.notna(row.get('games')) else 1
                league_id = int(row.get('liga_id', 1000)) if pd.notna(row.get('liga_id')) else 1000
                season = str(row.get('season_id', '2024/25')).strip()
                league_name = 'Export League'
            
            # Validate required fields
            if not player_name or player_name == 'Unknown' or pd.isna(player_name) or player_name.strip() == '':
                continue
            if not team_name or team_name == 'Unknown Team':
                continue
            
            # Set default values for missing stats
            rebounds_total = 0  # Not available in these CSVs
            assists_total = 0   # Not available in these CSVs
            
            # Calculate averages
            points_avg = points_total / games_played if games_played > 0 else 0
            
            # Create season string
            if season.isdigit() and len(season) == 4:
                season_year = int(season)
                season = f"{season_year}/{str(season_year + 1)[-2:]}"
            
            # Generate unique ID
            player_id = f"player_{abs(hash(f'{player_name}_{team_name}_{season}'))}_{idx}"
            
            # Insert into database
            cursor.execute("""
                INSERT OR REPLACE INTO current_player_stats (
                    id, player_name, team_name, league_id, games_played,
                    points_total, points_avg, rebounds_total, assists_total,
                    season, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                player_name,
                team_name,
                league_id,
                games_played,
                points_total,
                round(points_avg, 1),
                rebounds_total,
                assists_total,
                season,
                datetime.now().isoformat()
            ))
            
            imported += 1
            
            # Progress indicator
            if imported % 500 == 0:
                print(f"     📈 Processed {imported} players...")
                
        except Exception as e:
            print(f"     ⚠️ Error with row {idx}: {e}")
            continue
    
    return imported

def create_api_test_endpoint():
    """Create a simple test to verify our data"""
    
    db_path = "../league_cache.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 TESTING DATA ACCESS...")
        
        # Get total players
        cursor.execute("SELECT COUNT(*) FROM current_player_stats")
        total_players = cursor.fetchone()[0]
        print(f"📊 Total players in database: {total_players}")
        
        # Get top scorers
        cursor.execute("""
            SELECT player_name, team_name, points_avg, games_played, season
            FROM current_player_stats 
            WHERE games_played > 5
            ORDER BY points_avg DESC 
            LIMIT 10
        """)
        
        top_scorers = cursor.fetchall()
        print(f"\n🏆 TOP 10 SCORERS:")
        for i, (name, team, ppg, games, season) in enumerate(top_scorers, 1):
            print(f"   {i:2d}. {name} ({team}) - {ppg:.1f} PPG ({games} games, {season})")
        
        # Get teams
        cursor.execute("SELECT DISTINCT team_name FROM current_player_stats ORDER BY team_name")
        teams = cursor.fetchall()
        print(f"\n🏀 Found {len(teams)} teams:")
        for team in teams[:10]:  # Show first 10
            print(f"   - {team[0]}")
        if len(teams) > 10:
            print(f"   ... and {len(teams) - 10} more")
        
        # Get seasons
        cursor.execute("SELECT DISTINCT season FROM current_player_stats ORDER BY season DESC")
        seasons = cursor.fetchall()
        print(f"\n📅 Available seasons: {[s[0] for s in seasons]}")
        
        conn.close()
        
        print("\n✅ Database is ready for the frontend!")
        print("🎯 You can now use the API endpoints:")
        print("   GET /api/players - List all players")
        print("   GET /api/players/{id} - Get player profile")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    import_csv_to_database()
    create_api_test_endpoint()
