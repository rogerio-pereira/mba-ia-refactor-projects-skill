# Architecture Audit: code-smells-project

## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | Python (versão do interpretador não fixada no repositório) |
| Framework | Flask 3.1.1 com `flask-cors` 5.0.1 |
| Dependencies | `flask`, `flask-cors`, `sqlite3` e `werkzeug.security` |
| Domain | API de e-commerce para produtos, usuários, autenticação, pedidos e relatórios de vendas |
| Architecture | Há separação parcial entre `app.py`, `controllers.py`, repositórios e serviços, mas ainda existem violações de boundary: controller acessando banco diretamente, regras de negócio em repositório de relatório, schema e seed acoplados à infraestrutura e artefatos legados (`models.py`) que obscurecem a arquitetura |
| Source files | 19 arquivos analisados no diretório `code-smells-project`, totalizando aproximadamente 1009 linhas; 15 módulos Python e 4 arquivos de suporte/configuração |
| Entry point | `code-smells-project/app.py`; comando documentado: `python3 app.py` |
| Routes | `/`, `/produtos`, `/produtos/busca`, `/produtos/<id>`, `/usuarios`, `/usuarios/<id>`, `/login`, `/pedidos`, `/pedidos/usuario/<usuario_id>`, `/pedidos/<pedido_id>/status`, `/relatorios/vendas`, `/health` |
| Database | SQLite via `code-smells-project/database.py`, com criação de schema, seed inicial e migração de senhas legadas no boot |

## Phase 2: Architecture Audit

Project: `code-smells-project`

Stack: Python, Flask, SQLite

Analyzed scope: `code-smells-project/*.py`, `README.md`, `requirements.txt`, `.env`, `.env.example`

Approximate lines of code: 1009 total lines, incluindo 982 linhas Python

### Summary By Severity

| Severity | Count |
| --- | ---: |
| CRITICAL | 1 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |

## Findings

### [FIXED] [CRITICAL] Segredo ativo versionado no repositório
File: `code-smells-project/.env:1-5`, `code-smells-project/config.py:35-45`, `code-smells-project/app.py:34-35`  
Category: Security | Config  
Description: O arquivo `.env` versionado contém um `SECRET_KEY` real (`SECRET_KEY=minha-chave-super-secreta-123`), e a aplicação carrega automaticamente esse arquivo em import time por `load_env_file()`. A proteção em `app.py` apenas exige chave fora de `development`, mas não impede que um segredo real seja armazenado no repositório.  
Impact: Qualquer vazamento do código expõe a chave usada pela aplicação, comprometendo cookies assinados e qualquer funcionalidade futura que dependa de `SECRET_KEY`. Também normaliza uma prática insegura de versionar credenciais.  
Recommendation: Remover `.env` do versionamento, manter apenas `.env.example` com placeholder, carregar segredos exclusivamente por variáveis de ambiente injetadas no ambiente de execução e falhar no boot quando um valor placeholder for usado fora de ambiente local controlado.  
MVC Target: Config  
Validation: `python3 -m py_compile code-smells-project/*.py` passed; production boot with placeholder secret now fails explicitly and development boot still succeeds.

### [FIXED] [HIGH] Criação de pedido não protege estoque contra concorrência e pode gerar overselling
File: `code-smells-project/order_service.py:12-33`, `code-smells-project/product_repository.py:85-91`  
Category: Reliability | Architecture  
Description: A validação de estoque é feita em memória antes da escrita, e o decremento ocorre depois com `UPDATE produtos SET estoque = estoque - ? WHERE id = ?`, sem cláusula de guarda (`estoque >= ?`) e sem revalidação atômica no banco. Em cenários concorrentes, dois requests podem aprovar o mesmo estoque.  
Impact: O sistema pode vender itens acima do disponível, produzindo inconsistência financeira e operacional. O `commit` ao final da transação não resolve a condição de corrida porque a decisão já foi tomada sobre dados potencialmente obsoletos.  
Recommendation: Mover a verificação de disponibilidade para uma atualização atômica por item, com rollback ao primeiro conflito, ou aplicar bloqueio/transação com checagem no banco. Idealmente, encapsular a política de reserva de estoque em uma camada de serviço/repositório transacional explícita.  
MVC Target: Service  
Validation: `python3 -m py_compile code-smells-project/*.py` passed; `app.test_client()` smoke test confirmed a second order fails after the first one exhausts the same stock.

