#!/usr/bin/env python3
"""Mantém o quadro público em dia com os PRs da fila (data/fila.json).

Mesmo desenho do CoOps (LabTechUDF/CoOps): uma GitHub Action agendada lê a API
pública do GitHub com o GITHUB_TOKEN e grava o resultado no próprio repositório.
Aqui o resultado são issues deste repo, uma por PR da fila, com o rótulo de
status que o quadro (index.html) já sabe mostrar:

    sem PR aberto ainda        -> status:a-fazer
    PR aberto na org           -> status:em-revisao   (link no cartão)
    PR aceito (merge)          -> status:concluido    (issue fechada)
    PR fechado sem merge       -> status:a-fazer      (volta para a fila)

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
ROTULOS = {
    "status:ideia": "c5def5", "status:a-fazer": "fbca04", "status:em-andamento": "1d76db",
    "status:em-revisao": "5319e7", "status:concluido": "0e8a16", MARCA: "ededed",
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


def estado(pr):
    if pr is None:
        return "status:a-fazer", "ainda não aberto"
    if pr.get("merged_at"):
        return "status:concluido", f"aceito em {pr['merged_at'][:10]}"
    if pr["state"] == "open":
        return "status:em-revisao", "aberto, aguardando revisão"
    return "status:a-fazer", "fechado sem merge; volta para a fila"


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

    for item in dados["fila"]:
        pr = pr_da_fila(org, item["repo"], dono_fork, item["id"], token)
        status, situacao = estado(pr)
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


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub respondeu {e.code} em {e.url}")
