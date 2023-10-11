def createStartExpressions(home, away):
    home_winning_start = [
        f"Num emocionante confronto, o {home} triunfa sobre o {away} na Liga Portugal.",
        f"O {home} domina o {away} e sai vitorioso na Liga Portugal.",
        f"Em casa, o {home} conquista uma vitória decisiva contra o {away} na Liga Portugal.",
        f"{away} sofre uma derrota nas mãos do {home} na Liga Portugal.",
        f"Vitória memorável para o {home} numa partida épica contra o {away} na Liga Portugal."

    ]
    away_winning_start = [
        f"O {away} surpreende o {home} com uma vitória dramática na Liga Portugal.",
        f"O {away} derrota o {home} em confronto emocionante na Liga Portugal.",
        f"Num jogo eletrizante, o {away} supera o {home} na Liga Portugal.",
        f"O {away} brilha e vence o {home} na Liga Portugal.",
        f"Vitória histórica para o {away} sobre o {home} na Liga Portugal."
    ]
    draw_start = [
        f"{home} e {away} ficam empatados num emocionante confronto na Liga Portugal.",
        f"Partida bem disputada entre {home} e {away} termina em empate na Liga Portugal.",
        f"O {home} empata com o {away} num jogo onde ambas equipas estiveram em alto nível.",
        f"Um empate eletrizante marca o duelo entre {home} e {away} na Liga Portugal.",
        f"{home} e {away} dividem os pontos após empate na Liga Portugal."
    ]
    return [home_winning_start, away_winning_start, draw_start]


def createExpressions(home, away, minute, name):
    goal_home_eve = [
        f"Aos {minute} minutos, {name} marca um golo para a equipa da casa.",
        f"{name} deixa a sua marca aos {minute} minutos com um incrível golo.",
        f"No minuto {minute}, {name} coloca o {home} em vantagem.",
        f"Um golo crucial é apontado por {name} aos {minute} minutos para a equipa da casa.",
        f"O golo de {name} aos {minute} minutos emociona os adeptos do {home}."
    ]

    goal_away_eve = [
        f"Aos {minute} minutos, {name} marca um golo para a equipa visitante.",
        f"{name} deixa a sua marca aos {minute} minutos com um incrível golo.",
        f"No minuto {minute}, {name} coloca o {away} em vantagem.",
        f"Um golo crucial é apontado por {name} aos {minute} minutos.",
        f"O golo de {name} aos {minute} minutos agita o jogo."
    ]

    own_goal_home_eve = [
        f"Aos {minute} minutos, {name} marca um auto-golo contra a sua própria equipa.",
        f"{name} surpreendentemente coloca a bola na sua própria baliza aos {minute} minutos.",
        f"No minuto {minute}, {name} comete um auto-golo, aumentando a vantagem do {away}.",
        f"{name} contribui para o placar ao fazer um auto-golo aos {minute} minutos para a equipa da casa.",
        f"Num momento desafortunado, {name} marca um auto-golo aos {minute} minutos, deixando os adeptos do {home} perplexos."
    ]

    own_goal_away_eve = [
        f"Aos {minute} minutos, {name} marca um auto-golo contra a sua própria equipa.",
        f"{name} surpreendentemente coloca a bola na sua própria baliza aos {minute} minutos.",
        f"No minuto {minute}, {name} comete um auto-golo, dando uma vantagem ao {home}.",
        f"{name} contribui para o placar ao fazer um auto-golo aos {minute} minutos para a equipa visitante.",
        f"Num momento desafortunado, {name} marca um auto-golo aos {minute} minutos, deixando os adeptos do {away} perplexos."
    ]

    yellow_card_eve = [
        f"{name} recebe um cartão amarelo aos {minute} minutos.",
        f"Aos {minute} minutos, o árbitro adverte {name} com um cartão amarelo.",
        f"No minuto {minute}, {name} recebe um cartão amarelo.",
        f"O árbitro exibe um cartão amarelo a {name} aos {minute} minutos.",
        f"{name} comete uma infração e recebe um cartão amarelo aos {minute} minutos."
    ]

    red_card_eve = [
        f"{name} é expulso com um cartão vermelho aos {minute} minutos.",
        f"Aos {minute} minutos, o árbitro mostra o cartão vermelho a {name}.",
        f"No minuto {minute}, {name} é expulso com um cartão vermelho.",
        f"O {name} vai tomar banho mais cedo, o juiz da partida levanta a cartolina vermelha ao minuto {minute}.",
        f"{name} comete uma falta grave e é expulso com um cartão vermelho aos {minute} minutos."
    ]

    penalty_missed_home_eve = [
        f"{name} desperdiça uma grande penalidade para a equipa da casa aos {minute} minutos.",
        f"Aos {minute} minutos, {name} falha uma grande oportunidade de golo para o {home}.",
        f"No minuto {minute}, {name} não consegue converter uma grande penalidade a favor do {home}.",
        f"{name} erra na marca de grande penalidade aos {minute} minutos, frustrando os adeptos do {home}.",
        f"Num momento crítico, {name} não consegue marcar numa grande penalidade aos {minute} minutos, prejudicando a sua equipa da casa."
    ]

    penalty_missed_away_eve = [
        f"{name} desperdiça uma grande penalidade para a equipa visitante aos {minute} minutos.",
        f"Aos {minute} minutos, {name} falha uma grande oportunidade de golo para o {away}.",
        f"No minuto {minute}, {name} não consegue converter uma grande penalidade a favor do {away}.",
        f"{name} erra na marca de grande penalidade aos {minute} minutos, frustrando os adeptos do {away}.",
        f"Num momento crítico, {name} não consegue marcar numa grande penalidade aos {minute} minutos, prejudicando a sua equipa visitante."
    ]
    return [goal_home_eve, goal_away_eve, own_goal_home_eve, own_goal_away_eve, yellow_card_eve,
            red_card_eve, penalty_missed_home_eve, penalty_missed_away_eve]
