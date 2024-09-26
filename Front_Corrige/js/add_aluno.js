document.getElementById('adicionar-aluno-form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const nome = document.getElementById('nome');
    const matricula = document.getElementById('matricula');
    const turma = document.getElementById('turma');
    const materia = document.getElementById('materia');

   
    const url = new URL('http://127.0.0.1:8000/cadastro_aluno');
    url.searchParams.append('nome', nome.value);
    url.searchParams.append('matricula', matricula.value);
    url.searchParams.append('turma', turma.value);
    url.searchParams.append('materia', materia.value);


    fetch(url, {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorResponse => {
                console.error('Erro:', errorResponse);
                alert('Erro ao adicionar aluno')
                return Promise.reject();
            });
        }
        return response.json();
    })
    .then(result => {
        if (result){
            alert('Aluno adicionado com sucesso!');
            nome.value = ''
            matricula.value = ''
            turma.value = ''
            materia.value = ''
        }
    })
    .catch(error => {
        console.error('Erro de rede:', error);
    });
});
