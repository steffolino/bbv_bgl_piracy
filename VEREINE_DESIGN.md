# 🏀 VEREINE (CLUBS) ENTITY DESIGN

## 🎯 Problem: Missing Club Hierarchy

Currently we have:
- **Teams**: "BG Litzendorf", "BG Litzendorf 2", "BBC Bayreuth", "TSV Breitengüßbach"  
- **Players**: Individual players linked to teams  
- **Missing**: Parent club organization that groups related teams

## 🏟️ German Basketball Club Structure

```
VEREIN (Club) - Parent Organization
├── Team 1 (Herren)
├── Team 2 (Damen) 
├── Team 3 (U18 männlich)
├── Team 4 (U16 weiblich)
└── Contact Info, Website, Location
```

### Real Examples from Our Data:
- **BG Litzendorf e.V.**
  - Teams: "BG Litzendorf", "BG Litzendorf 2"
  - Website: https://bg-litzendorf.de/
  - Location: Litzendorf, Oberfranken
  
- **BBC Bayreuth e.V.**  
  - Teams: "BBC Bayreuth", "BBC Bayreuth 2", "BBC Bayreuth 3"
  - Location: Bayreuth, Oberfranken

## 🗄️ Enhanced Database Schema

### New Vereine Table:
```sql
CREATE TABLE vereine (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,              -- "BG Litzendorf e.V."
  short_name TEXT,                 -- "BG Litzendorf"  
  website TEXT,                    -- "https://bg-litzendorf.de/"
  email TEXT,
  phone TEXT,
  address_street TEXT,
  address_city TEXT,
  address_postal_code TEXT,
  address_state TEXT,              -- "Bayern"
  region TEXT,                     -- "Oberfranken"
  founded_year INTEGER,
  status TEXT DEFAULT 'active',    -- active, inactive, merged
  logo_url TEXT,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Enhanced Teams Table:
```sql
ALTER TABLE teams ADD COLUMN verein_id TEXT REFERENCES vereine(id);
ALTER TABLE teams ADD COLUMN team_number INTEGER; -- 1, 2, 3 for "BG Litzendorf 2"
ALTER TABLE teams ADD COLUMN category TEXT;       -- "Herren", "Damen", "U18", etc.
```

## 🤖 Team-to-Verein Mapping Algorithm

```python
def map_team_to_verein(team_name):
    """Map team names to parent verein"""
    
    # Clean and normalize
    team = team_name.strip()
    
    # Extract verein patterns
    patterns = [
        r'(BG\s+Litzendorf)',           # BG Litzendorf -> BG Litzendorf e.V.
        r'(BBC\s+\w+)',                # BBC Bayreuth -> BBC Bayreuth e.V.  
        r'(TSV\s+\w+)',                # TSV Breitengüßbach -> TSV Breitengüßbach e.V.
        r'(FC\s+\w+)',                 # 1. FC Baunach -> 1. FC Baunach e.V.
        r'(SpVgg\s+\w+)',              # SpVgg Rattelsdorf -> SpVgg Rattelsdorf e.V.
        r'(SV\s+\w+)',                 # SV Zapfendorf -> SV Zapfendorf e.V.
        r'(DJK\s+\w+)'                 # DJK Bamberg -> DJK Bamberg e.V.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, team, re.IGNORECASE)
        if match:
            base_name = match.group(1)
            return {
                'verein_name': f"{base_name} e.V.",
                'short_name': base_name,
                'team_number': extract_team_number(team),
                'category': extract_category(team)
            }
    
    return None
```

## 🔍 Data From Our Crawling

From our REAL data, we can extract:

### BG Litzendorf Teams:
- "BG Litzendorf" (main team)
- Multiple age groups: U16, U14, U12, Senioren

### Other Major Clubs:
- **BBC Bayreuth** (multiple teams)
- **TSV Breitengüßbach** (multiple teams)  
- **1. FC Baunach**
- **TS Lichtenfels**
- **SpVgg Rattelsdorf**
- **DJK Bamberg**

## 🌐 Website Data Integration

We can enhance vereine with web-scraped data:

```python
KNOWN_VEREINE_DATA = {
    'BG Litzendorf e.V.': {
        'website': 'https://bg-litzendorf.de/',
        'region': 'Oberfranken',
        'city': 'Litzendorf',
        'postal_code': '96215',
        'state': 'Bayern'
    },
    'BBC Bayreuth e.V.': {
        'website': 'https://bbc-bayreuth.de/',
        'region': 'Oberfranken', 
        'city': 'Bayreuth'
    }
    # Add more as we discover them
}
```

## 🚀 Implementation Steps

1. **Create Vereine table** in Prisma schema
2. **Analyze our team data** to extract verein patterns  
3. **Create mapping algorithm** for team -> verein
4. **Import/create vereine records** with known data
5. **Link teams to vereine** via foreign keys
6. **Enhance frontend** with club pages and hierarchy

## 📊 Basketball-Reference.com Integration

This enables new features:
- **/clubs/[vereinName]** - Club overview with all teams
- **/clubs/[vereinName]/teams** - All teams under club
- **/clubs/[vereinName]/history** - Club history across seasons
- **Club statistics** - Combined stats from all teams
- **Club player database** - All players who played for any club team

## 🎯 Next Actions

1. Update Prisma schema with Vereine table
2. Create team-to-verein mapping script using our REAL data
3. Import vereine data and link existing teams
4. Create club pages in frontend
5. Add club-level statistics and views

This will give us the complete German basketball club hierarchy that basketball-reference.com lacks!
