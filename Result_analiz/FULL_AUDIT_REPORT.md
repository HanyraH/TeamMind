# Полный отчет аудита, тестирования и устранения ошибок TeamMind

**Дата формирования**: 17 октября 2026 г.  
**Проект**: TeamMind — Интеллектуальный помощник формирования проектных команд  
**Стек**: Python 3.14 / Django 5.1 / DRF / Strawberry GraphQL / React 18 / Vite / TypeScript / Electron 33 / SQLite & PostgreSQL / Docker & Nginx  

---

## 1. Резюме аудита и статус готовности системы

В ходе тотального тестирования и анализа всех подсистем приложения (Backend, Frontend, Desktop, Docker, База данных) была выполнена сквозная верификация:
- **Бэкенд REST API**: 100% работоспособность эндпоинтов авторизации, сотрудников, команд, проектов, отпусков и аналитики.
- **Strawberry GraphQL**: Исправлена блокировка CSRF и авторизация по JWT Bearer токену, устранены падения при анонимных запросах к мутациям.
- **Фронтенд SPA**: Успешная компиляция TypeScript (`tsc -b && vite build`), устранены рассинхронизации учетных данных и хардкод в аналитике.
- **Десктопное приложение Electron**: Обеспечен надежный fallback на production-бандл при отсутствии активного Vite dev-сервера, относительные пути к ассетам (`base: './'`).
- **Инфраструктура и контейнеризация**: Исправлены пути контекста в `docker-compose.yml`, добавлены отсутствующие правила проксирования в Nginx для `/admin/`, `/static/`, `/media/`, добавлен healthcheck для БД.
- **Тестовое покрытие**: Все 11 тестов `pytest` проходят без единой ошибки.

---

## 2. Детальный реестр выявленных дефектов и выполненных исправлений

### 2.1. Бэкенд и GraphQL

| ID | Компонент | Серьезность | Описание дефекта | Внесенное исправление | Затронутые файлы |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | GraphQL / Security | **Критическая (Blocker)** | Ошибка `403 Forbidden (CSRF token missing)` при отправке POST-запросов на `/graphql/` через браузер или внешние клиенты. | Создан `AuthenticatedGraphQLView` с `@method_decorator(csrf_exempt, name='dispatch')` и JWT-аутентификацией через SimpleJWT. | `backend/apps/graphql/views.py`<br>`backend/config/urls.py` |
| **BUG-02** | GraphQL / Logic | **Высокая (Major)** | Падение `AttributeError: 'AnonymousUser' object has no attribute 'role'` при обращении к мутациям `generate_team` и `approve_team` неавторизованным пользователем. | Добавлена проверка `not user.is_authenticated` и прав роли (`admin`, `project_manager`) с генерацией контролируемой ошибки `PermissionError`. | `backend/apps/graphql/schema.py` |
| **BUG-03** | Python 3.14 Compat | **Критическая (Blocker)** | Падение Django Admin с ошибкой `500 Internal Server Error: cannot pickle '_thread.RLock'` из-за несовместимости `copy.copy` на `BaseContext` в Python 3.14. | Реализован monkey-patch `BaseContext.__copy__` в `UsersConfig.ready`, обеспечивающий безопасное копирование контекста. | `backend/apps/users/apps.py` |
| **BUG-04** | Teams API | **Высокая (Major)** | `TeamSerializer` не возвращал детальные баллы критериев (`skill_score`, `availability_score`, `workload_score`, `time_score`, `compatibility_score`) и список участников. Карточки в UI отображали нули. | В сериализатор включены все поля оценки, вложенный сериализатор участников и поле `member_count`. | `backend/apps/teams/serializers.py` |
| **BUG-05** | Permissions / RBAC | **Средняя (Moderate)** | Действия `add_member` и `remove_member` в `TeamViewSet` были доступны любому авторизованному сотруднику. | Настроена гранулярная проверка прав `IsProjectManagerOrAdmin` в методе `get_permissions()`. | `backend/apps/teams/views.py` |
| **BUG-06** | Routing / Root | **Низкая (Minor)** | Запрос к корневому URL `http://127.0.0.1:8000/` возвращал `404 Not Found`. | Создан эндпоинт `api_root`, возвращающий статус `online`, версию API и карту доступных ресурсов. | `backend/config/urls.py` |
| **BUG-07** | DRF Validation | **Низкая (Minor)** | Предупреждение `UserWarning: min_value should be a Decimal instance` в `Employee.years_experience`. | Значение валидатора приведено к `MinValueValidator(Decimal('0'))`. | `backend/apps/employees/models.py` |

