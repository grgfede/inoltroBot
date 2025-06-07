# 🤖 Telegram Forwarding Bot

Bot Telegram che inoltra automaticamente messaggi contenenti la parola **"rating"** da un **canale A** a un **canale B**.

## 🧩 Funzionalità

- Ascolta i messaggi dal canale sorgente (A)
- Inoltra nel canale di destinazione (B) solo quelli che contengono **"rating"**
- Basato su Webhook + aiohttp
- Test di avvio automatico per confermare il funzionamento
- Supporta foto, caption, testo e altro

---

## 🚀 Come configurare

### 1. Crea il Bot Telegram

1. Apri Telegram e cerca [@BotFather](https://t.me/BotFather)
2. Esegui il comando `/newbot`
3. Dai un nome e uno username (es. `my_forwarder_bot`)
4. Copia il **token del bot** → sarà simile a:
> 63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c

---

### 2. Imposta i canali

#### ✅ Aggiungi il bot come **admin** in entrambi i canali:

- ✅ Canale A (sorgente): il bot deve **leggere** i messaggi
- ✅ Canale B (destinazione): il bot deve **inoltrare** i messaggi

> ❗ Usa canali pubblici o privati con permessi completi (accesso via `chat_id`)

#### ✅ Recupera i `chat_id` dei canali:

Per canali:
- pubblici → usa `@nomecanale`
- privati → usa `-100<channel_id>`, puoi ottenerlo inoltrando un messaggio a un bot tipo `@userinfobot`

---

## ⚙️ Struttura del progetto

<pre>
.
├── bot.py           # Codice principale del bot
├── test.py          # Codice per testare inoltro messaggi
├── render.yaml      # Contiene tutte le variabili da usare
├── requirements.txt # Dipendenze Python
├── README.md        # Questo file
</pre>


---

## 📦 requirements.txt
<pre>
python-telegram-bot==20.7
aiohttp==3.9.5
</pre>
Installa con:
<pre>
pip install -r requirements.txt
</pre>
### ☁️ Deploy su Render
<ol>
  <liCrea repository su GitHub:    Carica i file bot.py, test.py, render.yaml, requirements.txt, README</li>
  <li>Crea Web Service su Render: https://render.com</li>
  <li>Third item</li>
  <li>Fourth item</li>
</ol>

2. Crea Web Service su Render
Vai su https://render.com
Clicca "New Web Service"

Collega il tuo repository GitHub

Configura:

Runtime: Python

Start command: python bot.py

Build command: (lascia vuoto)

Environment: Web Service

Region: EU/US (a piacere)

3. Aggiungi variabili d’ambiente
Vai nella sezione Environment di Render e aggiungi queste:

Variabile	Descrizione
BOT_TOKEN	Il token del bot fornito da BotFather
SOURCE_CHANNEL_ID	ID numerico del canale sorgente (es: -100...)
DEST_CHANNEL_ID	ID numerico del canale di destinazione
WEBHOOK_URL	L'URL completo del tuo servizio su Render, es:
https://mio-bot-su-render.onrender.com

🔗 Imposta il Webhook (una tantum)
Esegui questo comando curl sostituendo il tuo dominio e token:

bash
Copia
Modifica
curl -F "url=https://<your-domain>.onrender.com/webhook/<BOT_TOKEN>" \
"https://api.telegram.org/bot<BOT_TOKEN>/setWebhook"
Esempio reale:

bash
Copia
Modifica
curl -F "url=https://mio-bot-su-render.onrender.com/webhook/7678705134:AAFo9La8QEvreETFNQjpA3ulBut0fj59e4Y" \
"https://api.telegram.org/bot7678705134:AAFo9La8QEvreETFNQjpA3ulBut0fj59e4Y/setWebhook"
Per verificare:

bash
Copia
Modifica
curl https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
🔄 Mantieni Render sempre attivo (evita lo sleep)
Se usi il piano gratuito di Render, il bot va in pausa dopo 15 minuti.

✅ Soluzione gratuita: UptimeRobot
Vai su https://uptimerobot.com

Crea account

Aggiungi monitor di tipo HTTP(s)

Inserisci il tuo endpoint GET di healthcheck:

cpp
Copia
Modifica
https://<your-domain>.onrender.com/
Imposta ping ogni 5 minuti

Salva

Così il tuo bot non andrà mai a dormire.

✅ Test di avvio automatico
Il bot invierà un messaggio nel canale di destinazione al momento del deploy:

bash
Copia
Modifica
🚀 Bot avviato correttamente (test automatico)
🧪 Testa la funzionalità
Pubblica un messaggio nel canale sorgente (A) contenente la parola:

bash
Copia
Modifica
Questo è un test con la parola rating
Verifica che venga inoltrato nel canale destinazione (B).

🛠 Debug e logs
Su Render → Web Service → Logs puoi controllare eventuali errori o conferme:

ruby
Copia
Modifica
INFO:__main__:Messaggio inoltrato con successo
Oppure:

ruby
Copia
Modifica
ERROR:__main__:Errore durante inoltro: ...
👨‍💻 Autore
Sviluppato da [TUO_NOME]
Con supporto di ChatGPT 🤖
