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
    
    return {'message': 'Aluno atualizado com sucesso'}
    

@app.post("/correcao")
async def correcao_prova(
    alternativas: List[str] = Form(...),
    arquivo: UploadFile = File(None)
):
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
def cadastro(matricula: str, materia:str, pontuacao:str, prova:str):

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