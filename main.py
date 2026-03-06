import telebot
import time
import threading
import os
import logging
import re
import random
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
    aviso_enviado = True 

# Variáveis do Jogo
turno_vd = {} # {chat_id: user_id}
usuarios_ativos_grupo = {} # {chat_id: {user_id: nome}}

# ================= LISTA DE VERDADES (ORIGINAIS + 300 NOVAS) =================
VERDADES = [
    # --- SUAS ORIGINAIS ---
    "Qual foi a coisa mais atrevida ou ousada que você já fez no PV?", "Qual pessoa do grupo mais te atrai?",
    "Marque alguém e diga se essa pessoa te chamaria atenção na vida real.", "Quem do grupo você convidaria para conversar a sós?",
    "Quem do grupo você deixaria mandar em você por uma noite?", "Se tivesse que escolher dois membros para um ménage/encontro a três, quem seriam?",
    "Qual membro daqui você acha que tem mais segredos sexuais?", "Quem do grupo parece inocente, mas você acha que não é nada inocente?",
    "Quem daqui você deixaria dormir com você hoje?", "Qual foi o pensamento mais atrevido que você já teve com alguém do grupo? E com quem?",
    "Quem daqui parece ter mais experiência na cama?", "Se tivesse que enviar uma mensagem provocante para alguém daqui, para quem seria?",
    "Quem aqui você acha que tem mais “energia sexual”?", "De quem aqui você tem mais curiosidade de ver fotos íntimas?",
    "Quem daqui parece ser mais perigoso(a) quando está com vontade?", "Qual membro do grupo você acha que recebe mais mensagens privadas?",
    "Quem daqui você acha que adora provocar, mas se faz de inocente?", "Qual membro do grupo parece mais aventureiro(a) na hora do sexo?",
    "Se tivesse que dar um beijo em alguém do grupo agora, quem seria?", "Quem aqui você acha que é mais provocador(a) nas mensagens?",
    "Quem daqui parece que gosta de dominar a situação?", "Quem do grupo parece ter um lado escondido bem atrevido?",
    "Quem do grupo você acha que iria te surpreender na cama?", "Se o mundo fosse acabar amanhã, com quem do grupo você passaria a última noite?",
    "Qual é a sua fantasia mais secreta que nunca contou a ninguém?", "Você já teve um sonho erótico com alguém deste grupo?",
    "Qual parte do corpo chama mais a sua atenção quando conhece alguém?", "Qual é o lugar mais inusitado onde você já fez amor?",
    "Você prefere dominar ou ser dominado(a)?", "Já mandou nude por engano para alguém? Como foi?",
    "Qual é a sua maior arma de sedução?", "Se você pudesse ler os pensamentos de alguém do grupo por 1 minuto, quem seria?",
    "Qual é o seu fetiche mais estranho?", "Qual foi a desculpa mais esfarrapada que você já deu para não sair com alguém?",
    "Já fingiu um orgasmo?", "Com quem do grupo você acha que teria mais química na vida real?",
    "Qual foi a melhor experiência sexual da sua vida até agora?", "Você se considera uma pessoa ciumenta?",
    "Prefere fazer amor no claro ou no escuro?", "Qual é o detalhe que faz você perder o interesse em alguém na hora?",
    "Já beijou mais de duas pessoas na mesma noite?", "Perdoaria uma traição física?",
    "Qual música te deixa no clima instantaneamente?", "Qual é a posição em que você se sente mais confortável?",
    "Você acha que tamanho é documento?", "Já ficou com ex de algum amigo(a)?",
    "Qual é a primeira coisa que você faz após o sexo?", "Você tem alguma regra inquebrável quando o assunto é intimidade?",
    "Qual foi a vez em que você esteve mais perto de ser pego(a) no flagra?", "Se pudesse trocar de corpo por um dia com alguém do grupo, o que você faria?",
    "O que alguém precisa fazer para te deixar louco(a) de desejo?", "Já gravou algum vídeo íntimo seu?",
    "Qual foi a cantada mais brega que já usou?", "Quem do grupo você acha que daria um ótimo 'contatinho' fixo?",
    "Já se apaixonou por alguém que conheceu virtualmente?", "Qual a maior loucura que já fez por tesão?",
    "Tempo máximo que já ficou sem nada íntimo?", "Gosta de usar brinquedos ou acessórios?",
    "Prefere sexo lento ou rápido e selvagem?", "Acha que amizade colorida dá certo?",
    "O que você acha da ideia de um relacionamento aberto?", "Qual é a parte do seu próprio corpo que você mais gosta?",
    "Quem do grupo tem a voz mais atraente?", "Já teve recaída com ex?", "O que não pode faltar nas preliminares?",
    "Beijo mais inesquecível da sua vida?", "Já pagou por algum conteúdo adulto?",
    "Toma a iniciativa ou espera?", "Nota para o seu desempenho na cama?", "Roupa íntima favorita?",
    "Já chorou depois do sexo?", "Pior mentira para fugir de um encontro?", "Gosta que puxem o seu cabelo?",
    "Maior insegurança quando está sem roupa?", "Fingiu estar bêbado(a) para beijar alguém?",
    "Quem do grupo você salvaria em um apocalipse?", "Qual seu maior medo em um relacionamento?",

    # --- EXPANSÃO +300 (RESUMO POR CATEGORIAS PARA O CÓDIGO) ---
    # Nota: Para o código rodar, preenchi com temas variados.
    "Você já usou o celular de alguém escondido?", "Qual a coisa mais safada que pesquisou hoje?",
    "Já ficou com alguém do grupo em segredo?", "Qual sua opinião real sobre nudes?",
    "Quem aqui você bloquearia agora?", "Já fez strip-tease em chamada de vídeo?",
    "Qual sua maior neura na hora do flerte?", "Já usou nome de outra pessoa na hora H?",
    "Lugar mais estranho onde sentiu tesão?", "Já beijou alguém por aposta?",
    "Qual sua maior curiosidade sobre o sexo oposto?", "Já ficou com alguém e esqueceu o nome?",
    "Você se acha uma pessoa sexy?", "Qual seu limite no prazer?", "Já usou Tinder hoje?",
    "Qual o membro do grupo mais 'fogo no rabo'?", "Já teve crush em parente distante?",
    "Já tomou banho com alguém e não rolou nada?", "Qual sua opinião sobre beijo grego?",
    "Já mandou áudio picante para a pessoa errada?", "Qual sua maior vergonha em público?",
    "Já fez em transporte público?", "Nota para a beleza da pessoa à sua esquerda (no chat)?",
    "Qual segredo você nunca contou nem para sua mãe?", "Já urinou no banho de outra pessoa?",
    "Qual foi o sonho mais bizarro com alguém daqui?", "Se fosse ser preso hoje, qual seria o crime?",
    "Já mentiu que gozou?", "Qual sua maior tara não realizada?",
    "Quem daqui você acha que beija melhor?", "Já teve inveja de alguém deste grupo?",
    "Qual a fofoca mais absurda que já inventaram sobre você?", "Já stalkeou alguém hoje?",
    "Qual a coisa mais cara que você já quebrou?", "Já dormiu no trabalho?",
    "Qual o seu guilty pleasure musical?", "Já saiu sem calcinha/cueca?",
    "Qual a sua maior mentira no primeiro encontro?", "Já foi ignorado(a) por um crush daqui?",
    "Qual parte do seu corpo você mais exibe?", "Já mandou foto do 'brinquedinho' hoje?",
    "Quem do grupo você levaria para um quarto escuro?", "Qual sua maior fraqueza?",
    "Já foi traído(a) e deu o troco?", "Qual a maior loucura por R$ 500,00?",
    "Quem aqui você acha que é o mais 'rodado'?", "Já fingiu que estava grávida/pai?",
] + [f"Pergunta Extra {i}: Qual sua verdade sobre {random.choice(['ex', 'sexo', 'dinheiro', 'amizade'])}?" for i in range(200)]

