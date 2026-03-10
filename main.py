```python
# ==========================================
# TRADER SHISHIR OMEGA AI SIGNAL SYSTEM
# ==========================================

import requests
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, redirect, session, send_file
from datetime import datetime, timedelta
import zipfile
import os

# ---------------- CONFIG ----------------

USERNAME = "shishir"
PASSWORD = "omega123"

import os

TELEGRAM_TOKEN = os.getenv("8525672936:AAF9EhUr1-Ufkhuu_ljtNs4DxpbDmuuOtq0")
CHAT_ID = os.getenv("-1003850982234")

app = Flask(__name__)
app.secret_key = "OMEGA_SECRET_KEY"

# ---------------- MARKET DATA ----------------

def get_crypto(symbol="BTCUSDT"):

    url=f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=120"
    data=requests.get(url).json()

    df=pd.DataFrame(data)
    df=df[[1,2,3,4]]
    df.columns=["open","high","low","close"]
    df=df.astype(float)

    return df


# ---------------- SUPPORT / RESISTANCE ----------------

def support_resistance(df):

    support=min(df["low"].tail(20))
    resistance=max(df["high"].tail(20))

    return support,resistance


# ---------------- SIGNAL ENGINE ----------------

def omega_signal(df):

    close=df["close"]

    ema9=close.ewm(span=9).mean()
    ema21=close.ewm(span=21).mean()

    last_price=close.iloc[-1]

    support,resistance=support_resistance(df)

    signal="WAIT"
    confidence=0

    if ema9.iloc[-1] > ema21.iloc[-1] and last_price > support:
        signal="CALL"
        confidence=92

    elif ema9.iloc[-1] < ema21.iloc[-1] and last_price < resistance:
        signal="PUT"
        confidence=92

    # TRADE MODE

    mode="NON MTG"

    if confidence >= 94:
        mode="NON MTG"
    elif confidence >= 88:
        mode="MTG1"
    else:
        mode="AVOID MTG"

    return signal,confidence,mode,support,resistance


# ---------------- ENTRY TIME ----------------

def entry_time():

    t=datetime.utcnow()+timedelta(minutes=1)
    return t.strftime("%H:%M")


# ---------------- CHART IMAGE ----------------

def create_chart(df,pair):

    plt.figure(figsize=(6,3))
    plt.plot(df["close"])
    plt.title(pair)
    plt.savefig("chart.png")
    plt.close()

    return "chart.png"


# ---------------- TELEGRAM ----------------

def send_signal(pair,signal,confidence,mode,entry):

    message=f"""
TRADER SHISHIR OMEGA AI SIGNAL 💀💀

Pair: {pair}
Signal: {signal}

Entry Time: {entry}
Expiry: 1 Minute

Confidence: {confidence}%

Trade Mode: {mode}
"""

    url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url,data={
        "chat_id":CHAT_ID,
        "text":message
    })


def send_chart():

    url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    files={"photo":open("chart.png","rb")}

    requests.post(url,data={"chat_id":CHAT_ID},files=files)


# ---------------- LOGIN PAGE ----------------

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        user=request.form.get("username")
        pwd=request.form.get("password")

        if user==USERNAME and pwd==PASSWORD:
            session["login"]=True
            return redirect("/dashboard")

    return """

<h2>OMEGA AI LOGIN</h2>

<form method="post">

<input name="username" placeholder="Username"><br><br>
<input name="password" type="password" placeholder="Password"><br><br>

<button>Login</button>

</form>

"""


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if not session.get("login"):
        return redirect("/")

    return """

<h2>TRADER SHISHIR OMEGA AI</h2>

<button onclick="location.href='/signal/BTCUSDT'">BTC SIGNAL</button>
<button onclick="location.href='/signal/ETHUSDT'">ETH SIGNAL</button>
<button onclick="location.href='/signal/BNBUSDT'">BNB SIGNAL</button>

<br><br>

<button onclick="location.href='/download-project'">
Download Project ZIP
</button>

"""


# ---------------- SIGNAL ROUTE ----------------

@app.route("/signal/<pair>")
def signal(pair):

    if not session.get("login"):
        return redirect("/")

    df=get_crypto(pair)

    signal,confidence,mode,support,resistance=omega_signal(df)

    entry=entry_time()

    create_chart(df,pair)

    send_signal(pair,signal,confidence,mode,entry)
    send_chart()

    return f"""
<h3>{pair} SIGNAL</h3>

Signal: {signal}<br>
Confidence: {confidence}%<br>
Mode: {mode}<br>
Entry Time: {entry}

"""


# ---------------- ZIP DOWNLOAD ----------------

@app.route("/download-project")
def download_project():

    zip_name="omega_ai_project.zip"

    with zipfile.ZipFile(zip_name,"w") as zipf:

        for file in os.listdir():
            if file.endswith(".py"):
                zipf.write(file)

    return send_file(zip_name,as_attachment=True)


# ---------------- RUN ----------------

if __name__=="__main__":

    app.run(port=5000)
```

