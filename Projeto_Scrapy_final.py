# As bibliotecas utilizadas são:
# Pandas: para salvar os dados extraídos em um dataframe e assim salvá-los em um arquivo csv
# Selenium: para navegar pelo chrome e automatizar a captuda de dados de sites do tripadvisor
# Numpy: uso de uma função de condição específica
# Time: o uso do sleep apenas para dar um certo "alívio" para o código, porém, em casos de espera de objetos,
#       foi utilizado o WebDriverWait e expected_coditions

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
   

# Primeira interação com a abertura do Chrome com o Selenium e entra na url da página que
# queremos extrair os dados de avaliações 
window = webdriver.Chrome()

hotel = "https://www.tripadvisor.com/Hotel_Review-g45963-d91823-Reviews-Gold_Coast_Hotel_Casino-Las_Vegas_Nevada.html#REVIEWS"
nome_arquivo = "teste"
window.get(hotel)

#--------------------------------------------------------------------------------------------

# 1ª ação - Verifica se o botão de aceitar cookies aparece na tela e clica nele
id_button = "onetrust-accept-btn-handler"
WebDriverWait(window, 10).until(EC.presence_of_all_elements_located(("id", id_button)))
window.find_element(By.ID, id_button).click()

# 2ª ação - Verifica se o botão "All Languages" aparece na tela e clica nele
linguagem = "//*[@id='component_15']/div/div[3]/div[1]/div[1]/div[4]/ul/li[1]/label"
WebDriverWait(window, 10).until(EC.presence_of_all_elements_located((By.XPATH, linguagem)))
linguagem = window.find_element(By.XPATH, linguagem)
linguagem.click()

# Pega o número de avaliações (y) para podemos usar no nosso loop
linguagem_escolhida = window.find_element(By.CSS_SELECTOR, f"label[for*='LanguageFilter_0")
y = int(linguagem_escolhida.find_element(By.CSS_SELECTOR, "span[class*='POjZy").text[1:-1].replace(",",""))
print("Fim dos ajustes!\n")
print("Número de avaliações: ",y)
print("Número de páginas (url): ", round(y/5))

# Fim dos ajustes para deixar a página pronta para podermos extrair os dados
# ---------------------------------------------------------------------------------------



# Função que irá ser executada a cada página e pega 10 avaliações e retorna duas listas com esses elementos
def capturar_dados(i, j=""):
    print("\nPágina nº:", i, j)
    notas, datas = [], []
    
    #Sleep apenas para evitar erros (sleep não referenciado a qualquer objeto)
    sleep(0.6) 
    
    # Encontra na página a caixa maior da avaliação de cada pessoa (contendo nome, localização, comentário ...)
    pagina = window.find_elements(By.CSS_SELECTOR, "div.YibKl.MC.R2.Gi.z.Z.BB.pBbQr")
    
    # Loop para cada uma dessas caixas de avaliação
    for i in pagina:
        
        # Salva o nome da classe do objeto (bolinhas de avaliação) e manipula esse nome para pegarmos 
        # apenas a diferença do nome da classe que representa a nota (bubble_10, bubble_20 = 1, 2 ...)
        nota = i.find_element(By.CSS_SELECTOR, "span[class*='ui_bubble_rating']").get_attribute("class").split(" ")[1]
       
       # Tenta encontrar o objeto data na caixa, caso não apareça, armazena como "None", pois a avaliação
       # não possui data visível no site
        try: data = i.find_element(By.CSS_SELECTOR, "span[class*='teHYY']")
        except: data = "none"
        
        if data != "none":
            data = data.text.split(":")[1]
            
        # Dicionário para converter o nome da classe para número
        dic = {"bubble_50": 5, "bubble_40":4, "bubble_30":3, "bubble_20": 2, "bubble_10":1}
    
        # Adiciona os valores encontrados na caixa, nas listas "notas" e "datas"
        notas.append(dic[nota])
        datas.append(data)
  
    # Tenta locaizar o objeto (botão de dar skip da página), caso encontre, ele espera até ele
    # aparecer na tela e clica nele. Caso não encontre, ele continua para evitar erros de código
    try:
        WebDriverWait(window, 5).until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Next")))
        window.find_element(By.LINK_TEXT, "Next").click()
    except: print("Última página")
    
    # Retorna um conjunto de 10 notas e 10 datas, que estão armazenadas nas listas notas e datas
    return notas, datas
# --------------------------------------------------------------------------------------------------

# Com a função criada, devemos criar o loop próprio para executarmos para todas as páginas de avaliações
dados= []
dados1, dados2 = [], []

# Loop que irá percorrer n páginas. (Nesse caso, o tamanho será determinado pelo número de avaliações totais,
# pelo número de avaliações por página (10)
for i in range(1, np.where(y%10 == 0, y//10+1, y//10+2)):
    
    # Condição de espera de objeto ter aparecido na tela para poder chamar a função de coleta de dados 
    WebDriverWait(window, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.YibKl.MC.R2.Gi.z.Z.BB.pBbQr")))
    
    # Testa a primeira leitura na página, chamando a função de capturar os dados
    try:
        x,y = capturar_dados(i)
        dados1+= x
        dados2+= y
        
        # Tratamento dos dados retornados pela função, nesse caso seria cortar os espaços no começo e final das datas ex: (" September 2022")
        dados2 = [i.strip() for i in dados2]
        
        # Aqui nós salvamos os dados n
        df = pd.DataFrame({"Data": dados2, "Avaliação":dados1})
        df.to_csv(f"{nome_arquivo}.csv", sep=",")
        
    # Caso a primeira leitura NÃO funcione/ ocorreu algum erro de lentidão, a função capturar_dados irá executar a mesma página  
    # pela segunda vez. O uso do try/except nesse caso foi de grande utilidade para evitar que o código parasse derrepente por 
    # um simples erro de leitura. Dessa forma, a segunda leitura serviu como um "seguro" para evitar a perda de dados.
    except: 
        try:
            sleep(0.5)
            x,y = capturar_dados(i, "novo")
            dados1+= x
            dados2+= y 
            
            dados2 = [i.strip() for i in dados2]
            df = pd.DataFrame({"Data": dados2, "Avaliação":dados1})
            df.to_csv(f"{nome_arquivo}.csv", sep=",")
        
        # Caso dê um 3º erro, ele termina o código e é dado como fim do programa 
        except: break
        
print("fim do programa")


# --------------------------------------------------------------------------------------------------

# Obs: O fato de salvar em um csv toda vez que uma página capturasse os dados faz com que eu possa parar o código antes de finalizar
# toda a captura de dados, ou seja, a condição de capturar todos os dados até a última página pode ser antecipada caso eu decida 
# forçadamente fechar o programa e mesmo assim, ainda ter todos os dados que coletei até esse momento.

# No caso desse desafio, foi pedido dados de 2019 e do meio de 2021 para até os dias atuais. Nesse caso, o código foi usado para captura
# as avaliações mais recentes até chegar nos dados de 2018, pois assim, eu poderia fechar o código e ter a base necessária para a análise.