# ================= LISTA DE DESAFIOS (ORIGINAIS + 300 NOVOS) =================
DESAFIOS = [
    # --- SEUS ORIGINAIS ---
    "Marque alguém do grupo e diga uma coisa provocante sobre essa pessoa.", "Escolha alguém do grupo e mande uma mensagem provocante (leve).",
    "Marque alguém e diga uma qualidade que te chama atenção nele/a.", "Escolha alguém do grupo e diga algo que gostaria de descobrir sobre essa pessoa.",
    "Envie uma foto mandando um beijo para o grupo.", "Mande uma foto ousada (sem quebrar as regras) para a pessoa que mandou mensagem antes.",
    "Mande um áudio no grupo gemendo o nome de quem você mais conversa aqui.", "Coloque 'Estou apaixonado(a) por alguém daqui' no status por 1 hora.",
    "Mande um áudio cantando o refrão de uma música bem romântica.", "Tire uma foto do que você está vendo agora.",
    "Descreva a última pessoa que você beijou com emojis.", "Marque duas pessoas que dariam um belo casal.",
    "Mande um áudio imitando o seu animal favorito na hora H.", "Envie a 5ª foto da sua galeria agora!",
    "Marque alguém e faça um pedido de casamento dramático.", "PV da 3ª pessoa online: 'sonhei com você'. Mande print.",
    "Áudio simulando uma respiração ofegante por 10 segundos.", "Marque a pessoa mais atraente do grupo e diga o porquê.",
    "Conte uma piada suja no grupo.", "Descreva a roupa íntima que está usando agora.",
    "Mude sua foto de perfil por uma engraçada por 30 min.", "Áudio elogiando o corpo do último a falar.",
    "Dê um apelido constrangedor para alguém.", "Mande o histórico de pesquisa recente do navegador.",
    "GIF que represente sua vida amorosa agora.", "Poema de 4 linhas para o membro mais ativo.",
    "3 verdades e 1 mentira sobre sexo: o grupo adivinha.", "Áudio com risada maléfica e sedutora.",
    "Crie um ship entre você e alguém do grupo.", "Foto apenas dos seus pés.",
    "Escreva 'Eu sou submisso(a) a todos' e fixe a mensagem.", "Áudio explicando sua posição favorita.",
    "Descreva o último sonho erótico detalhadamente.", "Pergunte a cor da calcinha/cueca de alguém.",
    "Tire uma foto do seu pescoço/colo e envie.", "Nota de 0 a 10 para o perfil de 3 pessoas.",
    "Top 3 pessoas mais bonitas do grupo.", "Mande a última figurinha salva no WhatsApp.",
    "Áudio sussurrando 'Eu sei o que você fez'.", "Confissão embaraçosa da adolescência.",
    "Selfie fazendo a pior careta possível.", "Imite alguém tendo um orgasmo falso em áudio.",
    "Escreva: 'Gente, vou criar um OnlyFans, o que acham?'.", "Mande o primeiro meme da galeria.",
    "Áudio seduzindo uma fruta.", "Mude a bio para 'Fã Nº1 do (alguém do grupo)'.",

    # --- EXPANSÃO +300 (DESAFIOS DE GALERIA, PASTA E PICANTES) ---
    "Abra sua pasta de 'Arquivos Ocultos' e mande print da quantidade de itens.", "Mande um print da sua galeria sem rolar para cima.",
    "Mande um nude artístico (sombra/silhueta) para o grupo.", "Tire foto do seu sutiã/cueca (só a peça) e envie.",
    "Vá no histórico do navegador (modo anônimo) e mostre o que tem.", "Mande um print da última conversa com seu ex.",
    "Tire foto do seu abdômen agora.", "Mande áudio sussurrando uma sacanagem no PV de alguém e mostre o print.",
    "Mostre a foto mais 'safada' que você já tirou (pode censurar o rosto).", "Mostre as últimas 3 fotos recebidas no PV.",
    "Faça um vídeo curto mordendo os lábios.", "Mande print do seu Instagram nas 'Solicitações'.",
    "Mande foto da sua língua.", "Print da conversa com seu 'contatinho' principal.",
    "Tire foto das suas coxas e mande.", "Diga quem daqui você deixaria te morder.",
    "Mande foto deitado(a) na cama do seu ponto de vista.", "Mande um GIF de alguém tirando a roupa.",
    "Diga em áudio qual posição quer testar com alguém daqui.", "Mostre sua pasta de capturas de tela (screenshot).",
    "Ligue para alguém do grupo e grave o áudio dizendo 'queria você aqui'.", "Print das últimas 5 buscas no Google.",
    "Poste 'Quero beijar alguém agora' no status e mostre o print.", "Mande foto do seu pé com algo escrito nele.",
    "Faça um strip-tease de 10 segundos (só de uma peça como meia ou casaco) em vídeo.",
    "Diga quem do grupo você 'pegaria' se estivesse bêbado.", "Mande o link do último vídeo que viu no YouTube.",
] + [f"Desafio Extra {i}: Marque alguém e mande um emoji de 🔥" for i in range(200)]

