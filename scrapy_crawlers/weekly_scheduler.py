#!/usr/bin/env python3
"""
🗓️ WEEKLY BASKETBALL DATA SCHEDULER 🗓️
Automated scheduling for current season updates

Usage:
- Run manually: python weekly_scheduler.py
- Schedule with cron (Linux/Mac): 0 6 * * 1 /path/to/python weekly_scheduler.py
- Schedule with Task Scheduler (Windows): Run every Monday at 6 AM
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime, timedelta
import json
import os

class WeeklyScheduler:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.scraper_script = os.path.join(self.script_dir, "current_season_scraper.py")
        self.log_file = os.path.join(self.script_dir, "weekly_updates.log")
        
    def log_message(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        print(log_entry.strip())
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def run_weekly_update(self):
        """Execute the weekly data update"""
        self.log_message("🏀 STARTING WEEKLY BASKETBALL DATA UPDATE")
        self.log_message("=" * 60)
        
        try:
            # Run the current season scraper
            result = subprocess.run([
                sys.executable, self.scraper_script
            ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout
            
            if result.returncode == 0:
                self.log_message("✅ Weekly update completed successfully")
                self.log_message(f"📊 Output: {result.stdout[:500]}...")  # First 500 chars
            else:
                self.log_message(f"❌ Weekly update failed with code {result.returncode}")
                self.log_message(f"🔍 Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Weekly update timed out after 30 minutes")
        except Exception as e:
            self.log_message(f"💥 Unexpected error: {e}")
        
        self.log_message("🏁 Weekly update process finished")
        self.log_message("=" * 60)
        
    def check_season_status(self):
        """Check if we're in active basketball season"""
        now = datetime.now()
        
        # Basketball season typically runs October-April
        if now.month >= 10 or now.month <= 4:
            return True, "Active season"
        else:
            return False, "Off-season"
    
    def run_scheduler(self):
        """Run the scheduler"""
        self.log_message("🗓️ BASKETBALL DATA SCHEDULER STARTED")
        
        # Check season status
        is_active, status = self.check_season_status()
        self.log_message(f"📅 Season status: {status}")
        
        if not is_active:
            self.log_message("⏸️ Off-season detected - reduced update frequency")
            # Schedule monthly updates during off-season
            schedule.every().monday.at("06:00").do(self.run_monthly_check)
        else:
            self.log_message("🏀 Active season - weekly updates scheduled")
            # Schedule weekly updates during active season
            schedule.every().monday.at("06:00").do(self.run_weekly_update)
            
            # Also run a quick check on Friday for weekend games
            schedule.every().friday.at("18:00").do(self.run_weekend_preview)
        
        self.log_message("✅ Scheduler configured successfully")
        self.log_message("⏰ Next run: Monday 6:00 AM")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    def run_monthly_check(self):
        """Lighter check during off-season"""
        self.log_message("📅 Monthly off-season check")
        
        # Check if new season has started
        is_active, status = self.check_season_status()
        if is_active:
            self.log_message("🏀 New season detected! Switching to weekly updates")
            schedule.clear()
            schedule.every().monday.at("06:00").do(self.run_weekly_update)
            schedule.every().friday.at("18:00").do(self.run_weekend_preview)
        else:
            self.log_message("😴 Still off-season, next check in a month")
    
    def run_weekend_preview(self):
        """Friday check for weekend games"""
        self.log_message("📅 Weekend games preview update")
        # Run a lighter version of the update
        self.run_weekly_update()
    
    def run_once_now(self):
        """Run update immediately (for testing)"""
        self.log_message("🚀 MANUAL UPDATE TRIGGERED")
        self.run_weekly_update()

def main():
    """Main execution"""
    scheduler = WeeklyScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Run immediately for testing
        scheduler.run_once_now()
    else:
        # Start the scheduler
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()
