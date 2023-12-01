function formHTML(){
    return `
        <form class="w-75 m-auto d-flex justify-content-center align-items-center flex-grow-1">
            <div class="form-container w-100 d-flex justify-content-center align-items-center rounded">
                <select id="equipa" class="search-field form-select" aria-label="Equipa">
                    <option value="" selected>Equipa</option>
                    <option value="academica">Academica</option>
                    <option value="arouca">Arouca</option>
                    <option value="aves">Aves</option>
                    <option value="bsad">BSAD</option>
                    <option value="beira mar">Beira Mar</option>
                    <option value="belenenses">Belenenses</option>
                    <option value="benfica">Benfica</option>
                    <option value="boavista">Boavista</option>
                    <option value="braga">Braga</option>
                    <option value="chaves">Chaves</option>
                    <option value="estoril">Estoril</option>
                    <option value="fc portoo">FC Porto</option>
                    <option value="famalicao">Famalicao</option>
                    <option value="farense">Farense</option>
                    <option value="feirense">Feirense</option>
                    <option value="ferreira">Ferreira</option>
                    <option value="gil vicente">Gil Vicente</option>
                    <option value="guimaraes">Guimaraes</option>
                    <option value="leiria">Leiria</option>
                    <option value="maritimo">Maritimo</option>
                    <option value="moreirense">Moreirense</option>
                    <option value="nacional">Nacional</option>
                    <option value="naval">Naval</option>
                    <option value="olhanense">Olhanense</option>
                    <option value="penafiel">Penafiel</option>
                    <option value="portimonense">Portimonense</option>
                    <option value="rio ave">Rio Ave</option>
                    <option value="santa clara">Santa Clara</option>
                    <option value="setubal">Setubal</option>
                    <option value="sporting">Sporting</option>
                    <option value="tondela">Tondela</option>
                    <option value="u madeira">U. Madeira</option>
                    <option value="vizela">Vizela</option>
                </select>
                <div class="sep"></div>
                <select id="origem" class="search-field form-select" aria-label="Origem">
                    <option value="" selected>Origem</option>
                    <option value="record">Record</option>
                    <option value="ojogo">OJogo</option>
                    <option value="abola">ABola</option>
                </select>
                <div class="sep"></div>
                <input type="text" class="search-field flex-grow-1" placeholder="Pesquise por algo..."/>
                <button type="submit" class="search-field"><svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 512 512"><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg></button>
            </div>
        </form>
    `
}

function renderHome(){
    document.querySelector('body').innerHTML = `
    <div class="w-75">
        ${formHTML()}
    </div>
    `
    bindForm()
}

function loading(){
    document.querySelector('body').innerHTML = `<div class="spinner-grow" role="status"></div><div class="spinner-grow" role="status"></div><div class="spinner-grow" role="status"></div>`
}

function openArticle(article){
    localStorage.setItem('cachedResults', document.querySelector('ul').outerHTML)

    document.querySelector('ul').outerHTML = `
        <article class="d-flex justify-content-center">
            <a id="back"><svg xmlns="http://www.w3.org/2000/svg" height="16" width="14" viewBox="0 0 448 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2023 Fonticons, Inc.--><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/></svg></a>
            <div class="card w-75 m-auto expanded">
                <div class="card-body">
                    <a class="card-title">${article.title}</a>
                    <p class="card-text py-2">${article.content}</p>
                </div>
            </div>
        </article>
    `

    document.getElementById('back').addEventListener('click', renderCached)
}

function renderCached(){
    document.querySelector('article').outerHTML = localStorage.getItem('cachedResults')
    bindArticles()
}

function renderArticle(article){
    const icon = article.origin == 'record' 
        ? 'record.ico'
        : article.origin == 'ojogo'
            ? 'ojogo.png'
            : 'abola.ico'

    return `
        <div class="card">
            <div class="card-body">
                <a class="card-title">${article.title.trim()}<img class="origin" src="../static/${icon}"/></a>
                <h5 class="card-title">${article.date.substr(0, 10)}</h5>
                <p class="card-text">${article.content}</p>
            </div>
        </div>
    `
}

