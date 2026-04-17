"""
============================================================
PROBLEMA DE PO MISTA (MIP) - CASO NESTLÉ / KITKAT
============================================================
Contexto:
    Após o roubo de 12 toneladas de KitKat durante o transporte
    Itália → Polônia (abr/2026), a Nestlé precisou lançar uma
    plataforma de rastreio de lotes. O problema modelado aqui
    aborda a SELEÇÃO ÓTIMA DE PONTOS DE INSPEÇÃO E RASTREIO ao
    longo da cadeia de suprimentos, minimizando custo total
    enquanto garante cobertura mínima de segurança.

Sub-área de PO: Programação Inteira Mista (MIP)
    - Variáveis binárias: instalação/ativação de checkpoints
    - Variáveis contínuas: fluxo de produtos por rota
    - Restrições com pré-requisitos (dependência entre decisões)

Variáveis de Decisão (binárias):
    x1 = Instalar checkpoint em Milão (saída de fábrica)
    x2 = Instalar checkpoint em Bolonha (rota A)
    x3 = Instalar checkpoint em Trieste (rota B - costa)
    x4 = Instalar checkpoint em Ljubljana (fronteira ITA-SLO)
    x5 = Instalar checkpoint em Zagreb (Croácia)
    x6 = Instalar checkpoint em Viena (Áustria)
    x7 = Instalar checkpoint em Bratislava (Eslováquia)
    x8 = Instalar checkpoint em Varsóvia (destino)
    x9 = Ativar monitoramento GPS em tempo real no caminhão
    x10= Ativar integração com plataforma de rastreio por QR/lote

Restrições com pré-requisitos:
    R1: x8 (Varsóvia) só pode ser ativado se x1 (Milão) existir
    R2: x4 (Ljubljana) requer x1 (Milão) OU x3 (Trieste)
    R3: x7 (Bratislava) requer x6 (Viena)
    R4: x10 (plataforma) requer x9 (GPS)
    R5: Rota A (x2) e Rota B (x3) não podem ser ambas ativas simultaneamente
    R6: Cobertura mínima: ao menos 4 dos 8 checkpoints físicos devem ser instalados
    R7: Orçamento máximo de instalação: R$ 850.000
    R8: Se plataforma (x10) for ativa, ao menos 3 checkpoints físicos devem registrar dados
============================================================
"""

from pyomo.environ import (
    ConcreteModel, Var, Binary, NonNegativeReals,
    Objective, Constraint, SolverFactory, value, minimize
)

# ----------------------------------------------------------------
# 1. PARÂMETROS DO MODELO
# ----------------------------------------------------------------

# Custo de instalação/ativação de cada checkpoint (R$ mil)
custo = {
    'x1': 80,   # Milão
    'x2': 60,   # Bolonha
    'x3': 55,   # Trieste
    'x4': 70,   # Ljubljana
    'x5': 65,   # Zagreb
    'x6': 90,   # Viena
    'x7': 75,   # Bratislava
    'x8': 85,   # Varsóvia
    'x9': 50,   # GPS tempo real
    'x10': 40,  # Plataforma digital de rastreio
}

# Benefício de segurança de cada checkpoint (escala 0-100)
beneficio = {
    'x1': 90,
    'x2': 60,
    'x3': 65,
    'x4': 80,
    'x5': 55,
    'x6': 70,
    'x7': 75,
    'x8': 85,
    'x9': 95,
    'x10': 88,
}

orcamento_maximo = 850  # R$ mil

# ----------------------------------------------------------------
# 2. MODELO
# ----------------------------------------------------------------
model = ConcreteModel(name="KitKat_Supply_Chain_MIP")

# ----------------------------------------------------------------
# 3. VARIÁVEIS DE DECISÃO BINÁRIAS
# ----------------------------------------------------------------
model.x1  = Var(within=Binary, doc="Checkpoint Milão (saída fábrica)")
model.x2  = Var(within=Binary, doc="Checkpoint Bolonha (rota A)")
model.x3  = Var(within=Binary, doc="Checkpoint Trieste (rota B costeira)")
model.x4  = Var(within=Binary, doc="Checkpoint Ljubljana (fronteira ITA-SLO)")
model.x5  = Var(within=Binary, doc="Checkpoint Zagreb (Croácia)")
model.x6  = Var(within=Binary, doc="Checkpoint Viena (Áustria)")
model.x7  = Var(within=Binary, doc="Checkpoint Bratislava (Eslováquia)")
model.x8  = Var(within=Binary, doc="Checkpoint Varsóvia (destino final)")
model.x9  = Var(within=Binary, doc="GPS tempo real no caminhão")
model.x10 = Var(within=Binary, doc="Plataforma digital de rastreio por lote")

