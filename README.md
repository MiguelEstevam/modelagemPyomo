# 🍫 KitKat Supply Chain — Otimização por Programação Inteira Mista (MIP)

> Modelo de seleção ótima de pontos de inspeção na cadeia de suprimentos da Nestlé, motivado pelo roubo de 12 toneladas de KitKat durante transporte Itália → Polônia (abr/2026).

---

## 📌 Contexto do Problema

Após o incidente de segurança que resultou no roubo de KitKat em trânsito, a Nestlé precisou estruturar uma **plataforma de rastreio de lotes** ao longo da rota europeia. Este modelo de Pesquisa Operacional determina **quais checkpoints instalar e quais tecnologias ativar**, maximizando o benefício de segurança dentro de um orçamento limitado.

---

## 🧠 Sub-área de PO: Programação Inteira Mista (MIP)

O modelo combina:

- **Variáveis binárias** — decisões de instalar/ativar checkpoints físicos e tecnológicos
- **Restrições de pré-requisito** — dependências lógicas entre as decisões
- **Função objetivo de maximização** — benefício de segurança total

---

## 🗺️ Variáveis de Decisão

| Variável | Checkpoint / Ação | Custo (R$ mil) | Benefício (0–100) |
|----------|-------------------|:--------------:|:-----------------:|
| `x1` | Checkpoint Milão (saída de fábrica) | 80 | 90 |
| `x2` | Checkpoint Bolonha (rota A) | 60 | 60 |
| `x3` | Checkpoint Trieste (rota B – costeira) | 55 | 65 |
| `x4` | Checkpoint Ljubljana (fronteira ITA-SLO) | 70 | 80 |
| `x5` | Checkpoint Zagreb (Croácia) | 65 | 55 |
| `x6` | Checkpoint Viena (Áustria) | 90 | 70 |
| `x7` | Checkpoint Bratislava (Eslováquia) | 75 | 75 |
| `x8` | Checkpoint Varsóvia (destino final) | 85 | 85 |
| `x9` | Monitoramento GPS em tempo real | 50 | 95 |
| `x10` | Plataforma de rastreio por QR/lote | 40 | 88 |

---

## 📐 Restrições do Modelo

| ID | Tipo | Descrição | Formulação |
|----|------|-----------|------------|
| R1 | Pré-requisito | Varsóvia requer Milão | `x8 ≤ x1` |
| R2 | Pré-requisito | Ljubljana requer Milão **ou** Trieste | `x4 ≤ x1 + x3` |
| R3 | Pré-requisito | Bratislava requer Viena | `x7 ≤ x6` |
| R4 | Pré-requisito | Plataforma digital requer GPS | `x10 ≤ x9` |
| R5 | Exclusão mútua | Rota A e Rota B não podem coexistir | `x2 + x3 ≤ 1` |
| R6 | Cobertura mínima | Ao menos 4 checkpoints físicos | `Σ x1..x8 ≥ 4` |
| R7 | Orçamento | Custo total não ultrapassa R$ 850 mil | `Σ custo·xᵢ ≤ 850` |
| R8 | Cobertura tecnológica | Se plataforma ativa, ≥ 3 físicos | `Σ x1..x8 ≥ 3·x10` |

---

## ⚙️ Função Objetivo

**Maximizar** o benefício total de segurança:

```
max  Σ benefício[i] · x[i]    para i ∈ {x1, …, x10}
```

Implementado como minimização do negativo (compatível com o Pyomo/GLPK).

---

## 🚀 Como Executar

### Pré-requisitos

```bash
pip install pyomo
```

Instale também o solver **GLPK**:

```bash
# Ubuntu / Debian
sudo apt-get install glpk-utils

# macOS (Homebrew)
brew install glpk

# Windows
# Baixe em: https://sourceforge.net/projects/winglpk/
```

### Execução

```bash
python kitkat_mip.py
```

### Saída esperada

```
============================================================
RESOLVENDO MODELO MIP - NESTLÉ / KITKAT SUPPLY CHAIN
============================================================

Status do Solver  : ok
Condição termino  : optimal

--------------------------------------------------------------
Variável  Checkpoint/Ação                    Ativo?   Custo (R$mil)   Benefício
--------------------------------------------------------------
...
TOTAL     ...                                         XXX             XXX

Benefício máximo de segurança obtido : NNN pts
Custo total de implementação         : R$ NNN.000
Orçamento disponível                 : R$ 850.000
Orçamento restante                   : R$ NNN.000

--- Verificação das Restrições de Pré-Requisito ---
  ✓ OK | R1 - Varsóvia requer Milão
  ...
```

---

## 🏗️ Estrutura do Código

```
kitkat_mip.py
│
├── 1. Parâmetros          → custos e benefícios de cada checkpoint
├── 2. Modelo              → ConcreteModel (Pyomo)
├── 3. Variáveis           → 10 variáveis binárias (x1..x10)
├── 4. Função Objetivo     → maximizar benefício de segurança
├── 5. Restrições          → R1 a R8 (pré-requisitos + cobertura + orçamento)
├── 6. Resolução           → SolverFactory('glpk')
└── 7. Resultados          → tabela de decisões + verificação de restrições
```

---

## 📦 Dependências

| Biblioteca | Versão recomendada | Finalidade |
|------------|--------------------|------------|
| `pyomo` | ≥ 6.0 | Modelagem e resolução MIP |
| `glpk` | qualquer estável | Solver open-source para MIP |

---

## 🎓 Conceitos de PO Aplicados

- **MIP (Mixed Integer Programming)** — combinação de variáveis binárias com restrições lineares
- **Restrições de implicação lógica** — modelagem de pré-requisitos via inequações lineares
- **Exclusão mútua** — garantia de que apenas uma rota é escolhida
- **Set covering** — cobertura mínima de checkpoints ao longo da rota

---

## 📄 Licença

Projeto acadêmico/educacional. Dados e cenário são fictícios, inspirados no [incidente real de abr/2026](https://www.bbc.com/news/articles/c5yv9vgrydgo).
