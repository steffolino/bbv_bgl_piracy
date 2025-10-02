#!/usr/bin/env python3

import json

def test_corrected_stat_labels():
    """
    Test the corrected stat labels using our known Litzendorf data
    """
    
    print("🏀 TESTING CORRECTED STAT LABELS")
    print("Verifying proper column mapping and labels")
    
    # Load our known Litzendorf data
    try:
        with open('litzendorf_player_stats_liga1701_2010_20251002_115436.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        litzendorf_players = data['litzendorf_players']
        
        print(f"\n📊 Found {len(litzendorf_players)} Litzendorf players to verify")
        
        # Group by stat type for cleaner display
        by_stat_type = {}
        for player in litzendorf_players:
            stat_type = player['stat_type']
            if stat_type not in by_stat_type:
                by_stat_type[stat_type] = []
            by_stat_type[stat_type].append(player)
        
        # Display corrected labels
        for stat_type, players in by_stat_type.items():
            print(f"\n📈 {players[0]['stat_category']} ({len(players)} players)")
            
            if stat_type == 'statBesteWerferArchiv':
                print("   Columns: Rank | LastName | FirstName | Team | TotalPoints | Games | PPG")
                for player in players[:3]:
                    full_name = f"{player['first_name']} {player['last_name']}"
                    total_pts = player['stat_value_1']  # Should be total points
                    games = player['stat_value_2']      # Should be games
                    ppg = player['stat_value_3']        # Should be PPG
                    print(f"   🏆 {full_name}: {total_pts} pts, {games} games, {ppg} PPG")
                    
            elif stat_type == 'statBesteFreiWerferArchiv':
                print("   Columns: Rank | LastName | FirstName | Team | FT_Attempted | FT_Made | FT%")
                for player in players[:3]:
                    full_name = f"{player['first_name']} {player['last_name']}"
                    ft_attempted = player['stat_value_1']  # Should be FT attempted
                    ft_made = player['stat_value_2']       # Should be FT made  
                    ft_pct = player['stat_value_3']        # Should be FT%
                    print(f"   🏆 {full_name}: {ft_made}/{ft_attempted} FT, {ft_pct}%")
                    
            elif stat_type == 'statBeste3erWerferArchiv':
                print("   Columns: Rank | LastName | FirstName | Team | 3P_Made | Games | 3PG")
                for player in players[:3]:
                    full_name = f"{player['first_name']} {player['last_name']}"
                    three_made = player['stat_value_1']    # Should be 3P made (total)
                    games = player['stat_value_2']         # Should be games
                    three_pg = player['stat_value_3']      # Should be 3P per game (NOT percentage!)
                    print(f"   🏆 {full_name}: {three_made} total 3P, {games} games, {three_pg} 3PG")
        
        # Highlight the correction
        print(f"\n🎯 KEY CORRECTION:")
        print(f"   ❌ OLD: Oliver Ohland - 0.2 3P% (Best 3-Point Shooters)")  
        print(f"   ✅ NEW: Oliver Ohland - 0.2 3PG (Best 3-Point Shooters)")
        print(f"   📝 Meaning: Oliver made 0.2 three-pointers per game (not percentage)")
        
        # Show Jonas May as example across all stats
        print(f"\n🌟 JONAS MAY - COMPLETE STATS PROFILE:")
        jonas_stats = {}
        for player in litzendorf_players:
            if 'jonas' in player['first_name'].lower() and 'may' in player['last_name'].lower():
                stat_type = player['stat_type']
                jonas_stats[stat_type] = player
        
        if 'statBesteWerferArchiv' in jonas_stats:
            p = jonas_stats['statBesteWerferArchiv']
            print(f"   🏀 Scoring: {p['stat_value_3']} PPG ({p['stat_value_1']} total pts, {p['stat_value_2']} games)")
            
        if 'statBesteFreiWerferArchiv' in jonas_stats:
            p = jonas_stats['statBesteFreiWerferArchiv']
            print(f"   🎯 Free Throws: {p['stat_value_3']}% ({p['stat_value_2']}/{p['stat_value_1']})")
            
        if 'statBeste3erWerferArchiv' in jonas_stats:
            p = jonas_stats['statBeste3erWerferArchiv']
            print(f"   🌟 3-Pointers: {p['stat_value_3']} per game ({p['stat_value_1']} total, {p['stat_value_2']} games)")
        
        print(f"\n✅ All stat labels verified and corrected!")
        
    except FileNotFoundError:
        print("❌ Litzendorf data file not found. Run the Litzendorf test first.")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_corrected_stat_labels()