# ----------------------------------------------------------------
# 4. FUNÇÃO OBJETIVO
#    Maximizar o benefício total de segurança obtido
#    (equivale a minimizar o negativo do benefício)
# ----------------------------------------------------------------
def obj_rule(m):
    return -(
        beneficio['x1']  * m.x1  +
        beneficio['x2']  * m.x2  +
        beneficio['x3']  * m.x3  +
        beneficio['x4']  * m.x4  +
        beneficio['x5']  * m.x5  +
        beneficio['x6']  * m.x6  +
        beneficio['x7']  * m.x7  +
        beneficio['x8']  * m.x8  +
        beneficio['x9']  * m.x9  +
        beneficio['x10'] * m.x10
    )

model.obj = Objective(rule=obj_rule, sense=minimize)

# ----------------------------------------------------------------
# 5. RESTRIÇÕES
# ----------------------------------------------------------------

# R1 - PRÉ-REQUISITO: Varsóvia (x8) requer Milão (x1)
#      x8 <= x1  →  x8 - x1 <= 0
def r1_prerequisito_varsovia(m):
    return m.x8 <= m.x1

model.R1 = Constraint(rule=r1_prerequisito_varsovia,
    doc="PRE-REQ: Checkpoint Varsovia requer Milao ativo")

# R2 - PRÉ-REQUISITO: Ljubljana (x4) requer Milão (x1) OU Trieste (x3)
#      x4 <= x1 + x3
def r2_prerequisito_ljubljana(m):
    return m.x4 <= m.x1 + m.x3

model.R2 = Constraint(rule=r2_prerequisito_ljubljana,
    doc="PRE-REQ: Ljubljana requer Milao ou Trieste")

# R3 - PRÉ-REQUISITO: Bratislava (x7) requer Viena (x6)
#      x7 <= x6
def r3_prerequisito_bratislava(m):
    return m.x7 <= m.x6

model.R3 = Constraint(rule=r3_prerequisito_bratislava,
    doc="PRE-REQ: Bratislava requer Viena")

# R4 - PRÉ-REQUISITO: Plataforma digital (x10) requer GPS (x9)
#      x10 <= x9
def r4_prerequisito_plataforma(m):
    return m.x10 <= m.x9

model.R4 = Constraint(rule=r4_prerequisito_plataforma,
    doc="PRE-REQ: Plataforma digital requer GPS ativo")

# R5 - EXCLUSÃO MÚTUA: Rota A (x2) e Rota B (x3) não simultâneas
#      x2 + x3 <= 1
def r5_rotas_exclusivas(m):
    return m.x2 + m.x3 <= 1

model.R5 = Constraint(rule=r5_rotas_exclusivas,
    doc="Rota A (Bolonha) e Rota B (Trieste) sao mutuamente exclusivas")

# R6 - COBERTURA MÍNIMA: ao menos 4 checkpoints físicos (x1..x8)
#      x1+x2+x3+x4+x5+x6+x7+x8 >= 4
def r6_cobertura_minima(m):
    return m.x1 + m.x2 + m.x3 + m.x4 + m.x5 + m.x6 + m.x7 + m.x8 >= 4

model.R6 = Constraint(rule=r6_cobertura_minima,
    doc="Minimo de 4 checkpoints fisicos instalados")

# R7 - ORÇAMENTO: custo total <= R$ 850 mil
def r7_orcamento(m):
    return (
        custo['x1']  * m.x1  +
        custo['x2']  * m.x2  +
        custo['x3']  * m.x3  +
        custo['x4']  * m.x4  +
        custo['x5']  * m.x5  +
        custo['x6']  * m.x6  +
        custo['x7']  * m.x7  +
        custo['x8']  * m.x8  +
        custo['x9']  * m.x9  +
        custo['x10'] * m.x10
    ) <= orcamento_maximo

model.R7 = Constraint(rule=r7_orcamento,
    doc="Orcamento maximo de R$ 850 mil")

