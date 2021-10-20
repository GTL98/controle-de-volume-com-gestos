################################################################################################
#                                                                                              #
#  Toda a lógica mais detalhada está presente no arquivo "Controle de Volume com Jestos.ipynb" #
#                                                                                              #
#  Em caso de dúvidas, consultar a documentação:                                               #
#      - "Aula 1 - Rastreamento de mão (Introdução).ipynb" no link abaixo.                     #
#                                                                                              #
#  GitHub: https://github.com/GTL98/curso-completo-de-visao-computacional-avancada-com-python  #
#                                                                                              #
################################################################################################


# Importar as blbiotecas
import cv2
import time
import math
import numpy as np
import rastreamento_mao as rm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# Definir o tamanho da tela
largura_tela = 640
altura_tela = 480


# Taxa de frame (FPS)
tempo_anterior = 0
tempo_atual = 0

# Módulo DetectorMao
detector = rm.DetectorMao(deteccao_confianca=0.7, rastreamento_confianca=0.7)


# Módulo para mexer no volume
# código pego do repositório: https://github.com/AndreMiras/pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#print(volume.GetVolumeRange())  # vai de -65,25 a 0
volume_range = volume.GetVolumeRange()
min_volume = volume_range[0]
max_volume = volume_range[1]


# Captura de vídeo
cap = cv2.VideoCapture(0)
cap.set(3, largura_tela)
cap.set(4, altura_tela)
vol = 0
vol_barra = 400
vol_porcentagem = 0

while True:
    sucesso, imagem = cap.read()
    imagem = detector.encontrar_maos(imagem)
    lista_landmark = detector.encontrar_posicao(imagem, desenho=False)
    
    # Pegar as posições das landmarks que usaremos
    if lista_landmark:
        # Landmark número 4
        pos_4_x = lista_landmark[4][1]
        pos_4_y = lista_landmark[4][2]
        
        #Landmark número 8
        pos_8_x = lista_landmark[8][1]
        pos_8_y = lista_landmark[8][2]
        
        # Desenhar um círculo na landmark 4
        cv2.circle(imagem, (pos_4_x, pos_4_y), 10, (255, 0, 255), cv2.FILLED)
        
        # Desenhar um círculo na landmark 8
        cv2.circle(imagem, (pos_8_x, pos_8_y), 10, (255, 0, 255), cv2.FILLED)
        
        # Cirar uma linha entre as duas landmarks
        cv2.line(imagem, (pos_4_x, pos_4_y), (pos_8_x, pos_8_y), (255, 0, 255), 3)
        
        # Encontrar o meio da linha
        cx = (pos_4_x + pos_8_x) // 2
        cy = (pos_4_y + pos_8_y) // 2
        
        # Desenhar um círculo no meio da linha
        cv2.circle(imagem, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        
        # Descobrir o comprimento da linha
        comprimento = math.hypot(pos_8_x - pos_4_x, pos_8_y - pos_4_y)
        if comprimento < 50:
            cv2.circle(imagem, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
        if comprimento > 230:
            cv2.circle(imagem, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        
        # Range da mão: 50 - 200
        # Range do volume: -65,25 - 0
        
        # Converter o range da mão para o range do volume
        vol = np.interp(comprimento, [50, 200], [min_volume, max_volume])
        
        # Alterar o volume
        volume.SetMasterVolumeLevel(vol, None)
        
    # Desenhar um retângulo para a porcentagem de volume
    cv2.rectangle(imagem, (30, 120), (65, 370), (0, 255, 0), 3)
    
    # Converter o range do volume para o range do retângulo
    vol_barra = np.interp(comprimento, [50, 200], [370, 120])
    if vol_barra <= 145:
        cor_barra = (0, 0, 255)
    elif vol_barra >= 345:
        cor_barra = (255, 0, 0)
    else:
        cor_barra = (0, 255, 0)
    
    # Desenhar o retângulo de preenchimento
    cv2.rectangle(imagem, (30, int(vol_barra)), (65, 370), cor_barra, cv2.FILLED)
    
    # Converter o range de volume para porcentagem
    vol_porcentagem = np.interp(comprimento, [50, 200], [0, 100])
    if vol_porcentagem <= 10:
        cor_porcentagem = (255, 0, 0)
    elif vol_porcentagem >= 90:
        cor_porcentagem = (0, 0, 255)
    else:
        cor_porcentagem = (0, 255, 0)
    
    # Escrever a porcentagem na tela
    cv2.putText(imagem, f'{int(vol_porcentagem)}%', (20, 420), cv2.FONT_HERSHEY_COMPLEX, 1, cor_porcentagem, 2)
    
    # Configurar o FPS
    tempo_atual = time.time()
    fps = 1/(tempo_atual - tempo_anterior)
    tempo_anterior = tempo_atual
    
    # Mostrar o FPS na tela
    cv2.putText(imagem, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
    
    # Mostrar a imagem na tela
    cv2.imshow('Imagem', imagem)
    
    # Terminar o loop
    if cv2.waitKey(1) & 0xFF == ord('s'):
        break
        
# Fecha a tela de captura
cap.release()
cv2.destroyAllWindows()
