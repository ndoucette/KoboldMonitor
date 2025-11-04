# GemStone IV Bot Monitor Dashboard

A real-time web dashboard for monitoring multiple GemStone IV game characters running on a bot-sanctioned server with the Lich plugin system. The dashboard receives HTTP status updates from in-game Lich scripts and displays comprehensive character information in an "uberbar"-style interface with live WebSocket updates.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Lich Script Setup](#lich-script-setup)
- [API Documentation](#api-documentation)
- [Frontend Architecture](#frontend-architecture)
- [Key Features](#key-features)
- [Configuration](#configuration)
- [Technical Decisions](#technical-decisions)
- [Development Notes](#development-notes)

## Overview

### Purpose
Monitor an army of GemStone IV bot characters in real-time through a centralized web dashboard. Each character running a Lich script sends status updates via HTTP POST every 2 seconds, and the dashboard displays this information with live updates using WebSocket communication.

### Tech Stack
- **Backend**: Flask web framework with Flask-SocketIO
- **Real-time Communication**: Socket.IO (server and client)
- **Async Mode**: eventlet for WebSocket handling
- **Data Storage**: In-memory dictionary (no persistent database)
- **Frontend**: Vanilla JavaScript with Socket.IO client
- **Styling**: Custom CSS with retro gaming aesthetic

### Current Status
✅ Fully functional dashboard deployed and running on port 5000  
✅ Real-time character updates every 2 seconds  
✅ Collapsible effects sections with independent state per character  
✅ Inactive character detection and manual removal  
✅ TTL (Time To Level) calculation based on experience rate  
✅ Visual injury display using manequin system  

## Architecture

### Data Flow
```
Lich Scripts (in-game) 
    ↓ HTTP POST every 2s
Flask REST API (/api/character/update)
    ↓ Store in memory
    ↓ Broadcast via WebSocket
Socket.IO Server
    ↓ Real-time push
Browser Client (Socket.IO)
    ↓ Update DOM
Dashboard UI
```

### Backend Architecture (`main.py`)

#### Core Components
1. **Flask Application**: Standard Flask app with secret key for sessions
2. **Socket.IO Server**: Configured with `cors_allowed_origins="*"` and `async_mode='eventlet'`
3. **In-Memory Storage**: `character_states` dictionary indexed by character name
4. **Cleanup Thread**: Background daemon thread removes characters inactive for >5 minutes
5. **REST Endpoint**: `/api/character/update` receives character data via POST

#### Key Settings
- **Host**: `0.0.0.0` (accepts all connections)
- **Port**: `5000` (hardcoded)
- **Debug**: `False` (production mode)
- **Reloader**: `False` (no auto-restart)
- **Inactive Threshold**: 20 seconds (frontend detection)
- **Cleanup Threshold**: 300 seconds / 5 minutes (backend removal)

### Frontend Architecture (`templates/dashboard.html`)

#### Single-Page Application
The entire dashboard is a single HTML file with embedded CSS and JavaScript. This design choice simplifies deployment and reduces HTTP requests.

#### State Management
- **Global `characters` Object**: Stores all character data indexed by name
- **Expanded States Persistence**: Maintains which characters have effects expanded across dashboard updates
- **2-Second Update Cycle**: `updateDashboard()` runs every 2 seconds to refresh UI and check for inactive characters

#### CSS Grid Layout
```css
.dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    align-items: start;  /* CRITICAL: Prevents all cards expanding when one expands */
}
```

**Important**: The `align-items: start` property is essential. Without it, CSS Grid's default `stretch` behavior causes ALL character cards to expand to match the height of the tallest card when one character's effects are shown.

#### WebSocket Event Handling
- **`connect`**: Receives initial `characters_state` with all current data
- **`character_update`**: Receives individual character updates in real-time
- **`character_removed`**: Receives notification when backend removes inactive characters

## Quick Start

### Installation
```bash
# Clone or download project
cd gemstone-iv-bot-monitor

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Access Dashboard
Open browser to: `http://localhost:5000`

### Send Character Data from Lich Scripts
The repository includes a Lich script that automatically sends character data to the dashboard. See [Lich Script Setup](#lich-script-setup) for details.

## Lich Script Setup

### Overview
The `lich/web_status_reporter.lic` script runs inside the GemStone IV game client (via the Lich scripting system) and automatically collects character status data, sending it to the dashboard REST API every 3 seconds.

### Installation

1. **Copy the script to your Lich scripts directory**:
   ```bash
   # From this repository's lich/ directory
   cp lich/web_status_reporter.lic /path/to/lich/scripts/
   ```

2. **Start the script in-game**:
   ```
   ;web_status_reporter
   ```

3. **Configure for your dashboard URL** (if different from default):
   ```
   ;web_status_reporter --url=http://your-server-ip:5000/api/character/update
   ```

### Script Commands

**Basic Usage**:
```
;web_status_reporter                    # Start with default settings
;web_status_reporter --help             # Show help information
```

**Configuration Options**:
```
;web_status_reporter --url=URL          # Set dashboard endpoint URL
;web_status_reporter --interval=5       # Set update interval (seconds)
;web_status_reporter --api-key=KEY      # Set API key for authentication
;web_status_reporter --enable           # Enable the reporter
;web_status_reporter --disable          # Disable the reporter
```

**Example with Multiple Options**:
```
;web_status_reporter --url=https://your-dashboard.com/api/character/update --interval=2
```

### Default Configuration

The script defaults are:
- **URL**: `http://18.221.155.124:5000/api/character/update` (update this for your server)
- **Update Interval**: 3 seconds
- **API Key**: None (optional)
- **Enabled**: Yes

Settings are persisted in `CharSettings[:web_status_settings]` and saved between game sessions.

### Data Collected by Script

The Lich script automatically collects and sends:

**Character Info**:
- Name and level

**Vitals** (current/max/percent):
- Health, Mana, Stamina, Spirit

**Status**:
- Stance (offensive, defensive, guarded, etc.)
- Mindstate (clear, muddled, becoming numbed, etc.)
- Encumbrance (none, light, moderate, etc.)

**Injuries**:
- Wounds and scars for all body parts
- Compatible with dashboard's injury visualization system

**Location**:
- Current room ID and title

**Effects**:
- Active spells with remaining durations
- Buffs and debuffs
- Cooldowns

**Experience**:
- Experience to next level
- Next level percentage
- Field experience (current and max)
- Ascension experience
- Hourly experience rate (calculated automatically)
- Last experience pulse
- Percent of level cap

**Resources** (profession-dependent):
- Weekly/total resources for classes that have them
- Voln favor (if in Voln society)

**Daily Tracking**:
- Experience earned today
- Silver earned today (if using bank/ledger scripts)
- Bounty points earned (if using bounty_hud script)

**Metadata**:
- Timestamp
- Script version
- Update interval

### How It Works

1. **Experience Tracking**: The script tracks experience changes over time to calculate hourly rates and pulse amounts (based on uberbar_eo logic)

2. **Effects Monitoring**: Uses the Effects API to track active spells, buffs, debuffs, and cooldowns with remaining durations

3. **Automatic Updates**: Runs in a loop, sending data at the configured interval (default 3 seconds)

4. **Error Handling**: Gracefully handles missing data, API failures, and network issues without crashing

5. **Silent Operation**: Uses `hide_me` and `silence_me` to run quietly in the background

### Compatibility Notes

- **Lich Version**: Requires Lich >= 5.11.0
- **Based On**: uberbar_eo by elanthia-online contributors
- **Game**: GemStone IV only

### Troubleshooting

**Script not sending data**:
1. Check that the dashboard server is running: `curl http://localhost:5000/api/characters`
2. Verify URL is correct in script settings
3. Enable debug mode in Lich to see error messages

**Data not appearing on dashboard**:
1. Check browser console for WebSocket connection errors
2. Verify character name matches between script and dashboard
3. Ensure server is reachable from game client (firewall/network)

**Experience rate showing 0**:
- The script needs time to track experience changes
- Gain some experience, wait a few minutes for hourly rate to calculate

### Keeping Interfaces Consistent

The Lich script is stored in this repository (even though it runs in Lich's scripts directory) to ensure the data format sent by the script matches what the dashboard expects. 

**When modifying the dashboard's API**:
1. Update `main.py` REST endpoint
2. Update the corresponding section in `lich/web_status_reporter.lic`
3. Test with actual game data before deploying

**When modifying displayed data**:
1. Check if the Lich script already sends that data
2. If not, add collection logic to `collect_status_data()` in the Lich script
3. Update dashboard's `createCharacterCard()` function to display it

## API Documentation

### POST /api/character/update

**Purpose**: Receive character status updates from Lich scripts

**Request Headers**:
```
Content-Type: application/json
```

**Request Body Example**:
```json
{
  "character": {
    "name": "Darkstone",
    "level": 47,
    "experience": {
      "current": 2156789,
      "tnl": 843211,
      "rate_per_hour": 45000
    },
    "vitals": {
      "health": 185,
      "max_health": 185,
      "mana": 142,
      "max_mana": 142,
      "stamina": 98,
      "max_stamina": 120,
      "spirit": 8,
      "max_spirit": 8
    },
    "location": {
      "room_name": "Darkstone Cavern",
      "room_id": 12345
    },
    "status": {
      "stance": "offensive",
      "encumbrance": 45
    },
    "injuries": {
      "head": 0,
      "neck": 0,
      "chest": 1,
      "abdomen": 0,
      "back": 0,
      "right_arm": 0,
      "left_arm": 2,
      "right_hand": 0,
      "left_hand": 0,
      "right_leg": 0,
      "left_leg": 0,
      "right_eye": 0,
      "left_eye": 0,
      "nerves": 0
    },
    "effects": {
      "spells": [
        {
          "name": "Spirit Defense",
          "id": 103,
          "duration": 3600,
          "remaining": 2847
        },
        {
          "name": "Elemental Defense I",
          "id": 401,
          "duration": 3600,
          "remaining": 1234
        }
      ],
      "active_spells": [
        {
          "name": "Haste",
          "id": 506,
          "duration": 1200,
          "remaining": 456
        }
      ],
      "cooldowns": []
    }
  }
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Character Darkstone updated successfully"
}
```

**Response (Error)**:
```json
{
  "error": "Invalid character data"
}
```

**Side Effects**:
1. Character data stored in `character_states` dictionary
2. Server timestamp added: `data['server_timestamp'] = time.time()`
3. WebSocket event broadcast to all connected clients

### GET /api/characters

**Purpose**: Retrieve all active characters (updated within last 20 seconds)

**Response Example**:
```json
{
  "Darkstone": {
    "character": { /* full character data */ },
    "server_timestamp": 1757287600.123
  },
  "Vecto": {
    "character": { /* full character data */ },
    "server_timestamp": 1757287599.456
  }
}
```

### GET /

**Purpose**: Serve the main dashboard HTML page

**Response**: HTML page with embedded CSS and JavaScript

## Frontend Architecture

### Character Card Structure

Each character is displayed in a card with the following sections:

```
┌─────────────────────────────────┐
│ [X]  CHARACTER NAME       Lvl 47│  ← Header (close button if inactive)
│ Room Name                        │  ← Location
│                                  │
│ Health:  ████████████ 185/185   │  ← Vitals (color-coded bars)
│ Mana:    ████████████ 142/142   │
│ Stamina: ████████      98/120   │
│ Spirit:  ████████████   8/8     │
│                                  │
│ 2.1M XP | 843K TNL | 18h 45m    │  ← Progression
│                                  │
│ [███████] [███████] [███████]   │  ← Manequin (injuries)
│                                  │
│ Stance: offensive  Enc: 45%     │  ← Stats
│                                  │
│ [Show Effects (3)] ▼            │  ← Toggle button
│ ┌─ Spells ─────────────────┐   │  ← Collapsible effects
│ │ Spirit Defense (103)      │   │    (shown when expanded)
│ │ ████████████ 47:27        │   │
│ └───────────────────────────┘   │
└─────────────────────────────────┘
```

### Key JavaScript Functions

#### `updateDashboard()`
- **Called**: Every 2 seconds via `setInterval`
- **Purpose**: Rebuild entire dashboard HTML and detect inactive characters
- **State Preservation**: Saves and restores expanded effects states using character-specific IDs
- **Inactive Detection**: Characters not updated in >20 seconds get blinking red overlay and close button

#### `toggleEffects(characterName)`
- **Triggered**: Click on "Show Effects" / "Hide Effects" button
- **Behavior**: Toggles `.expanded` class on `#effects-{characterName}` element
- **Display Logic**: 
  - Default: `display: none`
  - Expanded: `display: block` (via `.effects-list.expanded` CSS class)

#### `removeCharacter(charName)`
- **Triggered**: Click close button (only visible on inactive cards)
- **Behavior**: 
  1. Delete character from `characters` object
  2. Call `updateDashboard()` to remove from DOM

#### `formatTimeRemaining(seconds)`
- **Purpose**: Convert seconds to "XXh XXm" format for countdowns
- **Used For**: Effect durations and TTL display

#### `calculateTimeToLevel(expNeeded, hourlyRate)`
- **Purpose**: Estimate hours and minutes until next level
- **Formula**: `(expNeeded / hourlyRate)` = hours, then convert remainder to minutes
- **Display**: "18h 45m" format

### Effects Section Implementation

Each character has an independent effects section with unique IDs:

```html
<div id="effects-{characterName}" class="effects-list">
  <!-- Spells category -->
  <div class="effect-category">
    <div class="effect-category-title">Spells</div>
    <!-- Individual spell items with progress bars -->
  </div>
  
  <!-- Active Spells category -->
  <div class="effect-category">
    <div class="effect-category-title">Active Spells</div>
    <!-- Individual active spell items -->
  </div>
  
  <!-- Cooldowns category (if any) -->
</div>
```

**State Persistence During Updates**:
```javascript
// Before rebuilding dashboard
const expandedStates = {};
document.querySelectorAll('.effects-list.expanded').forEach(list => {
    const charName = list.id.replace('effects-', '');
    expandedStates[charName] = true;
});

// After rebuilding dashboard
for (const [charName, isExpanded] of Object.entries(expandedStates)) {
    if (isExpanded) {
        const effectsList = document.getElementById('effects-' + charName);
        const toggle = document.getElementById('toggle-' + charName);
        if (effectsList && toggle) {
            effectsList.classList.add('expanded');
            toggle.textContent = `Hide Effects (${totalEffects})`;
        }
    }
}
```

## Key Features

### 1. Real-Time Updates
- Dashboard receives WebSocket push every time a character sends an update
- No polling needed - instant updates when character state changes
- All connected clients see updates simultaneously

### 2. Inactive Detection
- Characters not updated in >20 seconds get red blinking overlay
- Close button appears in upper-left corner for manual removal
- Backend automatically removes characters inactive for >5 minutes

### 3. Independent Effects Expansion
- Each character card has collapsible effects section
- Clicking "Show Effects" expands only that character's effects
- State persists across dashboard updates (every 2 seconds)
- Progress bars show remaining duration for each effect

### 4. TTL (Time To Level) Calculation
- Calculates estimated time until next level based on:
  - Experience needed (TNL)
  - Current hourly experience rate
- Function: `calculateTimeToLevel(expNeeded, hourlyRate)`
- Formula: `hours = (expNeeded / hourlyRate)`, `minutes = (hours % 1) * 60`
- Displays as "18h 45m" format

### 5. Visual Injury Display
- Manequin-style representation using colored blocks
- Injury levels: 0 (gray), 1 (yellow), 2 (orange), 3+ (red)
- Body parts laid out in anatomical grid pattern

### 6. Color-Coded Vitals
- Health: Red (#ff4444)
- Mana: Blue (#4444ff)
- Stamina: Orange (#ff9944)
- Spirit: Purple (#aa44ff)
- Progress bars show current/max with percentage width

### 7. Retro Gaming Aesthetic
- Font: Courier New (monospace)
- Color scheme: Cyan (#00ffff) and blue tones
- Dark background with gradient cards
- Matches "uberbar" Lich plugin style

## Configuration

### Port Configuration
**Default**: Port 5000 (hardcoded in `main.py`)

To change port:
```python
# In main.py, line 104
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, ...)  # Change 5000 to desired port
```

### Timing Thresholds

**Inactive Detection (Frontend)**:
```javascript
// In dashboard.html, line 489
const INACTIVE_THRESHOLD = 20000; // 20 seconds in milliseconds
// Used on line 711: if ((currentTime - lastUpdate) > (INACTIVE_THRESHOLD / 1000))
```

**Backend Cleanup**:
```python
# In main.py
INACTIVE_THRESHOLD_SECONDS = 20  # For /api/characters endpoint
# Line 90: 300 seconds = 5 minutes for background cleanup
```

**Dashboard Update Frequency**:
```javascript
// In dashboard.html
setInterval(updateDashboard, 2000);  // 2 seconds
```

### CORS Configuration
```python
# In main.py
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
```
**Note**: Wildcard CORS is enabled for Socket.IO. This assumes a trusted network environment.

## Technical Decisions

### Why In-Memory Storage?
- **No Persistence Needed**: Character states are transient - if a bot goes offline, its state doesn't need to persist
- **Simplicity**: No database setup, migrations, or queries needed
- **Performance**: Instant reads/writes, no I/O overhead
- **Trade-off**: Data lost on server restart (acceptable for this use case)

### Why Eventlet Async Mode?
- **WebSocket Compatibility**: Works reliably with Flask-SocketIO
- **Lightweight**: No heavy async framework needed (like asyncio)
- **Proven**: Standard choice for Flask real-time applications

### Why Single HTML File?
- **Deployment Simplicity**: One template file, no asset bundling
- **Performance**: No multiple HTTP requests for CSS/JS files
- **Maintenance**: All frontend code in one place for quick edits

### Why 2-Second Update Cycle?
- **Matches Lich Update Frequency**: Lich scripts send updates every ~2 seconds
- **Responsive UI**: Feels real-time without excessive re-rendering
- **Performance**: Acceptable CPU usage for rebuilding DOM every 2s

### Why Full Dashboard Rebuild?
Rather than updating individual card elements, we rebuild the entire dashboard HTML:
- **Simplicity**: Single code path for rendering
- **State Consistency**: Guarantees UI matches data state
- **Easy Debugging**: No stale DOM elements or partial updates
- **Acceptable Performance**: Dashboard typically has 5-20 characters, rendering is fast

## Development Notes

### Common Gotchas

#### 1. CSS Grid Alignment
**Problem**: When one character's effects expand, ALL cards expanded in height.  
**Solution**: Add `align-items: start` to `.dashboard` grid container.  
**Why**: CSS Grid defaults to `align-items: stretch`, making all items match the tallest item's height.

#### 2. Effects State Persistence
**Problem**: Expanded effects collapse every 2 seconds when dashboard updates.  
**Solution**: Store expanded state before rebuilding, restore after.  
**Implementation**: Check for `.expanded` class, save character names, reapply class after DOM rebuild.

#### 3. Unique Element IDs
**Problem**: Multiple characters with same effect names need unique DOM IDs.  
**Solution**: Prefix all IDs with character name: `effects-{characterName}`, `toggle-{characterName}`.  
**Critical**: Without this, toggleEffects() would affect wrong character.

#### 4. Server Timestamp
**Problem**: Can't trust client-provided timestamps for inactive detection.  
**Solution**: Backend adds `server_timestamp` field on receipt.  
**Why**: Prevents malicious/buggy clients from appearing always-active.

### Testing the Dashboard

#### Manual Testing
1. Start server: `python main.py`
2. Open dashboard: `http://localhost:5000`
3. Send test POST request with curl or Postman
4. Verify character appears immediately
5. Stop sending updates, verify red overlay after 20 seconds
6. Click close button, verify character removed

#### Test POST Request
```bash
curl -X POST http://localhost:5000/api/character/update \
  -H "Content-Type: application/json" \
  -d '{
    "character": {
      "name": "TestChar",
      "level": 50,
      "vitals": {
        "health": 200, "max_health": 200,
        "mana": 150, "max_mana": 150,
        "stamina": 100, "max_stamina": 100,
        "spirit": 10, "max_spirit": 10
      },
      "location": {"room_name": "Test Room"},
      "status": {"stance": "defensive", "encumbrance": 30},
      "experience": {"current": 1000000, "tnl": 500000, "rate_per_hour": 30000},
      "injuries": {},
      "effects": {"spells": [], "active_spells": [], "cooldowns": []}
    }
  }'
```

### Modifying the Dashboard

#### Adding New Character Data Fields
1. **Backend**: No changes needed (stores entire JSON)
2. **Frontend**: Modify `createCharacterCard()` function to access new fields
3. **Example**: Add character class/profession
   ```javascript
   // In createCharacterCard(), after level display
   const profession = data.character.profession || 'Unknown';
   html += `<div class="profession">${profession}</div>`;
   ```

#### Changing Visual Style
All CSS is in `<style>` block at top of `dashboard.html`:
- Colors: Search for hex codes (#00ffff, #ff4444, etc.)
- Font: Change `font-family: 'Courier New'` globally
- Card size: Modify `minmax(280px, 1fr)` in `.dashboard` grid
- Spacing: Adjust `gap: 20px` in `.dashboard`

#### Adding New API Endpoints
1. Add route in `main.py`:
   ```python
   @app.route('/api/your-endpoint', methods=['GET'])
   def your_handler():
       # Your logic
       return jsonify(result)
   ```
2. Restart server to apply changes

### Future Enhancement Ideas
- **Database Persistence**: Add PostgreSQL for historical data tracking
- **Authentication**: Secure dashboard with login system
- **Character Filtering**: Add search/filter controls for large bot armies
- **Alert System**: Notify when characters die, run out of resources, etc.
- **Statistics Dashboard**: Show aggregate stats across all characters
- **Mobile Responsive**: Optimize layout for mobile viewing
- **Dark/Light Theme Toggle**: User preference for color scheme

## Dependencies

See `requirements.txt` for exact versions:
- Flask==3.1.2
- Flask-SocketIO==5.5.1
- eventlet==0.40.3

## License & Usage

This project is designed for use on bot-sanctioned GemStone IV servers where automation is permitted. Ensure compliance with your server's automation policies.

---

**For Coding Agents**: This README contains everything you need to understand, modify, and extend this dashboard. Key architectural decisions are explained with rationale. If you're making changes, pay special attention to the "Technical Decisions" and "Common Gotchas" sections to avoid known pitfalls.