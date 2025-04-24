# CRM - Backend Athenas ™️ 🚀

O **Athenas** é um CRM backend desenvolvido para atender correspondentes bancários que intermediam operações com bancos públicos e privados. Com foco em regras de negócios personalizadas, o sistema suporta empresas de pequeno e grande porte, integrando-se a bancos como `Facta`, `Master`, `Daycoval`, `Bradesco`, entre outros.

---

## 🎯 Objetivo

O Athenas foi projetado para otimizar a intermediação bancária, oferecendo:
- Gestão eficiente de colaboradores, operações, finanças e administração.
- Integração com APIs de bancos para agilizar consultas e validações.
- Conformidade com a LGPD para tratamento de dados sensíveis.
- Automatização de processos, como cálculos de comissões e relatórios financeiros.

---

## 📋 Sumário

- [Núcleo de Colaboradores](#núcleo-de-colaboradores)
- [Gestão Operacional](#gestão-operacional)
- [Gestão Financeira](#gestão-financeira)
- [Gestão Administrativa](#gestão-administrativa)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura de Software](#arquitetura-de-software)
- [Configuração](#configuração)
- [Uso](#uso)
- [Tomada de Decisão](#tomada-de-decisão)
- [Autor](#autor)

---

## Núcleo de Colaboradores

O Athenas centraliza a gestão de colaboradores, registrando e caracterizando vendas para intermediação bancária. O sistema consome APIs REST de bancos internos, permitindo consultas rápidas e precisas para servidores públicos, federais e celetistas.

---

## Gestão Operacional

A gestão operacional do Athenas agiliza a intermediação com bancos, processando dados sensíveis validados em conformidade com a LGPD. O sistema garante eficiência e segurança nas operações financeiras realizadas.

---

## gestão Financeira

O módulo financeiro minimiza erros em cálculos de comissões entre correspondentes bancários e bancos. Ele automatiza:
- Cálculo e persistência de comissões internas e externas.
- Emissão de relatórios financeiros.
- Monitoramento de pagamentos.

---

## Gestão Administrativa

O Athenas oferece indicadores globais sobre o desempenho do sistema e dos colaboradores, incluindo:
- Estatísticas de ganhos e perdas.
- Automatização de planilhas para maior desempenho.
- Backups de dados sensíveis entre servidores e o sistema.

---

## 🛠️ Tecnologias Utilizadas

O CRM foi desenvolvido com tecnologias modernas para garantir escalabilidade, segurança e desempenho:

- **Linguagem**: Python
- **Framework**: Flask (microsserviços)
- **Banco de Dados**: PostgreSQL
- **ORM**: SQLAlchemy
- **Testes**: Pytest (testes unitários)
- **CI/CD**: Jenkins para deploy automatizado
- **Servidor**: Gunicorn (Linux)

---

## Arquitetura de Software

O Athenas segue a **Layered Architecture** (arquitetura em camadas), garantindo modularidade e escalabilidade. O banco de dados relacional PostgreSQL suporta a persistência de dados, adaptando-se às necessidades do negócio.

### Estrutura de Diretórios

```plaintext
src/
├── core/         # Lógica central do sistema
├── db/           # Configurações do banco de dados
├── models/       # Modelos ORM
├── resource/     # Endpoints da API
├── service/      # Regras de negócio
├── settings/     # Configurações do sistema
├── static/       # Arquivos estáticos
├── utils/        # Utilitários
├── app.py        # Ponto de entrada da aplicação
├── manage.py     # Scripts de gerenciamento
├── gunicorn.conf.py  # Configurações do Gunicorn
```

---


## 🤔 Tomada de Decisão

Após análise detalhada das necessidades do negócio, optamos pelo desenvolvimento de um CRM personalizado com o **Flask** devido à sua flexibilidade, leveza e ampla adoção. Embora outros frameworks tenham sido considerados, o Flask foi escolhido por permitir entregas rápidas e atender às demandas de um projeto de nível nacional. Recomenda-se, no entanto, uma curva de aprendizado em princípios web, engenharia de software e estruturas de dados para maximizar seu potencial.

---

## 👤 Autor

**Hedris Pereira**  
Desenvolvedor Backend do **Athenas ™️**  
🚀 *Inovação e eficiência em cada linha de código.*