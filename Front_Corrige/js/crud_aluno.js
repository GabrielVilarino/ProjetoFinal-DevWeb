document.getElementById('buscar-aluno-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const matricula = document.getElementById('matricula');
    const nome = document.getElementById('nome');
    const turma = document.getElementById('turma');
    const materia = document.getElementById('materia');

    const url = new URL('http://127.0.0.1:8000/dados_alunos');
    url.searchParams.append('matricula', matricula.value)

    fetch(url)
    .then(response => response.json())
    .then(alunos => {
        const aluno = alunos[0]
        if (aluno) {
            nome.value = aluno.nome;
            turma.value = aluno.turma;
            materia.value = aluno.materia;
            document.getElementById('aluno-info').classList.remove('hidden');
        } else {
            alert('Aluno não encontrado!');
            nome.value = '';
            turma.value = '';
            materia.value = '';
            document.getElementById('aluno-info').classList.add('hidden')
        }
    })
    .catch(error => console.error('Erro ao buscar o aluno:', error));
});

document.getElementById('atualizar-btn').addEventListener('click', function() {
    const matricula = document.getElementById('matricula');
    const nome = document.getElementById('nome');
    const turma = document.getElementById('turma');
    const materia = document.getElementById('materia');

    const url = new URL('http://127.0.0.1:8000/update_aluno');
    url.searchParams.append('matricula', matricula.value)
    url.searchParams.append('nome', nome.value)
    url.searchParams.append('turma', turma.value)
    url.searchParams.append('materia', materia.value)

    fetch(url, {
        method: 'PUT',
    })
    .then(response => response.json())
    .then(result => {
        alert('Aluno atualizado com sucesso!');
    })
    .catch(error => console.error('Erro ao atualizar o aluno:', error));
});

document.getElementById('excluir-btn').addEventListener('click', function() {
    const matricula = document.getElementById('matricula');
    const nome = document.getElementById('nome');
    const turma = document.getElementById('turma');
    const materia = document.getElementById('materia');

    const url = new URL('http://127.0.0.1:8000/delete_aluno');
    url.searchParams.append('matricula', matricula.value)

    if (confirm('Tem certeza que deseja excluir este aluno?')) {
        fetch(url, {
            method: 'DELETE'
        })
        .then(response => {
            if (response){
                matricula.value = ''
                nome.value = ''
                turma.value = ''
                materia.value = ''
                document.getElementById('aluno-info').classList.add('hidden');
                alert('Aluno excluído com sucesso!');
            }
            
        })
        .catch(error => console.error('Erro ao excluir o aluno:', error));
    }
});
