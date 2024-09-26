import cv2
import pickle
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import extrairGabarito as exG
import numpy as np

def correcao_prova(img_bytes : bytes, alternativas: list):
    campos = []
    with open(r'C:\Users\gabri\OneDrive\Documentos\BACK_CORRIGE\script_camera\campos.pkl', 'rb') as arquivo:
        campos = pickle.load(arquivo)

    resp = []
    with open(r'C:\Users\gabri\OneDrive\Documentos\BACK_CORRIGE\script_camera\resp.pkl', 'rb') as arquivo:
        resp = pickle.load(arquivo)

    respostas_corretas = []

    for indice, alternativa in enumerate(alternativas):
        respostas_corretas.append(f'{indice + 1}-{alternativa}')

    # respostasCorretas = ["1-A", "2-C", "3-B", "4-A", "5-D"]
    # imagem_path = r'C:\Users\gabri\OneDrive\Documentos\PROJETO FINAL\tmp\img.jpeg'

    nparr = np.frombuffer(img_bytes, np.uint8)
    imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Verificar se a imagem foi carregada corretamente
    if imagem is None:
        print(f"Erro ao carregar a imagem. Verifique o arquivo e tente novamente.")
    else:
        imagem = cv2.resize(imagem, (600, 700))

        # Tentar extrair o maior contorno
        gabarito, bbox = exG.extrairMaiorCtn(imagem)

        if gabarito is None:
            # Se não encontrar nenhum contorno, exibir a mensagem e encerrar
            cv2.putText(imagem, "Nenhum contorno encontrado", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('img', imagem)
            cv2.waitKey(0)  # Espera até você fechar a imagem
            cv2.destroyAllWindows()
        else:
            imgGray = cv2.cvtColor(gabarito, cv2.COLOR_BGR2GRAY)
            ret, imgTh = cv2.threshold(imgGray, 70, 255, cv2.THRESH_BINARY_INV)
            cv2.rectangle(imagem, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 3)

            respostas = []
            for id, vg in enumerate(campos):
                x = int(vg[0])
                y = int(vg[1])
                w = int(vg[2])
                h = int(vg[3])
                cv2.rectangle(gabarito, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(imgTh, (x, y), (x + w, y + h), (255, 255, 255), 1)
                campo = imgTh[y:y + h, x:x + w]
                height, width = campo.shape[:2]
                tamanho = height * width
                pretos = cv2.countNonZero(campo)
                percentual = round((pretos / tamanho) * 100, 2)

                if percentual >= 15:
                    cv2.rectangle(gabarito, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    respostas.append(resp[id])

            # Comparar com as respostas corretas
            erros = 0
            acertos = 0
            respostas_acertadas = []
            respostas_erradas = []

            if len(respostas) == len(respostas_corretas):
                for num, res in enumerate(respostas):
                    if res == respostas_corretas[num]:
                        acertos += 1
                        respostas_acertadas.append(res)
                    else:
                        erros += 1
                        respostas_erradas.append(res)

                pontuacao = int(acertos * 2)
                # cv2.putText(imagem, f'ACERTOS: {acertos}, PONTOS: {pontuacao}', (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            

            # # Exibir as imagens processadas
            # cv2.imshow('img', imagem)
            # cv2.imshow('Gabarito', gabarito)
            # cv2.imshow('IMG TH', imgTh)
            # cv2.waitKey(0)  # Espera até você fechar as janelas
            # cv2.destroyAllWindows()
            return pontuacao, respostas_acertadas, respostas_erradas
