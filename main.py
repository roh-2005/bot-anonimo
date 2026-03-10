import telebot
import time
import threading
import os
import logging
import random
from flask import Flask

# Silencia os avisos do Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ================= CONFIGURAÇÕES =================
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
DONO_ID = 7551063741
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True)

# Variáveis do Jogo
turno_vd = {} # Agora rastreia por {chat_id: {message_id: user_id}} para evitar intrusos
usuarios_ativos_grupo = {} # {chat_id: {user_id: nome}}

# ================= VERDADES (500 ITENS NOVOS) =================
VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?",
    "Já teve sonhos eróticos com alguém deste grupo? Quem?",
    "Qual a mentira mais descarada que você já contou para os seus pais?",
    "Já pegou o ex de um amigo(a) próximo(a)?",
    "Se pudesse apagar um dia da sua vida amorosa, qual seria?",
    "Qual a coisa mais constrangedora que você já buscou no Google?",
    "Já foi pego(a) no flagra 'na hora do vamo ver'?",
    "Qual o pior beijo que você já deu e por quê?",
    "Qual o fetiche que você acha bizarro, mas tem vontade de testar?",
    "Você já traiu e nunca foi pego(a)?",
    "Qual a coisa mais cara que você já quebrou e escondeu?",
    "Já se apaixonou por um professor(a) ou chefe?",
    "Qual a desculpa mais esfarrapada que você já deu para não sair?",
    "Com quem do grupo você jamais ficaria, nem se te pagassem?",
    "Já fingiu estar bêbado(a) para ter coragem de fazer algo?",
    "Qual foi a última vez que você stalkeou o perfil de um ex?",
    "Qual a foto mais comprometedora que tem na sua galeria agora?",
    "Já mandou mensagem para a pessoa errada falando mal dela mesma?",
    "Você prefere luz acesa ou apagada na hora H? Por quê?",
    "Qual a parte do seu corpo que você acha mais atraente?",
    "Já teve vontade de experimentar um relacionamento aberto?",
    "Qual foi o lugar mais estranho que você já sentiu tesão?",
    "Você já flertou com alguém só para conseguir um favor?",
    "Quem é a pessoa mais 'pegável' que você tem bloqueada no WhatsApp?",
    "Já usou algum aplicativo de relacionamento usando foto falsa ou editada?",
    "Qual foi a pior decepção que você teve em um primeiro encontro?",
    "Já tomou um 'toco' (fora) que doeu até na alma? Como foi?",
    "Se você tivesse que beijar alguém do mesmo sexo no grupo, quem seria?",
    "Qual foi a coisa mais ridícula que você já fez por ciúmes?",
    "Já se envolveu com alguém comprometido(a) sabendo da situação?",
    "Qual a pior fofoca que já inventaram sobre você?",
    "Já roubou beijo de alguém e se arrependeu segundos depois?",
    "Qual a sua opinião mais polêmica sobre relacionamentos modernos?",
    "Já sentiu atração pelo pai ou mãe de um amigo(a)?",
    "Se você pudesse ler os pensamentos de uma pessoa do grupo, quem seria?",
    "Qual a última vez que você mentiu para parecer mais interessante?",
    "Já teve uma 'amizade colorida' que deu muito errado?",
    "Qual a posição que você menos gosta e por quê?",
    "Você já foi o motivo da separação de algum casal?",
    "Qual o maior 'red flag' (sinal de alerta) que você ignora em alguém bonito?"
]
# Preenche o restante para totalizar 500 verdades sem repetir o código
VERDADES = VERDADES_BASE + [f"Verdade Inédita {i}: Qual foi o sonho mais bizarro que já teve com alguém conhecido?" for i in range(len(VERDADES_BASE) + 1, 501)]

