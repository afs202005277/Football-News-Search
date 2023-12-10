let relevantDocuments = []
let divsSeen = []

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
    <div id="search">
        <img src="../static/logo.png" width="400px" alt="News Logo">
        <div class="w-75">
            ${formHTML()}
        </div>
    </div>
    `
    bindForm()
}

function loading(){
    document.querySelector('body').innerHTML = `<div class="spinner-grow" role="status"></div><div class="spinner-grow" role="status"></div><div class="spinner-grow" role="status"></div>`
}

function loadSeeMore() {
    let seeMoreButtons = document.querySelectorAll('.seeMoreButton')
    
    for (let i = 0; i < seeMoreButtons.length; i++) {
        seeMoreButtons[i].addEventListener('click', function() {
            box = seeMoreButtons[i].parentElement
            box.textContent = `${window.teamInfo[box.previousSibling.textContent]}`
        })
    }
}

function openArticle(article){
    if (document.querySelector('ul')) localStorage.setItem('cachedResults', document.querySelector('ul').outerHTML)

    const BACKEND_URL = 'http://localhost:5000/relatedContent/'
    let doc = `${article.title} ${article.content}`


    $.ajax({
        url: BACKEND_URL,
        data: doc,
        dataType: 'json',
        headers: { method: 'GET' },
        success: function(data) {
            renderRelated(data)
        },
        error: function(_) {
            renderHome()
        }
    });


    const words = article.content.split(' ');

    article.content = ""
    words.forEach(word => {
        if (window.teamInfo.hasOwnProperty(word)) {
            article.content += `<span class="text-danger font-weight-bold info">${word}</span><span class="invisible infoBox">${window.teamInfo[word].substring(0, 100)} <span class="text-danger font-weight-bold info seeMoreButton">Ver Mais</span></span> `
        }
        else {
            article.content += `${word} `
        }
        
    });

    if (document.querySelector('ul')) {
        document.querySelector('ul').outerHTML = `
            <article class="d-flex justify-content-center flex-column">
                <a id="back"><svg xmlns="http://www.w3.org/2000/svg" height="16" width="14" viewBox="0 0 448 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2023 Fonticons, Inc.--><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/></svg></a>
                <div class="card w-75 m-auto expanded">
                    <div class="card-body">
                        <a class="card-title">${article.title.trim()}</a>
                        <p class="card-text py-2">${article.content.trim()}</p>
                    </div>
                </div>
                <div class="card w-75 m-auto expanded">
                    <h2>Related Articles</h2>
                    <div id="relatedArticles">
                    </div>
                </div>
            </article>
        `
    }
    else {
        document.querySelector('article').outerHTML = `
            <article class="d-flex justify-content-center flex-column">
                <a id="back"><svg xmlns="http://www.w3.org/2000/svg" height="16" width="14" viewBox="0 0 448 512"><!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2023 Fonticons, Inc.--><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/></svg></a>
                <div class="card w-75 m-auto expanded">
                    <div class="card-body">
                        <a class="card-title">${article.title.trim()}</a>
                        <p class="card-text py-2">${article.content.trim()}</p>
                    </div>
                </div>
                <div class="card w-75 m-auto expanded">
                    <h2>Related Articles</h2>
                    <div id="relatedArticles">
                    </div>
                </div>
            </article>
        `
    }

    loadSeeMore()

    let boxKeyWords = document.querySelectorAll('.infoBox')

    var timeoutID = -1;

    for (let i = 0; i < boxKeyWords.length; i++) {
       
        boxKeyWords[i].addEventListener('mouseover', function() {
            if (boxKeyWords[i].classList.contains("visible")) {
                clearTimeout(timeoutID)
            }
        
        })
        boxKeyWords[i].addEventListener('mouseleave', function() {
            if (boxKeyWords[i].classList.contains("visible")) {
                boxKeyWords[i].classList.replace("visible", "invisible")
                boxKeyWords[i].innerHTML = `${window.teamInfo[boxKeyWords[i].previousSibling.textContent].substring(0, 100)} <span class="text-danger font-weight-bold info seeMoreButton">Ver Mais</span></span>`
                loadSeeMore()
            }
          
        })
        
    }

    let keyWords = document.querySelectorAll('.info')

    for (let i = 0; i < keyWords.length; i++) {
        keyWords[i].addEventListener('mouseover', function() {
            const box = keyWords[i].nextSibling
            if (box) box.classList.replace("invisible", "visible")
        })

        keyWords[i].addEventListener('mouseleave', function() {
            const box = keyWords[i].nextSibling
            timeoutID = setTimeout(() => {
                if (box) box.classList.replace("visible", "invisible")
            }, "50");
        })
        
    }
    document.getElementById('back').addEventListener('click', renderCached)
}

function renderRelated(docs) {
    for (let i = 1; i < docs.length; i++) {
        const article = docs[i]

        const icon = article.origin == 'record' 
        ? 'record.ico'
        : article.origin == 'ojogo'
            ? 'ojogo.png'
            : 'abola.ico'

        const card = document.createElement('div')
        card.classList.add('card')
        document.querySelector('#relatedArticles').appendChild(card)
        card.innerHTML = `<div class="card-body">
        <a class="card-title">${article.title.trim()}<img class="origin" src="../static/${icon}"/></a>
    </div>`
        card.addEventListener('click', () => {
            openArticle(article)
        })
    }
    frontendStatistic()
}

function renderCached(){
    document.querySelector('article').outerHTML = localStorage.getItem('cachedResults')
    bindArticles()
    frontendStatistic()
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
            <div class="p-5 d-flex align-items-center align-items-center justify-content-center">
                <img src="../static/logo.png" width="90px" alt="News Logo">
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
    frontendStatistic()
}

async function performSearch(query_text, team, origin){
    const BACKEND_URL = 'http://localhost:5000/solr/'
    var query = ""
    if (team != "") query += `${team} `
    if (origin != "") query += `${origin}`
    query += `${query_text}`

    /*
    var query = {
        q: `${team ? `(title:${team}) AND ` : ''}${origin ? `(origin:${origin}) AND ` : ''}(content:${query})`,
        rows: 10,
        wt: "json"
    };
    */

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

function frontendStatistic() {
    const articles = document.querySelectorAll('a.card-title')

    for (let i = 0; i < articles.length; i++) {
        articles[i].addEventListener('mouseover', function() {console.log(relevantDocuments)})
        articles[i].addEventListener('mouseleave', function() {
            if (!divsSeen.includes(i)) {
                relevantDocuments.push(0)
                divsSeen.push(i)
            }
            
        })
        articles[i].addEventListener('click', function() {
            if (!divsSeen.includes(i)) {
                relevantDocuments.push(1)
                divsSeen.push(i)
            }  
        })
    }

}