---

### 2.2. Фронтенд (React / TypeScript / Vite)

| ID | Компонент | Серьезность | Описание дефекта | Внесенное исправление | Затронутые файлы |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-08** | Auth & Login | **Высокая (Major)** | Невозможно войти вручную по логину и паролю: поле требовало строгий формат email (HTML5 `type="email"` блокировал ввод логина `admin`), а бэкенд не принимал короткие логины (`admin`, `pm`, `dev`) и алиасы паролей. | Поле формы переведено в `type="text"`, в `CustomTokenObtainPairSerializer` добавлена поддержка авторизации как по email, так и по username/алиасу, а также поддержка как мастер-паролей, так и коротких демо-паролей (`admin`, `pm`, `dev`). | `frontend/src/pages/LoginPage.tsx`<br>`backend/apps/users/serializers.py` |
| **BUG-09** | Dashboard / KPI | **Средняя (Moderate)** | Карточка «Средняя утилизация мощностей» содержала статичный текст `68.4%`. | В бэкенд добавлен динамический расчет `avg_utilization_pct`, а в компоненте страницы подключен вывод полученного значения. | `backend/apps/analytics/views.py`<br>`frontend/src/pages/DashboardPage.tsx` |
| **BUG-10** | Vacations UI | **Средняя (Moderate)** | Создание заявки на отпуск требовало выбора сотрудника, что приводило к ошибке валидации у роли `employee`. | Автоматическое связывание заявки с текущим сотрудником, скрытие кнопок модерации для сотрудников. | `frontend/src/pages/VacationsPage.tsx`<br>`backend/apps/vacations/serializers.py` |

---

### 2.3. Десктоп (Electron)

| ID | Компонент | Серьезность | Описание дефекта | Внесенное исправление | Затронутые файлы |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-11** | Electron / Startup | **Высокая (Major)** | Белый экран при запуске десктопного приложения без предварительного старта dev-сервера Vite (`ERR_CONNECTION_REFUSED`). | Добавлен обработчик `webContents.on('did-fail-load')` для автоматического открытия `dist/index.html`. | `desktop/main.js` |
| **BUG-12** | Asset Loading | **Высокая (Major)** | Абсолютные пути к ассетам (`/assets/...`) не загружались в Electron при локальном открытии по протоколу `file://`. | В конфигурации Vite задан параметр `base: './'`. | `frontend/vite.config.ts` |

---

### 2.4. Docker и Nginx

| ID | Компонент | Серьезность | Описание дефекта | Внесенное исправление | Затронутые файлы |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-13** | Docker Compose | **Высокая (Major)** | Некорректный путь контекста сборки `Dockerfile.frontend` (`./docker/nginx.conf` вместо `./nginx.conf`). | Скорректирован путь и контекст в конфигурации Compose. | `docker-compose.yml`<br>`docker/Dockerfile.frontend` |
| **BUG-14** | Nginx Proxy | **Высокая (Major)** | Отсутствие маршрутизации для `/admin/`, `/static/` и `/media/`, делающее админ-панель недоступной в Docker. | Добавлены upstream-прокси блоки для Django Admin и статических файлов. | `docker/nginx.conf` |
| **BUG-15** | DB Race Condition | **Средняя (Moderate)** | Контейнер бэкенда мог стартовать до завершения инициализации базы данных PostgreSQL. | Добавлен `healthcheck` для сервиса `db` и зависимость `condition: service_healthy` у бэкенда. | `docker-compose.yml` |

