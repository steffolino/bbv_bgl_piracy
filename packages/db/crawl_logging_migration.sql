-- Migration to add crawl logging tables
-- This should be added to a new migration file

CREATE TABLE crawl_sessions (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  session_name TEXT NOT NULL,
  spider_name TEXT NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME,
  status TEXT NOT NULL DEFAULT 'running', -- 'running', 'completed', 'failed', 'aborted'
  total_requests INTEGER DEFAULT 0,
  successful_requests INTEGER DEFAULT 0,
  failed_requests INTEGER DEFAULT 0,
  items_scraped INTEGER DEFAULT 0,
  leagues_discovered INTEGER DEFAULT 0,
  error_message TEXT,
  configuration TEXT, -- JSON string of spider configuration
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crawl_logs (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  session_id TEXT NOT NULL REFERENCES crawl_sessions(id),
  timestamp DATETIME NOT NULL,
  level TEXT NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
  logger_name TEXT NOT NULL,
  message TEXT NOT NULL,
  url TEXT,
  response_status INTEGER,
  response_time_ms INTEGER,
  league_id TEXT,
  season_year INTEGER,
  match_count INTEGER,
  error_details TEXT, -- JSON string for detailed error info
  metadata TEXT, -- JSON string for additional context
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crawl_discoveries (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  session_id TEXT NOT NULL REFERENCES crawl_sessions(id),
  league_id TEXT NOT NULL,
  season_year INTEGER NOT NULL,
  league_name TEXT,
  district_name TEXT,
  match_count INTEGER DEFAULT 0,
  team_count INTEGER DEFAULT 0,
  data_quality TEXT, -- 'complete', 'partial', 'minimal'
  discovery_phase TEXT, -- 'confirmed_expansion', 'systematic_discovery', 'adjacent_exploration'
  url TEXT NOT NULL,
  response_time_ms INTEGER,
  discovered_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crawl_errors (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  session_id TEXT NOT NULL REFERENCES crawl_sessions(id),
  url TEXT NOT NULL,
  error_type TEXT NOT NULL, -- 'network', 'parsing', 'validation', 'timeout'
  error_message TEXT NOT NULL,
  error_code INTEGER,
  league_id TEXT,
  season_year INTEGER,
  retry_count INTEGER DEFAULT 0,
  stack_trace TEXT,
  request_headers TEXT, -- JSON string
  response_headers TEXT, -- JSON string
  response_body TEXT,
  occurred_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX idx_crawl_logs_session_timestamp ON crawl_logs(session_id, timestamp);
CREATE INDEX idx_crawl_logs_level ON crawl_logs(level);
CREATE INDEX idx_crawl_logs_league ON crawl_logs(league_id, season_year);
CREATE INDEX idx_crawl_discoveries_session ON crawl_discoveries(session_id);
CREATE INDEX idx_crawl_discoveries_league ON crawl_discoveries(league_id, season_year);
CREATE INDEX idx_crawl_errors_session ON crawl_errors(session_id);
CREATE INDEX idx_crawl_errors_type ON crawl_errors(error_type);

-- Views for easy querying
CREATE VIEW v_recent_crawl_activity AS
SELECT 
  cs.session_name,
  cs.spider_name,
  cs.status,
  cs.start_time,
  cs.end_time,
  cs.total_requests,
  cs.successful_requests,
  cs.failed_requests,
  cs.items_scraped,
  cs.leagues_discovered,
  CAST((julianday(COALESCE(cs.end_time, datetime('now'))) - julianday(cs.start_time)) * 24 * 60 AS INTEGER) as duration_minutes,
  COUNT(DISTINCT cl.id) as log_entries,
  COUNT(DISTINCT cd.id) as discoveries,
  COUNT(DISTINCT ce.id) as errors
FROM crawl_sessions cs
LEFT JOIN crawl_logs cl ON cs.id = cl.session_id
LEFT JOIN crawl_discoveries cd ON cs.id = cd.session_id  
LEFT JOIN crawl_errors ce ON cs.id = ce.session_id
GROUP BY cs.id
ORDER BY cs.start_time DESC;

CREATE VIEW v_league_discovery_summary AS
SELECT 
  cd.league_id,
  cd.season_year,
  cd.league_name,
  cd.district_name,
  cd.match_count,
  cd.team_count,
  cd.data_quality,
  cd.discovery_phase,
  cd.discovered_at,
  cs.session_name,
  cs.spider_name
FROM crawl_discoveries cd
JOIN crawl_sessions cs ON cd.session_id = cs.id
ORDER BY cd.discovered_at DESC;
