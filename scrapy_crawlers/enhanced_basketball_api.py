#!/usr/bin/env python3
"""
Enhanced Basketball Analytics API Bridge
Serves real basketball data for player-centric analytics platform
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_basketball_db():
    """Get basketball analytics database connection"""
    return sqlite3.connect('basketball_analytics.db')

def get_crawl_db():
    """Get crawl logs database connection"""
    return sqlite3.connect('crawl_logs.db')

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM matches')
        match_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM teams')
        team_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'matches': match_count,
            'teams': team_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/dashboard')
def dashboard():
    """Dashboard overview with real basketball statistics"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute('SELECT COUNT(*) FROM matches')
        total_matches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM matches WHERE home_score > 0 OR guest_score > 0')
        completed_matches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teams')
        total_teams = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT league_id) FROM leagues')
        total_leagues = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT season_year) FROM seasons')
        total_seasons = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(season_year), MAX(season_year) FROM seasons')
        min_year, max_year = cursor.fetchone()
        
        # Recent activity
        cursor.execute('''
            SELECT m.kickoff_date, m.home_team_name, m.guest_team_name, m.result
            FROM matches m
            WHERE m.home_score > 0 OR m.guest_score > 0
            ORDER BY m.kickoff_date DESC
            LIMIT 10
        ''')
        recent_matches = cursor.fetchall()
        
        # Top scoring matches
        cursor.execute('''
            SELECT m.home_team_name, m.guest_team_name, m.result, 
                   (m.home_score + m.guest_score) as total_points
            FROM matches m
            WHERE m.home_score > 0 AND m.guest_score > 0
            ORDER BY total_points DESC
            LIMIT 10
        ''')
        top_scoring = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'overview': {
                'total_matches': total_matches,
                'completed_matches': completed_matches,
                'total_teams': total_teams,
                'total_leagues': total_leagues,
                'seasons_covered': total_seasons,
                'year_range': f"{min_year}-{max_year}",
                'completion_rate': round(completed_matches / max(total_matches, 1) * 100, 1)
            },
            'recent_matches': [
                {
                    'date': match[0],
                    'home_team': match[1],
                    'guest_team': match[2],
                    'result': match[3]
                } for match in recent_matches
            ],
            'top_scoring_games': [
                {
                    'home_team': match[0],
                    'guest_team': match[1],
                    'result': match[2],
                    'total_points': match[3]
                } for match in top_scoring
            ]
        })
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams')
def teams():
    """Get all teams with their statistics"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        # Get teams with their latest season stats
        cursor.execute('''
            SELECT t.team_permanent_id, t.team_name, t.team_name_small,
                   t.first_seen_season, t.last_seen_season, t.total_seasons,
                   ts.games_played, ts.wins, ts.losses, ts.avg_points_for, ts.avg_points_against
            FROM teams t
            LEFT JOIN team_season_stats ts ON t.team_permanent_id = ts.team_permanent_id 
                AND ts.season_year = t.last_seen_season
            ORDER BY t.team_name
        ''')
        teams_data = cursor.fetchall()
        
        teams = []
        for team in teams_data:
            teams.append({
                'id': team[0],
                'name': team[1],
                'short_name': team[2],
                'first_season': team[3],
                'last_season': team[4],
                'total_seasons': team[5],
                'latest_stats': {
                    'games': team[6] or 0,
                    'wins': team[7] or 0,
                    'losses': team[8] or 0,
                    'ppg': round(team[9] or 0, 1),
                    'papg': round(team[10] or 0, 1),
                    'win_pct': round((team[7] or 0) / max(team[6] or 1, 1) * 100, 1)
                }
            })
        
        conn.close()
        return jsonify(teams)
        
    except Exception as e:
        logger.error(f"Teams error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/teams/<int:team_id>')
def team_detail(team_id):
    """Get detailed team information including season history"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        # Team basic info
        cursor.execute('''
            SELECT team_permanent_id, team_name, team_name_small, club_id,
                   first_seen_season, last_seen_season, total_seasons
            FROM teams WHERE team_permanent_id = ?
        ''', (team_id,))
        team_info = cursor.fetchone()
        
        if not team_info:
            return jsonify({'error': 'Team not found'}), 404
        
        # Season history
        cursor.execute('''
            SELECT season_year, league_id, games_played, wins, losses,
                   points_for, points_against, avg_points_for, avg_points_against,
                   point_differential
            FROM team_season_stats
            WHERE team_permanent_id = ?
            ORDER BY season_year DESC
        ''', (team_id,))
        season_stats = cursor.fetchall()
        
        # Recent matches
        cursor.execute('''
            SELECT match_id, season_year, kickoff_date, 
                   CASE WHEN home_team_id = ? THEN guest_team_name ELSE home_team_name END as opponent,
                   CASE WHEN home_team_id = ? THEN 'home' ELSE 'away' END as venue,
                   result, home_score, guest_score
            FROM matches
            WHERE (home_team_id = ? OR guest_team_id = ?) 
                AND (home_score > 0 OR guest_score > 0)
            ORDER BY kickoff_date DESC
            LIMIT 20
        ''', (team_id, team_id, team_id, team_id))
        recent_matches = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'team': {
                'id': team_info[0],
                'name': team_info[1],
                'short_name': team_info[2],
                'club_id': team_info[3],
                'first_season': team_info[4],
                'last_season': team_info[5],
                'total_seasons': team_info[6]
            },
            'season_history': [
                {
                    'season': stat[0],
                    'league_id': stat[1],
                    'games': stat[2],
                    'wins': stat[3],
                    'losses': stat[4],
                    'points_for': stat[5],
                    'points_against': stat[6],
                    'ppg': round(stat[7], 1),
                    'papg': round(stat[8], 1),
                    'differential': round(stat[9], 1),
                    'win_pct': round(stat[3] / max(stat[2], 1) * 100, 1)
                } for stat in season_stats
            ],
            'recent_matches': [
                {
                    'match_id': match[0],
                    'season': match[1],
                    'date': match[2],
                    'opponent': match[3],
                    'venue': match[4],
                    'result': match[5],
                    'score': f"{match[6]}:{match[7]}" if match[6] and match[7] else match[5]
                } for match in recent_matches
            ]
        })
        
    except Exception as e:
        logger.error(f"Team detail error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/leagues')
def leagues():
    """Get all leagues with statistics"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT l.league_id, l.name, l.district_name,
                   COUNT(DISTINCT s.season_year) as seasons,
                   COUNT(DISTINCT m.match_id) as total_matches,
                   COUNT(DISTINCT CASE WHEN m.home_score > 0 OR m.guest_score > 0 THEN m.match_id END) as completed_matches
            FROM leagues l
            LEFT JOIN seasons s ON l.league_id = s.league_id
            LEFT JOIN matches m ON l.league_id = m.league_id
            GROUP BY l.league_id, l.name, l.district_name
            ORDER BY seasons DESC, completed_matches DESC
        ''')
        leagues_data = cursor.fetchall()
        
        leagues = []
        for league in leagues_data:
            leagues.append({
                'id': league[0],
                'name': league[1] or f"League {league[0]}",
                'district': league[2] or "Unknown",
                'seasons': league[3] or 0,
                'total_matches': league[4] or 0,
                'completed_matches': league[5] or 0,
                'completion_rate': round((league[5] or 0) / max(league[4] or 1, 1) * 100, 1)
            })
        
        conn.close()
        return jsonify(leagues)
        
    except Exception as e:
        logger.error(f"Leagues error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/seasons')
def seasons():
    """Get all seasons with statistics"""
    try:
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.season_year, COUNT(DISTINCT s.league_id) as leagues,
                   SUM(s.total_matches) as total_matches,
                   SUM(s.completed_matches) as completed_matches,
                   COUNT(DISTINCT ts.team_permanent_id) as teams
            FROM seasons s
            LEFT JOIN team_season_stats ts ON s.season_year = ts.season_year
            GROUP BY s.season_year
            ORDER BY s.season_year DESC
        ''')
        seasons_data = cursor.fetchall()
        
        seasons = []
        for season in seasons_data:
            seasons.append({
                'year': season[0],
                'leagues': season[1],
                'total_matches': season[2] or 0,
                'completed_matches': season[3] or 0,
                'teams': season[4] or 0,
                'completion_rate': round((season[3] or 0) / max(season[2] or 1, 1) * 100, 1)
            })
        
        conn.close()
        return jsonify(seasons)
        
    except Exception as e:
        logger.error(f"Seasons error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/matches')
def matches():
    """Get matches with optional filtering"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 200)
        team_id = request.args.get('team_id')
        season = request.args.get('season')
        league_id = request.args.get('league_id')
        
        offset = (page - 1) * limit
        
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if team_id:
            where_conditions.append('(m.home_team_id = ? OR m.guest_team_id = ?)')
            params.extend([team_id, team_id])
        
        if season:
            where_conditions.append('m.season_year = ?')
            params.append(season)
            
        if league_id:
            where_conditions.append('m.league_id = ?')
            params.append(league_id)
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Get matches
        cursor.execute(f'''
            SELECT m.match_id, m.season_year, m.league_id, m.kickoff_date, m.kickoff_time,
                   m.home_team_name, m.guest_team_name, m.result, m.home_score, m.guest_score,
                   m.confirmed, m.cancelled, m.forfeit
            FROM matches m
            WHERE {where_clause}
            ORDER BY m.kickoff_date DESC, m.kickoff_time DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])
        
        matches_data = cursor.fetchall()
        
        # Get total count
        cursor.execute(f'SELECT COUNT(*) FROM matches m WHERE {where_clause}', params)
        total_count = cursor.fetchone()[0]
        
        matches = []
        for match in matches_data:
            matches.append({
                'id': match[0],
                'season': match[1],
                'league_id': match[2],
                'date': match[3],
                'time': match[4],
                'home_team': match[5],
                'guest_team': match[6],
                'result': match[7],
                'home_score': match[8],
                'guest_score': match[9],
                'confirmed': bool(match[10]),
                'cancelled': bool(match[11]),
                'forfeit': bool(match[12])
            })
        
        conn.close()
        
        return jsonify({
            'matches': matches,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logger.error(f"Matches error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-teams')
def top_teams():
    """Get top performing teams by various metrics"""
    try:
        metric = request.args.get('metric', 'differential')  # differential, ppg, wins
        season = request.args.get('season')
        limit = min(int(request.args.get('limit', 20)), 100)
        
        conn = get_basketball_db()
        cursor = conn.cursor()
        
        # Build query based on metric
        order_by = 'ts.point_differential DESC'
        if metric == 'ppg':
            order_by = 'ts.avg_points_for DESC'
        elif metric == 'wins':
            order_by = 'ts.wins DESC, (ts.wins * 1.0 / ts.games_played) DESC'
        
        where_clause = 'ts.games_played >= 5'
        params = []
        
        if season:
            where_clause += ' AND ts.season_year = ?'
            params.append(season)
        
        cursor.execute(f'''
            SELECT t.team_name, ts.season_year, ts.league_id, ts.games_played,
                   ts.wins, ts.losses, ts.avg_points_for, ts.avg_points_against,
                   ts.point_differential, (ts.wins * 1.0 / ts.games_played * 100) as win_pct
            FROM team_season_stats ts
            JOIN teams t ON ts.team_permanent_id = t.team_permanent_id
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ?
        ''', params + [limit])
        
        teams_data = cursor.fetchall()
        
        teams = []
        for team in teams_data:
            teams.append({
                'name': team[0],
                'season': team[1],
                'league_id': team[2],
                'games': team[3],
                'wins': team[4],
                'losses': team[5],
                'ppg': round(team[6], 1),
                'papg': round(team[7], 1),
                'differential': round(team[8], 1),
                'win_pct': round(team[9], 1)
            })
        
        conn.close()
        return jsonify(teams)
        
    except Exception as e:
        logger.error(f"Top teams error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/sessions')
def crawl_sessions():
    """Get crawl session information"""
    try:
        conn = get_crawl_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_name, spider_name, start_time, end_time, status,
                   total_requests, successful_requests, items_scraped
            FROM crawl_sessions
            ORDER BY start_time DESC
        ''')
        sessions = cursor.fetchall()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'name': session[0],
                'spider': session[1],
                'start_time': session[2],
                'end_time': session[3],
                'status': session[4],
                'requests': session[5],
                'successful': session[6],
                'items': session[7]
            })
        
        conn.close()
        return jsonify(session_list)
        
    except Exception as e:
        logger.error(f"Crawl sessions error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏀 Starting Enhanced Basketball Analytics API")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET /health - Health check")
    print("  GET /api/dashboard - Dashboard overview")
    print("  GET /api/teams - All teams")
    print("  GET /api/teams/<id> - Team details")
    print("  GET /api/leagues - All leagues")
    print("  GET /api/seasons - All seasons")
    print("  GET /api/matches - Matches (with filtering)")
    print("  GET /api/analytics/top-teams - Top performing teams")
    print("  GET /api/crawl/sessions - Crawl sessions")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
