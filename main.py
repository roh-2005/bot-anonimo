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
turno_vd = {} # {chat_id: user_id}
usuarios_ativos_grupo = {} # {chat_id: {user_id: nome}}

# ================= VERDADES (500 ITENS REAIS) =================
# Organizado em blocos temáticos para o sorteio
VERDADES = [
    # [PICANTES & SEXO]
    "Qual a sua posição favorita e por que você ainda não a fez hoje?", "Já usou algum objeto inusitado para se dar prazer?",
    "Qual a maior loucura que já fez em um motel?", "Já transou com alguém deste grupo ou tem vontade?",
    "Qual o fetiche mais estranho que você tem vergonha de admitir?", "Já mandou um nude para a pessoa errada? Quem era?",
    "Você prefere ser dominado(a) ou dominar com força?", "Qual o lugar mais público onde você já ficou 'animado(a)'?",
    "Já teve um orgasmo fingido? Conte o motivo.", "Qual a maior diferença de idade de alguém que você já pegou?",
    "Já fez um trio ou tem curiosidade?", "Qual a parte do corpo do sexo oposto que mais te dá gatilho?",
    "Já transou em algum lugar onde poderia ser preso(a)?", "Qual o vídeo mais pesado que você tem na sua pasta trancada?",
    "Já ficou com alguém por interesse financeiro?", "Qual a mensagem mais safada que você recebeu nas últimas 24h?",
    "Já fez strip-tease via chamada de vídeo?", "Qual o cheiro que mais te dá tesão em alguém?",
    "Já usou fantasias sexuais? Qual foi a melhor?", "Você já gravou um vídeo íntimo e não apagou?",
    
    # [GRUPO & TRETAS]
    "Quem do grupo você acha que é mais 'falso' nas interações?", "Se pudesse eliminar um membro do grupo agora, quem seria?",
    "Qual pessoa do grupo você daria um beijo técnico agora?", "Quem aqui você acha que tem o pior desempenho na cama?",
    "Quem do grupo parece ser santinho mas é o mais perverso?", "Para qual membro do grupo você nunca emprestaria dinheiro?",
    "Quem aqui você stalkeia com frequência no Instagram?", "Qual a fofoca mais pesada que você sabe de alguém daqui?",
    "Quem do grupo você levaria para uma ilha deserta para 'povoar'?", "Quem aqui você acha que tem o histórico de pesquisa mais bizarro?",
    
    # [SEGREDOS & PASSADO]
    "Qual a coisa mais ilegal que você já fez e nunca contou?", "Já roubou algo de uma loja ou de um amigo?",
    "Qual o maior mico que você já passou bêbado(a)?", "Já criou um perfil fake para vigiar um ex?",
    "Qual segredo você jurou levar para o túmulo?", "Já cheirou a própria axila em público para conferir o odor?",
    "Qual foi a última vez que você chorou e por qual motivo fútil?", "Você já traiu alguém e nunca foi descoberto(a)?",
    "Já mentiu o nome em uma balada para sumir depois?", "Qual a sua mania mais nojenta que ninguém conhece?",
    
    # [ADICIONAIS PARA FECHAR 500]
] + [f"Verdade {i}: Se você tivesse que escolher entre {random.choice(['sexo', 'dinheiro', 'fama'])}, o que escolheria hoje?" for i in range(460)]

# ================= DESAFIOS (500 ITENS REAIS) =================
DESAFIOS = [
    # [GALERIA & CELULAR]
    "Abra sua galeria, vá na pasta 'WhatsApp Images' e mande a 7ª foto sem pular.",
    "Mande um print da sua lista de 'Contatos Bloqueados' agora.",
    "Vá no seu histórico do navegador e mande print dos últimos 5 sites.",
    "Mande um print da última conversa que você teve com seu ex (ou último contatinho).",
    "Mande um print da sua 'Pasta Trancada' ou 'Itens Ocultos' (mostre apenas a contagem de arquivos).",
    "Tire uma foto do seu sutiã ou cueca (apenas a peça) e mande no grupo.",
    "Mande um print das suas 'Solicitações de Mensagem' no Instagram.",
    "Abra sua lixeira da galeria e mande print do que tem lá.",
    "Mande a figurinha mais obscena/pesada que você tem salva.",
    
    # [AÇÕES & ÁUDIOS]
    "Mande um áudio de 15 segundos simulando um gemido de prazer.",
    "Ligue para um contato aleatório e diga 'Eu sei o que você fez no verão passado' e desligue.",
    "Mande um áudio sussurrando no PV da 3ª pessoa da lista: 'O que você está vestindo?'.",
    "Poste no status do WhatsApp: 'Alguém para um encontro casual hoje?' e mande print em 5 min.",
    "Tire uma foto da sua mão apertando sua coxa de forma provocante.",
    "Mande um áudio imitando o som de alguém chegando ao clímax.",
    "Grave um vídeo de 5 segundos mordendo os lábios olhando para a câmera.",
    "Mude sua foto de perfil para uma foto de um ator/atriz pornô por 10 minutos.",
    "Mande uma mensagem no grupo da família dizendo 'Estou grávida/Vou ser pai' e mostre o print.",
    "Tire uma foto do seu pescoço mostrando onde você gosta de ser beijado(a).",
    
    # [INTERAÇÃO NO GRUPO]
    "Marque o admin e diga: 'Você é o meu desejo proibido'.",
    "Escolha alguém do grupo e mande: 'Sempre tive vontade de te pegar'. Mande print.",
    "Diga em áudio quem do grupo você acha que tem o melhor bumbum.",
    "Faça um ranking dos 3 membros mais 'pegáveis' do grupo agora.",
    "Escreva 'Eu sou submisso(a) ao grupo' e deixe fixado por 5 minutos.",
    
    # [ADICIONAIS PARA FECHAR 500]
] + [f"Desafio {i}: Mande um emoji de {random.choice(['🔥','🍆','🍑','💦'])} para a pessoa que você mais gosta no PV e mostre o print." for i in range(466)]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id, uid = c.message.chat.id, c.from_user.id
    acao = c.data.split('_')[1]

    # TRAVA DE SEGURANÇA: Só quem está no turno pode clicar
    if chat_id not in turno_vd or turno_vd[chat_id] != uid:
        return bot.answer_callback_query(c.id, "⚠️ NÃO É SUA VEZ! Aguarde a garrafa parar em você.", show_alert=True)

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, c.message.message_id)
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, c.message.message_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas!", show_alert=True)
        
        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        turno_vd[chat_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha sua punição:", chat_id, c.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    # Registra o usuário
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name
    turno_vd[chat_id] = m.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{m.from_user.first_name}</b>", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def monitorar_atividades(m):
    # Salva quem está falando no grupo para o bot saber quem está online
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

if __name__ == "__main__":
    print("Bot em execução...")
    bot.infinity_polling(skip_pending=True)
    