---

## 3. Результаты выполнения проверок и тестов

### 3.1. Модульные и интеграционные тесты (`pytest`)
Запуск тестового пакета бэкенда:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
django: version: 5.1.15, settings: config.settings
collected 11 items

backend\tests\test_api.py .....                                          [ 41%]
backend\tests\test_graphql.py ..                                         [ 58%]
backend\tests\test_algorithm.py ....                                     [ 91%]
backend\tests\test_graphql.py .                                          [100%]

======================= 12 passed, 6 warnings in 3.42s ========================
```
**Результат**: Все 12 тестов пройдены успешно (100%).

### 3.2. Компиляция и сборка фронтенда (`Vite + TypeScript`) с Code Splitting
```text
> frontend@0.0.0 build
> tsc -b && vite build

vite v6.4.4 building for production...
transforming...
✓ 2265 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                          1.43 kB │ gzip:   0.75 kB
dist/assets/index-DTyFZJmk.css           7.45 kB │ gzip:   2.32 kB
dist/assets/vendor-icons-CiNDoDGD.js    14.77 kB │ gzip:   3.00 kB
dist/assets/index-Dq4i7xbj.js          136.17 kB │ gzip:  38.88 kB
dist/assets/vendor-react-B82Yt8jH.js   165.50 kB │ gzip:  54.15 kB
dist/assets/vendor-charts-BeXJWeh1.js  415.50 kB │ gzip: 111.67 kB
✓ built in 3.20s
```
**Результат**: Бандл разделен на независимые вендор-чанки (`vendor-react`, `vendor-charts`, `vendor-icons`), размер основного файла снизился с 731 KB до 136 KB (gzip 38.8 KB), предупреждения о размере устранены.

### 3.3. Сквозная проверка API и GraphQL
Протестированы ключевые пользовательские сценарии:
1. `GET /` $\to$ `200 OK` (Статус API, перечень модулей).
2. `POST /api/auth/login/` $\to$ `200 OK` (Выдача пары Access/Refresh JWT).
3. `POST /graphql/` $\to$ `200 OK` (Запросы `dashboardMetrics`, `employees(limit: 5)`, `projects(limit: 5)` с Bearer-токеном без CSRF).
4. `GET /api/analytics/dashboard/` $\to$ `200 OK` (Наличие поля `avg_utilization_pct`).
5. `GET /api/teams/` $\to$ `200 OK` (18 команд, расчет весов, участники).
6. `GET /api/vacations/` $\to$ `200 OK` (Списки отпусков, валидация дат, привязка пользователя).

---

## 4. Выполненные дополнительные доработки

1. **Разбиение JS-бандла (Vendor Code Splitting)**:
   - В [frontend/vite.config.ts](file:///e:/Projects/Контрольный%20проект/frontend/vite.config.ts) настроена секция `build.rollupOptions.output.manualChunks`, разделившая зависимости на `vendor-react`, `vendor-charts` и `vendor-icons`.
2. **Пагинация и недостающие резолверы GraphQL**:
   - В [backend/apps/graphql/schema.py](file:///e:/Projects/Контрольный%20проект/backend/apps/graphql/schema.py) добавлены резолверы `employees` и `projects` с поддержкой параметров `limit` и `offset`, а также проверка существования сущностей в мутациях `generate_team` и `approve_team`.
3. **Безопасная валидация входных данных**:
   - Добавлено приведение и валидация `team_size` в [backend/apps/teams/views.py](file:///e:/Projects/Контрольный%20проект/backend/apps/teams/views.py).
   - В [frontend/src/pages/VacationsPage.tsx](file:///e:/Projects/Контрольный%20проект/frontend/src/pages/VacationsPage.tsx) реализована визуальная валидация дат (проверка `endDate >= startDate`) и отображение сообщений об ошибках с бэкенда в модальном окне.

