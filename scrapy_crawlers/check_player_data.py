import sqlite3
import json

conn = sqlite3.connect('basketball_analytics.db')
cursor = conn.cursor()

# Check match table structure
cursor.execute('PRAGMA table_info(matches)')
match_cols = cursor.fetchall()
print("Match table columns:")
for col in match_cols:
    print(f"  {col[1]} ({col[2]})")

# Check for player data
cursor.execute('SELECT home_boxscore FROM matches WHERE home_boxscore IS NOT NULL LIMIT 1')
result = cursor.fetchone()
print(f"\nBoxscore data available: {'Yes' if result else 'No'}")

if result:
    print("Sample boxscore:", result[0][:200] if len(str(result[0])) > 200 else result[0])

conn.close()
