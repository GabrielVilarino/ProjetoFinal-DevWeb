function formatarPontuacao(label){
    partes = label.split(' ')
    pontuacao = partes[1]

    return pontuacao
}

function processarResultado(result) {
    const { respostas_corretas, respostas_erradas, pontuacao } = result; // Desestrutura o JSON

    const labelAcertos = document.getElementById('questoesAcertadas');
    const labelErros = document.getElementById('questoesErradas');
    const labelPontuacao = document.getElementById('pontuacao');
    const divResultado = document.getElementById('resultado')

    divResultado.style.display = 'flex'

    if (respostas_corretas && Array.isArray(respostas_corretas)) {
        labelAcertos.textContent += respostas_corretas.join(', ');
    }

    if (respostas_erradas && Array.isArray(respostas_erradas)) {
        labelErros.textContent += respostas_erradas.join(', ');
    }

    if (pontuacao !== undefined) {
        labelPontuacao.textContent += pontuacao;
    }
}

document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const labelAcertos = document.getElementById('questoesAcertadas');
    const labelErros = document.getElementById('questoesErradas');
    const labelPontuacao = document.getElementById('pontuacao');

    labelAcertos.textContent = 'Questões Acertadas: ';
    labelErros.textContent = 'Questões Erradas: ';
    labelPontuacao.textContent = 'Pontuação: ';

    const alternativas = document.getElementById('alternativas').value.split(',').map(alt => alt.trim());
    const arquivo = document.getElementById('arquivo').files[0];

    const formData = new FormData();
    alternativas.forEach(alt => formData.append('alternativas', alt));

    if (arquivo) {
        formData.append('arquivo', arquivo);
    }

    // console.log('FormData Conteúdo:');
    // for (const pair of formData.entries()) {
    //     console.log(`${pair[0]}: ${pair[1]}`);
    // }

    fetch('http://127.0.0.1:8000/correcao', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorResponse => {
                console.error('Erro:', errorResponse);
            });
        }
        return response.json();
    })
    .then(result => {
        processarResultado(result);
        const data = JSON.stringify(result);
        console.log(data);
    })
    .catch(error => {
        console.error('Erro de rede:', error);
        alert('Erro de rede. Verifique o console para mais detalhes.');
    });
});

document.getElementById('btnEnviar').addEventListener('click', function() {

    const divResultado = document.getElementById('resultado');
    const displayStyle = window.getComputedStyle(divResultado).display;

    if (displayStyle === 'none') {
        alert('Faça a correção de uma prova para poder salvar!');
        return
    }

    const matricula = document.getElementById('matricula');
    const materia = document.getElementById('materia');
    const alternativas = document.getElementById('alternativas');
    const arquivo = document.getElementById('arquivo');
    const prova = document.getElementById('prova');
    const labelPontuacao = document.getElementById('pontuacao').textContent;
    
    const pontuacao = formatarPontuacao(labelPontuacao)
    
    const url = new URL('http://127.0.0.1:8000/inserir_nota');
    url.searchParams.append('matricula', matricula.value);
    url.searchParams.append('materia', materia.value);
    url.searchParams.append('pontuacao', pontuacao);
    url.searchParams.append('prova', prova.value);

    fetch(url, {
        method: 'PUT',
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorResponse => {
                console.error('Erro:', errorResponse);
                if (response.status === 404) {
                    alert('Registro não encontrado. Verifique se a matrícula e a matéria estão corretas.');
                } else if (response.status === 500) {
                    alert('Erro interno do servidor. Tente novamente mais tarde.');
                } else {
                    alert(`Erro: ${JSON.stringify(errorResponse)}`);
                }
            });
        }
        return response.json();
    })
    .then(result => {
        if(result){
            alert(result.message)
            matricula.value = '';
            materia.value = '';
            alternativas.value = '';
            arquivo.value = '';
            prova.selectedIndex = 0;

            divResultado.style.display = 'none';
        }
        
    })
    .catch(error => {
        console.error('Erro de rede:', error);
    });
});