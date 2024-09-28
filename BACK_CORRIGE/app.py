from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from script_camera import main
from src import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
def login(matricula: str, senha: str):
    """
    Realiza o login verificando a matrícula e a senha no banco de dados.

    Parâmetros:
    - matricula (str): Matrícula do usuário.
    - senha (str): Senha do usuário.

    Retorna:
    - True se o login for bem-sucedido.
    - False se as credenciais forem inválidas.
    - Lança uma exceção HTTP 500 em caso de erro.
    """
    try:
        query = '''
            SELECT matricula
            FROM devweb.admin
            WHERE matricula = :matricula
            AND senha = :senha
        '''
        params = {'matricula': matricula, 'senha': senha}
        
        results = db.execute_query(query, params)

        if not results:
            return False

        return True

    except Exception as e:
        print(f"Erro durante o login: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/busca_aluno")
def busca_aluno(matricula: str | None = None):
    """
    Busca informações de alunos e suas notas. Se a matrícula for fornecida, 
    retorna os dados do aluno correspondente, caso contrário, retorna os dados de todos os alunos.

    Parâmetros:
    - matricula (str | None): Matrícula do aluno. Opcional.

    Retorna:
    - Lista de dicionários contendo o nome do aluno, a matéria e suas notas.
    - Lança uma exceção HTTP 404 se o aluno não for encontrado.
    - Lança uma exceção HTTP 500 em caso de erro.
    """
    try:
        query = '''
            SELECT a.nome,
                   h.materia,
                   h.prova_1,
                   h.prova_2,
                   h.prova_3,
                   h.prova_4
            FROM devweb.alunos a
            JOIN devweb.historico h ON a.matricula = h.matricula_aluno
        '''

        params = None

        if matricula or matricula is not None and matricula.strip() != '':
            query += 'WHERE a.matricula = :matricula '
            params = {'matricula': matricula}

        query += 'ORDER BY a.matricula'
        
        results = db.execute_query(query, params)

        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        
        alunos_data = []
        for aluno_data in results:
            aluno = {
                "nome": aluno_data[0],
                "materia": aluno_data[1],
                "prova_1": aluno_data[2],
                "prova_2": aluno_data[3],
                "prova_3": aluno_data[4],
                "prova_4": aluno_data[5]
            }
            alunos_data.append(aluno)

        return alunos_data

    except Exception as e:
        print(f"Erro durante o login: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/dados_alunos")
def dados_aluno(matricula: str | None = None):
    """
    Busca informações básicas de alunos, como nome, turma e matéria. 
    Se a matrícula for fornecida, retorna os dados do aluno correspondente; 
    caso contrário, retorna os dados de todos os alunos.

    Parâmetros:
    - matricula (str | None): Matrícula do aluno. Opcional.

    Retorna:
    - Lista de dicionários contendo o nome, turma e matéria do aluno.
    - Lança uma exceção HTTP 404 se o aluno não for encontrado.
    - Lança uma exceção HTTP 500 em caso de erro.
    """
    try:
        query = '''
            SELECT nome,
                   turma,
                   materia
            FROM devweb.alunos a
        '''

        params = None

        if matricula or matricula is not None and matricula.strip() != '':
            query += 'WHERE a.matricula = :matricula '
            params = {'matricula': matricula}

        query += 'ORDER BY a.matricula'
        
        results = db.execute_query(query, params)

        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        
        alunos_data = []
        for aluno_data in results:
            aluno = {
                "nome": aluno_data[0],
                "turma": aluno_data[1],
                "materia": aluno_data[2],
            }
            alunos_data.append(aluno)

        return alunos_data

    except Exception as e:
        print(f"Erro durante o login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cadastro_aluno")
def cadastro(matricula: str, nome:str, materia:str, turma:str):
    """
    Cadastra um novo aluno no banco de dados e adiciona seu histórico acadêmico.

    Parâmetros:
    - matricula (str): Matrícula do aluno.
    - nome (str): Nome do aluno.
    - materia (str): Matéria associada ao aluno.
    - turma (str): Turma do aluno.

    Processos:
    - Insere os dados do aluno na tabela 'alunos'.
    - Adiciona a matrícula e a matéria na tabela 'historico'.
    
    Retorna:
    - Mensagem de sucesso se o aluno for cadastrado corretamente.
    - Lança exceções HTTP 404 ou 500 em caso de erro.
    """
    query = """
            INSERT INTO devweb.alunos (matricula, nome, materia, turma)
            VALUES (:matricula, :nome, :materia, :turma)
            RETURNING matricula
            """
    params = {"matricula": matricula, "nome": nome, "materia": materia, "turma": turma}

    try:
        result = db.execute_query(query, params)
        if len(result) > 0:
            matricula_inserida = result[0][0]
        else:
            raise HTTPException(status_code=404, detail="Erro ao adicionar aluno")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

    query_insert_historico = """
                            INSERT INTO devweb.historico (matricula_aluno, materia)
                            VALUES (:matricula_aluno, :materia)
                            RETURNING matricula_aluno
                            """
    params_historico = {"matricula_aluno": matricula_inserida, "materia": materia}

    try:
        result = db.execute_query(query_insert_historico, params_historico)
        if len(result) == 0:
            raise HTTPException(status_code=404, detail="Erro ao adicionar histórico")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    
    return {'message': 'Aluno cadastrado com sucesso'}


