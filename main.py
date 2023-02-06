from flask import Flask , render_template, session, request, redirect, url_for
from flask.globals import request
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from dateutil import tz
from getpass import getpass
import pymysql



import time
import logging
import configparser
import sys
import os
import pandas as pd


    


app = Flask(__name__)
app.secret_key = 'secret key'

@app.route("/")
def começar():
    return render_template("login.html")

@app.route("/inicio")
def inicio():
    return render_template("login.html")

@app.route("/loginrico", methods=["POST","GET"])
def loginrico():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    con=pymysql.connect(host='localhost',user='root',password='Claudiaeleo41@')
    mycursor=con.cursor()
    query = 'use userdata'
    mycursor.execute(query)
    query = 'select * from data where username=%s and password=%s'
    mycursor.execute(query,(nome,senha))
    row=mycursor.fetchone()
    if row==None:
        return render_template("erro.html")
    else:
        return render_template("index.html")

@app.route("/botaored")
def botaored():
    return render_template("redefinir.html")

@app.route("/redefinirsenha", methods=["POST","GET"])
def redefinirsenha():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    con=pymysql.connect(host='localhost',user='root',password='Claudiaeleo41@',database='userdata')
    mycursor=con.cursor()
    query='select * from data where username=%s'
    mycursor.execute(query,(nome))
    row=mycursor.fetchone()
    if row==None:
        return "Usuario não existente"
    else:
        query='update data set password=%s where username=%s'
        mycursor.execute(query,(senha,nome))
        con.commit()
        con.close()
        return render_template("login.html")

@app.route("/stop")
def stop():
    return render_template("index.html")
                



