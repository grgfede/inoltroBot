
# 🤖 Telegram Forwarding Bot

Bot Telegram che inoltra automaticamente messaggi contenenti la parola **"rating"** da un **canale A** a un **canale B**.

## 🧩 Funzionalità

 - Ascolta i messaggi dal canale sorgente (A)
 - Inoltra nel canale di destinazione (B) solo quelli che contengono **"rating"**
 - Basato su Webhook + aiohttp
 - Test di avvio automatico per confermare il funzionamento
 - Supporta foto, caption, testo e altro

## ⚙️ Struttura del progetto

<pre>
.
├── bot.py           # Codice principale del bot
├── test.py          # Codice per testare inoltro messaggi
├── render.yaml      # Contiene tutte le variabili da usare
├── requirements.txt # Dipendenze Python
├── README.md        # Questo file
</pre>

## :mailbox: Configurazione Telegram

### 1. Crea il Bot Telegram
 - Apri Telegram e cerca [@BotFather](https://t.me/BotFather)
 -  Esegui il comando `/newbot`
 - Dai un nome e uno username (es. `my_forwarder_bot`)
 - Copia il **token del bot** → sarà simile a:
   63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c

### 2. Imposta i canali

 Aggiungi il bot creato come **admin** in entrambi i canali:

- ✅ Canale A (sorgente): il bot deve **leggere** i messaggi
- ✅ Canale B (destinazione): il bot deve **inoltrare** i messaggi

## ☁️ Deploy su Render
Per poter far eseguire correttamente il bot, è necessario utilizzare una piattaforma di host.
Quindi:

 - Clona il progetto da github
 - Crea un nuovo progetto **Web Service** su [Render](https://render.com)
 - Collega il tuo repository GitHub
Ora è necessario configurare le impostazioni del server:
 - Build Command: `pip install -r requirements.txt`
 - Start Command: `python3 bot.py`
#### Configurazione variabili di ambiente

|Nome variabile|Valore|
|--|--|
|BOT_TOKEN| Token ricavato da [@BotFather](https://t.me/BotFather) |
| SOURCE_CHANNEL_ID |ID canale di origine (Canale A)|
|DEST_CHANNEL_ID|ID canale di destinazione (Canale B)|
|WEBHOOK_URL|Ricavato da [Render](https://render.com). Esempio: https://mio-bot-su-render.onrender.com|
|WEBHOOK_PATH|/webhook/<BOT_TOKEN>|

**NB:** Per canali:
- pubblici → usa `@nomecanale`
- privati → usa `-100<channel_id>`, puoi ottenerlo inoltrando un messaggio del canale al bot [@userinfobot](https://telegram.me/userinfobot).

## 🔗 Imposta il WebHook (una tantum)
Ogni volta che il server viene avviato, bisogna settare il webHook tramite la cURL **SetWebHook**:

    curl -F "url=https://<your-domain>.onrender.com/webhook/<BOT_TOKEN>" \
    "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook"

Per verificare se la WebHook è stata settata, lanciare la cURL **CheckWebHook** la quale risponderà:

    {
	    "ok":  true,
	    "result":  {
		    "url":"https://<your-domain>.onrender.com/webhook/<BOT_TOKEN>",
		    "has_custom_certificate":  false,
		    "pending_update_count":  0,
		    "max_connections":  40,
		    "ip_address":  "<IP_ADDRESS>"
	    }
    }
**NB:** Nel caso in cui la voce "url" non è valorizzata, allora è necessario settare la WebHook.

Eseguite le corrette configurazioni, potete effettuare il deploy dell'applicativo tramite Render.

## :alarm_clock:Evitare lo sleep
Il piano gratuito di Render garantisce un tempo di attività di 15 minuti, successivamente il server va in sleep.
Per evitare che il bot smetta di funzionare, si usa un servizio di **ping** gratuito.
### CronJobs

 - Vai su [CronJobs](https://cron-job.org/en/)
 - Registra un account gratuito
 - Crea un crobJobs dove:
 -- URL: `<your-domain>.onrender.com`
 -- Esecuzione programmata: 10 minuti
In questo modo scheduliamo un ping sul nostro server ogni 10 minuti così da evitare che il server vada in sleep.

👨‍💻 Autore
Sviluppato da [FedericoBarbarossa](https://telegram.me/grgfede)

