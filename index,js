import { useMultiFileAuthState, makeWASocket, DisconnectReason } from "@whiskeysockets/baileys";
import axios from "axios";
import qrcode from "qrcode-terminal";

async function startSock() {
  const { state, saveCreds } = await useMultiFileAuthState("auth_info_baileys");

  const sock = makeWASocket({
    auth: state,
  });

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("Scan the QR Code:");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "close") {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      console.log("❌ Disconnected: ", " Reconnecting:");
      if (shouldReconnect) {
        startSock();
      }
    } else if (connection === "open") {
      console.log("✅ Connected to WhatsApp");
    }
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    const msg = messages[0];
    const jid = msg.key.remoteJid;

    if (
      !msg.message ||                           // No message content
      msg.key.fromMe ||                         // Sent by the bot itself
      !jid.endsWith("@s.whatsapp.net")          // Not a personal chat
    ) {
      console.log(`Ignored message from non-personal chat: ${jid}`);
      return;
    }

    const sender = jid;
    const senderName = msg.pushName || "Unknown";
    const text =
      msg.message.conversation || msg.message.extendedTextMessage?.text;

    console.log(`📩 From ${senderName} (${sender}): ${text}`);

    try {
      const res = await axios.post("http://localhost:5001/process", {
        message: text,
        user_id: sender, // Unique ID for chat history tracking
      });

      const reply = res.data.reply || "Sorry, couldn't process your message.";
      await sock.sendMessage(sender, { text: reply });
    } catch (err) {
      console.error("❌ Error communicating with backend:", err.message);
    }
  });
}

startSock();
