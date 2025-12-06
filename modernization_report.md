# 📋 Пакет модернізації Legacy-системи

**Проект:** [Назва вашого проекту]  
**Студент:** [Ваше ПІБ]  
**Спеціальність:** 121 Інженерія програмного забезпечення  
**Дисципліна:** Реінженерія програмного забезпечення

---

## 🎯 Executive Summary

**Проблема:**  
[Опишіть основні проблеми Legacy-системи: технічний борг, складність підтримки, повільність розробки нових фічей]

**Рішення:**  
[Короткий опис застосованого підходу до модернізації]

**Результат:**  
- Зниження Cyclomatic Complexity на X%
- Покращення Maintainability Index на X пунктів
- Збільшення Test Coverage до X%
- Зменшення Technical Debt Ratio на X%

---

## 📊 ЧАСТИНА А: Технічний звіт "Before & After"

### 1. Метрики якості коду

#### Зведена таблиця метрик

| Модуль/Компонент | Метрика | До рефакторингу | Після рефакторингу | Покращення |
|------------------|---------|-----------------|-------------------|------------|
| `UserService` | Cyclomatic Complexity | 25 | 8 | ↓ 68% |
| `UserService` | Maintainability Index | 42 | 78 | ↑ 86% |
| `OrderProcessor` | Cyclomatic Complexity | 18 | 6 | ↓ 67% |
| `OrderProcessor` | Test Coverage | 15% | 85% | ↑ 467% |
| **Загальні показники** | | | | |
| Весь проект | Technical Debt Ratio | 8.5% | 2.3% | ↓ 73% |
| Весь проект | Code Duplication | 12% | 3% | ↓ 75% |

#### Інструменти вимірювання
- **Cyclomatic Complexity:** [SonarQube / Radon / Pylint]
- **Maintainability Index:** [Visual Studio Code Metrics / SonarQube]
- **Test Coverage:** [Coverage.py / JaCoCo / Jest]
- **Technical Debt:** [SonarQube / CodeClimate]

### 2. Аналіз "Гарячих точок" (Hotspots)

#### Найбільш проблемні компоненти

**🔥 Hotspot #1: Клас `UserService`**

**Проблема:**
- Метод `processUserRequest()` містив 150+ рядків коду
- Cyclomatic Complexity = 25 (критичний рівень)
- Порушення Single Responsibility Principle

**Застосовані патерни рефакторингу:**
1. ✅ **Extract Method** - виділили 5 окремих методів
2. ✅ **Replace Conditional with Polymorphism** - замінили 15+ if-else на стратегію
3. ✅ **Introduce Parameter Object** - об'єднали параметри в DTO

**Результат:**
```
До:  Complexity = 25, LOC = 150
Після: Complexity = 8, LOC = 45
```

**🔥 Hotspot #2: Клас `OrderProcessor`**

[Аналогічний опис для іншого проблемного компонента]

### 3. Звіт про вразливості (Security Analysis)

#### Результати SAST сканування

**Інструмент:** [Bandit / Snyk / SonarQube Security]

| Категорія вразливості | До рефакторингу | Після рефакторингу |
|-----------------------|-----------------|-------------------|
| 🔴 Critical | 2 | 0 |
| 🟠 High | 5 | 1 |
| 🟡 Medium | 12 | 3 |
| 🔵 Low | 8 | 2 |

**Виправлені критичні вразливості:**
1. **SQL Injection** в модулі `DatabaseHelper`
   - Замінили конкатенацію SQL на параметризовані запити
2. **Hardcoded Secrets** в конфігурації
   - Перенесли в змінні оточення (.env файл)

---

## 🏗️ ЧАСТИНА Б: Архітектурна трансформація

### 1. Діаграма "AS-IS" (Як було)

```
┌─────────────────────────────────────────┐
│         Monolithic Application          │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   UserController (500 LOC)      │   │
│  │   - handles HTTP requests       │   │
│  │   - validates data              │   │
│  │   - calls database directly     │   │
│  │   - sends emails                │   │
│  │   - logs everything             │   │
│  └──────────────┬──────────────────┘   │
│                 │ tight coupling        │
│                 ↓                       │
│  ┌─────────────────────────────────┐   │
│  │   MySQL Database                │   │
│  │   - 50+ tables                  │   │
│  │   - no clear separation         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘

Проблеми:
❌ High Coupling - всі компоненти жорстко зв'язані
❌ Low Cohesion - один клас робить все
❌ Важко тестувати - неможливо змокати залежності
❌ Важко масштабувати - все в одному процесі
```