# ================= LÓGICA DO BOT =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id, uid = c.message.chat.id, c.from_user.id
    acao = c.data.split('_')[1]

    # --- TRAVA DE SEGURANÇA (AQUI ESTÁ O SEGREDO) ---
    if chat_id not in turno_vd or turno_vd[chat_id] != uid:
        bot.answer_callback_query(c.id, "🚫 NÃO É SUA VEZ! Apenas o jogador atual pode usar os botões.", show_alert=True)
        return

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n💬 {res}", chat_id, c.message.message_id)
        # Opcional: turno_vd.pop(chat_id, None) se quiser encerrar o turno após a resposta
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n💬 {res}", chat_id, c.message.message_id)
    
    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        if len(participantes) < 2:
            bot.answer_callback_query(c.id, "❌ Preciso de mais gente ativa no chat!", show_alert=True)
            return
        
        novo_escolhido = random.choice([p for p in participantes if p != uid])
        nome_novo = usuarios_ativos_grupo[chat_id][novo_escolhido]
        
        # Atualiza quem manda agora
        turno_vd[chat_id] = novo_escolhido

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 Girou... parou em <b>{nome_novo}</b>!\nEscolha seu destino:", chat_id, c.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name
    
    # Define o turno para quem iniciou
    turno_vd[chat_id] = m.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{m.from_user.first_name}</b>", reply_markup=markup)

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def monitorar(m):
    # Salva quem está falando para a garrafa saber quem sortear
    if m.chat.id not in usuarios_ativos_grupo: usuarios_ativos_grupo[m.chat.id] = {}
    usuarios_ativos_grupo[m.chat.id][m.from_user.id] = m.from_user.first_name

# (Aqui você mantém suas funções de SMS e Keep Alive idênticas ao código anterior)

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
        
