# WhatsApp Agent 📱

A simple WhatsApp chat bot built with [Baileys](https://github.com/adiwajshing/Baileys) that forwards incoming messages to a local FastAPI server and sends back its replies.

## Features

- Connects to WhatsApp via Baileys without requiring WhatsApp Web
- Automatically displays a QR code in terminal for authentication
- Sends incoming messages to a FastAPI assistant endpoint
- Handles plain-text and captioned media messages
- Fallbacks with a default reply when no valid response is received
- Auto-reconnects on network drops (unless explicitly logged out)

## Prerequisites

- Node.js v16+ & npm
- Python 3.8+ (for FastAPI backend)
- A running FastAPI server exposed at `http://localhost:8000/assistant`

## Installation

1. Clone this repository or copy the `Whatsapp_Agent` folder.
2. Install Node dependencies:
   ```powershell
   cd Whatsapp_Agent
   npm install
   ```
3. Ensure your FastAPI assistant is running:
   ```bash
   uvicorn assistant:app --reload
   ```

### Setup & Dependencies
Run the following in your terminal (PowerShell) from the `Whatsapp_Agent` folder:
```powershell
npm init -y                        # initialize a new package.json
npm install @whiskeysockets/baileys@latest axios qrcode-terminal
npm install -g nodemon            # (optional) auto-restart on changes
```

### Create `index.js`
Paste the WhatsApp agent script into a file named `index.js` in the same folder:
```javascript
// index.js
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const FASTAPI_URL = 'http://localhost:8000/assistant';

async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
  const sock = makeWASocket({ auth: state, printQRInTerminal: true, browser: ['WhatsApp Agent','Chrome','1.0'] });
  sock.ev.on('creds.update', saveCreds);
  sock.ev.on('connection.update', async update => { /* ...connection logic... */ });
  sock.ev.on('messages.upsert', async m => { /* ...message handling... */ });
}

connectToWhatsApp().catch(e => console.error(e));
```

### Run the Bot
Start the agent with:
```powershell
node index.js
# or with nodemon for live reload
nodemon index.js
```

## Configuration

- **FASTAPI_URL**: By default points to `http://localhost:8000/assistant`. Update in `index.js` if your API is hosted elsewhere.
- **Multi-account sessions**: To manage multiple WhatsApp numbers, set the `WA_AUTH_FOLDER` environment variable before starting:
  ```powershell
  node index.js
  ```
  This creates a separate `auth_info_baileys` folder per session.

## Usage

Start the bot:

```powershell
cd Whatsapp_Agent
node index.js
```

Scan the QR code using your WhatsApp mobile app. Once connected, any message you send to your new bot contact will be forwarded to your FastAPI assistant. Replies from the assistant will be sent back automatically.

## Logs

- ✅ indicates successful connection
- 💬 logs inbound messages
- 📝 logs API responses
- 🤖 logs outgoing replies
- 🔄 logs reconnection attempts

## Troubleshooting

- **Stuck on QR**: Delete the `auth_info_baileys` folder and restart to force a fresh login.
- **FastAPI errors**: Verify your assistant endpoint is running and reachable.
- **Unexpected disconnects**: Ensure your network is stable; the bot will retry on non-logout events.

## Possible Future Enhancements

- **Customer Support Automation**: Integrate ticketing, FAQ bots, and escalation workflows for seamless user support.
- **E-Commerce & Online Shopping**: Connect product catalogs, shopping carts, and order processing for in-chat transactions.
- **AI Agent Orchestration**: Plug into multiple AI services or custom agents to route specialized tasks and improve response accuracy.
- **Advanced NLP & Personalization**: Leverage sentiment analysis, context tracking, and user profiling for more accurate and tailored replies.
- **Scalability & Multi-User Handling**: Deploy in clustered environments or serverless platforms to support high volumes of concurrent users.
- **Analytics & Monitoring**: Add dashboards for conversation metrics, response times, and system health tracking.