### 2. Діаграма "TO-BE" (Як стало)

```
┌──────────────────────────────────────────────────────┐
│              Layered Architecture                    │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │         Presentation Layer                     │ │
│  │  ┌─────────────┐    ┌─────────────┐          │ │
│  │  │ UserController   PaymentController│          │ │
│  │  └──────┬──────┘    └──────┬───────┘          │ │
│  └─────────┼───────────────────┼──────────────────┘ │
│            ↓                   ↓                    │
│  ┌─────────────────────────────────────────────────┐ │
│  │         Business Logic Layer                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │UserService PaymentService NotificationSvc│    │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘    │ │
│  └───────┼─────────────┼─────────────┼───────────┘ │
│          ↓             ↓             ↓             │
│  ┌─────────────────────────────────────────────────┐ │
│  │         Data Access Layer                       │ │
│  │  ┌──────────┐  ┌──────────┐                   │ │
│  │  │UserRepository PaymentRepository│                   │ │
│  │  └────┬─────┘  └────┬─────┘                   │ │
│  └───────┼─────────────┼────────────────────────── │ │
│          ↓             ↓                           │
│  ┌──────────────────────────────────────┐         │
│  │      Database (ORM abstraction)      │         │
│  └──────────────────────────────────────┘         │
└──────────────────────────────────────────────────────┘

Переваги:
✅ Low Coupling - шари взаємодіють через інтерфейси
✅ High Cohesion - кожен клас має одну відповідальність
✅ Тестовність - можна легко мокати залежності
✅ Масштабованість - шари можна виділити в окремі сервіси
```

### 3. ADR (Architectural Decision Record)

#### ADR-001: Впровадження ORM замість прямих SQL-запитів

