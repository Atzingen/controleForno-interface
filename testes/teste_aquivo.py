import banco_dados

with open('teste.txt', "w") as arquivo_texto:						# Abre o arquivo que ir� ser escrito
    arquivo_texto.write('Arquivo gerado automaticamente - Dados do forno - LAFAC USP \n \n \n')						# Cabe�alho
    arquivo_texto.write('chave \t Data e horario completo  \tt_0 \t\ts1 \ts2 \ts3 \ts4 \ts5 \ts6\texperimento\n\n') # informa��es sobre as colunas
    for i in d:																	# loop para andar por todas as linhas de dados
        arquivo_texto.write('\n')												# pula uma linha
        for j in i:																# loop pelas colunas
            arquivo_texto.write(str(j) + '\t')									# adiciona os dados e um tab
    arquivo_texto.close()