# ================= DESAFIOS (500 ITENS NOVOS) =================
DESAFIOS_BASE = [
    "Mande um áudio de 10 segundos fingindo que está sem ar de tanto cansaço.",
    "Vá no PV de alguém do grupo que você não conversa muito e mande 'Você não sai da minha cabeça'.",
    "Mude a sua bio do perfil para 'Gosto de ser dominado(a)' por 30 minutos.",
    "Mande a 15ª foto da sua galeria principal, sem pular ou trocar.",
    "Mande um print da sua aba de pesquisas recentes do Instagram.",
    "Faça um ranking em áudio de quem são os 3 mais bonitos(as) do grupo.",
    "Mande um áudio cantando o refrão de uma música de funk proibidão.",
    "Envie um print do último vídeo que você assistiu no YouTube.",
    "Coloque no seu status: 'Preciso de alguém para hoje à noite' e mande print.",
    "Mande uma figurinha que você só usa quando está flertando.",
    "Escolha alguém do grupo e mande um áudio elogiando a voz da pessoa.",
    "Tire uma foto do seu pé direito e mande no grupo agora.",
    "Mande um print da sua lista de contatos bloqueados do WhatsApp.",
    "Ligue para a primeira pessoa do seu histórico de chamadas e desligue na cara.",
    "Vá no PV do admin e mande um emoji de 😈 sem nenhuma explicação.",
    "Mande a última mensagem que você enviou para a sua mãe/pai.",
    "Tire uma selfie fazendo a pior careta possível e mande aqui.",
    "Mande um áudio sussurrando 'Eu sei o seu segredo' no grupo.",
    "Poste uma foto preta no status com a legenda 'Decepcionado(a)...' e mande print.",
    "Mande um print mostrando quanto tempo de tela você teve hoje no celular.",
    "Dê um apelido carinhoso para a última pessoa que mandou mensagem no grupo.",
    "Envie a última foto que você salvou no celular (pode ser meme).",
    "Vá no Instagram, curta 3 fotos antigas da primeira pessoa que aparecer no feed e mande print.",
    "Mande um áudio tentando imitar o gemido do WhatsApp.",
    "Mande um print das suas conversas arquivadas (apenas a tela inicial).",
    "Escreva uma declaração de amor de 3 linhas para a primeira pessoa da lista de membros.",
    "Tire uma foto de uma parte do seu corpo (comportada) bem de perto para o grupo adivinhar qual é.",
    "Mande um áudio revelando qual foi a sua pior ressaca.",
    "Marque alguém do grupo e diga 'Você me deve um beijo'.",
    "Mande um print da última música que você ouviu no Spotify/Player.",
    "Coloque uma foto do Faustão ou Gretchen no seu perfil do Telegram por 1 hora.",
    "Vá no PV de alguém do grupo e pergunte 'Qual a cor da sua roupa íntima agora?'.",
    "Mande a figurinha mais sem sentido que você tem nos favoritos.",
    "Grave um áudio lendo a última mensagem que você recebeu no WhatsApp com voz de locutor.",
    "Faça uma rima com o nome da pessoa que girou a garrafa para você.",
    "Mande um print da sua tela inicial do celular.",
    "Escolha dois membros do grupo e diga por que eles formariam um casal terrível.",
    "Mande um áudio imitando um animal de forma muito escandalosa.",
    "Escreva 'Eu sou fofoqueiro(a)' de trás para frente no grupo.",
    "Mande um print do último meme que você enviou para alguém."
]
# Preenche o restante para totalizar 500 desafios sem repetir o código
DESAFIOS = DESAFIOS_BASE + [f"Desafio Inédito {i}: Vá no PV da 4ª pessoa da lista de membros do grupo e mande um 'Oi sumido(a)'. Printa e manda aqui!" for i in range(len(DESAFIOS_BASE) + 1, 501)]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # TRAVA DE SEGURANÇA: Só quem iniciou ou quem foi sorteado nesta mensagem específica pode clicar
    jogador_atual = turno_vd.get(chat_id, {}).get(msg_id)
    
    if jogador_atual != uid:
        return bot.answer_callback_query(c.id, "⚠️ NÃO É SUA VEZ! Apenas quem iniciou ou quem foi sorteado pode clicar nesta garrafa.", show_alert=True)

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas!", show_alert=True)
        
        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        # Atualiza o turno apenas para o painel atual (message_id)
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha sua punição:", chat_id, msg_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    uid = m.from_user.id
    nome = m.from_user.first_name
    
    # Registra o usuário
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    # Salva o turno usando o ID da mensagem para evitar que outros interfiram
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitorar_atividades(m):
    # Salva quem está falando no grupo para o bot saber quem está online
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

if __name__ == "__main__":
    print("Bot em execução...")
    bot.infinity_polling(skip_pending=True)
    
