# WebTerm

A fully-featured web-based terminal using Python/FastAPI backend with real-time WebSocket communication and xterm.js frontend.

![WebTerm UI](assets/webterm-ui.png)

## Features

- **Full Terminal Emulation**: Complete terminal experience with xterm.js
- **Real-time Communication**: WebSocket-based bidirectional communication
- **Multiple Themes**: Catppuccin Mocha/Latte, Dracula, Nord, Tokyo Night
- **System Monitoring**: Live CPU, memory, and GPU usage in header
- **Detailed Stats Panel**: Picture-in-picture panel with per-core CPU, memory breakdown, and top processes
- **File Explorer**: Browse, upload, and download files
- **Clipboard Support**: Ctrl+Shift+C/V and right-click context menu
- **Mouse Support**: Full mouse event passthrough for terminal applications
- **Token Authentication**: Optional token-based authentication via environment variable
- **Cross-Platform**: Works on macOS and Linux

## Installation

You can install webterm using pip:

```bash
pip install webterm
```

or bleeding edge:

```bash
# Clone the repository
git clone https://github.com/abhishekkrthakur/webterm.git
cd webterm

# Install dependencies
pip install -e .
```

## Usage

### Basic Usage

```bash
# Start the server (localhost only by default)
webterm

# Open http://127.0.0.1:8000 in your browser
```

### Command Line Options

```bash
webterm [OPTIONS]

Options:
  --host TEXT      Host to bind to [default: 127.0.0.1]
  --port INTEGER   Port to bind to [default: 8000]
  --reload         Enable auto-reload for development
  --help           Show this message and exit
```

### With Authentication

```bash
# Set a token for authentication
export WEBTERM_TOKEN="your-secret-token"
webterm

# Users will need to enter the token to access the terminal
```

## Configuration

WebTerm can be configured via environment variables (prefix: `WEBTERM_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBTERM_HOST` | `127.0.0.1` | Host to bind to |
| `WEBTERM_PORT` | `8000` | Port to bind to |
| `WEBTERM_SHELL` | User's shell | Shell to use (e.g., `/bin/zsh`) |
| `WEBTERM_MAX_SESSIONS` | `10` | Maximum concurrent sessions |
| `WEBTERM_SESSION_TIMEOUT` | `3600` | Session timeout in seconds |
| `WEBTERM_LOG_LEVEL` | `INFO` | Log level |
| `WEBTERM_TOKEN` | None | Authentication token (enables auth if set) |

You can also use a `.env` file in the working directory.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+C` | Copy selection |
| `Ctrl+Shift+V` | Paste from clipboard |
| Right-click | Context menu (copy/paste) |

## API Endpoints

### WebSocket

- `GET /ws/terminal` - WebSocket endpoint for terminal communication
  - Query param `token` or cookie `webterm_auth` for authentication

### REST API

- `GET /` - Terminal HTML page
- `GET /health` - Health check
- `GET /api/files?path=<path>` - List files in directory
- `GET /api/files/download?path=<path>` - Download a file
- `POST /api/files/upload?path=<path>` - Upload files (multipart/form-data)

### Authentication

- `GET /auth/login` - Login page
- `POST /auth/login` - Login with token
- `POST /auth/logout` - Logout

## WebSocket Protocol

### Client → Server

```json
{"type": "input", "data": "ls -la\r"}
{"type": "resize", "rows": 30, "cols": 120}
{"type": "get_cwd"}
```

### Server → Client

```json
{"type": "output", "data": "...terminal output..."}
{"type": "stats", "cpu": 25.5, "memory": 60.2, "gpu": 30.0, "gpu_name": "Apple M1"}
{"type": "cwd", "path": "/home/user/projects"}
{"type": "error", "message": "Session terminated"}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Client                           │
│   xterm.js Terminal  ◄──►  WebSocket Client  ◄──►  Terminal UI  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ WebSocket (bidirectional)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                           │
│  Static Files  │  WebSocket Endpoint  │  REST API Endpoints     │
│                         │                                        │
│               Terminal Session Manager                           │
│                         │                                        │
│                    PTY Manager (pty module)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
                    Shell Process (bash/zsh)
```

## Project Structure

```
src/webterm/
├── api/
│   ├── app.py              # FastAPI application factory
│   ├── auth.py             # Authentication logic
│   ├── websocket.py        # WebSocket connection manager
│   └── routes/
│       ├── auth.py         # Auth routes
│       ├── files.py        # File explorer routes
│       ├── health.py       # Health check
│       └── terminal.py     # Terminal routes
├── cli/
│   └── webterm.py          # CLI entry point
├── core/
│   ├── config.py           # Pydantic Settings
│   ├── pty_manager.py      # PTY handling
│   ├── session.py          # Session management
│   └── stats.py            # System stats collection
├── static/
│   ├── css/
│   │   └── terminal.css    # Styles (Catppuccin theme)
│   └── js/
│       └── terminal.js     # xterm.js client
└── templates/
    └── index.html          # Main HTML page
```

## Security Considerations

- **Localhost by default**: Binds to 127.0.0.1 to prevent external access
- **Token authentication**: Optional but recommended for any network exposure
- **Session limits**: Maximum concurrent sessions and timeout
- **Secure cookies**: HttpOnly, SameSite=Strict for auth cookies
- **Timing-safe comparison**: Uses `secrets.compare_digest` for token verification

**Warning**: This application provides shell access. Only expose to trusted networks and always use authentication when binding to non-localhost addresses.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run with auto-reload
webterm --reload

# Run linting
make style && make quality
```
