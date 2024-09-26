function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseFloat(str));
}

document.getElementById('login-btn').addEventListener('click', function(event) {
    event.preventDefault();
    
    const matricula = document.getElementById('matricula');
    const senha = document.getElementById('senha');

    if (matricula.value === "" || senha.value === "") {
        alert("Por favor, preencha ambos os campos.");
        return
    }

    if (!isNumeric(matricula.value)){
        alert("Matricula só pode conter número")
        return
    }

    const url = new URL('http://127.0.0.1:8000/login');
    url.searchParams.append('matricula', matricula.value);
    url.searchParams.append('senha', senha.value);

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorResponse => {
                console.error('Erro:', errorResponse);
                alert(`Erro: ${JSON.stringify(errorResponse)}`);
            });
        }
        return response.json();
    })
    .then(result => {
        if (result === true) {
            alert("Login realizado com sucesso!");
            matricula.value = ''
            senha.value = ''
            window.location.href = '/index.html'; 
        } else {
            alert("Usuário ou senha incorretos.");
        }
    })
    .catch(error => {
        console.error('Erro de rede:', error);
        alert('Erro de rede. Verifique o console para mais detalhes.');
    });

});