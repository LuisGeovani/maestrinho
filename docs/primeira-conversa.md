# Primeiros passos com o Maestro

Do zero até a equipe trabalhando. Vale para qualquer projeto e qualquer máquina com o Maestri.

## 1. Preparar (uma vez por máquina)

1. Instale a skill (README, "Instalação").
2. Rode o kit do Maestro e copie a linha do preset que ele imprime:
   ```
   python <maestrinho>/skills/maestro-equipe/maestro/instalar.py
   ```
3. Cadastre o preset "Maestro" com essa linha (num terminal com o modo Maestro ligado, ou peça a um Maestro que já exista).
4. Ponha o preset "Maestro" no **Quick Start**: Configurações → Terminal → Quick Start. O Quick Start tem limite de vagas; se estiver cheio, tire um preset antigo de lá (o preset continua existindo).

Os presets dos produtores (Haiku, Sonnet, Agy Hydrogen, Agy Neon, OpenCode Gratis...) não precisam ser criados à mão: o Maestro propõe e cria na primeira conversa, com o seu ok.

## 2. Abrir o Maestro

1. Abra o workspace do projeto no Maestri.
2. Na barra de cima do canvas, escolha a ferramenta **Terminal** (ícone `>_`) e arraste no canvas para desenhar o terminal.
3. Na janela **New Terminal**, clique em **Maestro**. Ele abre em Opus 5.5, effort medium, com o modo Maestro ligado e o kit ativo.

## 3. A primeira mensagem

Cole e troque só a última linha:

```
Você é o Maestro deste workspace. Carregue a skill maestro-equipe e faça o "Início de sessão" dela.

1. Rode o inventario.py e o cotas.py da skill e me mostre em poucas linhas o que temos: ferramentas, modelos, cotas e quem já está conectado.
2. Proponha a formação da equipe para este projeto. Se já existirem terminais e papéis feitos com a versão antiga da skill (nome "Maestro" fixo, presets com caminho de projeto, codinomes antigos), diga quais manter, quais trocar com --replace pelos presets por modelo de references/setup.md (crie os que não existirem) e quais papéis reescrever pelo references/papeis.md. Anote a formação em .maestri/equipe.md.
3. Me mostre a proposta numa tabela (terminal, ferramenta, modelo, effort, perfis) e espere meu ok antes de criar presets, recrutar, trocar ou reescrever qualquer coisa.

Regras deste projeto: commits só no meu nome, sem Co-Authored-By; push só quando eu autorizar.
Depois do setup, o primeiro objetivo é: <descreva aqui o que você quer fazer no projeto>.
```

## 4. O que esperar

| Momento | O Maestro deve | Sinal de problema |
|---|---|---|
| 1ª resposta | mostrar inventário, cotas e a tabela da equipe proposta, e parar | recrutar ou editar algo antes do seu ok |
| Depois do ok | configurar o Antigravity se faltar (com backup), criar presets e papéis, recrutar, anotar `.maestri/equipe.md` e fazer um teste rápido de comunicação | despachar para um terminal que ainda está abrindo, sem usar o `maestri_batch.py` |
| Cada pedido | quebrar em tarefas, escolher modelo e effort por tarefa, despachar em background, responder curto e esperar | ler código, rodar build ou editar arquivo ele mesmo (o kit bloqueia; se ele contornar, avise) |
| Dúvidas | decidir sozinho o que a skill já define (modelo, effort, config do Antigravity, confiança de pasta, permissões no escopo, ofertas de plugin) e só avisar | perguntar coisas assim; pergunta é só para push, ação irreversível, gasto de dinheiro, trabalho de outra pessoa e decisão de produto |
| Retorno | mandar revisar por outra família, decidir os apontamentos, conferir o escopo com `git diff --stat` e te dar uma tabela de quem fez o quê | dizer que algo foi testado sem relatório que prove |

## 5. No dia a dia

Fale o que você quer, do jeito que falaria com uma pessoa:

- "Implementa a tela de contato."
- "Corrige o bug do mapa que não abre o ponto pela pesquisa."
- "Quero opiniões diferentes sobre trocar o banco para Postgres."
- "Pesquisa como fazer X e me traz as opções."
- "Quanto de cota temos? Quem está parado?"

Ele não precisa que você escolha o modelo. Se quiser influenciar, diga a prioridade: "capricha, é crítico" (sobe o nível da tarefa) ou "faz no mais barato" (desce o modelo/effort).

## 6. Se algo der errado

| Sintoma | O que fazer |
|---|---|
| Comandos `recruit`/`preset` dizem "This terminal is not the Maestro" | ligue a opção Maestro nesse terminal no canvas e espere alguns segundos |
| O Maestro está fazendo o trabalho ele mesmo | confira se ele foi aberto pelo preset "Maestro" (o banner mostra Opus e o kit bloqueia ferramentas); se não, abra pelo preset |
| Um terminal não responde ou voltou para o shell | peça ao Maestro: "religue o <nome> com --replace" |
| Pergunta do Maestro sumiu ou foi respondida sozinha | o aviso de um terminal caiu em cima; peça para ele repetir a pergunta |
| Cota acabando | pergunte "como está a cota?": ele roda o `cotas.py` e redistribui |

Problemas técnicos conhecidos e correções: `skills/maestro-equipe/references/setup.md`.
