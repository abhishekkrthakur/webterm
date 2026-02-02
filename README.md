# WebTerm

A fully-featured web-based terminal using Python/FastAPI backend with real-time WebSocket communication and xterm.js frontend.

WebTerm is particularly useful for accessing remote machines through a web browser, eliminating the need for dedicated SSH clients or terminal applications. 

![WebTerm UI](assets/webterm-ui.png)

Here are some common use cases:

- **Remote Server Access**: Install WebTerm on a remote server and access a full terminal session from any device with a web browser. This is especially useful when working from machines where installing an SSH client isn't possible or convenient.

- **Development Environments**: Access your remote development environment (cloud VMs, dev containers, or headless servers) directly from a browser tab. No need to configure SSH keys or remember connection strings—just bookmark the URL.

- **Mobile & Tablet Access**: Need to quickly check logs or run a command on your server from your phone or tablet? WebTerm provides a touch-friendly terminal interface that works on any device with a modern browser.

- **Firewall-Friendly Access**: WebTerm uses standard HTTP/WebSocket protocols (ports 80/443), making it easier to access terminals in environments where SSH port 22 might be blocked or restricted.

- **Shared Access & Demos**: Provide temporary terminal access to team members or demonstrate server configurations without sharing SSH credentials—just share a URL with an authentication token.

- **Browser-Based Workflows**: Integrate terminal access into browser-based workflows, dashboards, or internal tools without requiring users to switch to a separate terminal application.

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

## Secure Usage with Tailscale

For secure remote access to WebTerm, we recommend using [Tailscale](https://tailscale.com/), a zero-config VPN that creates a secure network between your devices.

Tailscale provides end-to-end encrypted access without exposing your terminal to the public internet. There are two recommended approaches:

### Option 1: Bind to Tailscale IP Address

Find your machine's Tailscale IP address and bind WebTerm directly to it:

```bash
# Find your Tailscale IP
tailscale ip -4

# Bind WebTerm to your Tailscale IP (e.g., 100.x.y.z)
webterm --host 100.x.y.z --port 8000

# With authentication (recommended)
export WEBTERM_TOKEN="your-secret-token"
webterm --host 100.x.y.z --port 8000
```

### Option 2: Use Tailscale Serve

Bind WebTerm to localhost and use Tailscale's serve feature to expose it on your tailnet:

```bash
# Start WebTerm on localhost
export WEBTERM_TOKEN="your-secret-token"
webterm --host 127.0.0.1 --port 8000

# In another terminal, expose it via Tailscale (runs in background)
tailscale serve --bg 8000
```

This creates a secure HTTPS endpoint accessible only to devices on your tailnet.

### Access Requirements

**Important**: With either approach, clients must be connected to the same Tailscale network (tailnet) to access WebTerm. This ensures that only your authorized devices can reach the terminal.

**Benefits of using Tailscale:**
- End-to-end encryption
- No firewall configuration needed
- Access from any device on your tailnet
- No public internet exposure
- Built-in access controls and audit logs

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
