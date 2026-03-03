import telebot
import time
import threading
import os
import logging
from flask import Flask

# Silencia os avisos do Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ================= CONFIGURAÇÕES =================
# Certifique-se de que esses IDs e Token estão corretos
TOKEN = "8600770877:AAEvpkG_o-B1mly5qndH9EBXmybSElkTL3A"
DONO_ID = 7551063741
ID_GRUPO_FIXO = -1003664995426  
FONTE_ESTILIZADA = "𝐌𝐄𝐍𝐒𝐀𝐆𝐄𝐌 𝐀𝐍𝐎‌𝐍𝐈𝐌𝐀"

# Inicialização do Bot com modo HTML
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True)

class Estado:
    usuarios_autorizados = set()
    last_msg_time = {}

# ================= KEEP ALIVE (SERVIDOR WEB) =================
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot de Mensagens Anônimas Online!"

def run_web_server():
    # O Render exige que o bot escute na porta definida pelo sistema
    porta = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)

# Inicia o servidor em uma thread separada
threading.Thread(target=run_web_server, daemon=True).start()

# ================= LÓGICA DO BOT =================

@bot.message_handler(commands=['sms'])
def menu_grupo(m):
    if m.chat.type == 'private': return
    
    try:
        status = bot.get_chat_member(m.chat.id, m.from_user.id).status
        if status not in ['administrator', 'creator'] and m.from_user.id != DONO_ID:
            return
    except: return

    markup = telebot.types.InlineKeyboardMarkup()
    btn_url = f"t.me/{bot.get_me().username}?start=enviar"
    markup.add(telebot.types.InlineKeyboardButton("📤 ENVIAR MENSAGEM ANÔNIMA", url=btn_url))
    
    bot.send_message(
        m.chat.id, 
        "💌 <b>CORREIO ANÔNIMO ATIVADO!</b>\n\nClique no botão abaixo para confessar no meu privado. O sigilo é absoluto.",
        reply_markup=markup
    )

@bot.message_handler(commands=['start'])
def start_pv(m):
    if m.chat.type != 'private': return
    if "enviar" in m.text:
        Estado.usuarios_autorizados.add(m.from_user.id)
        bot.send_message(m.from_user.id, "🔓 <b>MODO ANÔNIMO ATIVADO!</b>\n\nEscreva sua mensagem abaixo. Menções com @ funcionam normalmente.")
    else:
        bot.send_message(m.from_user.id, "👋 Use o link de envio disponível no grupo.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['photo', 'audio', 'voice', 'video', 'sticker', 'document'])
def bloquear_midia(m):
    bot.reply_to(m, "🚫 <b>SISTEMA:</b> Apenas mensagens de texto são permitidas.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['text'])
def enviar_confissao(m):
    uid = m.from_user.id
    agora = time.time()

    if uid not in Estado.usuarios_autorizados:
        return bot.reply_to(m, "⚠️ Inicie pelo botão do grupo!")

    if agora - Estado.last_msg_time.get(uid, 0) < 3:
        return bot.reply_to(m, "⏳ Aguarde 3 segundos.")

    Estado.last_msg_time[uid] = agora

    try:
        # Limpa caracteres que podem quebrar o HTML
        msg_usuario = m.text.replace("<", "&lt;").replace(">", "&gt;")
        
        template = f"💌 {FONTE_ESTILIZADA} 💌\n\n💬 {msg_usuario}"
        
        bot.send_message(ID_GRUPO_FIXO, template, parse_mode="HTML")
        bot.send_message(uid, "🚀 <b>Enviada com sucesso!</b>")
    except Exception as e:
        bot.send_message(uid, f"❌ Erro ao enviar: Tente novamente mais tarde.")

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    print(f"🔥 Bot Anônimo Ativado no Grupo: {ID_GRUPO_FIXO}")
    bot.infinity_polling(skip_pending=True)
