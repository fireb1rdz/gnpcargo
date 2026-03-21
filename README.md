# GNP-ERP

## Arquitetura do Projeto

Este projeto adota uma **arquitetura modular**, inspirada em **Domain-Driven Design (DDD)** e **Clean Architecture**, adaptada ao ecossistema Django.

### Objetivos principais

* evitar acoplamento entre apps
* permitir evolução modular
* manter regras de negócio fora de views, forms e models
* facilitar testes, manutenção e substituição de implementações

---

## Visão Geral da Estrutura

```
apps/
└── aplicacao/
    └── factories/
        └── modelo_factory.py
    └── services/
        └── modelo_service.py

domain/
├── bootstrap/
│   └── service_container.py
├── contracts/
│   ├── aplicacao.py
│   └── importers/
│       └── aplicacao.py
├── dto/
│   └── modelo.py
└── registry/
    └── module_registry.py
```

---

## Regra de Ouro de Dependência

```
apps  ───▶ domain   ✅ permitido
domain ───▶ apps    ❌ proibido
```

### Comunicação correta entre apps

```
App A → contract → bootstrap → App B
```

❌ **Nunca**:

```python
from apps.outro_app.services import OutroService
```

✅ **Sempre**:

```python
from domain.bootstrap.services import get_outro_service
```

---

## Camadas da Arquitetura

### `domain/` — Núcleo do sistema (framework-agnostic)

O `domain` representa o **coração do sistema**.

* Não depende de Django
* Não conhece ORM, request, settings ou infraestrutura
* Define **contratos**, **DTOs** e **mecanismos de integração**

---

### `domain/contracts/` — Contratos (interfaces)

Define **o que o sistema faz**, nunca **como**.

#### `domain/contracts/aplicacao.py`

* Contratos específicos de um domínio ou app
* Normalmente definidos com `ABC`
* Exemplo:

```python
class ModeloServiceInterface(ABC):
    @abstractmethod
    def criar(...):
        ...
```

#### `domain/contracts/importers.py`

* Contratos para importação (XML, CSV, API etc.)
* Usam `ABC` e `Protocol`
* Permitem múltiplas implementações por apps distintos

---

### `domain/dto/` — Data Transfer Objects

DTOs são usados para **transportar dados entre camadas**.

Características:

* objetos simples
* não acessam banco
* não possuem regras de negócio
* não dependem de Django

Exemplo:

```python
@dataclass
class ModeloDTO:
    id: str
    nome: str
```

---

### `domain/bootstrap/` — Bootstrap / Service Locator

Responsável por **resolver e fornecer implementações concretas** dos contracts.

Centraliza a criação de serviços e elimina imports diretos entre apps.

Exemplo:

```python
def get_modelo_service() -> ModeloServiceInterface:
    return ModeloService()
```

**Benefícios**:

* evita dependências circulares
* facilita troca de implementação
* simplifica testes e mocks

---

### `domain/registry/` — Registro de módulos

Usado para **descoberta dinâmica de módulos**, especialmente em cenários como:

* importadores
* plugins
* ERP modular
* extensões opcionais

Exemplo:

```python
ModuleRegistry.register("fiscal", FiscalService())
```

Uso posterior:

```python
fiscal = ModuleRegistry.get("fiscal")
```

---

## `apps/` — Implementação concreta (Django)

Contém os **apps Django reais**, responsáveis por:

* models
* services
* integrações externas
* factories
* ORM

### `apps/*/services/` — Services de aplicação

#### Exemplo: `apps/aplicacao/services/modelo_service.py`

Responsabilidades:

* implementar regras de negócio
* implementar **contracts do domain**
* usar ORM, models e bibliotecas externas

Restrições:

* ❌ nunca define contratos
* ❌ nunca acessa services de outros apps diretamente

Exemplo:

```python
class ModeloService(ModeloServiceInterface):
    ...
```

---

## Factories de Models

Este projeto adota **factories como padrão arquitetural** para criação de models.

### Objetivo das factories

Centralizar e padronizar a criação de models, garantindo que:

* regras de criação fiquem em um único lugar
* defaults e normalizações sejam consistentes
* a criação não fique espalhada por views, forms ou services

> **Factory constrói o model corretamente.**
> **Service decide quando e por que criar.**

---

### Onde ficam as factories

Factories pertencem à **camada de infraestrutura**, portanto ficam **dentro do app dono do model**.

Exemplo:

```
apps/
└── entities/
    ├── models.py
    ├── services/
    └── factories/
        ├── entity_factory.py
        └── party_factory.py
```

⚠️ O `domain` **nunca** contém factories de models.

---

### Responsabilidade da factory

Uma factory **pode**:

* definir valores padrão
* normalizar dados
* validar pré-condições simples
* criar relacionamentos diretos
* encapsular chamadas ao ORM

Uma factory **não deve**:

* orquestrar fluxos complexos
* acessar outros apps
* conter regras de negócio de alto nível

---

### Exemplo de factory

```python
class PartyFactory:
    @staticmethod
    def create(*, tenant, entity, role, alias=None):
        return Party.objects.create(
            tenant=tenant,
            entity=entity,
            role=role,
            alias=alias or entity.name,
        )
```

---

### Relação entre View, Service e Factory

Fluxo correto:

```
View / Form
   ↓
Service (regra de negócio)
   ↓
Factory (construção)
   ↓
Model (ORM)
```

A view **nunca cria models diretamente**.

---

### Factories de teste

Factories usadas apenas para testes (ex.: FactoryBoy) **não fazem parte da arquitetura**:

```
tests/
└── factories/
```

Nunca devem ser reutilizadas em código de produção.

---

## Onde cada coisa deve ficar

| Tipo                          | Local               |
| ----------------------------- | ------------------- |
| Regras de negócio             | `apps/*/services/`  |
| Interfaces (ABCs / Protocols) | `domain/contracts/` |
| DTOs                          | `domain/dto/`       |
| Registro global               | `domain/registry/`  |
| Service locator / bootstrap   | `domain/bootstrap/` |

---

## Benefícios da Arquitetura

* ✅ Apps desacoplados
* ✅ Regras de negócio centralizadas
* ✅ Testes mais simples
* ✅ Substituição de implementações sem impacto
* ✅ ERP realmente modular
* ✅ Evita “Django spaghetti”

---

## Conclusão

Essa arquitetura:

* **faz sentido**
* é **usada no mundo real**
* escala bem para sistemas:

  * SaaS
  * ERPs
  * multi-tenant (`django-tenants`)
  * plataformas extensíveis

Ela exige disciplina, mas o custo inicial é pago com **manutenibilidade, escala e clareza arquitetural**.

---
