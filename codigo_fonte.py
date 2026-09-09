"""
codigo_fonte.py
================
Nucleo Cognitivo da Aurora Siger (NCAS) - Atividade Integradora

ARQUIVO PRINCIPAL DO SISTEMA. Basta executar:  python3 codigo_fonte.py

Este programa registra, organiza, consulta e interpreta informacoes
operacionais de uma colonia espacial ficticia chamada "Aurora Siger".
Ele usa:
  - um arquivo de texto (registros_colonia.txt) para logs sequenciais;
  - um arquivo JSON (dados_colonia.json) para dados estruturados
    (modulos, alertas, interacoes e prompts);
  - regras logicas booleanas (com simplificacao demonstrada);
  - prompts estruturados e uma simulacao local de assistente de IA
    generativa (sem chamada a nenhuma API externa);
  - uma demonstracao simples de otimizacao (erro quadratico medio,
    gradiente descendente e regularizacao).
"""

import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Caminhos dos arquivos utilizados pelo sistema
# ---------------------------------------------------------------------------
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
ARQ_DADOS = os.path.join(DIR_BASE, "dados_colonia.json")       # JSON estruturado
ARQ_REGISTROS = os.path.join(DIR_BASE, "registros_colonia.txt")  # Texto (logs)


# ---------------------------------------------------------------------------
# SECAO 1 - MANIPULACAO DE ARQUIVOS (texto e JSON)
# ---------------------------------------------------------------------------
def carregar_dados():
    """Le todo o arquivo dados_colonia.json e retorna um dicionario Python."""
    with open(ARQ_DADOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados):
    """Grava o dicionario Python de volta em dados_colonia.json."""
    with open(ARQ_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def gravar_registro_texto(categoria, texto):
    """
    Adiciona uma linha ao arquivo de texto registros_colonia.txt em modo
    append ('a'), marcando a categoria do registro (ex: MANUTENCAO,
    LOG_ACESSO, ALERTA) para manter o arquivo organizado.
    """
    carimbo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{categoria}] [{carimbo}] {texto}\n"
    with open(ARQ_REGISTROS, "a", encoding="utf-8") as arquivo:
        arquivo.write(linha)


