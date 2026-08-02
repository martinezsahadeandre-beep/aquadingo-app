"""
Lógica de dados do AquaDingo - independente de UI, reaproveitada tanto por
testes automatizados quanto pelo app Kivy (main.py).
"""
import json
import os
import random
from datetime import date, timedelta

APP_DIR = os.path.join(os.path.expanduser("~"), ".aquadingo")
DATA_FILE = os.path.join(APP_DIR, "data.json")

DEFAULT_DATA = {
    "nome": "Amigo(a) da Água",
    "meta_ml": 2000,
    "xp": 0,
    "streak": 0,
    "melhor_streak": 0,
    "ultimo_dia_ativo": None,
    "hoje_ml": 0,
    "historico": {},
    "conquistas": [],
    "lembretes_ativos": True,
    "intervalo_lembrete_min": 60,
}

CONQUISTAS = [
    {"id": "streak_3", "nome": "Gotinha Persistente", "desc": "3 dias seguidos batendo a meta", "check": lambda d: d["streak"] >= 3},
    {"id": "streak_7", "nome": "Semana Hidratada", "desc": "7 dias seguidos batendo a meta", "check": lambda d: d["streak"] >= 7},
    {"id": "streak_14", "nome": "Duas Semanas de Água", "desc": "14 dias seguidos batendo a meta", "check": lambda d: d["streak"] >= 14},
    {"id": "streak_30", "nome": "Mestre da Hidratação", "desc": "30 dias seguidos batendo a meta", "check": lambda d: d["streak"] >= 30},
    {"id": "total_10l", "nome": "Primeiros 10 Litros", "desc": "10 litros bebidos no total", "check": lambda d: total_bebido(d) >= 10000},
    {"id": "total_50l", "nome": "Meio Century", "desc": "50 litros bebidos no total", "check": lambda d: total_bebido(d) >= 50000},
    {"id": "total_100l", "nome": "Rio Pessoal", "desc": "100 litros bebidos no total", "check": lambda d: total_bebido(d) >= 100000},
    {"id": "nivel_5", "nome": "Hidratado Nível 5", "desc": "Alcance o nível 5", "check": lambda d: nivel_de(d["xp"]) >= 5},
    {"id": "nivel_10", "nome": "Lenda da Água", "desc": "Alcance o nível 10", "check": lambda d: nivel_de(d["xp"]) >= 10},
]

FRASES_MOTIVACIONAIS = [
    "Cada gole conta!",
    "Seu corpo agradece!",
    "Vamos, falta pouco pra meta!",
    "Beber água é um superpoder.",
    "Constância é tudo — nem que seja um golinho.",
    "A Gotinha acredita em você!",
    "Hidratação em dia, mente em dia.",
    "Você está mandando bem hoje!",
]

FRASES_META_BATIDA = [
    "META BATIDA! Você é incrível!",
    "Isso aí! Mais um dia hidratado!",
    "Perfeito! A Gotinha está orgulhosa de você!",
    "Você venceu o dia!",
]

FRASES_LEMBRETE = [
    "Que tal um golinho de água agora?",
    "Sua Gotinha sente sua falta... beba água!",
    "Pausa pra hidratar!",
    "Já bebeu água nessa última hora?",
]


def hoje_str():
    return date.today().isoformat()


def nivel_de(xp):
    nivel = 1
    xp_restante = xp
    custo = 300
    while xp_restante >= custo:
        xp_restante -= custo
        nivel += 1
        custo += 100
    return nivel


def xp_para_proximo_nivel(xp):
    nivel = 1
    xp_restante = xp
    custo = 300
    while xp_restante >= custo:
        xp_restante -= custo
        nivel += 1
        custo += 100
    return xp_restante, custo


def total_bebido(d):
    total = sum(d["historico"].values())
    total += d.get("hoje_ml", 0)
    return total


def carregar_dados():
    os.makedirs(APP_DIR, exist_ok=True)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for k, v in DEFAULT_DATA.items():
                if k not in dados:
                    dados[k] = v
        except (json.JSONDecodeError, OSError):
            dados = dict(DEFAULT_DATA)
    else:
        dados = dict(DEFAULT_DATA)
    return dados


def salvar_dados(d):
    os.makedirs(APP_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def processar_virada_de_dia(d):
    hoje = date.today()
    ultimo = d.get("ultimo_dia_ativo")

    if ultimo is None:
        d["ultimo_dia_ativo"] = hoje.isoformat()
        return d

    ultimo_data = date.fromisoformat(ultimo)
    if ultimo_data == hoje:
        return d

    d["historico"][ultimo] = d.get("hoje_ml", 0)

    dias_perdidos = (hoje - ultimo_data).days
    bateu_meta_ontem = d["historico"][ultimo] >= d["meta_ml"]

    if dias_perdidos == 1 and bateu_meta_ontem:
        d["streak"] += 1
    else:
        d["streak"] = 0

    d["melhor_streak"] = max(d["melhor_streak"], d["streak"])
    d["hoje_ml"] = 0
    d["ultimo_dia_ativo"] = hoje.isoformat()
    return d


def checar_novas_conquistas(d):
    """Retorna lista de conquistas recém desbloqueadas e já marca em d."""
    novas = []
    for c in CONQUISTAS:
        if c["id"] not in d["conquistas"] and c["check"](d):
            d["conquistas"].append(c["id"])
            novas.append(c)
    return novas


def adicionar_agua(d, ml):
    """Aplica a lógica de adicionar água, retorna (bateu_meta_agora: bool)."""
    if ml <= 0:
        return False
    estava_abaixo = d["hoje_ml"] < d["meta_ml"]
    d["hoje_ml"] += ml
    d["xp"] += max(1, ml // 10)
    bateu_meta_agora = estava_abaixo and d["hoje_ml"] >= d["meta_ml"]
    if bateu_meta_agora:
        d["xp"] += 50
    return bateu_meta_agora
