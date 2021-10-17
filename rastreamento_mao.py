################################################################################################
#                                                                                              #
#  Todo esse código será feito na extensão .py para que seja possível usá-lo nos projetos.     #
#                                                                                              #
#  Todas as anotações e explicações sobre o que está sendo usado nesse documento podem ser     #
#  encontradas no documento "Aula 1 - Rastramento de mão (Introdução).ipynb".                  #
#                                                                                              #
#  GitHub: https://github.com/GTL98/curso-completo-de-visao-computacional-avancada-com-python  #
#                                                                                              #
################################################################################################


import cv2
import mediapipe as mp
import time


class DetectorMao:
    def __init__(self, modo=False, max_maos=2, deteccao_confianca=0.5, rastreamento_confianca=0.5):
        self.modo = modo
        self.max_maos = max_maos
        self.deteccao_confianca = deteccao_confianca
        self.rastreamento_confianca = rastreamento_confianca


        # Mãos
        self.mpMaos = mp.solutions.hands
        self.maos = self.mpMaos.Hands(self.modo, self.max_maos, self.deteccao_confianca, self.rastreamento_confianca)

        # Desenhar as landmarks
        self.mp_desenho = mp.solutions.drawing_utils

    def encontrar_maos(self, imagem, desenho=True):
        # Converter a cor da imagem (o Mediapipe usa somente imagens em RGB e o OpenCV captura em BGR)
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

        # Resultado do processamento da imagem
        self.resultados = self.maos.process(imagem_rgb)

        # Colocar as landmarks na mão
        if self.resultados.multi_hand_landmarks:
            for mao_landmark in self.resultados.multi_hand_landmarks:
                if desenho:
                    self.mp_desenho.draw_landmarks(imagem, mao_landmark, self.mpMaos.HAND_CONNECTIONS,
                                             self.mp_desenho.DrawingSpec(color=(0, 0, 255)),
                                             self.mp_desenho.DrawingSpec(color=(0, 255, 0)))
                    
        return imagem
    
    def encontrar_posicao(self, imagem, num_mao=0, desenho=True):
        lista_landmark = []
        
        if self.resultados.multi_hand_landmarks:
            minha_mao = self.resultados.multi_hand_landmarks[num_mao]
            
            for item, landmark in enumerate(minha_mao.landmark):
                altura, largura, centro = imagem.shape
                cx, cy = int(landmark.x*largura), int(landmark.y*altura)
                lista_landmark.append([item, cx, cy])
                
                if desenho:
                    cv2.circle(imagem, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
            
        return lista_landmark


def main():
    tempo_anterior = 0
    tempo_atual = 0
    
    cap = cv2.VideoCapture(0)
    
    detector = DetectorMao()
    
    while True:
        sucesso, imagem = cap.read()
        imagem = detector.encontrar_maos(imagem)
        lista_landmark = detector.encontrar_posicao(imagem)
        
        # Configurar o FPS da captura
        tempo_atual = time.time()
        fps = 1 / (tempo_atual - tempo_anterior)
        tempo_anterior = tempo_atual

        # Colcar o valor de FPS na tela
        cv2.putText(imagem, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # Mostrar a imagem na tela
        cv2.imshow('Imagem', imagem)
        
        # Terminar o loop
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    
    # Fechar a tela de captura
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
