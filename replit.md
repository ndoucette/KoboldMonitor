# GemStone IV Bot Monitor

## Overview

A real-time web dashboard for monitoring GemStone IV game character status and bot activities. The application receives character data updates via REST API from Lich scripts running in-game and displays this information through a responsive web interface with live updates using WebSocket communication.

**Status**: Fully functional dashboard deployed and running on port 5000.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Flask-SocketIO for WebSocket support
- **Real-time Communication**: Socket.IO implementation with eventlet async mode for bidirectional communication
- **Data Storage**: In-memory dictionary storage for character states (no persistent database)
- **API Design**: RESTful endpoint (`/api/character/update`) for receiving character status updates
- **Session Management**: Simple secret key configuration for Flask sessions
- **Cleanup System**: Automatic removal of characters inactive for more than 5 minutes
- **Active Character Endpoint**: `/api/characters` returns characters updated within last 20 seconds

### Frontend Architecture
- **Template Engine**: Flask's built-in Jinja2 templating
- **Styling**: Custom CSS with retro gaming aesthetic matching uberbar plugin (Courier New font, cyan/blue color scheme)
- **Layout**: CSS Grid-based responsive dashboard for character tiles
- **Real-time Updates**: Socket.IO client-side integration for live character status updates every 2 seconds
- **Vitals Display**: Color-coded health (red), mana (blue), stamina (orange), and spirit (purple) bars
- **Inactive Detection**: Blinking red overlay for characters not updated in >20 seconds
- **Character Data**: Comprehensive display including level, experience, vitals, location, status, and injuries

### Data Flow Architecture
- **Input**: Character status data received from external Lich scripts via HTTP POST
- **Processing**: Server timestamps added to incoming data, stored in memory
- **Output**: Real-time broadcasting to all connected web clients via WebSocket events
- **State Management**: Character states indexed by character name with automatic cleanup logic

### Security Considerations
- **CORS**: Wildcard CORS policy enabled for Socket.IO connections
- **Authentication**: No authentication layer implemented (assumes trusted network environment)
- **Input Validation**: Basic JSON validation for character data structure

## External Dependencies

### Runtime Dependencies
- **Flask**: Core web framework
- **Flask-SocketIO**: WebSocket communication layer
- **eventlet**: Asynchronous networking library for Socket.IO backend

### Frontend Dependencies
- **Socket.IO Client**: CDN-hosted client library (v4.5.4) for real-time communication

### Game Integration
- **Lich Scripts**: External game automation scripts that send character data updates
- **GemStone IV**: Target game environment providing character status information

### Infrastructure
- **No Database**: Uses in-memory storage only
- **No External APIs**: Self-contained monitoring system
- **Static Assets**: Minimal external dependencies (single CDN for Socket.IO)