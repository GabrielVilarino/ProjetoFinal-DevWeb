document.addEventListener('DOMContentLoaded', function() {
    popularTabela();
});


function popularTabela() {
    const url = new URL('http://127.0.0.1:8000/busca_aluno');

    fetch(url)
        .then(response => {
            if (!response.ok) {
                alert('Erro ao buscar alunos.');
                return Promise.reject();
            }
            return response.json();
        })
        .then(data => {
            atualizarTabela(data);
        })
        .catch(error => {
            console.error('Erro de rede:', error);
            alert('Erro ao buscar alunos. Verifique o console para mais detalhes.');
        });
}


document.getElementById('search-btn').addEventListener('click', function() {
    const matricula = document.getElementById('search-matricula').value.trim();
    pesquisarAluno(matricula);
});

function pesquisarAluno(matricula) {
    const url = new URL('http://127.0.0.1:8000/busca_aluno');
    url.searchParams.append('matricula', matricula);

    fetch(url)
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    alert('Aluno não encontrado.');
                } else {
                    alert('Erro ao buscar aluno.');
                }
                return Promise.reject();
            }
            return response.json();
        })
        .then(data => {
            atualizarTabela(data);
        })
        .catch(error => {
            console.error('Erro de rede:', error);
        });
}

function atualizarTabela(alunos) {
    const tabelaBody = document.querySelector('#tabela-alunos tbody');
    
    tabelaBody.innerHTML = '';

    alunos.forEach(aluno => {
        const linha = document.createElement('tr');

        const prova_1 = aluno.prova_1 ? parseFloat(aluno.prova_1) : 0;
        const prova_2 = aluno.prova_2 ? parseFloat(aluno.prova_2) : 0;
        const prova_3 = aluno.prova_3 ? parseFloat(aluno.prova_3) : 0;
        const prova_4 = aluno.prova_4 ? parseFloat(aluno.prova_4) : 0;

        const media = (prova_1 + prova_2 + prova_3 + prova_4) / 4;

        linha.innerHTML = `
            <td>${aluno.nome}</td>
            <td>${aluno.materia}</td>
            <td>${aluno.prova_1 !== null ? aluno.prova_1 : '-'}</td>
            <td>${aluno.prova_2 !== null ? aluno.prova_2 : '-'}</td>
            <td>${aluno.prova_3 !== null ? aluno.prova_3 : '-'}</td>
            <td>${aluno.prova_4 !== null ? aluno.prova_4 : '-'}</td>
            <td>${media}</td> <!-- Exibir a média das notas -->
        `;

        tabelaBody.appendChild(linha);
    });
}