**Статус:** Прийнято  
**Дата:** [2024-12-06]  
**Автори:** [Ваше ім'я]

**Контекст:**
Початкова система використовувала сирі SQL-запити, що призводило до:
- SQL-ін'єкцій через конкатенацію рядків
- Дублювання коду запитів у різних модулях
- Складності при міграціях бази даних
- Відсутності типової безпеки

**Рішення:**
Впровадити ORM (Object-Relational Mapping) - [SQLAlchemy / Hibernate / Sequelize]

**Альтернативи:**
1. Залишити SQL-запити, але використовувати параметризацію
   - ❌ Не вирішує проблему дублювання коду
2. Використовувати Query Builder
   - ❌ Все ще потребує багато boilerplate коду

**Наслідки:**

**Позитивні:**
- ✅ Автоматична параметризація запитів (захист від SQL-ін'єкцій)
- ✅ Типова безпека на рівні коду
- ✅ Автоматична генерація міграцій
- ✅ Легше тестувати (можна мокати моделі)
- ✅ Менше boilerplate коду

**Негативні:**
- ⚠️ Крива навчання для команди
- ⚠️ Складніші запити можуть бути менш продуктивними
- ⚠️ Додаткова абстракція може ускладнити налагодження

**Приклад трансформації:**

**До (сирий SQL):**
```python
def get_user_orders(user_id):
    query = f"SELECT * FROM orders WHERE user_id = {user_id}"  # SQL INJECTION!
    cursor.execute(query)
    return cursor.fetchall()
```

**Після (ORM):**
```python
def get_user_orders(user_id: int) -> List[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()
```

---

## 🧪 ЧАСТИНА В: Інфраструктура та якість

### 1. Стратегія тестування (Testing Pyramid)

```
              /\
             /  \
           /  E2E  \          10% - End-to-End (UI tests)
          /  Tests  \
         /────────────\
        /              \
       /  Integration   \     30% - Integration Tests
      /      Tests       \
     /────────────────────\
    /                      \
   /      Unit Tests        \  60% - Unit Tests
  /_________________________ \
```

#### Приклади критичних Unit-тестів

**Test #1: Валідація бізнес-логіки оплати**

```python
def test_process_payment_insufficient_funds():
    """
    Критичний тест: система не повинна дозволяти оплату
    якщо недостатньо коштів на рахунку
    """
    # Arrange
    user = User(id=1, balance=50.0)
    order = Order(id=1, amount=100.0)
    payment_service = PaymentService()
    
    # Act & Assert
    with pytest.raises(InsufficientFundsError):
        payment_service.process_payment(user, order)
    
    # Переконуємось, що баланс не змінився
    assert user.balance == 50.0
```

**Test #2: Перевірка розрахунку знижок**

```python
def test_calculate_discount_for_premium_user():
    """
    Критичний тест: premium користувачі отримують 20% знижку
    """
    # Arrange
    user = User(id=1, membership="premium")
    cart = ShoppingCart(items=[
        Item(price=100.0),
        Item(price=50.0)
    ])
    discount_calculator = DiscountCalculator()
    
    # Act
    final_price = discount_calculator.calculate(user, cart)
    
    # Assert
    assert final_price == 120.0  # 150 - 20% = 120
```

**Test #3: Перевірка обробки помилок API**

```python
def test_user_registration_duplicate_email():
    """
    Критичний тест: система не дозволяє реєстрацію
    з вже існуючим email
    """
    # Arrange
    existing_user = User(email="test@example.com")
    db.add(existing_user)
    registration_service = RegistrationService()
    
    # Act & Assert
    with pytest.raises(DuplicateEmailError):
        registration_service.register(
            email="test@example.com",
            password="password123"
        )
```

#### Покриття тестами

| Модуль | Unit Tests | Integration Tests | Coverage |
|--------|-----------|-------------------|----------|
| `services/` | 45 | 12 | 87% |
| `repositories/` | 28 | 8 | 92% |
| `controllers/` | 15 | 10 | 78% |
| `utils/` | 20 | 0 | 95% |

### 2. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml

┌────────────────────────────────────────────────────────┐
│                   CI/CD Pipeline                       │
└────────────────────────────────────────────────────────┘

Trigger: Push to any branch, Pull Request to main

┌─────────────┐
│  Checkout   │
│    Code     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Install   │
│ Dependencies│
└──────┬──────┘
       │
       ↓
┌─────────────┐      ❌ FAIL → Block merge
│   Linting   │ ────→ ✅ PASS → Continue
│ (ESLint/    │
│  Pylint)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ❌ FAIL → Block merge
│ Static      │ ────→ ✅ PASS → Continue
│ Analysis    │
│ (SonarQube) │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ❌ FAIL → Block merge
│  Run Tests  │ ────→ ✅ PASS → Continue
│ (Unit +     │
│ Integration)│
└──────┬──────┘
       │
       ↓
┌─────────────┐      < 80% → Warning
│  Coverage   │ ────→ ≥ 80% → Continue
│   Report    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Build     │
│   Docker    │
│   Image     │
└──────┬──────┘
       │
       ↓ (only on main branch)
┌─────────────┐
│   Deploy    │
│  to Staging │
└─────────────┘
```

**Приклад конфігурації:**

```yaml
name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --max-line-length=120 --exclude=venv
    
    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Check coverage threshold
      run: |
        coverage report --fail-under=80
    
    - name: SonarQube Analysis
      uses: sonarsource/sonarqube-scan-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    
    - name: Build Docker image
      if: github.ref == 'refs/heads/main'
      run: |
        docker build -t myapp:latest .
```

### 3. Інструкція з розгортання

#### Швидкий старт з Docker Compose

**Передумови:**
- Docker Engine 20.10+
- Docker Compose 2.0+

**Крок 1: Клонування репозиторію**
```bash
git clone https://github.com/your-username/your-project.git
cd your-project
```

**Крок 2: Налаштування змінних оточення**
```bash
cp .env.example .env
# Відредагуйте .env файл з вашими налаштуваннями
```

**Крок 3: Запуск всіх сервісів**
```bash
docker-compose up -d
```

**Крок 4: Застосування міграцій**
```bash
docker-compose exec app python manage.py migrate
```

**Крок 5: Створення суперкористувача (опційно)**
```bash
docker-compose exec app python manage.py createsuperuser
```

**Доступ до додатку:**
- Веб-інтерфейс: http://localhost:8000
- API документація: http://localhost:8000/api/docs
- Адмін-панель: http://localhost:8000/admin

#### Docker Compose конфігурація

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

#### Корисні команди

```bash
# Перегляд логів
docker-compose logs -f app

# Перезапуск сервісів
docker-compose restart

# Зупинка всіх сервісів
docker-compose down

# Зупинка з видаленням volumes
docker-compose down -v

# Запуск тестів
docker-compose exec app pytest

# Перевірка стану сервісів
docker-compose ps
```

---

## 📈 Результати та висновки

### Досягнуті результати

✅ **Покращення якості коду:**
- Зниження технічного боргу на 73%
- Покращення читабельності коду
- Стандартизація стилю коду

✅ **Підвищення тестовності:**
- Покриття тестами збільшено з 15% до 85%
- Додано 108 unit-тестів
- Впроваджено CI/CD з автоматичним тестуванням

✅ **Покращення безпеки:**
- Виправлено 2 критичні вразливості
- Впроваджено SAST у CI/CD
- Додано валідацію вхідних даних

✅ **Архітектурні покращення:**
- Розділення на шари (Layered Architecture)
- Зниження зв'язності між компонентами
- Покращення можливості масштабування

### Наступні кроки (Roadmap)

**Короткострокові (1-2 місяці):**
- [ ] Рефакторинг модуля звітності
- [ ] Додавання E2E тестів
- [ ] Оптимізація продуктивності БД запитів

**Середньострокові (3-6 місяців):**
- [ ] Виділення сервісу нотифікацій в окремий мікросервіс
- [ ] Впровадження кешування (Redis)
- [ ] Міграція на асинхронну обробку задач (Celery/RabbitMQ)

**Довгострокові (6-12 місяців):**
- [ ] Повна міграція на мікросервісну архітектуру
- [ ] Впровадження Event-Driven Architecture
- [ ] Контейнеризація та оркестрація (Kubernetes)

---

## 📚 Використані ресурси

### Інструменти
- **Аналіз коду:** SonarQube, ESLint, Pylint
- **Тестування:** Pytest, Jest, JUnit
- **CI/CD:** GitHub Actions, GitLab CI
- **Контейнеризація:** Docker, Docker Compose

### Література та джерела
1. Martin Fowler - "Refactoring: Improving the Design of Existing Code"
2. Robert C. Martin - "Clean Code"
3. Michael Feathers - "Working Effectively with Legacy Code"
4. [Conventional Commits](https://www.conventionalcommits.org/)
5. [12-Factor App](https://12factor.net/)

---

## 📂 Структура репозиторію

```
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD конфігурація
├── docs/
│   ├── MODERNIZATION_REPORT.md    # Цей документ
│   ├── ADR/
│   │   └── ADR-001-orm.md         # Architectural Decision Records
│   └── diagrams/
│       ├── as-is.png              # Діаграма початкової архітектури
│       └── to-be.png              # Діаграма нової архітектури
├── src/                           # Код додатку
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   └── models/
├── tests/                         # Тести
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker-compose.yml             # Docker конфігурація
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎤 Презентація (Скрипт для захисту)

### Слайд 1: Проблема (1 хв)
"Доброго дня! Я [Ваше ім'я], і сьогодні представлю результати модернізації [назва проекту].

**Що боліло у старого коду?**
- Монолітна архітектура з жорсткими зв'язками
- Критична складність методів (Complexity = 25)
- Відсутність тестів (Coverage < 15%)
- SQL-ін'єкції та інші вразливості
- Технічний борг сягнув 8.5%"

### Слайд 2: Рішення (2 хв)
"**Що конкретно ми зробили?**

Дозвольте показати найстрашніший шматок коду і як він виглядає зараз.

[Показати порівняння: 150 рядків до → 45 рядків після]

Ключові зміни:
- Розділили на шари (Layered Architecture)
- Впровадили ORM замість сирих SQL
- Додали 108 unit-тестів
- Налаштували CI/CD з автоматичними перевірками"

### Слайд 3: Результат (1 хв)
"**Наскільки знизився технічний борг?**

Цифри говорять самі за себе:
- ↓ 73% Technical Debt Ratio
- ↑ 467% Test Coverage (з 15% до 85%)
- ↓ 68% Cyclomatic Complexity
- 0 критичних вразливостей"

### Слайд 4: План (1 хв)
"**Що ще треба доробити?**

Короткостроково:
- Рефакторинг модуля звітності
- Додавання E2E тестів

Довгостроково:
- Поступовий перехід до мікросервісів
- Event-Driven Architecture

Дякую за увагу! Готовий відповісти на запитання."

---

## 🔗 Посилання

- **Репозиторій:** [https://github.com/your-username/project](https://github.com/your-username/project)
- **Live Demo:** [https://your-project.com](https://your-project.com)
- **Презентація:** [Google Slides / PowerPoint link]
- **Metrics Dashboard:** [SonarQube link]

---

**Дата фінального звіту:** [Дата]  
**Версія документа:** 1.0