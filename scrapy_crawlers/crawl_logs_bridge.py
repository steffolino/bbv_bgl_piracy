#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
from crawl_logs_api import CrawlLogsAPI
import os
import sys

# Add the scrapy project to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the crawl logs API
crawl_api = CrawlLogsAPI('crawl_logs.db')

@app.route('/api/crawl/sessions', methods=['GET'])
def get_crawl_sessions():
    """Get recent crawl sessions"""
    try:
        limit = int(request.args.get('limit', 20))
        sessions = crawl_api.get_recent_sessions(limit)
        
        return jsonify({
            'sessions': [
                {
                    'id': s.id,
                    'session_name': s.session_name,
                    'spider_name': s.spider_name,
                    'start_time': s.start_time,
                    'end_time': s.end_time,
                    'status': s.status,
                    'total_requests': s.total_requests,
                    'successful_requests': s.successful_requests,
                    'failed_requests': s.failed_requests,
                    'items_scraped': s.items_scraped,
                    'leagues_discovered': s.leagues_discovered,
                    'duration_minutes': s.duration_minutes
                }
                for s in sessions
            ],
            'total': len(sessions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/sessions/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed session information"""
    try:
        details = crawl_api.get_session_details(session_id)
        if not details:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/logs/search', methods=['GET'])
def search_logs():
    """Search crawl logs"""
    try:
        session_id = request.args.get('session_id')
        level = request.args.get('level')
        search_term = request.args.get('search')
        league_id = request.args.get('league_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        logs = crawl_api.search_logs(
            session_id=session_id,
            level=level,
            search_term=search_term,
            league_id=league_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'logs': [
                {
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'level': log.level,
                    'logger_name': log.logger_name,
                    'message': log.message,
                    'url': log.url,
                    'response_status': log.response_status,
                    'response_time_ms': log.response_time_ms,
                    'league_id': log.league_id,
                    'season_year': log.season_year,
                    'match_count': log.match_count,
                    'metadata': log.metadata
                }
                for log in logs
            ],
            'total': len(logs),
            'filters': {
                'session_id': session_id,
                'level': level,
                'search_term': search_term,
                'league_id': league_id,
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/discoveries', methods=['GET'])
def search_discoveries():
    """Search crawl discoveries"""
    try:
        session_id = request.args.get('session_id')
        league_name = request.args.get('league_name')
        district_name = request.args.get('district_name')
        min_matches = int(request.args.get('min_matches', 0)) if request.args.get('min_matches') else None
        season_year = int(request.args.get('season_year')) if request.args.get('season_year') else None
        data_quality = request.args.get('data_quality')
        limit = int(request.args.get('limit', 100))
        
        discoveries = crawl_api.search_discoveries(
            session_id=session_id,
            league_name=league_name,
            district_name=district_name,
            min_matches=min_matches,
            season_year=season_year,
            data_quality=data_quality,
            limit=limit
        )
        
        return jsonify({
            'discoveries': [
                {
                    'id': d.id,
                    'league_id': d.league_id,
                    'season_year': d.season_year,
                    'league_name': d.league_name,
                    'district_name': d.district_name,
                    'match_count': d.match_count,
                    'team_count': d.team_count,
                    'data_quality': d.data_quality,
                    'discovery_phase': d.discovery_phase,
                    'url': d.url,
                    'discovered_at': d.discovered_at
                }
                for d in discoveries
            ],
            'total': len(discoveries)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/statistics', methods=['GET'])
def get_crawl_statistics():
    """Get crawl statistics"""
    try:
        days = int(request.args.get('days', 30))
        stats = crawl_api.get_crawl_statistics(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/league/<league_id>/history', methods=['GET'])
def get_league_history(league_id):
    """Get discovery history for a specific league"""
    try:
        history = crawl_api.get_league_discovery_history(league_id)
        return jsonify({
            'league_id': league_id,
            'history': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crawl/sessions/<session_id>/report', methods=['GET'])
def export_session_report(session_id):
    """Export comprehensive session report"""
    try:
        report = crawl_api.export_session_report(session_id)
        if not report:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'crawl-logs-api',
        'timestamp': '2025-09-29T14:00:00Z'
    })

if __name__ == '__main__':
    print("🚀 Starting Crawl Logs API Bridge...")
    print("📊 Available endpoints:")
    print("   GET /api/crawl/sessions")
    print("   GET /api/crawl/sessions/<id>")
    print("   GET /api/crawl/logs/search")
    print("   GET /api/crawl/discoveries")
    print("   GET /api/crawl/statistics")
    print("   GET /api/crawl/league/<id>/history")
    print("   GET /health")
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
