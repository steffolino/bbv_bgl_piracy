# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PlayerStatsItem(scrapy.Item):
    # Player information
    player_id = scrapy.Field()
    name = scrapy.Field()
    team = scrapy.Field()
    
    # Game stats
    points = scrapy.Field()
    rebounds = scrapy.Field()
    assists = scrapy.Field()
    steals = scrapy.Field()
    blocks = scrapy.Field()
    turnovers = scrapy.Field()
    
    # Shooting stats
    field_goals_made = scrapy.Field()
    field_goals_attempted = scrapy.Field()
    three_pointers_made = scrapy.Field()
    three_pointers_attempted = scrapy.Field()
    free_throws_made = scrapy.Field()
    free_throws_attempted = scrapy.Field()
    
    # Game info
    match_id = scrapy.Field()
    date = scrapy.Field()
    season = scrapy.Field()
    
    # Meta
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class MatchItem(scrapy.Item):
    match_id = scrapy.Field()
    date = scrapy.Field()
    home_team = scrapy.Field()
    away_team = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    season = scrapy.Field()
    league_id = scrapy.Field()
    
    # Meta
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class TeamItem(scrapy.Item):
    team_id = scrapy.Field()
    name = scrapy.Field()
    league = scrapy.Field()
    season = scrapy.Field()
    
    # Meta
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
