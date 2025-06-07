# [ENG]🤖 Telegram Forwarding Bot

A Telegram bot that automatically forwards messages containing the word "rating" from Channel A to Channel B.

##  🧩Features

-   Listens to messages from the telegram source channel (A)
    
-   Forwards only messages containing "rating" to the telegram destination channel (B)
    
-   Built using Webhook + aiohttp
    
-   Automatic startup test to confirm functionality
    
-   Supports photos, captions, text, and more
    

## ⚙️Project Structure
<pre>
.  
├── bot.py # Main bot code  
├── test.py # Code for testing message forwarding  
├── render.yaml # Contains all variables to be used  
├── requirements.txt # Python dependencies  
├── README.md # This file
</pre>
## :mailbox:Telegram Setup

### 1.  Create the Telegram Bot
    

-   Open Telegram and search for [@BotFather](https://t.me/BotFather)
    
-   Run the command `/newbot`
    
-   Give it a name and a username (e.g., `my_forwarder_bot`)
    
-   Copy the **bot token** → it will look like: `63xxxxxx71:AAFoxxxxn0hwA-2TVSxxxNf4c`
    

### 2.  Set Up the Channels
    

Add the created bot as an **admin** in both channels:

-  ✅ Channel A (source): the bot must **read** messages
    
-   ✅Channel B (destination): the bot must **forward** messages
    

## ☁️Deploy on Render

To run the bot correctly, you need to use a hosting platform. So:

-   Clone the project from GitHub
    
-   Create a new **Web Service** project on [Render](https://render.com)
    
-   Link your GitHub repository
    

Now configure the server settings:

-   Build Command: `pip install -r requirements.txt`
    
-   Start Command: `python3 bot.py`
    

#### Environment Variables Configuration

|Variable Name| Value |
|--|--|
|BOT_TOKEN|Token obtained from @BotFather|
|SOURCE_CHANNEL_ID|Source channel ID (Channel A)|
|DEST_CHANNEL_ID|Destination channel ID (Channel B)|
|WEBHOOK_URL|URL from Render. Example: https://my-bot-on-render.onrender.com|
|WEBHOOK_PATH|/webhook/<BOT_TOKEN>|

**Note**: For channels:

-   Public → use `@channelusername`
-   Private → use `-100<channel_id>`, which you can get by forwarding a channel message to the bot [@userinfobot](https://telegram.me/userinfobot).
    
## 🔗Set the WebHook (one-time)

Every time the server starts, you must set the webhook via cURL:

    curl -F "url=https://<your-domain>.onrender.com/webhook/<BOT_TOKEN>" "[https://api.telegram.org/bot](https://api.telegram.org/bot)<BOT_TOKEN>/setWebhook"

To verify if the webhook is set, run the cURL:

    curl --location '[https://api.telegram.org/bot](https://api.telegram.org/bot)<BOT_TOKEN>/setWebhook' --form 'url="https://your-bot.onrender.com/webhook/<BOT_TOKEN>"'

which will respond with:

    {  
    "ok": true,  
    "result": {  
	    "url": "https://<your-omain>.onrender.com/webhook/<BOT_TOKEN>",  
	    "has_custom_certificate": false,  
	    "pending_update_count": 0,  
	    "max_connections": 40,  
	    "ip_address": "<IP_ADDRESS>"  
	    }  
    }

**Note**: If the "url" field is empty, the webhook needs to be set.

After completing the correct configurations, you can deploy the application via Render.

## :alarm_clock:Avoid Sleep

Render’s free plan guarantees 15 minutes uptime before the server goes to sleep. To prevent the bot from stopping, use a free ping service.

### CronJobs

-   Go to [CronJobs](https://cron-job.org/en/)
-   Register a free account
-   Create a cron job with:
    -   URL: `<your-domain>.onrender.com`
    -   Scheduled execution: every 10 minutes
        

This schedules a ping to your server every 10 minutes to keep it awake.

Author

Developed by [FedericoBarbarossa](https://telegram.me/grgfede)

---

# [ITA]🤖 Telegram Forwarding Bot

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
Ogni volta che il server viene avviato, bisogna settare il webHook tramite la cURL:

    curl -F "url=https://<your-domain>.onrender.com/webhook/<BOT_TOKEN>" \
    "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook"

Per verificare se la WebHook è stata settata, lanciare la cURL

    curl --location 'https://api.telegram.org/bot<BOT_TOKEN>/setWebhook' \
    --form 'url="https://inoltrobot.onrender.com/webhook/7<BOT_TOKEN>"'

 la quale risponderà:

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


