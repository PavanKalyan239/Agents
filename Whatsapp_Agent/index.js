const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const axios = require('axios');

// WhatsApp-specific config
const FASTAPI_URL = 'http://localhost:8000/assistant'; // FastAPI endpoint

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        browser: ['WhatsApp Agent', 'Chrome', '1.0'],
        syncFullHistory: false,
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n📲 Scan this QR Code to authenticate:\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'open') {
            console.log(`✅ WhatsApp Agent connected!`);
            try {
                await axios.get(`${FASTAPI_URL}`, {
                    params: {
                        input: "Bot connected.",
                    },
                });
            } catch (err) {
                console.error('⚠️ Failed to notify FastAPI:', err.message);
            }
        }

        if (connection === 'close') {
            const error = lastDisconnect?.error;
            const shouldReconnect = error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Connection closed:', error?.message);
            if (shouldReconnect) {
                console.log('🔄 Reconnecting...');
                connectToWhatsApp();
            } else {
                console.log('🚪 Logged out. Please delete `auth_info_baileys` and restart the bot.');
            }
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg || m.type !== 'notify') return;

        const sender = msg.key.remoteJid;
        const isFromSelf = msg.key.fromMe;
        let text = null;

        // Extract message text
        if (msg.message?.conversation) {
            text = msg.message.conversation;
        } else if (msg.message?.extendedTextMessage?.text) {
            text = msg.message.extendedTextMessage.text;
        } else if (msg.message?.imageMessage?.caption) {
            text = msg.message.imageMessage.caption;
        }

        if (text) {
            if (isFromSelf) {
                console.log(`🤖 Bot Replied to ${sender}: "${text}"`);
            } else {
                console.log(`💬 Received from ${sender}: "${text}"`);

                try {
                    const response = await axios.get(`${FASTAPI_URL}`, {
                        params: {
                            input: text,
                        },
                    });
                    console.log(`📝 FastAPI response:`, response.data);
                    // Inspect the FastAPI response structure
                    let reply;
                    if (typeof response.data === 'string') {
                        reply = response.data;
                    } else if (response.data && typeof response.data === 'object') {
                        // Adjust this property name based on your FastAPI response
                        reply = response.data.response || response.data.reply || response.data.text;
                    }
                    if (!reply || typeof reply !== 'string') {
                        reply = "Sorry, I couldn't understand that.";
                    }

                    await sock.sendMessage(sender, { text: reply });
                } catch (error) {
                    console.error(`🔥 Error while responding to ${sender}:`, error.message);
                    await sock.sendMessage(sender, {
                        text: "Oops! Something went wrong. Please try again shortly.",
                    });
                }
            }
        } else {
            console.log(`🤷 Message received from ${sender}, but no text found.`);
        }
    });
}

// Launch the agent
connectToWhatsApp().catch((err) => {
    console.error('❌ Fatal error during connection:', err.message);
});
