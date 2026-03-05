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
    tempo_expiracao = 0 
    aviso_enviado = True # Controla para não repetir a mensagem de "tempo esgotado"

# ================= KEEP ALIVE & MONITORAMENTO =================
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot Online!"

def run_web_server():
    porta = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)

# Função que checa o tempo em segundo plano
def verificar_tempo_automatico():
    while True:
        agora = time.time()
        # Se o tempo acabou e ainda não avisamos o grupo
        if Estado.tempo_expiracao > 0 and agora > Estado.tempo_expiracao:
            if not Estado.aviso_enviado:
                try:
                    bot.send_message(
                        ID_GRUPO_FIXO, 
                        "⏰ <b>TEMPO ESGOTADO!</b>\nO correio anônimo foi desligado automaticamente. Envie no privado apenas quando um ADM religar."
                    )
                    Estado.aviso_enviado = True
                    Estado.tempo_expiracao = 0
                except Exception as e:
                    print(f"Erro ao enviar aviso automático: {e}")
        
        time.sleep(10) # Checa a cada 10 segundos para economizar recursos

# Inicia as threads
threading.Thread(target=run_web_server, daemon=True).start()
threading.Thread(target=verificar_tempo_automatico, daemon=True).start()

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
def handle_sms(m):
    if m.chat.type == 'private': return
    
    try:
        status = bot.get_chat_member(m.chat.id, m.from_user.id).status
        if status not in ['administrator', 'creator'] and m.from_user.id != DONO_ID:
            return
    except: return

    args = m.text.split()
    
    # CASO 1: /sms -> Indeterminado
    if len(args) == 1:
        Estado.tempo_expiracao = 2524608000 # Ano 2050
        Estado.aviso_enviado = True # Não precisa de aviso automático
        msg_texto = "💌 <b>CORREIO ANÔNIMO ATIVADO!</b>\nO bot está ligado por tempo indeterminado."
    
    else:
        comando_secundario = args[1].lower()

        # CASO 2: /sms off -> Desliga na hora
        if comando_secundario == "off":
            Estado.tempo_expiracao = 0
            Estado.aviso_enviado = True
            return bot.send_message(m.chat.id, "📴 <b>CORREIO ANÔNIMO DESLIGADO!</b>")

        # CASO 3: /sms [tempo] -> Com cronômetro
        segundos = calcular_segundos(comando_secundario)
        if segundos is None:
            return bot.reply_to(m, "❌ Use <code>/sms 10m</code> ou <code>/sms off</code>")

        Estado.tempo_expiracao = time.time() + segundos
        Estado.aviso_enviado = False # Habilita o aviso para quando o tempo acabar
        msg_texto = f"💌 <b>CORREIO ANÔNIMO ATIVADO!</b>\nDuração: <b>{comando_secundario}</b>."

    markup = telebot.types.InlineKeyboardMarkup()
    btn_url = f"t.me/{bot.get_me().username}?start=enviar"
    markup.add(telebot.types.InlineKeyboardButton("📤 ENVIAR MENSAGEM ANÔNIMA", url=btn_url))
    bot.send_message(m.chat.id, msg_texto, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_pv(m):
    if m.chat.type != 'private': return
    if time.time() > Estado.tempo_expiracao:
        return bot.send_message(m.chat.id, "🚫 <b>SISTEMA:</b> O bot está offline.")
    
    if "enviar" in m.text:
        Estado.usuarios_autorizados.add(m.from_user.id)
        bot.send_message(m.from_user.id, "🔓 <b>MODO ANÔNIMO ATIVADO!</b>")
    else:
        bot.send_message(m.from_user.id, "👋 Use o link do grupo.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['text'])
def enviar_confissao(m):
    uid = m.from_user.id
    agora = time.time()

    if agora > Estado.tempo_expiracao:
        return bot.reply_to(m, "🚫 <b>SISTEMA:</b> Bot offline.")

    if uid not in Estado.usuarios_autorizados:
        return bot.reply_to(m, "⚠️ Inicie pelo botão do grupo!")

    if agora - Estado.last_msg_time.get(uid, 0) < 3:
        return bot.reply_to(m, "⏳ Aguarde.")

    Estado.last_msg_time[uid] = agora

    try:
        msg_usuario = m.text.replace("<", "&lt;").replace(">", "&gt;")
        template = f"💌 {FONTE_ESTILIZADA} 💌\n\n💬 {msg_usuario}"
        bot.send_message(ID_GRUPO_FIXO, template, parse_mode="HTML")
        bot.send_message(uid, "🚀 <b>Enviada!</b>")
    except Exception:
        bot.send_message(uid, "❌ Erro.")

@bot.message_handler(func=lambda m: m.chat.type == 'private', content_types=['photo', 'audio', 'voice', 'video', 'sticker', 'document'])
def bloquear_midia(m):
    bot.reply_to(m, "🚫 <b>Apenas texto!</b>")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
    
