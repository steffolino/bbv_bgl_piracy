"""
Basketball Statistics API
Provides REST endpoints for custom stats and player card generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from basketball_stats_engine import BasketballStatsEngine
from team_analyzer import TeamAnalyzer
import tempfile
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize the stats engine and team analyzer
stats_engine = BasketballStatsEngine('real_players_extracted.json')
team_analyzer = TeamAnalyzer('real_players_extracted.json')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'players_count': len(stats_engine.players_data)})

@app.route('/api/players/advanced-stats', methods=['POST'])
def calculate_advanced_stats():
    """Calculate advanced statistics for a player"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        
        # Find player
        player = next((p for p in stats_engine.players_data if p.get('name', '').lower() == player_name.lower()), None)
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        advanced_stats = stats_engine.calculate_advanced_stats(player)
        
        return jsonify({
            'player': player,
            'advanced_stats': advanced_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/custom-stat', methods=['POST'])
def calculate_custom_stat():
    """Calculate custom statistic for all players"""
    try:
        data = request.get_json()
        formula = data.get('formula')
        stat_name = data.get('name', 'Custom Stat')
        
        if not formula:
            return jsonify({'error': 'Formula is required'}), 400
        
        results = []
        
        for player in stats_engine.players_data:
            try:
                result = stats_engine.create_custom_stat(formula, player)
                if result is not None:
                    results.append({
                        'name': player.get('name', 'Unknown'),
                        'team': player.get('team', 'Unknown'),
                        'value': result,
                        'rank': 0  # Will be set after sorting
                    })
            except Exception as e:
                print(f"Error calculating stat for {player.get('name')}: {e}")
        
        # Sort by value descending and assign ranks
        results.sort(key=lambda x: x['value'], reverse=True)
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return jsonify({
            'stat_name': stat_name,
            'formula': formula,
            'results': results[:100]  # Limit to top 100
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/card', methods=['POST'])
def generate_player_card():
    """Generate vintage basketball card for a player"""
    try:
        data = request.get_json()
        player_name = data.get('player_name')
        style = data.get('style', 'vintage')
        
        if not player_name:
            return jsonify({'error': 'Player name is required'}), 400
        
        # Generate card
        card_data = stats_engine.generate_player_card(player_name, style=style)
        
        if not card_data:
            return jsonify({'error': 'Player not found or card generation failed'}), 404
        
        return jsonify({
            'image_base64': card_data['image_base64'],
            'player': card_data['player'],
            'advanced_stats': card_data['advanced_stats']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/bulk-cards', methods=['POST'])
def generate_bulk_cards():
    """Generate cards for multiple players"""
    try:
        data = request.get_json()
        method = data.get('method', 'top')
        count = data.get('count', 10)
        category = data.get('category')
        team = data.get('team')
        style = data.get('style', 'vintage')
        
        players_to_process = []
        
        if method == 'top':
            # Get top players by points
            sorted_players = sorted(stats_engine.players_data, 
                                  key=lambda p: float(p.get('points', 0)), reverse=True)
            players_to_process = sorted_players[:count]
        elif method == 'category' and category:
            players_to_process = [p for p in stats_engine.players_data 
                                if p.get('endpoint') == category][:20]
        elif method == 'team' and team:
            players_to_process = [p for p in stats_engine.players_data 
                                if p.get('team') == team][:20]
        
        cards = []
        for player in players_to_process:
            card_data = stats_engine.generate_player_card(player.get('name'), style=style)
            if card_data:
                cards.append({
                    'image_base64': card_data['image_base64'],
                    'player_name': player.get('name'),
                    'team': player.get('team')
                })
        
        return jsonify({
            'cards': cards,
            'total_generated': len(cards)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export filtered player data as CSV"""
    try:
        data = request.get_json()
        players = data.get('players', stats_engine.players_data)
        filename = data.get('filename', 'basketball_export')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            export_path = stats_engine.export_table_data(players, 'csv', filename)
            
        return send_file(export_path, as_attachment=True, download_name=f"{filename}.csv")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/charts', methods=['GET'])
def get_dashboard_charts():
    """Get interactive charts for statistics dashboard"""
    try:
        charts = stats_engine.create_statistics_dashboard()
        return jsonify(charts)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/top/<int:count>', methods=['GET'])
def get_top_players(count):
    """Get top N players by points"""
    try:
        sorted_players = sorted(stats_engine.players_data, 
                              key=lambda p: float(p.get('points', 0)), reverse=True)
        top_players = sorted_players[:count]
        
        # Add advanced stats to each player
        for player in top_players:
            player['advanced_stats'] = stats_engine.calculate_advanced_stats(player)
        
        return jsonify({
            'players': top_players,
            'total_count': len(stats_engine.players_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Team endpoints
@app.route('/api/teams', methods=['GET'])
def get_all_teams():
    """Get list of all teams"""
    try:
        teams = team_analyzer.get_all_teams()
        return jsonify({
            'teams': teams,
            'total_count': len(teams)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/search', methods=['GET'])
def search_teams():
    """Search teams by name"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter q is required'}), 400
        
        teams = team_analyzer.search_teams(query)
        return jsonify({
            'teams': teams,
            'query': query
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/<team_name>', methods=['GET'])
def get_team_details(team_name):
    """Get detailed team information"""
    try:
        league_id = request.args.get('league_id', type=int)
        season_id = request.args.get('season_id', type=int)
        
        # Debug logging
        print(f"🔍 API Call: team='{team_name}', league={league_id}, season={season_id}")
        print(f"📝 Available teams containing '{team_name.lower()}':")
        
        # Find similar team names
        similar_teams = []
        for existing_team in team_analyzer.teams.keys():
            if team_name.lower() in existing_team.lower() or existing_team.lower() in team_name.lower():
                similar_teams.append(existing_team)
                print(f"   - '{existing_team}'")
        
        team_details = team_analyzer.get_team_details(team_name, league_id, season_id)
        
        if not team_details:
            print(f"❌ No team details found for '{team_name}'")
            # Return helpful error with suggestions
            return jsonify({
                'error': 'Team not found',
                'searched_for': team_name,
                'similar_teams': similar_teams[:10],
                'suggestion': similar_teams[0] if similar_teams else None
            }), 404
        
        print(f"✅ Found team: {team_details['roster_size']} players")
        return jsonify(team_details)
    
    except Exception as e:
        print(f"💥 API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/leagues/<int:league_id>/standings', methods=['GET'])
def get_league_standings(league_id):
    """Get league standings"""
    try:
        season_id = request.args.get('season_id', type=int)
        if not season_id:
            return jsonify({'error': 'season_id parameter is required'}), 400
        
        standings = team_analyzer.get_league_standings(league_id, season_id)
        return jsonify(standings)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/teams', methods=['GET'])
def debug_teams():
    """Debug endpoint to see available teams"""
    try:
        league_id = request.args.get('league_id', type=int)
        season_id = request.args.get('season_id', type=int)
        
        # Get all teams
        all_teams = {}
        litzendorf_teams = []
        
        for player in stats_engine.players_data:
            team = player.get('team', '')
            liga = player.get('liga_id')
            season = player.get('season_id')
            
            # Track all teams
            key = f"{team}|{liga}|{season}"
            if key in all_teams:
                all_teams[key] += 1
            else:
                all_teams[key] = 1
            
            # Track Litzendorf variations
            if 'litzendorf' in team.lower():
                litzendorf_teams.append({
                    'team': team,
                    'liga_id': liga,
                    'season_id': season,
                    'player': player.get('name', 'Unknown')
                })
        
        # Filter by league/season if provided
        filtered_teams = {}
        if league_id and season_id:
            for key, count in all_teams.items():
                team, liga, season = key.split('|')
                if int(liga) == league_id and int(season) == season_id:
                    filtered_teams[team] = count
        
        return jsonify({
            'total_teams': len(all_teams),
            'filtered_teams': filtered_teams if league_id and season_id else {},
            'litzendorf_variations': litzendorf_teams[:20],  # Limit to first 20
            'query': {
                'league_id': league_id,
                'season_id': season_id
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org_name>', methods=['GET'])
def get_organization_info(org_name):
    """Get organization/verein information"""
    try:
        org_info = team_analyzer.get_organization_info(org_name)
        return jsonify({
            'organization': org_info,
            'name': org_name
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