function bindArticles(){
    const data = JSON.parse(localStorage.getItem("data"))

    const articles = document.querySelectorAll('a')
    for(let i = 0; i < articles.length; i++)
        articles[i].addEventListener('click', () => {
            openArticle(data[i])
        })
}

function renderResults(data){
    localStorage.setItem("data", JSON.stringify(data))

    document.querySelector('body').innerHTML = `
        <main>
            <div class="p-5 d-flex align-items-center">
                <svg xmlns="http://www.w3.org/2000/svg" id="icon" class="mr-5" height="48" width="48" viewBox="0 0 512 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2023 Fonticons, Inc.--><path d="M417.3 360.1l-71.6-4.8c-5.2-.3-10.3 1.1-14.5 4.2s-7.2 7.4-8.4 12.5l-17.6 69.6C289.5 445.8 273 448 256 448s-33.5-2.2-49.2-6.4L189.2 372c-1.3-5-4.3-9.4-8.4-12.5s-9.3-4.5-14.5-4.2l-71.6 4.8c-17.6-27.2-28.5-59.2-30.4-93.6L125 228.3c4.4-2.8 7.6-7 9.2-11.9s1.4-10.2-.5-15l-26.7-66.6C128 109.2 155.3 89 186.7 76.9l55.2 46c4 3.3 9 5.1 14.1 5.1s10.2-1.8 14.1-5.1l55.2-46c31.3 12.1 58.7 32.3 79.6 57.9l-26.7 66.6c-1.9 4.8-2.1 10.1-.5 15s4.9 9.1 9.2 11.9l60.7 38.2c-1.9 34.4-12.8 66.4-30.4 93.6zM256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm14.1-325.7c-8.4-6.1-19.8-6.1-28.2 0L194 221c-8.4 6.1-11.9 16.9-8.7 26.8l18.3 56.3c3.2 9.9 12.4 16.6 22.8 16.6h59.2c10.4 0 19.6-6.7 22.8-16.6l18.3-56.3c3.2-9.9-.3-20.7-8.7-26.8l-47.9-34.8z"/></svg>
                ${formHTML()}
            </div>
            ${data.length == 0
                ? '<div id="noresults">Sem Resultados :(</div>'
                : `
                <ul class="p-0 mx-5 mt-0 h-100 overflow-scroll">
                    ${data.map(renderArticle).join('')}
                </ul>
                `
            }
        </main>
    `

    bindArticles()
    bindForm()
}

async function performSearch(query, team, origin){
    const BACKEND_URL = 'http://localhost:5000/solr/'

    var query = {
        q: `${team ? `(title:${team}) AND ` : ''}${origin ? `(origin:${origin}) AND ` : ''}(content:${query})`,
        rows: 10,
        wt: "json"
    };

    loading()

    $.ajax({
        url: BACKEND_URL,
        data: query,
        dataType: 'json',
        headers: { method: 'GET' },
        success: function(data) {
            console.log(data)
            renderResults(data)
        },
        error: function(_) {
            renderHome()
        }
    });
}

function bindForm(){
    const form = document.querySelector('form')
    if(!form) return

    form.addEventListener('submit', e => {
        e.preventDefault()

        const input = document.querySelector('input')
        if(!input) return

        const team = document.getElementById('equipa')
        if(!team) return

        const origin = document.getElementById('origem')
        if(!origin) return

        console.log('Query: ', input.value)
        console.log('Filter Equipa: ', team.value ? team.value : 'None')
        console.log('Filter Origem: ', origin.value ? origin.value : 'None')

        if(input.value !== '')
            performSearch(input.value, team.value, origin.value)
    })
}

renderHome()
