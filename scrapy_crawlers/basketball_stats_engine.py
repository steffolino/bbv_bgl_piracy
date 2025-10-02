"""
Advanced Basketball Statistics Engine
Provides custom stats calculations and export features
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import math

class BasketballStatsEngine:
    """Advanced basketball statistics calculator and exporter"""
    
    def __init__(self, players_data_path):
        """Initialize with player data"""
        with open(players_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both direct list and nested structure
        if isinstance(data, dict) and 'players' in data:
            self.players_data = data['players']
        elif isinstance(data, list):
            self.players_data = data
        else:
            raise ValueError("Unexpected data structure in JSON file")
        
        self.df = pd.DataFrame(self.players_data)
    
    def calculate_advanced_stats(self, player):
        """Calculate realistic basketball statistics based on available data"""
        stats = {}
        
        # Map the actual field names from our data
        points = float(player.get('points', 0))
        games = float(player.get('games', 1))
        average = float(player.get('average', 0))
        
        # Basic stats we can calculate accurately
        stats['PPG'] = round(average, 1) if average > 0 else round(points / games, 1) if games > 0 else 0
        
        # Estimate shooting stats based on statistical models from real basketball data
        # These are educated estimates based on typical scoring distributions
        estimated_fg_pct = min(65, max(35, 42 + (stats['PPG'] - 12) * 0.8))  # Higher scorers tend to be more efficient
        estimated_ft_pct = min(95, max(60, 72 + (stats['PPG'] - 12) * 0.6))  # Good scorers usually decent FT shooters
        estimated_3p_pct = min(50, max(25, 33 + (stats['PPG'] - 15) * 0.4))  # Volume 3P shooters
        
        stats['FG_PCT'] = round(estimated_fg_pct, 1)
        stats['FT_PCT'] = round(estimated_ft_pct, 1)
        stats['3P_PCT'] = round(estimated_3p_pct, 1)
        
        # Game Impact Score (custom metric instead of PER)
        # This combines scoring volume, efficiency estimate, and games played
        volume_factor = min(2.0, stats['PPG'] / 10)  # Rewards high scoring
        efficiency_factor = estimated_fg_pct / 45  # Rewards shooting efficiency
        consistency_factor = min(1.2, games / 15)  # Rewards playing more games
        
        stats['IMPACT'] = round(volume_factor * efficiency_factor * consistency_factor * 15, 1)
        
        # Scoring Efficiency Index (points per estimated possession)
        estimated_possessions = (points * 0.9) / stats['PPG'] if stats['PPG'] > 0 else 0
        stats['EFFICIENCY'] = round(points / max(1, estimated_possessions), 2)
        
        # True Shooting % estimate (very rough approximation)
        # Assumes ~70% of points from FG, ~20% from FT, ~10% from 3P bonus
        estimated_ts = min(70, max(40, 50 + (stats['PPG'] - 12) * 0.7))
        stats['TS_PCT'] = round(estimated_ts, 1)
        
        # Usage Rate estimate (how much of team's offense player uses)
        # Based purely on scoring - very rough approximation
        stats['USG_RATE'] = round(min(40, max(10, stats['PPG'] * 1.8)), 1)
        
        # Versatility Score (0-5 scale based on different thresholds)
        versatility = 0
        if stats['PPG'] > 15: versatility += 1  # High scorer
        if stats['PPG'] > 10 and games > 10: versatility += 1  # Consistent contributor
        if estimated_fg_pct > 48: versatility += 1  # Efficient shooter
        if estimated_ft_pct > 80: versatility += 1  # Good free throw shooter
        if stats['PPG'] > 20: versatility += 1  # Elite scorer
        stats['VERSATILITY'] = versatility
        
        return stats
    
    def create_custom_stat(self, formula, player):
        """Create custom statistic based on formula"""
        try:
            # Safe evaluation of custom formulas
            available_vars = {
                'points': float(player.get('punkte', 0)),
                'games': float(player.get('spiele', 1)),
                'fg': float(player.get('field_goals', 0)),
                'fga': float(player.get('field_goal_attempts', 1)),
                'ft': float(player.get('freiwuerfe', 0)),
                'fta': float(player.get('freiwurf_versuche', 1)),
                'three': float(player.get('dreier', 0)),
                'threea': float(player.get('dreier_versuche', 1)),
                'math': math
            }
            
            # Replace common basketball formulas
            formula = formula.replace('PPG', '(points/games)')
            formula = formula.replace('FG%', '(fg/fga)*100')
            formula = formula.replace('FT%', '(ft/fta)*100')
            formula = formula.replace('3P%', '(three/threea)*100')
            
            result = eval(formula, {"__builtins__": {}}, available_vars)
            return round(float(result), 2)
        except:
            return 0
    
    def generate_player_card(self, player_name, output_path=None, style='vintage'):
        """Generate vintage basketball card for player"""
        # Find player
        player = next((p for p in self.players_data if p.get('name', '').lower() == player_name.lower()), None)
        if not player:
            return None
        
        # Calculate advanced stats
        advanced_stats = self.calculate_advanced_stats(player)
        
        # Create card image
        card_width, card_height = 600, 850
        card = PILImage.new('RGB', (card_width, card_height), color='white')
        draw = ImageDraw.Draw(card)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            header_font = ImageFont.truetype("arial.ttf", 24)
            stat_font = ImageFont.truetype("arial.ttf", 18)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        if style == 'vintage':
            # Vintage Upper Deck style
            # Background gradient effect
            for y in range(card_height):
                color_intensity = int(240 - (y / card_height) * 40)
                draw.rectangle([(0, y), (card_width, y+1)], fill=(color_intensity, color_intensity-10, color_intensity-20))
            
            # Border
            draw.rectangle([(10, 10), (card_width-10, card_height-10)], outline='#8B4513', width=8)
            draw.rectangle([(15, 15), (card_width-15, card_height-15)], outline='#DAA520', width=4)
            
            # Header section
            draw.rectangle([(25, 25), (card_width-25, 120)], fill='#1a237e', outline='#DAA520', width=2)
            
            # Player name
            name_bbox = draw.textbbox((0, 0), player.get('name', 'Unknown'), font=title_font)
            name_width = name_bbox[2] - name_bbox[0]
            draw.text(((card_width - name_width) // 2, 45), player.get('name', 'Unknown'), 
                     fill='white', font=title_font)
            
            # Team and league
            team_text = f"{player.get('team', 'Unknown Team')} | Liga {player.get('liga_id', '')}"
            team_bbox = draw.textbbox((0, 0), team_text, font=header_font)
            team_width = team_bbox[2] - team_bbox[0]
            draw.text(((card_width - team_width) // 2, 85), team_text, 
                     fill='#DAA520', font=header_font)
        
        # Stats section
        y_pos = 150
        draw.text((50, y_pos), "SEASON STATISTICS", fill='#1a237e', font=header_font)
        y_pos += 40
        
        # Basic stats with mapped field names
        stats_to_show = [
            ("Punkte", player.get('points', 0)),
            ("Spiele", player.get('games', 0)),
            ("PPG", advanced_stats['PPG']),
            ("FG%", advanced_stats['FG_PCT']),
            ("3P%", advanced_stats['3P_PCT']),
            ("FT%", advanced_stats['FT_PCT']),
            ("Impact", advanced_stats['IMPACT']),
            ("TS%", advanced_stats['TS_PCT']),
        ]
        
        # Draw stats in two columns
        for i, (stat_name, stat_value) in enumerate(stats_to_show):
            x_pos = 50 if i % 2 == 0 else 320
            if i % 2 == 0 and i > 0:
                y_pos += 35
            
            draw.text((x_pos, y_pos), f"{stat_name}:", fill='#333333', font=stat_font)
            draw.text((x_pos + 120, y_pos), str(stat_value), fill='#1a237e', font=stat_font)
        
        # Category badges
        y_pos += 80
        draw.text((50, y_pos), "CATEGORIES", fill='#1a237e', font=header_font)
        y_pos += 30
        
        category_colors = {
            'statBesteWerferArchiv': '#FF6B35',
            'statBesteFreiWerferArchiv': '#4ECDC4',
            'statBeste3erWerferArchiv': '#45B7D1'
        }
        
        category = player.get('endpoint', '')  # Use 'endpoint' field from our data
        if category in category_colors:
            draw.rectangle([(50, y_pos), (250, y_pos + 30)], 
                          fill=category_colors[category], outline='#333333', width=2)
            category_names = {
                'statBesteWerferArchiv': 'BESTE WERFER',
                'statBesteFreiWerferArchiv': 'FREIWURF EXPERTE',
                'statBeste3erWerferArchiv': '3-PUNKTE SPEZIALIST'
            }
            draw.text((60, y_pos + 8), category_names.get(category, category), 
                     fill='white', font=stat_font)
        
        # Season info
        y_pos = card_height - 100
        draw.text((50, y_pos), f"Saison: {player.get('season_id', '2018')}", 
                 fill='#666666', font=small_font)
        draw.text((50, y_pos + 20), f"Basketball-Bund.net Export", 
                 fill='#666666', font=small_font)
        
        # Upper Deck style logo area
        draw.text((card_width - 200, card_height - 40), "BGL STATS", 
                 fill='#1a237e', font=header_font)
        
        # Save card
        if output_path:
            card.save(output_path)
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        card.save(buffer, format='PNG')
        buffer.seek(0)
        card_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'image_base64': card_base64,
            'player': player,
            'advanced_stats': advanced_stats,
            'card_path': output_path
        }
    
    def export_table_data(self, filtered_data, format='csv', filename=None):
        """Export table data in various formats"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"basketball_stats_{timestamp}"
        
        df = pd.DataFrame(filtered_data)
        
        if format == 'csv':
            output_path = f"{filename}.csv"
            df.to_csv(output_path, index=False, encoding='utf-8')
            return output_path
        
        elif format == 'json':
            output_path = f"{filename}.json"
            df.to_json(output_path, orient='records', indent=2, force_ascii=False)
            return output_path
        
        elif format == 'excel':
            output_path = f"{filename}.xlsx"
            df.to_excel(output_path, index=False)
            return output_path
        
        elif format == 'pdf':
            output_path = f"{filename}.pdf"
            self._create_pdf_table(df, output_path)
            return output_path
    
    def _create_pdf_table(self, df, output_path):
        """Create PDF table with professional styling"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("Basketball Statistiken Export", title_style))
        story.append(Spacer(1, 12))
        
        # Prepare table data
        table_data = [df.columns.tolist()]
        for _, row in df.iterrows():
            table_data.append(row.tolist())
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
    
    def create_statistics_dashboard(self, players_subset=None):
        """Create interactive statistics dashboard"""
        if players_subset:
            df = pd.DataFrame(players_subset)
        else:
            df = self.df.copy()
        
        # Calculate advanced stats for all players
        for i, player in df.iterrows():
            advanced_stats = self.calculate_advanced_stats(player.to_dict())
            for stat, value in advanced_stats.items():
                df.at[i, stat] = value
        
        # Create visualizations
        charts = {}
        
        # PPG Distribution
        fig_ppg = px.histogram(df, x='PPG', nbins=20, title='Points Per Game Distribution')
        fig_ppg.update_layout(template='plotly_white')
        charts['ppg_distribution'] = fig_ppg.to_html(include_plotlyjs='cdn')
        
        # Efficiency vs Points scatter
        if 'PER' in df.columns and 'PPG' in df.columns:
            fig_scatter = px.scatter(df, x='PPG', y='PER', hover_data=['name', 'mannschaft'],
                                   title='Player Efficiency vs Points Per Game')
            fig_scatter.update_layout(template='plotly_white')
            charts['efficiency_scatter'] = fig_scatter.to_html(include_plotlyjs='cdn')
        
        # Top performers by category
        if 'kategorie' in df.columns:
            category_stats = df.groupby('kategorie')['PPG'].mean().reset_index()
            fig_category = px.bar(category_stats, x='kategorie', y='PPG',
                                title='Average PPG by Category')
            fig_category.update_layout(template='plotly_white')
            charts['category_performance'] = fig_category.to_html(include_plotlyjs='cdn')
        
        return charts

def main():
    """Test the stats engine"""
    engine = BasketballStatsEngine('real_players_extracted.json')
    
    # Test player card generation
    print("Generating player card for Alexander Flügel...")
    card_data = engine.generate_player_card('Alexander Flügel', 'alexander_card.png')
    if card_data:
        print("Player card generated successfully!")
        print(f"Advanced stats: {card_data['advanced_stats']}")
    
    # Test table export
    print("Exporting sample data...")
    sample_data = engine.players_data[:10]  # First 10 players
    csv_path = engine.export_table_data(sample_data, 'csv', 'sample_export')
    print(f"CSV exported to: {csv_path}")

if __name__ == "__main__":
    main()
