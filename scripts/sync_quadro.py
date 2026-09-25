#!/usr/bin/env python3
"""Mantém o quadro público em dia com os PRs da fila (data/fila.json).

Mesmo desenho do CoOps (LabTechUDF/CoOps): uma GitHub Action agendada lê a API
pública do GitHub com o GITHUB_TOKEN e grava o resultado no próprio repositório.
Aqui o resultado são issues deste repo, uma por PR da fila, com o rótulo de
status que o quadro (index.html) já sabe mostrar:

    PR aceito (merge)                         -> status:concluido    (issue fechada)
    PR aberto na org                          -> status:em-revisao   (link no cartão)
    PR aberto com mudança pedida na revisão   -> status:em-andamento (sendo corrigido)
    próximo do repo (anterior aberto/aceito)  -> status:em-andamento (pronto e testado; abre em seguida)
    demais PRs da fila                        -> status:a-fazer      (esperam o anterior)
    PR fechado sem merge                      -> status:a-fazer      (volta para a fila)

E um cartão por pendência de data/pendencias.json (decisões e dados que dependem
de pessoas) em status:ideia. Resolvida = alguém FECHA o cartão no quadro (vai para
Concluído e não reabre) ou ela sai da lista.

Só lê a org e só escreve issues/rótulos deste repositório. Sem nomes: o cartão
mostra id, título, issues que fecha e o resultado da suíte medido localmente.

    python scripts/sync_quadro.py --dry-run   # mostra o que faria (precisa só de leitura)
    python scripts/sync_quadro.py             # aplica (na Action)
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
ROOT = pathlib.Path(__file__).resolve().parents[1]
MARCA = "fila-pr"  # rótulo que identifica os cartões mantidos por este script
MARCA_PEND = "pendencia"
ROTULOS = {
    "status:ideia": "c5def5", "status:a-fazer": "fbca04", "status:em-andamento": "1d76db",
    "status:em-revisao": "5319e7", "status:concluido": "0e8a16", MARCA: "ededed", MARCA_PEND: "ededed",
}


def call(method, path, token, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read() or "null")


def pr_da_fila(org, repo, dono_fork, pid, token):
    prs = call("GET", f"/repos/{org}/{repo}/pulls?state=all&head={dono_fork}:pr/{pid}&per_page=10", token)
    return prs[0] if prs else None  # o mais recente primeiro


def mudanca_pedida(org, repo, pr, token):
    reviews = call("GET", f"/repos/{org}/{repo}/pulls/{pr['number']}/reviews?per_page=100", token)
    ultimo = {}
    for r in reviews:  # vale a última revisão de cada pessoa
        ultimo[r["user"]["login"]] = r["state"]
    return "CHANGES_REQUESTED" in ultimo.values()


def estado(pr, anterior_andou, mudanca=False):
    """anterior_andou: o PR anterior do mesmo repo já está aberto ou aceito (ou não há anterior)."""
    if pr and pr.get("merged_at"):
        return "status:concluido", f"aceito em {pr['merged_at'][:10]}"
    if pr and pr["state"] == "open":
        if mudanca:
            return "status:em-andamento", "aberto; a revisão pediu mudanças, sendo corrigido"
        return "status:em-revisao", "aberto, aguardando revisão"
    if anterior_andou:
        return "status:em-andamento", "pronto e testado; é o próximo a abrir neste repositório"
    nota = "fechado sem merge; volta para a fila" if pr else "espera o anterior do mesmo repositório"
    return "status:a-fazer", nota


def corpo(item, org, pr, situacao):
    linhas = [f"**Repositório:** {org}/{item['repo']}", f"**Situação:** {situacao}"]
    if pr:
        linhas.append(f"**PR:** {pr['html_url']}")
    if item["fecha"]:
        linhas.append("**Fecha:** " + ", ".join(f"{org}/{item['repo']}{n}" for n in item["fecha"]))
    if item["depende"]:
        linhas.append("**Depende de:** " + ", ".join(item["depende"]))
    linhas.append(f"**Suíte na ponta do PR (medida localmente):** {item['suite']}")
    linhas.append("\n_Cartão mantido pela Action `sync-quadro` a partir de `data/fila.json`. Não edite à mão._")
    return "\n\n".join(linhas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    este = os.environ.get("GITHUB_REPOSITORY")          # dono/estagio-publico
    dono_fork = os.environ.get("GITHUB_REPOSITORY_OWNER")  # quem abre os PRs pelo fork
    if not (este and dono_fork):
        sys.exit("defina GITHUB_REPOSITORY e GITHUB_REPOSITORY_OWNER (a Action já define)")
    dados = json.loads((ROOT / "data" / "fila.json").read_text())
    org = dados["org"]

    existentes = {r["name"] for r in call("GET", f"/repos/{este}/labels?per_page=100", token)}
    for nome, cor in ROTULOS.items():
        if nome not in existentes:
            print(f"rótulo novo: {nome}")
            if not args.dry_run:
                call("POST", f"/repos/{este}/labels", token, {"name": nome, "color": cor})

    cartoes = {}
    pagina = 1
    while True:
        lote = call("GET", f"/repos/{este}/issues?state=all&labels={MARCA}&per_page=100&page={pagina}", token)
        for i in lote:
            if i["title"].startswith("[") and "]" in i["title"]:
                cartoes[i["title"][1:i["title"].index("]")]] = i
        if len(lote) < 100:
            break
        pagina += 1

    ultimo_do_repo = {}  # repo -> PR (ou None) do item anterior da fila
    for item in dados["fila"]:
        pr = pr_da_fila(org, item["repo"], dono_fork, item["id"], token)
        anterior = ultimo_do_repo.get(item["repo"], "nenhum")
        anterior_andou = anterior == "nenhum" or (anterior is not None and (
            anterior.get("merged_at") or anterior["state"] == "open"))
        mudanca = bool(pr and pr["state"] == "open" and mudanca_pedida(org, item["repo"], pr, token))
        ultimo_do_repo[item["repo"]] = pr
        status, situacao = estado(pr, anterior_andou, mudanca)
        titulo = f"[{item['id']}] {item['titulo']}"
        desejado = {"title": titulo, "body": corpo(item, org, pr, situacao), "labels": [MARCA, status],
                    "state": "closed" if status == "status:concluido" else "open"}
        atual = cartoes.get(item["id"])
        if atual is None:
            print(f"{item['id']}: cria cartão ({status})")
            if not args.dry_run:
                novo = call("POST", f"/repos/{este}/issues", token,
                            {k: desejado[k] for k in ("title", "body", "labels")})
                if desejado["state"] == "closed":
                    call("PATCH", f"/repos/{este}/issues/{novo['number']}", token, {"state": "closed"})
            continue
        rotulos = sorted(r["name"] for r in atual["labels"])
        mudou = (atual["title"] != titulo or (atual["body"] or "") != desejado["body"]
                 or rotulos != sorted(desejado["labels"]) or atual["state"] != desejado["state"])
        print(f"{item['id']}: {'atualiza' if mudou else 'sem mudança'} ({status})")
        if mudou and not args.dry_run:
            call("PATCH", f"/repos/{este}/issues/{atual['number']}", token, desejado)

    sincroniza_pendencias(este, token, args.dry_run)


def fechada_por_pessoa(este, issue, token):
    """Fechada por alguém no quadro (não por esta Action)."""
    quem = (call("GET", f"/repos/{este}/issues/{issue['number']}", token).get("closed_by") or {})
    return quem.get("type") != "Bot" and not quem.get("login", "").endswith("[bot]")


def sincroniza_pendencias(este, token, dry_run):
    caminho = ROOT / "data" / "pendencias.json"
    if not caminho.exists():
        return
    pendencias = json.loads(caminho.read_text())["pendencias"]
    atuais = {}
    for i in call("GET", f"/repos/{este}/issues?state=all&labels={MARCA_PEND}&per_page=100", token):
        if i["title"].startswith("[") and "]" in i["title"]:
            atuais[i["title"][1:i["title"].index("]")]] = i
    for p in pendencias:
        titulo = f"[{p['id']}] {p['titulo']}"
        corpo_p = (f"{p['texto']}\n\n_Depende de decisão ou dado de pessoas; sai do quadro quando for resolvida. "
                   "Cartão mantido pela Action `sync-quadro` a partir de `data/pendencias.json`._")
        desejado = {"title": titulo, "body": corpo_p, "labels": [MARCA_PEND, "status:ideia"], "state": "open"}
        atual = atuais.pop(p["id"], None)
        if atual is not None and atual["state"] == "closed" and fechada_por_pessoa(este, atual, token):
            # Alguém fechou o cartão no quadro: a pendência foi resolvida. Não reabre.
            rotulos = sorted(r["name"] for r in atual["labels"])
            if rotulos != sorted([MARCA_PEND, "status:concluido"]):
                print(f"{p['id']}: resolvida no quadro, vai para Concluído")
                if not dry_run:
                    call("PATCH", f"/repos/{este}/issues/{atual['number']}", token,
                         {"labels": [MARCA_PEND, "status:concluido"]})
            else:
                print(f"{p['id']}: resolvida no quadro")
            continue
        if atual is None:
            print(f"{p['id']}: cria cartão de pendência")
            if not dry_run:
                call("POST", f"/repos/{este}/issues", token, {k: desejado[k] for k in ("title", "body", "labels")})
            continue
        mudou = (atual["title"] != titulo or (atual["body"] or "") != corpo_p or atual["state"] != "open"
                 or sorted(r["name"] for r in atual["labels"]) != sorted(desejado["labels"]))
        print(f"{p['id']}: {'atualiza' if mudou else 'sem mudança'} (pendência)")
        if mudou and not dry_run:
            call("PATCH", f"/repos/{este}/issues/{atual['number']}", token, desejado)
    for pid, atual in atuais.items():  # saiu da lista = resolvida
        if atual["state"] == "open":
            print(f"{pid}: pendência resolvida, fecha o cartão")
            if not dry_run:
                call("PATCH", f"/repos/{este}/issues/{atual['number']}", token,
                     {"state": "closed", "labels": [MARCA_PEND, "status:concluido"]})


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub respondeu {e.code} em {e.url}")
