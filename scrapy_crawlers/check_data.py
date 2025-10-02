#!/usr/bin/env python3
import json

try:
    with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        print(f"✅ Found {len(data)} players in list format")
        if data:
            sample = data[0]
            print(f"Sample player: {sample.get('name', 'No name')} - Team: {sample.get('team', 'No team')}")
    elif isinstance(data, dict) and 'players' in data:
        players = data['players']
        print(f"✅ Found {len(players)} players in dict format")
        if players:
            sample = players[0]
            print(f"Sample player: {sample.get('name', 'No name')} - Team: {sample.get('team', 'No team')}")
    else:
        print("❌ Unexpected data format")
        print(f"Data type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")

except FileNotFoundError:
    print("❌ File 'real_players_extracted.json' not found")
except json.JSONDecodeError as e:
    print(f"❌ JSON decode error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