@app.put("/update_aluno")
def update_aluno(matricula: str, nome: str, materia: str, turma: str):
    """
    Atualiza as informações de um aluno no banco de dados, incluindo nome, matéria e turma.
    Também atualiza a matéria correspondente no histórico do aluno.

    Parâmetros:
    - matricula (str): Matrícula do aluno.
    - nome (str): Novo nome do aluno.
    - materia (str): Nova matéria do aluno.
    - turma (str): Nova turma do aluno.

    Retorna:
    - Mensagem de sucesso se o aluno for atualizado corretamente.
    - Lança exceções HTTP 404 se o aluno não for encontrado ou houver erro ao atualizar.
    - Lança exceção HTTP 500 em caso de erro interno.
    """
    query = """
            UPDATE devweb.alunos
            SET
                nome = :nome,
                materia = :materia,
                turma = :turma
            WHERE
                matricula = :matricula

            RETURNING materia
            """

    params = {"matricula": matricula, "nome": nome, "materia": materia, "turma": turma}

    try:
        result = db.execute_query(query, params)
        if result:
            query_materia = """
                            UPDATE devweb.historico
                            SET
                                materia = :materia
                            WHERE
                                matricula_aluno = :matricula
                            RETURNING materia
                            """
            params_materia = {"matricula": matricula, "materia": materia}

            result_materia = db.execute_query(query_materia, params_materia)

            if result_materia:
                return {"message": f"Aluno atualizado com sucesso."}
            else:
                raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        else:
            raise HTTPException(status_code=404, detail="Erro ao atualizar aluno")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    

@app.post("/correcao")
async def correcao_prova(
    alternativas: List[str] = Form(...),
    arquivo: UploadFile = File(None)
):
    """
    Corrige uma prova com base nas alternativas fornecidas e um arquivo de imagem opcional.

    Parâmetros:
    - alternativas (List[str]): Lista de alternativas selecionadas pelo aluno.
    - arquivo (UploadFile | None): Arquivo de imagem da prova para correção (opcional).

    Retorna:
    - Dicionário contendo:
      - 'respostas_corretas': Lista de respostas corretas, se houver.
      - 'respostas_erradas': Lista de respostas incorretas, se houver.
      - 'pontuacao': Pontuação total da prova.
      
    Lança exceção HTTP 500 em caso de erro.
    """
    try:
        data = {}

        if arquivo:
            contents = await arquivo.read()

            pontuacao, respostas_acertadas, respostas_erradas = main.correcao_prova(img_bytes=contents, alternativas=alternativas)
            
            
            if len(respostas_acertadas) != 0:
                data['respostas_corretas'] = respostas_acertadas
            
            if len(respostas_erradas) != 0:
                data['respostas_erradas'] = respostas_erradas
            
            data['pontuacao'] = pontuacao

        return data

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.put("/inserir_nota")
def inserir_nota(matricula: str, materia:str, pontuacao:str, prova:str):
    """
    Insere ou atualiza a nota de uma prova específica para um aluno em uma determinada matéria.

    Parâmetros:
    - matricula (str): Matrícula do aluno.
    - materia (str): Matéria em que a prova foi realizada.
    - pontuacao (str): Pontuação obtida na prova.
    - prova (str): Nome da prova (ex: prova_1, prova_2).

    Retorna:
    - Mensagem de sucesso se a nota for inserida ou atualizada corretamente.
    - Lança exceções HTTP 404 se o registro não for encontrado.
    - Lança exceção HTTP 500 em caso de erro interno.
    """
    query = f"""
            UPDATE devweb.historico
            SET
                {prova} = :pontuacao
            WHERE
                matricula_aluno = :matricula
            AND
                materia = :materia
            RETURNING matricula_aluno
            """
    params = {"pontuacao": int(pontuacao), "matricula": matricula, "materia": materia}

    try:
        result = db.execute_query(query, params)
        if len(result) > 0:
            matricula_inserida = result[0][0]
        else:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    
    return {'message': 'Nota Inserida com sucesso!'}


@app.delete("/delete_aluno")
def delete_aluno(matricula: str):
    """
    Exclui um aluno e seu histórico do banco de dados com base na matrícula.

    Parâmetros:
    - matricula (str): Matrícula do aluno a ser deletado.

    Processo:
    - Exclui o histórico do aluno da tabela 'historico'.
    - Exclui o registro do aluno da tabela 'alunos' se o histórico for removido com sucesso.

    Retorna:
    - Mensagem de sucesso se o aluno e seu histórico forem deletados corretamente.
    - Lança exceção HTTP 404 se o aluno ou o histórico não forem encontrados.
    - Lança exceção HTTP 500 em caso de erro interno.
    """
    try:
        query = '''
            DELETE FROM devweb.historico
            WHERE matricula_aluno = :matricula
            RETURNING matricula_aluno
        '''
        params = {'matricula': matricula}

        result = db.execute_query(query, params)

        if result:
            query_delete = '''
                            DELETE FROM devweb.alunos
                            WHERE matricula = :matricula
                            RETURNING matricula
                           '''
            params = {'matricula': matricula}

            result_delete = db.execute_query(query_delete, params)

            if result_delete:
                return {"message": f"Aluno com matrícula {matricula} foi deletado com sucesso."}
            else:
                raise HTTPException(status_code=404, detail="Aluno não encontrado.")

        else:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    except Exception as e:
        print(f"Erro durante a exclusão: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")