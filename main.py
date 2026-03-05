import telebot
import time
import threading
import os
import logging
import re
from flask import Flask

# Silencia os avisos do Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ================= CONFIGURAÇÕES =================
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
DONO_ID = 7551063741
ID_GRUPO_FIXO = -1003664995426  
FONTE_ESTILIZADA = "𝐌𝐄𝐍𝐒𝐀𝐆𝐄𝐌 𝐀𝐍𝐎‌𝐍𝐈𝐌𝐀"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True)

class Estado:
    usuarios_autorizados = set()
    last_msg_time = {}
    tempo_expiracao = 0  # Timestamp de quando o bot deve desligar

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot Online!"

def run_web_server():
    porta = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)

threading.Thread(target=run_web_server, daemon=True).start()

# ================= FUNÇÕES AUXILIARES =================
def calcular_segundos(tempo_str):
    match = re.match(r"(\d+)([smh])", tempo_str.lower())
    if not match: return None
    valor, unidade = int(match.group(1)), match.group(2)
    if unidade == 's': return valor
    if unidade == 'm': return valor * 60
    if unidade == 'h': return valor * 3600
    return None

# ================= LÓGICA DO BOT =================

@bot.message_handler(commands=['sms'])
def menu_grupo(m):
    if m.chat.type == 'private': return
    
    try:
        status = bot.get_chat_member(m.chat.id, m.from_user.id).status
        if status not in ['administrator', 'creator'] and m.from_user.id != DONO_ID:
            return
    except: return

    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "⚠️ Use: <code>/sms 30s</code>, <code>/sms 10m</code> ou <code>/sms 1h</code>")

    segundos = calcular_segundos(args[1])
    if segundos is None:
        return bot.reply_to(m, "❌ Formato de tempo inválido! Use s, m ou h.")

    Estado.tempo_expiracao = time.time() + segundos
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn_url = f"t.me/{bot.get_me().username}?start=enviar"
    markup.add(telebot.types.InlineKeyboardButton("📤 ENVIAR MENSAGEM ANÔNIMA", url=btn_url))
    
    bot.send_message(
        m.chat.id, 
        f"💌 <b>CORREIO ANÔNIMO ATIVADO!</b>\n\nO bot aceitará mensagens pelos próximos <b>{args[1]}</b>.\nO sigilo é absoluto.",
        reply_markup=markup
    )

@bot.message_handler(commands=['smsoff'])
def desligar_grupo(m):
    if m.chat.type == 'private': return
    
    try:
        status = bot.get_chat_member(m.chat.id, m.from_user.id).status
        if status not in ['administrator', 'creator'] and m.from_user.id != DONO_ID:
            return
    except: return

    Estado.tempo_expiracao = 0 # Reseta o tempo para agora
    bot.send_message(m.chat.id, "📴 <b>CORREIO ANÔNIMO DESLIGADO!</b>\nNenhuma mensagem será enviada ao grupo até que um ADM ligue novamente.")

@bot.message_handler(commands=['start'])
def start_pv(m):
    if m.chat.type != 'private': return
    
    # Verifica se o bot está OFF
    if time.time() > Estado.tempo_expiracao:
        return bot.send_message(m.chat.id, "🚫 <b>SISTEMA:</b> O bot está offline no momento. Aguarde um administrador ligá-lo pelo grupo.")
    
    if "enviar" in m.text:
        Estado.usuarios_autorizados.add(m.from_user.id)
        bot.send_message(m.from_user.id, "🔓 <b>MODO ANÔNIMO ATIVADO!</b>\n\nEscreva sua mensagem abaixo.")
    else:
        bot.send_message(m.from_user.id, "👋 Use o link de envio disponível no grupo.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['text'])
def enviar_confissao(m):
    uid = m.from_user.id
    agora = time.time()

    # Verifica se o tempo expirou durante o uso
    if agora > Estado.tempo_expiracao:
        return bot.reply_to(m, "🚫 <b>SISTEMA:</b> O bot acabou de ser desligado. Sua mensagem não foi enviada.")

    if uid not in Estado.usuarios_autorizados:
        return bot.reply_to(m, "⚠️ Inicie pelo botão do grupo!")

    if agora - Estado.last_msg_time.get(uid, 0) < 3:
        return bot.reply_to(m, "⏳ Aguarde 3 segundos.")

    Estado.last_msg_time[uid] = agora

    try:
        msg_usuario = m.text.replace("<", "&lt;").replace(">", "&gt;")
        template = f"💌 {FONTE_ESTILIZADA} 💌\n\n💬 {msg_usuario}"
        bot.send_message(ID_GRUPO_FIXO, template, parse_mode="HTML")
        bot.send_message(uid, "🚀 <b>Enviada com sucesso!</b>")
    except Exception:
        bot.send_message(uid, f"❌ Erro ao enviar.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['photo', 'audio', 'voice', 'video', 'sticker', 'document'])
def bloquear_midia(m):
    bot.reply_to(m, "🚫 <b>SISTEMA:</b> Apenas mensagens de texto são permitidas.")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
    