# R8 - COBERTURA TECNOLÓGICA: se plataforma ativa (x10=1),
#      ao menos 3 checkpoints físicos devem estar ativos
#      x1+x2+x3+x4+x5+x6+x7+x8 >= 3*x10
def r8_plataforma_cobertura(m):
    return m.x1 + m.x2 + m.x3 + m.x4 + m.x5 + m.x6 + m.x7 + m.x8 >= 3 * m.x10

model.R8 = Constraint(rule=r8_plataforma_cobertura,
    doc="Se plataforma digital ativa, ao menos 3 checkpoints fisicos")

# ----------------------------------------------------------------
# 6. RESOLUÇÃO
# ----------------------------------------------------------------
solver = SolverFactory('glpk')

print("=" * 60)
print("RESOLVENDO MODELO MIP - NESTLÉ / KITKAT SUPPLY CHAIN")
print("=" * 60)

results = solver.solve(model, tee=False)

# ----------------------------------------------------------------
# 7. APRESENTAÇÃO DOS RESULTADOS
# ----------------------------------------------------------------
print(f"\nStatus do Solver  : {results.solver.status}")
print(f"Condição termino  : {results.solver.termination_condition}")

checkpoints = {
    'x1':  ('Milão (saída fábrica)',        'x1'),
    'x2':  ('Bolonha (rota A)',             'x2'),
    'x3':  ('Trieste (rota B costeira)',    'x3'),
    'x4':  ('Ljubljana (fronteira ITA-SLO)','x4'),
    'x5':  ('Zagreb (Croácia)',             'x5'),
    'x6':  ('Viena (Áustria)',              'x6'),
    'x7':  ('Bratislava (Eslováquia)',      'x7'),
    'x8':  ('Varsóvia (destino final)',     'x8'),
    'x9':  ('GPS tempo real',              'x9'),
    'x10': ('Plataforma digital de rastreio','x10'),
}

variaveis = {
    'x1': model.x1, 'x2': model.x2, 'x3': model.x3,
    'x4': model.x4, 'x5': model.x5, 'x6': model.x6,
    'x7': model.x7, 'x8': model.x8, 'x9': model.x9,
    'x10': model.x10,
}

print("\n" + "-" * 60)
print(f"{'Variável':<6} {'Checkpoint/Ação':<35} {'Ativo?':<8} {'Custo (R$mil)':<15} {'Benefício'}")
print("-" * 60)

custo_total = 0
beneficio_total = 0

for key, (nome, var_key) in checkpoints.items():
    val = int(round(value(variaveis[key])))
    ativo = "✓ SIM" if val == 1 else "✗ NÃO"
    c = custo[key] * val
    b = beneficio[key] * val
    custo_total += c
    beneficio_total += b
    print(f"{key:<6} {nome:<35} {ativo:<8} {c:<15} {b}")

print("-" * 60)
print(f"{'TOTAL':<6} {'':<35} {'':<8} {custo_total:<15} {beneficio_total}")
print(f"\nBenefício máximo de segurança obtido : {beneficio_total} pts")
print(f"Custo total de implementação         : R$ {custo_total}.000")
print(f"Orçamento disponível                 : R$ {orcamento_maximo}.000")
print(f"Orçamento restante                   : R$ {orcamento_maximo - custo_total}.000")

# Verificar restrições de pré-requisito
print("\n--- Verificação das Restrições de Pré-Requisito ---")
x = {k: int(round(value(v))) for k, v in variaveis.items()}

checks = [
    ("R1 - Varsóvia requer Milão",        x['x8'] <= x['x1']),
    ("R2 - Ljubljana requer Milão ou Trieste", x['x4'] <= x['x1'] + x['x3']),
    ("R3 - Bratislava requer Viena",      x['x7'] <= x['x6']),
    ("R4 - Plataforma requer GPS",        x['x10'] <= x['x9']),
    ("R5 - Rotas A e B exclusivas",       x['x2'] + x['x3'] <= 1),
    ("R6 - ≥4 checkpoints físicos",       sum(x[f'x{i}'] for i in range(1,9)) >= 4),
    ("R7 - Orçamento ≤ 850",             custo_total <= orcamento_maximo),
    ("R8 - Plataforma exige ≥3 físicos",  sum(x[f'x{i}'] for i in range(1,9)) >= 3*x['x10']),
]

for desc, ok in checks:
    status = "✓ OK" if ok else "✗ VIOLADA"
    print(f"  {status} | {desc}")

print("\n" + "=" * 60)
print("FIM DA EXECUÇÃO")
print("=" * 60)