def ler_registros_texto():
    """Le todas as linhas do arquivo de registros com readlines()."""
    with open(ARQ_REGISTROS, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
    return [linha.strip() for linha in linhas]


# ---------------------------------------------------------------------------
# SECAO 2 - MODULOS DA COLONIA
# ---------------------------------------------------------------------------
def listar_modulos():
    return carregar_dados()["modulos"]


def usuario_pode_consultar(autorizado, modulo_ativo):
    """Regra booleana simples: LIBERAR = AUTORIZADO AND MODULO_ATIVO."""
    return autorizado and modulo_ativo


def consultar_modulo(nome_modulo, usuario="Sistema"):
    """
    Consulta um modulo pelo nome, aplicando a regra logica:
    Liberar consulta apenas se o usuario estiver autorizado E o modulo
    estiver ativo (secao 1.4 do enunciado).
    """
    modulos = listar_modulos()
    modulo = next((m for m in modulos if m["nome"].lower() == nome_modulo.lower()), None)

    if modulo is None:
        gravar_registro_texto("LOG_ACESSO", f"Usuario: {usuario} | Acao: CONSULTA_MODULO_NAO_ENCONTRADO:{nome_modulo}")
        return None

    autorizado = bool(usuario)
    ativo = modulo["status"] == "ativo"

    if usuario_pode_consultar(autorizado, ativo):
        gravar_registro_texto("LOG_ACESSO", f"Usuario: {usuario} | Acao: CONSULTA_LIBERADA:{modulo['nome']}")
        return modulo

    gravar_registro_texto("LOG_ACESSO", f"Usuario: {usuario} | Acao: CONSULTA_NEGADA:{modulo['nome']}")
    return None


# ---------------------------------------------------------------------------
# SECAO 3 - CADASTRO DE MANUTENCAO (arquivo texto)
# ---------------------------------------------------------------------------
def registrar_manutencao(modulo_id, modulo_nome, descricao):
    """Cadastra um novo registro de manutencao no arquivo de texto."""
    texto = f"{modulo_id} ({modulo_nome}): {descricao}"
    gravar_registro_texto("MANUTENCAO", texto)


def listar_manutencoes():
    """Retorna apenas as linhas de manutencao do arquivo de registros."""
    return [linha for linha in ler_registros_texto() if linha.startswith("[MANUTENCAO]")]


# ---------------------------------------------------------------------------
# SECAO 4 - ALERTAS OPERACIONAIS (JSON)
# ---------------------------------------------------------------------------
def gerar_id_alerta(alertas):
    return f"ALT-{len(alertas) + 1:03d}"


def registrar_alerta(modulo, tipo_ocorrencia, prioridade, critico, mensagem):
    """Cadastra um novo alerta, gravando em dados_colonia.json."""
    dados = carregar_dados()
    novo_alerta = {
        "id": gerar_id_alerta(dados["alertas"]),
        "modulo": modulo,
        "tipo_ocorrencia": tipo_ocorrencia,
        "prioridade": prioridade,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "critico": critico,
        "mensagem": mensagem,
    }
    dados["alertas"].append(novo_alerta)
    salvar_dados(dados)
    gravar_registro_texto("ALERTA", f"Novo alerta {novo_alerta['id']} - {modulo} - {tipo_ocorrencia}")
    return novo_alerta


def listar_alertas():
    return carregar_dados()["alertas"]


def buscar_alerta_por_id(alerta_id):
    return next((a for a in listar_alertas() if a["id"] == alerta_id), None)


# ---------------------------------------------------------------------------
# SECAO 5 - REGRAS LOGICAS E SIMPLIFICACAO BOOLEANA
# ---------------------------------------------------------------------------
def gerar_alerta_regra_original(falha, critico):
    """
    Regra original (exemplo do enunciado):
    ALERTA = (FALHA AND CRITICO) OR (FALHA AND NOT CRITICO)
    """
    return (falha and critico) or (falha and not critico)


def gerar_alerta_regra_simplificada(falha):
    """Regra simplificada por Teorema de Simplificacao (absorcao): ALERTA = FALHA."""
    return falha


def permitir_operacao_regra_original(falha_seguranca, inconsistencia_dados):
    """
    Regra original:
    BLOQUEAR = FALHA_SEGURANCA OR INCONSISTENCIA_DADOS
    PERMITIR_OPERACAO = NOT (FALHA_SEGURANCA OR INCONSISTENCIA_DADOS)
    """
    bloquear = falha_seguranca or inconsistencia_dados
    return not bloquear


def permitir_operacao_regra_simplificada(falha_seguranca, inconsistencia_dados):
    """
    Regra simplificada por Teorema de De Morgan:
    NOT (A OR B) = (NOT A) AND (NOT B)
    """
    return (not falha_seguranca) and (not inconsistencia_dados)


def requer_atencao_imediata_original(critico, prioridade_alta):
    """
    Regra usada na funcionalidade "Analisar alerta operacional":
    REQUER_ATENCAO = (CRITICO AND PRIORIDADE_ALTA) OR (CRITICO AND NOT PRIORIDADE_ALTA)
    """
    return (critico and prioridade_alta) or (critico and not prioridade_alta)


def requer_atencao_imediata_simplificada(critico):
    """Regra simplificada por Teorema de Simplificacao: REQUER_ATENCAO = CRITICO."""
    return critico


def demonstrar_equivalencia_logica():
    """
    Testa (tabela-verdade completa) todas as combinacoes de entrada e
    confirma que a regra original e a regra simplificada por De Morgan
    produzem sempre o mesmo resultado.
    """
    resultados = []
    for falha_seguranca in (True, False):
        for inconsistencia in (True, False):
            original = permitir_operacao_regra_original(falha_seguranca, inconsistencia)
            simplificada = permitir_operacao_regra_simplificada(falha_seguranca, inconsistencia)
            resultados.append({
                "falha_seguranca": falha_seguranca,
                "inconsistencia_dados": inconsistencia,
                "original": original,
                "simplificada": simplificada,
                "equivalentes": original == simplificada,
            })
    return resultados


# ---------------------------------------------------------------------------
# SECAO 6 - ENGENHARIA DE PROMPTS E SIMULACAO DE ASSISTENTE
# (nenhuma chamada real de API e feita; tudo e simulado localmente)
# ---------------------------------------------------------------------------
def carregar_prompt(prompt_id=None, tecnica=None):
    prompts = carregar_dados()["prompts"]
    if prompt_id:
        return next((p for p in prompts if p["id"] == prompt_id), None)
    return next((p for p in prompts if p["tecnica"] == tecnica), None)


def registrar_interacao(usuario, pergunta, resposta, tipo_prompt):
    dados = carregar_dados()
    numero = len(dados["interacoes"]) + 1
    nova = {
        "id": f"INT-{numero:03d}",
        "usuario": usuario,
        "pergunta": pergunta,
        "resposta": resposta,
        "tipo_prompt": tipo_prompt,
        "data": datetime.now().strftime("%Y-%m-%d"),
    }
    dados["interacoes"].append(nova)
    salvar_dados(dados)
    gravar_registro_texto("LOG_ACESSO", f"Usuario: {usuario} | Acao: INTERACAO_ASSISTENTE:{tipo_prompt}")
    return nova


def simular_resumo_alerta_zero_shot(alerta):
    """Simulacao local do prompt zero-shot de resumo de alerta."""
    prompt_usado = carregar_prompt(tecnica="zero-shot")["template"].format(alerta=alerta["mensagem"])
    risco = "ALTO" if alerta["critico"] else "MODERADO"
    resposta = (
        f"O modulo {alerta['modulo']} apresenta ocorrencia de '{alerta['tipo_ocorrencia']}' "
        f"com risco {risco}. Recomenda-se verificacao pela equipe tecnica."
    )
    return prompt_usado, resposta


def contar_palavras_urgentes(texto, palavras_urgentes=None):
    if palavras_urgentes is None:
        palavras_urgentes = ["falha critica", "perdemos contato", "vazamento", "incendio", "emergencia"]
    texto = texto.lower()
    return sum(1 for palavra in palavras_urgentes if palavra in texto)


def simular_classificacao_solicitacao_few_shot(solicitacao):
    """Simulacao local do prompt few-shot de classificacao de solicitacao."""
    prompt_usado = carregar_prompt(tecnica="few-shot")["template"].format(solicitacao=solicitacao)
    classificacao = "URGENTE" if contar_palavras_urgentes(solicitacao) > 0 else "NORMAL"
    return prompt_usado, classificacao


def simular_saida_estruturada(registro_tecnico, modulo, prioridade):
    """Simulacao de 'structured output': resposta devolvida como dicionario (JSON)."""
    prompt_usado = carregar_prompt(tecnica="structured-output")["template"].format(registro=registro_tecnico)
    saida = {
        "modulo": modulo,
        "status": "requer_atencao",
        "prioridade": prioridade,
        "resumo": registro_tecnico[:80],
    }
    return prompt_usado, saida


def simular_resposta_padronizada_centro_controle(alerta):
    """Simulacao do prompt PROMPT-CTRL-01, usado na funcionalidade 'Analisar alerta operacional'."""
    prompt_usado = carregar_prompt(prompt_id="PROMPT-CTRL-01")["template"].format(alerta=alerta["mensagem"])
    nivel = "CRITICO" if alerta["critico"] else "NAO CRITICO"
    acao = "Escalonar para equipe tecnica imediatamente" if alerta["critico"] else "Monitorar e reavaliar em 24h"
    resposta = f"{alerta['modulo']} / {nivel} / {acao}"
    return prompt_usado, resposta


def analisar_alerta_operacional(alerta_id, usuario="Sistema"):
    """
    Funcionalidade de exemplo dada no enunciado (secao 2):
    1) Carrega um alerta salvo em JSON;
    2) Verifica se ele e critico utilizando uma regra booleana simplificada;
    3) Exibe um prompt estruturado para gerar uma resposta padronizada ao
       centro de controle.
    """
    alerta = buscar_alerta_por_id(alerta_id)
    if alerta is None:
        return None

    prioridade_alta = alerta["prioridade"] == "alta"
    original = requer_atencao_imediata_original(alerta["critico"], prioridade_alta)
    simplificada = requer_atencao_imediata_simplificada(alerta["critico"])
    assert original == simplificada, "As regras deveriam ser equivalentes"

    prompt_usado, resposta_padronizada = simular_resposta_padronizada_centro_controle(alerta)
    registrar_interacao(usuario, prompt_usado, resposta_padronizada, "structured-output")

    return {
        "alerta": alerta,
        "requer_atencao_imediata": simplificada,
        "prompt_usado": prompt_usado,
        "resposta_padronizada": resposta_padronizada,
    }


# ---------------------------------------------------------------------------
# SECAO 7 - ANALISE SIMPLES DE OTIMIZACAO (MSE, GRADIENTE DESCENDENTE, REGULARIZACAO)
# ---------------------------------------------------------------------------
def treinar_peso_urgencia(dados_treino, taxa_aprendizado=0.05, epocas=20, lambda_reg=0.01):
    """
    Demonstracao didatica dos conceitos de Erro Quadratico Medio (MSE),
    Gradiente Descendente e Regularizacao L2. Otimiza um unico peso 'w'
    que converte a contagem de palavras-chave urgentes em uma
    aproximacao (0 a 1) da probabilidade de a solicitacao ser urgente.

    dados_treino: lista de tuplas (x, y) onde x = numero de palavras-chave
    encontradas e y = rotulo real (1.0 = urgente, 0.0 = normal).
    """
    peso = 0.0
    historico_erro = []

    for _ in range(epocas):
        erro_quadratico_total = 0.0
        gradiente_total = 0.0

        for x, y in dados_treino:
            y_previsto = peso * x
            erro = y_previsto - y
            erro_quadratico_total += erro ** 2
            gradiente_total += 2 * erro * x

        n = len(dados_treino)
        erro_quadratico_medio = erro_quadratico_total / n
        # Regularizacao L2: penaliza pesos muito grandes, evitando overfitting
        gradiente_medio = (gradiente_total / n) + (2 * lambda_reg * peso)

        peso -= taxa_aprendizado * gradiente_medio
        historico_erro.append(round(erro_quadratico_medio, 4))

    return peso, historico_erro


def demonstrar_otimizacao_classificador():
    """
    Usa alguns exemplos rotulados manualmente para treinar o peso do
    classificador de urgencia e mostrar o MSE caindo a cada epoca, isto
    e, o modelo "aprendendo" por gradiente descendente.
    """
    exemplos_rotulados = [
        ("O modulo de suporte de vida esta com falha critica.", 1.0),
        ("Gostaria de solicitar mais horas de treino na academia.", 0.0),
        ("Perdemos contato com a base ha 3 horas.", 1.0),
        ("Poderiam revisar o cardapio do refeitorio?", 0.0),
        ("Ha um vazamento no modulo de purificacao de agua.", 1.0),
    ]
    dados_treino = [(contar_palavras_urgentes(texto), rotulo) for texto, rotulo in exemplos_rotulados]
    peso_final, historico_erro = treinar_peso_urgencia(dados_treino)
    return peso_final, historico_erro


# ---------------------------------------------------------------------------
# INTERFACE DE LINHA DE COMANDO (MENU)
# ---------------------------------------------------------------------------
def exibir_menu():
    print("\n=== NUCLEO COGNITIVO DA AURORA SIGER (NCAS) ===")
    print(" 1. Listar modulos da colonia")
    print(" 2. Consultar um modulo especifico")
    print(" 3. Cadastrar registro de manutencao")
    print(" 4. Listar registros de manutencao")
    print(" 5. Cadastrar alerta operacional")
    print(" 6. Listar alertas")
    print(" 7. Analisar alerta operacional (regra + prompt padronizado)")
    print(" 8. Demonstrar regra logica (De Morgan) sobre bloqueio de operacao")
    print(" 9. Simular assistente: resumir um alerta (zero-shot)")
    print("10. Simular assistente: classificar solicitacao (few-shot)")
    print("11. Simular assistente: gerar saida estruturada (JSON)")
    print("12. Demonstrar otimizacao simples (MSE + gradiente descendente)")
    print(" 0. Sair")


def executar():
    print("Bem-vindo(a) ao Nucleo Cognitivo da Aurora Siger.")
    usuario = input("Identifique-se (nome do usuario): ").strip() or "Tripulante"

    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            for modulo in listar_modulos():
                print(f"- {modulo['id']} | {modulo['nome']} | status: {modulo['status']}")

        elif opcao == "2":
            nome = input("Nome do modulo: ").strip()
            modulo = consultar_modulo(nome, usuario)
            print(modulo if modulo else "Consulta negada ou modulo nao encontrado.")

        elif opcao == "3":
            modulo_id = input("ID do modulo: ").strip()
            modulo_nome = input("Nome do modulo: ").strip()
            descricao = input("Descricao da manutencao: ").strip()
            registrar_manutencao(modulo_id, modulo_nome, descricao)
            print("Registro de manutencao salvo com sucesso.")

        elif opcao == "4":
            for linha in listar_manutencoes():
                print(linha)

        elif opcao == "5":
            modulo = input("Modulo afetado: ").strip()
            tipo = input("Tipo de ocorrencia: ").strip()
            prioridade = input("Prioridade (baixa/media/alta): ").strip()
            critico = input("E critico? (s/n): ").strip().lower() == "s"
            mensagem = input("Mensagem resumida: ").strip()
            alerta = registrar_alerta(modulo, tipo, prioridade, critico, mensagem)
            print(f"Alerta {alerta['id']} registrado com sucesso.")

        elif opcao == "6":
            for alerta in listar_alertas():
                print(f"- {alerta['id']} | {alerta['modulo']} | {alerta['tipo_ocorrencia']} | prioridade: {alerta['prioridade']}")

        elif opcao == "7":
            alerta_id = input("ID do alerta a analisar (ex: ALT-001): ").strip()
            resultado = analisar_alerta_operacional(alerta_id, usuario)
            if resultado is None:
                print("Alerta nao encontrado.")
            else:
                print(f"\nAlerta: {resultado['alerta']}")
                print(f"Requer atencao imediata (regra simplificada CRITICO): {resultado['requer_atencao_imediata']}")
                print(f"\nPrompt estruturado utilizado:\n{resultado['prompt_usado']}")
                print(f"\nResposta padronizada ao centro de controle:\n{resultado['resposta_padronizada']}")

        elif opcao == "8":
            print("\nRegra original: PERMITIR = NOT (FALHA_SEGURANCA OR INCONSISTENCIA_DADOS)")
            print("Regra simplificada (De Morgan): PERMITIR = (NOT FALHA_SEGURANCA) AND (NOT INCONSISTENCIA_DADOS)\n")
            for linha in demonstrar_equivalencia_logica():
                print(linha)

        elif opcao == "9":
            alertas = listar_alertas()
            if not alertas:
                print("Nenhum alerta cadastrado.")
            else:
                alerta = alertas[-1]
                prompt_usado, resposta = simular_resumo_alerta_zero_shot(alerta)
                registrar_interacao(usuario, prompt_usado, resposta, "zero-shot")
                print(f"\nPrompt utilizado:\n{prompt_usado}")
                print(f"\nResposta simulada:\n{resposta}")

        elif opcao == "10":
            solicitacao = input("Descreva a solicitacao da tripulacao: ").strip()
            prompt_usado, classificacao = simular_classificacao_solicitacao_few_shot(solicitacao)
            registrar_interacao(usuario, prompt_usado, classificacao, "few-shot")
            print(f"\nPrompt utilizado:\n{prompt_usado}")
            print(f"\nClassificacao simulada: {classificacao}")

        elif opcao == "11":
            registro = input("Descreva o registro tecnico: ").strip()
            modulo = input("Modulo relacionado: ").strip()
            prioridade = input("Prioridade (baixa/media/alta): ").strip()
            prompt_usado, saida = simular_saida_estruturada(registro, modulo, prioridade)
            registrar_interacao(usuario, prompt_usado, json.dumps(saida, ensure_ascii=False), "structured-output")
            print(f"\nPrompt utilizado:\n{prompt_usado}")
            print(f"\nSaida estruturada (JSON):\n{json.dumps(saida, ensure_ascii=False, indent=2)}")

        elif opcao == "12":
            peso_final, historico_erro = demonstrar_otimizacao_classificador()
            print("\nErro Quadratico Medio (MSE) por epoca de treinamento:")
            for epoca, erro in enumerate(historico_erro, start=1):
                print(f"  Epoca {epoca:02d}: MSE = {erro}")
            print(f"\nPeso final aprendido pelo gradiente descendente: {round(peso_final, 4)}")

        elif opcao == "0":
            print("Encerrando o Nucleo Cognitivo da Aurora Siger. Ate a proxima.")
            break

        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    executar()