### [HIGH] Atualização de status aceita pedidos inexistentes e ainda dispara notificação
File: `code-smells-project/order_repository.py:51-59`, `code-smells-project/order_service.py:83-85`, `code-smells-project/controllers.py:106-110`  
Category: Reliability  
Description: `order_repository.atualizar_status_pedido()` sempre retorna `True`, sem checar `rowcount`. Em seguida, `order_service.atualizar_status_pedido()` dispara notificação independentemente de o pedido existir, e o controller devolve sucesso para o cliente.  
Impact: A API confirma operações que não ocorreram e pode emitir notificações falsas, tornando o estado externo do sistema inconsistente com o estado persistido.  
Recommendation: Verificar se o `UPDATE` afetou uma linha, lançar erro 404 quando o pedido não existir e só notificar após confirmação de persistência válida.  
MVC Target: Service  

### [HIGH] Schema permissivo demais compromete integridade de dados
File: `code-smells-project/database.py:38-77`, `code-smells-project/validators.py:51-85`, `code-smells-project/auth_service.py:14-34`  
Category: Architecture | Reliability  
Description: As tabelas são criadas sem `NOT NULL`, sem `UNIQUE` para `usuarios.email` e sem `FOREIGN KEY` entre `pedidos`, `itens_pedido`, `usuarios` e `produtos`. A validação de aplicação não fecha essas lacunas: e-mails não são validados quanto a formato/unicidade e pedidos aceitam `usuario_id` sem confirmar existência do usuário.  
Impact: O banco aceita registros órfãos, duplicados e semanticamente inválidos, o que degrada a confiabilidade do login, relatórios e fluxo de pedidos. Em SQLite, deixar a integridade apenas na camada Python é frágil e difícil de auditar.  
Recommendation: Reforçar o schema com constraints de banco (`NOT NULL`, `UNIQUE`, `FOREIGN KEY`), habilitar `PRAGMA foreign_keys = ON`, validar unicidade/forma de e-mail e checar existência de usuário antes da criação do pedido.  
MVC Target: Model  

### [MEDIUM] Controller de health bypassa service/repository e conhece detalhes de persistência
File: `code-smells-project/controllers.py:116-136`  
Category: Architecture  
Description: `health_check()` acessa `get_db()` diretamente, executa SQL inline e monta a resposta HTTP no mesmo bloco. Isso quebra a boundary adotada no restante da aplicação, onde acesso a dados tende a ficar em repositórios e orquestração em serviços.  
Impact: O controller passa a conhecer estrutura de banco e detalhes de contagem, aumentando acoplamento e reduzindo reutilização/testabilidade. Mudanças simples de persistência exigirão alteração na camada HTTP.  
Recommendation: Extrair um `health_service` ou `system_repository` para encapsular as consultas operacionais e deixar o controller apenas traduzir request/response.  
MVC Target: Controller  

### [MEDIUM] Regra de desconto de faturamento está misturada com acesso a dados
File: `code-smells-project/report_repository.py:8-41`  
Category: Architecture | Maintainability  
Description: O repositório consulta o banco e, na mesma função, aplica regras de negócio de desconto por faixa de faturamento. Essa regra não é de persistência; ela é lógica de domínio/aplicação.  
Impact: A camada de acesso a dados fica responsável por política comercial, o que dificulta testes unitários, reutilização da regra em outros canais e futura troca de persistência.  
Recommendation: Limitar o repositório à coleta de dados agregados e mover o cálculo de desconto/ticket para um serviço de relatório.  
MVC Target: Service  