@app.route("/login", methods=["POST","GET"])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    conta = request.form.get('conta')
    valor = request.form.get('valor')

    stopwin = request.form.get('stopwin')
    stoploss = request.form.get('stoploss')
    martingale = request.form.get('martingale')
    valorgale = request.form.get('valorgale')
    nivel = request.form.get('nivel')
    sorosgale = request.form.get('sorosgale')
    sinais = request.form.get('sinais')
    sinais_list = sinais.split("\n")
    sinais_concatenados = []
    for sinal in sinais_list:
        sinais_concatenados.append(sinal.replace("\n", ""))

    sinais_string = "".join(sinais_concatenados)
    
    


    def Martingale(valor):
        valorGale = float(valorgale)
        lucro_esperado = float(valor) * valorGale
        return float(lucro_esperado)


    def Payout(par, timeframe):
        API.subscribe_strike_list(par, timeframe)
        while True:
            d = API.get_digital_current_profit(par, timeframe)
            if d > 0:
                break
            time.sleep(1)
        API.unsubscribe_strike_list(par, timeframe)
        return float(d / 100)


    def banca():
        return API.get_balance()

    def configuracao():
        configparser.RawConfigParser()

        return {'entrada': valor, 'stop_win': stopwin, 'stop_loss': stoploss, 'payout': 0, 'banca_inicial': banca(), 'martingale': martingale, 'valorGale': valorgale, 'sorosgale': sorosgale, 'niveis': nivel}
            
    def carregaSinais():
        f = open("sinais.txt", "w")
        f.write(sinais_string)
        f.close()

        x = open('sinais.txt')
        y = []
        for i in x.readlines():
            y.append(i)
        x.close
        return y

    def entradas(par, entrada, direcao, config, opcao, timeframe):
        if opcao == 'digital':
            status, id = API.buy_digital_spot(par, entrada, direcao, timeframe)

            while True:
                status, lucro = API.check_win_digital_v2(id)
                #print(API.check_win_digital_v2(id))
                if status:
                    banca_att = banca()
                    stop_loss = False
                    stop_win = False
                    if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
                        stop_loss = True
                    if round((banca_att - float(config['banca_inicial'])), 2) >= abs(float(config['stop_win'])):
                        stop_win = True
                    if lucro > 0:
                        return 'win', round(lucro, 2), stop_win
                    elif lucro == 0.0:
                        return 'doji', 0, False
                    else:
                        return 'loss', round(lucro, 2), stop_loss
                    break

        elif opcao == 'binaria':
            status, id = API.buy(entrada, par, direcao, timeframe)

            if status:
                resultado, lucro = API.check_win_v3(id)
                #print(API.check_win_v3(id))

                banca_att = banca()
                stop_loss = False
                stop_win = False

                if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
                    stop_loss = True

                if round((banca_att - float(config['banca_inicial'])), 2) >= abs(float(config['stop_win'])):
                    stop_win = True

                if resultado:
                    if resultado == 'win':
                        return resultado, round(lucro, 2), stop_win
                    elif resultado == 'equal':
                        return 'doji', 0, False
                    elif resultado == 'loose':
                        return 'loss', round(lucro, 2), stop_loss
                else:
                    return 'error', 0, False
            else:
                return 'opcao errado', 0, False

    def timestamp_converter():
        hora = datetime.now()
        tm = tz.gettz('America/Sao Paulo')
        hora_atual = hora.astimezone(tm)
        return hora_atual.strftime('%H:%M:%S')

    def Timeframe(timeframe):

        if timeframe == 'M1':
            return 1

        elif timeframe == 'M5':
            return 5

        elif timeframe == 'M15':
            return 15

        elif timeframe == 'M30':
            return 30

        elif timeframe == 'H1':
            return 60
        else:
            return 'erro'

    def checkProfit(par, timeframe):
        all_asset = API.get_all_open_time()
        profit = API.get_all_profit()

        digital = 0
        binaria = 0

        if timeframe == 60:
            return 'binaria'

        if all_asset['digital'][par]['open']:
            digital = Payout(par, timeframe)
            digital = round(digital, 2)

        if all_asset['turbo'][par]['open']:
            binaria = round(profit[par]["turbo"], 2)

        if binaria < digital:
            return "digital"

        elif digital < binaria:
            return "binaria"

        elif digital == binaria:
            return "digital"

        else:
            "erro"

    def Mensagem(mensagem):
         print(mensagem)

    logging.disable(level=(logging.DEBUG))
    API = IQ_Option(email, senha)
    API.connect()
    API.change_balance(conta)
    if API.check_connect():
        os.system('cls')
        print('# Conectado com sucesso!')
    
    
    config = configuracao()

    config['banca_inicial'] = banca()

    valor_entrada = config['entrada']
    valor_entrada_b = float(valor_entrada)

    lucro = 0
    lucroTotal = 0

    sinais = carregaSinais()

    




    for x in sinais:
        timeframe_retorno = Timeframe(x.split(';')[0])
        timeframe = 0 if (timeframe_retorno == 'error') else timeframe_retorno
        par = x.split(';')[1].upper()
        minutos_lista = x.split(';')[2]
        direcao = x.split(';')[3].lower().replace('\n', '')
        mensagem_paridade = f'EM ESPERA: {par} | TEMPO: {str(timeframe)}M | HORA: {str(minutos_lista)} | DIREÇÃO: {direcao}'
        Mensagem(mensagem_paridade)
        opcao = 'error'
        # print(par)
        verf = False
        while True:
            t = timestamp_converter()

            if minutos_lista < t:
                break

            s = minutos_lista
            f = '%H:%M:%S'
            dif = abs((datetime.strptime(t, f) - datetime.strptime(s, f)).total_seconds())
            #print('Agora: ',t)
            #print('Falta: ',dif)

            # Verifica opção binário ou digita quando falta 25 seg
            if dif == 25:
                opcao = checkProfit(par, timeframe)


            #Inicia a operação 2 seg antes
            entrar = True if (dif == 1) else False

            if entrar:
                Mensagem('\n\n INICIANDO OPERAÇÃO..')
                dir = False
                dir = direcao

                if dir:
                    mensagem_operacao = f'ATIVO: {par} | OPÇÃO: {opcao} | HORA: {str(minutos_lista)} | DIREÇÃO: {dir}'
                    Mensagem(mensagem_operacao)
                    valor_entrada = valor_entrada_b
                    opcao = 'binaria' if (opcao == 60) else opcao
                    resultado, lucro, stop = entradas(par, valor_entrada, dir, config, opcao, timeframe)
                    lucroTotal += lucro
                    mensagem_resultado = f' RESULTADO ->  {resultado} | R${str(lucro)}\n Lucro: R${str(round(lucroTotal, 2))}\n'
                    Mensagem(mensagem_resultado)

                    # print(resultado)
                    if resultado == 'error':
                        break

                    if resultado == 'win' or resultado == 'doji':
                        break

                    if stop:
                        mensagem_stop = f'\nStop {resultado.upper()} batido!'
                        Mensagem(mensagem_stop)
                        sys.exit()

                    if resultado == 'loss' and config['martingale'] == 'S':
                        valor_entrada = Martingale(float(valor_entrada))
                        for i in range(int(config['niveis']) if int(config['niveis']) > 0 else 1):

                            mensagem_martingale = f' MARTINGALE NIVEL {str(i+1)}..'
                            Mensagem(mensagem_martingale)
                            resultado, lucro, stop = entradas(par, valor_entrada, dir, config, opcao, timeframe)
                            lucroTotal += lucro
                            mensagem_resultado_martingale = f' RESULTADO ->  {resultado} | R${str(lucro)}\n Lucro: R${str(round(lucroTotal, 2))}\n'
                            Mensagem(mensagem_resultado_martingale)

                            if stop:
                                mensagem_stop = f'\nStop {resultado.upper()} batido!'
                                Mensagem(mensagem_stop)
                                sys.exit()

                            if resultado == 'win' or resultado == 'doji':
                                #print('\n')
                                break
                            else:
                                valor_entrada = Martingale(float(valor_entrada))
                        break
                    else:
                        break
            time.sleep(0.1)
        # break
    Mensagem(' Lista de sinais finalizada!')
    banca_att = banca()
    Mensagem(f' Banca: R${banca_att}')
    Mensagem(f' Lucro: R${str(round(lucroTotal, 2))}')
    sys.exit()


if __name__=="__main__":
    app.run(debug=True)