### [MEDIUM] Artefatos legados e código morto obscurecem a arquitetura real
File: `code-smells-project/models.py:1-25`, `code-smells-project/user_repository.py:42-49`, `code-smells-project/controllers.py:9-17`, `code-smells-project/validators.py:11-12`  
Category: Maintainability  
Description: `models.py` atua apenas como fachada de aliases para serviços e repositórios, mas não é usado pelo fluxo principal. Além disso, `get_usuario_por_email_e_senha()` e `parse_json_payload()` permanecem definidos sem uso. Esses artefatos sugerem uma arquitetura anterior e criam uma superfície de manutenção enganosa.  
Impact: Novos desenvolvedores tendem a inferir boundaries errados, aumentando risco de regressão ou duplicação ao adicionar funcionalidades. Código morto também preserva APIs perigosas, como a busca por senha em texto puro.  
Recommendation: Remover a fachada legada e funções não utilizadas, ou documentar explicitamente uma camada de compatibilidade se ela for necessária.  
MVC Target: Composition Root  

### [LOW] Logging operacional usa `print` e expõe dados de negócio sem padronização
File: `code-smells-project/controllers.py:19-22`, `code-smells-project/controllers.py:30-34`, `code-smells-project/controllers.py:45-52`, `code-smells-project/controllers.py:69-83`, `code-smells-project/notification_service.py:1-11`, `code-smells-project/app.py:75-78`  
Category: Maintainability | Reliability  
Description: O projeto registra eventos por `print`, incluindo e-mails e IDs de pedido, sem níveis de log, correlação, mascaramento ou integração com o logger do Flask.  
Impact: Observabilidade fica limitada e dados operacionais podem vazar em stdout sem contexto estruturado. Em produção, isso dificulta troubleshooting e governança sobre dados sensíveis.  
Recommendation: Padronizar logging com `app.logger` ou `logging`, definir níveis (`info`, `warning`, `error`) e evitar registrar identificadores sensíveis sem necessidade.  
MVC Target: Middleware  

### [LOW] Serialização de produto é duplicada em múltiplos pontos
File: `code-smells-project/product_repository.py:10-20`, `code-smells-project/product_repository.py:30-39`, `code-smells-project/product_repository.py:117-128`  
Category: Maintainability  
Description: O mapeamento de `sqlite3.Row` para dicionário de produto é repetido em três trechos praticamente idênticos.  
Impact: Pequenas mudanças no contrato de resposta exigem alterações repetidas e aumentam a chance de inconsistência entre endpoints.  
Recommendation: Extrair um serializer/helper privado único para produtos, seguindo o padrão já adotado em `_serialize_usuario()`.  
MVC Target: Helper  

## Deprecated API Detection

Nenhum uso claramente depreciado de Flask 3.1.1 foi identificado nos arquivos analisados. Os principais problemas atuais são de segurança operacional, integridade transacional e separação de responsabilidades.

## Proposed Phase 3 Refactoring Plan

1. [FIXED] Remover `.env` do controle de versão, tratar `SECRET_KEY` como segredo externo e endurecer a validação de configuração por ambiente.
2. [FIXED] Reescrever a criação de pedidos para usar reserva/decremento de estoque atômicos e falhar corretamente em conflitos de concorrência.
3. Corrigir o fluxo de atualização de status para validar existência do pedido antes de persistir e notificar.
4. Reforçar o schema SQLite com constraints reais (`NOT NULL`, `UNIQUE`, `FOREIGN KEY`) e alinhar validadores ao novo contrato.
5. Extrair consultas operacionais de `health_check()` para uma camada própria de serviço/repositório.
6. Separar a lógica de desconto do `report_repository` e mantê-la em um serviço de domínio.
7. Eliminar código morto e camadas de compatibilidade que não participam do fluxo ativo.
8. Substituir `print` por logging estruturado e consolidar serializers repetidos.

Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
