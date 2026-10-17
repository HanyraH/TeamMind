"""
Management command to seed the database with demo data.
Includes 100+ employees, departments, positions, skills, projects, tasks,
vacations, preferences, and pre-computed team variants.
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, UserRole
from apps.employees.models import (
    Department, Position, Skill, Employee, EmployeeSkill,
    WorkPreference, CompatibilityPreference
)
from apps.projects.models import Project, ProjectSkillRequirement, Task, TaskAssignment
from apps.vacations.models import Vacation
from apps.teams.models import TeamRun, Team, TeamMember


class Command(BaseCommand):
    help = 'Populates the database with realistic demo data (>100 employees, projects, etc.)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))
        random.seed(42)

        # 1. Users
        self.stdout.write('Creating core users...')
        admin_user, _ = User.objects.get_or_create(
            email='admin@teammind.ru',
            defaults={
                'username': 'admin',
                'first_name': 'Александр',
                'last_name': 'Смирнов',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('AdminPassword123!')
        admin_user.save()

        pm_user, _ = User.objects.get_or_create(
            email='pm@teammind.ru',
            defaults={
                'username': 'pm_elena',
                'first_name': 'Елена',
                'last_name': 'Васильева',
                'role': UserRole.PROJECT_MANAGER,
                'is_staff': True,
            }
        )
        pm_user.set_password('ManagerPassword123!')
        pm_user.save()

        dev_user, _ = User.objects.get_or_create(
            email='dev@teammind.ru',
            defaults={
                'username': 'dev_dmitry',
                'first_name': 'Дмитрий',
                'last_name': 'Ковалев',
                'role': UserRole.EMPLOYEE,
            }
        )
        dev_user.set_password('DevPassword123!')
        dev_user.save()

        # 2. Departments
        self.stdout.write('Creating departments...')
        dept_data = [
            ('Frontend-разработка', 'Разработка клиентских веб- и desktop-интерфейсов'),
            ('Backend-разработка', 'Серверная бизнес-логика, базы данных и API'),
            ('Дизайн и UI/UX', 'Проектирование пользовательского опыта и визуальные дизайн-системы'),
            ('Тестирование и QA', 'Ручное и автоматизированное обеспечение качества'),
            ('DevOps и инфраструктура', 'CI/CD, контейнеризация, мониторинг и облачные среды'),
            ('Аналитика данных', 'BI-аналитика, сбор метрик, модели данных и отчетность'),
        ]
        departments = {}
        for name, desc in dept_data:
            dept, _ = Department.objects.get_or_create(name=name, defaults={'description': desc})
            departments[name] = dept

        # 3. Positions
        self.stdout.write('Creating positions...')
        pos_data = [
            ('Frontend-разработка', ['Junior Frontend Разработчик', 'Middle Frontend Разработчик', 'Senior Frontend Разработчик', 'Lead Frontend Разработчик']),
            ('Backend-разработка', ['Junior Python/Django Разработчик', 'Middle Python/Django Разработчик', 'Senior Python/Django Разработчик', 'Backend Архитектор']),
            ('Дизайн и UI/UX', ['Junior UI/UX Дизайнер', 'Middle Продуктовый Дизайнер', 'Senior UI/UX Дизайнер']),
            ('Тестирование и QA', ['Junior QA Инженер', 'Middle QA Automation Инженер', 'Senior QA Lead']),
            ('DevOps и инфраструктура', ['Middle DevOps Инженер', 'Senior SRE/DevOps Инженер']),
            ('Аналитика данных', ['Junior Аналитик данных', 'Middle BI Аналитик', 'Senior Data Scientist']),
        ]
        positions = {}
        for dept_name, pos_list in pos_data:
            dept = departments[dept_name]
            for pos_name in pos_list:
                pos, _ = Position.objects.get_or_create(name=pos_name, department=dept)
                positions[pos_name] = pos

        # 4. Skills
        self.stdout.write('Creating skills catalog...')
        skills_info = [
            # Technical
            ('React', Skill.SkillCategory.TECHNICAL, 'Разработка на библиотеке React и хуках'),
            ('TypeScript', Skill.SkillCategory.TECHNICAL, 'Строгая типизация JavaScript'),
            ('Vue.js', Skill.SkillCategory.TECHNICAL, 'Разработка на фреймворке Vue.js'),
            ('HTML/CSS/SCSS', Skill.SkillCategory.TECHNICAL, 'Адаптивная и семантическая верстка'),
            ('Python', Skill.SkillCategory.TECHNICAL, 'Разработка на языке Python'),
            ('Django', Skill.SkillCategory.TECHNICAL, 'Бэкенд на Django и DRF'),
            ('PostgreSQL', Skill.SkillCategory.TECHNICAL, 'Проектирование и оптимизация БД PostgreSQL'),
            ('GraphQL', Skill.SkillCategory.TECHNICAL, 'Работа с GraphQL схемами и резолверами'),
            ('Docker', Skill.SkillCategory.TECHNICAL, 'Контейнеризация и Docker Compose'),
            ('CI/CD', Skill.SkillCategory.TECHNICAL, 'Настройка пайплайнов GitHub Actions / GitLab'),
            ('Kubernetes', Skill.SkillCategory.TECHNICAL, 'Оркестрация микросервисов'),
            ('Figma', Skill.SkillCategory.TECHNICAL, 'Проектирование макетов и UI-kit'),
            ('Pytest', Skill.SkillCategory.TECHNICAL, 'Автоматизированное тестирование на Python'),
            ('Cypress / Playwright', Skill.SkillCategory.TECHNICAL, 'E2E автоматизация тестирования веб-приложений'),
            ('Pandas / NumPy', Skill.SkillCategory.TECHNICAL, 'Анализ данных и математические расчеты'),
            ('REST API Design', Skill.SkillCategory.TECHNICAL, 'Проектирование надежных контрактов API'),
            ('Linux Administration', Skill.SkillCategory.TECHNICAL, 'Администрирование серверов Linux'),
            # Soft
            ('Коммуникация', Skill.SkillCategory.SOFT, 'Эффективный обмен информацией в кросс-функциональной команде'),
            ('Менторинг', Skill.SkillCategory.SOFT, 'Обучение и поддержка младших специалистов'),
            ('Управление временем', Skill.SkillCategory.SOFT, 'Приоритизация задач и соблюдение дедлайнов'),
            ('Критическое мышление', Skill.SkillCategory.SOFT, 'Оценка рисков и поиск первопричин проблем'),
            # Management
            ('Agile / Scrum', Skill.SkillCategory.MANAGEMENT, 'Работа по спринтам и фасилитация встреч'),
            ('Оценка трудоёмкости', Skill.SkillCategory.MANAGEMENT, 'Декомпозиция и точный расчет проектных сроков'),
            # Domain
            ('FinTech', Skill.SkillCategory.DOMAIN, 'Знание специфики платежных систем и банковского ПО'),
            ('E-Commerce', Skill.SkillCategory.DOMAIN, 'Опыт создания интернет-магазинов и каталогов'),
        ]
        skills = {}
        for name, cat, desc in skills_info:
            skill, _ = Skill.objects.get_or_create(name=name, defaults={'category': cat, 'description': desc})
            skills[name] = skill

        # 5. Employees (> 100)
        self.stdout.write('Generating 105 realistic employees with profiles, skills and preferences...')
        first_names_male = ['Александр', 'Михаил', 'Максим', 'Артем', 'Даниил', 'Иван', 'Дмитрий', 'Кирилл', 'Никита', 'Андрей', 'Роман', 'Сергей', 'Алексей', 'Илья', 'Павел', 'Владислав', 'Егор', 'Тимофей']
        last_names_male = ['Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Петров', 'Соколов', 'Михайлов', 'Новиков', 'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев', 'Семенов', 'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев']
        first_names_female = ['Анастасия', 'Мария', 'Дарья', 'Анна', 'Полина', 'Виктория', 'Екатерина', 'София', 'Алиса', 'Ксения', 'Александра', 'Варвара', 'Вероника', 'Алена', 'Елизавета']
        last_names_female = ['Иванова', 'Смирнова', 'Кузнецова', 'Попова', 'Васильева', 'Петрова', 'Соколова', 'Михайлова', 'Новикова', 'Федорова', 'Морозова', 'Волкова', 'Алексеева', 'Лебедева', 'Семенова']

        all_skills_list = list(skills.values())
        all_positions_list = list(positions.values())
        created_employees = []

        # Connect dev_user to first employee
        emp_dev, created = Employee.objects.get_or_create(
            user=dev_user,
            defaults={
                'department': departments['Backend-разработка'],
                'position': positions['Senior Python/Django Разработчик'],
                'weekly_hours': 40,
                'chronotype': Employee.Chronotype.OWL,
                'preferred_work_start': '11:00',
                'preferred_work_end': '20:00',
                'preferred_meeting_start': '13:00',
                'preferred_meeting_end': '18:00',
                'work_format': Employee.WorkFormat.REMOTE,
                'bio': 'Опытный бэкенд разработчик с фокусом на high-load сервисы и Django/PostgreSQL.',
            }
        )
        created_employees.append(emp_dev)

        for i in range(1, 106):
            is_female = (i % 3 == 0)
            if is_female:
                fn = random.choice(first_names_female)
                ln = random.choice(last_names_female)
            else:
                fn = random.choice(first_names_male)
                ln = random.choice(last_names_male)

            username = f'emp_{i}_{fn.lower()}'
            email = f'{fn.lower()}.{ln.lower()}{i}@teammind.ru'

            u, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': fn,
                    'last_name': ln,
                    'role': UserRole.EMPLOYEE,
                }
            )
            u.set_password('Password123!')
            u.save()

            pos = random.choice(all_positions_list)
            dept = pos.department
            chronotype = random.choice([Employee.Chronotype.LARK, Employee.Chronotype.OWL, Employee.Chronotype.INTERMEDIATE])
            
            if chronotype == Employee.Chronotype.LARK:
                w_start, w_end = '08:00', '17:00'
                m_start, m_end = '09:00', '15:00'
            elif chronotype == Employee.Chronotype.OWL:
                w_start, w_end = '11:00', '20:00'
                m_start, m_end = '13:00', '18:00'
            else:
                w_start, w_end = '09:30', '18:30'
                m_start, m_end = '10:30', '17:30'

            hours = random.choice([40, 40, 40, 40, 30, 20])
            status = Employee.EmploymentStatus.ACTIVE if i <= 95 else random.choice([Employee.EmploymentStatus.ON_VACATION, Employee.EmploymentStatus.INACTIVE])

            emp, _ = Employee.objects.get_or_create(
                user=u,
                defaults={
                    'department': dept,
                    'position': pos,
                    'weekly_hours': hours,
                    'chronotype': chronotype,
                    'preferred_work_start': w_start,
                    'preferred_work_end': w_end,
                    'preferred_meeting_start': m_start,
                    'preferred_meeting_end': m_end,
                    'work_format': random.choice([Employee.WorkFormat.HYBRID, Employee.WorkFormat.REMOTE, Employee.WorkFormat.OFFICE]),
                    'status': status,
                    'bio': f'Специалист направления {dept.name}. Стаж {random.randint(1, 10)} лет.',
                }
            )
            created_employees.append(emp)

            # Assign 3-6 skills per employee
            assigned_skills = random.sample(all_skills_list, random.randint(3, 6))
            for s_idx, skill_obj in enumerate(assigned_skills):
                lvl = random.randint(2, 5) if 'Senior' in pos.name or 'Lead' in pos.name else random.randint(1, 4)
                EmployeeSkill.objects.get_or_create(
                    employee=emp,
                    skill=skill_obj,
                    defaults={
                        'level': lvl,
                        'years_experience': Decimal(str(round(random.uniform(0.5, 8.0), 1))),
                        'is_primary': (s_idx == 0),
                    }
                )

            # Work preferences
            WorkPreference.objects.get_or_create(
                employee=emp,
                defaults={
                    'communication_style': random.choice([
                        WorkPreference.CommunicationStyle.ASYNC,
                        WorkPreference.CommunicationStyle.SYNC,
                        WorkPreference.CommunicationStyle.MIXED
                    ]),
                    'collaboration_style': random.choice([
                        WorkPreference.CollaborationStyle.COLLABORATIVE,
                        WorkPreference.CollaborationStyle.INDEPENDENT,
                        WorkPreference.CollaborationStyle.FLEXIBLE
                    ]),
                    'preferred_team_size_min': 2,
                    'preferred_team_size_max': random.choice([5, 6, 8]),
                    'prefers_stable_teams': True,
                }
            )

        # 6. Compatibility Preferences (random pairs)
        self.stdout.write('Generating mutual compatibility ratings...')
        for _ in range(60):
            e1, e2 = random.sample(created_employees, 2)
            score = random.choice([1, 2, 2, -1, -2])  # positive or negative synergy
            reason = 'Отличный опыт совместной работы' if score > 0 else 'Конфликт рабочих стилей'
            CompatibilityPreference.objects.get_or_create(
                employee=e1,
                other_employee=e2,
                defaults={'score': score, 'note': reason}
            )

        # 7. Vacations
        self.stdout.write('Generating vacations calendar...')
        today = date.today()
        for emp in created_employees[:30]:
            # Some past, some ongoing, some upcoming
            offset_days = random.randint(-20, 60)
            duration = random.randint(7, 14)
            v_start = today + timedelta(days=offset_days)
            v_end = v_start + timedelta(days=duration)
            v_status = Vacation.VacationStatus.APPROVED if offset_days <= 14 else random.choice([
                Vacation.VacationStatus.PENDING, Vacation.VacationStatus.APPROVED
            ])
            Vacation.objects.get_or_create(
                employee=emp,
                start_date=v_start,
                end_date=v_end,
                defaults={
                    'vacation_type': random.choice([
                        Vacation.VacationType.ANNUAL,
                        Vacation.VacationType.ANNUAL,
                        Vacation.VacationType.SICK,
                        Vacation.VacationType.REMOTE,
                    ]),
                    'status': v_status,
                    'reason': 'Плановый отпуск',
                    'reviewed_by': pm_user if v_status == Vacation.VacationStatus.APPROVED else None,
                }
            )

        # 8. Projects & Tasks
        self.stdout.write('Creating projects and tasks...')
        p1 = Project.objects.create(
            name='Корпоративный портал FinTech 2.0',
            description='Масштабное обновление личного кабинета банка для юридических лиц с интеграцией 1С и налоговых сервисов.',
            status=Project.ProjectStatus.ACTIVE,
            priority=Project.Priority.HIGH,
            manager=pm_user,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=60),
            planned_hours=480,
        )

        p2 = Project.objects.create(
            name='Мобильное приложение лояльности (B2C)',
            description='Кроссплатформенное приложение для клиентов с персональными скидками и push-уведомлениями.',
            status=Project.ProjectStatus.ACTIVE,
            priority=Project.Priority.MEDIUM,
            manager=pm_user,
            start_date=today - timedelta(days=15),
            end_date=today + timedelta(days=75),
            planned_hours=360,
        )

        p3 = Project.objects.create(
            name='Интеллектуальная система аналитики загрузки',
            description='Сквозной сбор метрик производительности команд и прогнозирование рисков задержки дедлайнов.',
            status=Project.ProjectStatus.PLANNING,
            priority=Project.Priority.CRITICAL,
            manager=pm_user,
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=90),
            planned_hours=520,
        )

        p4 = Project.objects.create(
            name='Платформа микросервисов для интеграций',
            description='Перенос монолитных шлюзов на событийно-ориентированную архитектуру и Docker/K8s.',
            status=Project.ProjectStatus.PLANNING,
            priority=Project.Priority.HIGH,
            manager=pm_user,
            start_date=today + timedelta(days=14),
            end_date=today + timedelta(days=120),
            planned_hours=600,
        )

        # Skill requirements for projects
        reqs_data = [
            (p1, [('React', 3, True, 2), ('TypeScript', 3, True, 2), ('Python', 4, True, 1), ('Django', 3, True, 1), ('PostgreSQL', 3, True, 1), ('Figma', 2, False, 1)]),
            (p2, [('React', 3, True, 1), ('TypeScript', 3, True, 1), ('Figma', 3, True, 1), ('Pytest', 2, True, 1)]),
            (p3, [('Python', 4, True, 2), ('PostgreSQL', 3, True, 1), ('Pandas / NumPy', 3, True, 1), ('React', 3, True, 1), ('Docker', 3, False, 1)]),
            (p4, [('Python', 4, True, 2), ('Docker', 4, True, 1), ('Kubernetes', 3, True, 1), ('CI/CD', 3, True, 1), ('PostgreSQL', 4, True, 1)]),
        ]
        for proj, req_list in reqs_data:
            for s_name, min_l, is_m, cnt in req_list:
                ProjectSkillRequirement.objects.get_or_create(
                    project=proj,
                    skill=skills[s_name],
                    defaults={'min_level': min_l, 'is_mandatory': is_m, 'required_count': cnt}
                )

        # Tasks for P1
        task1 = Task.objects.create(
            project=p1,
            name='Архитектура и схема базы данных',
            description='Проектирование нормализованной схемы в PostgreSQL и миграций',
            status=Task.TaskStatus.DONE,
            estimated_hours=40,
        )
        task1.required_skills.add(skills['PostgreSQL'], skills['Python'])

        task2 = Task.objects.create(
            project=p1,
            name='REST API эндпоинты авторизации и профиля',
            description='JWT аутентификация, профили и роли доступа',
            status=Task.TaskStatus.IN_PROGRESS,
            estimated_hours=60,
        )
        task2.required_skills.add(skills['Django'], skills['REST API Design'])

        task3 = Task.objects.create(
            project=p1,
            name='UI-компоненты личного кабинета',
            description='Таблицы, фильтры, карточки счетов и формы заявок на React',
            status=Task.TaskStatus.IN_PROGRESS,
            estimated_hours=80,
        )
        task3.required_skills.add(skills['React'], skills['TypeScript'])

        # Task assignments (creates workload on employees)
        for emp in created_employees[:15]:
            TaskAssignment.objects.get_or_create(
                task=random.choice([task1, task2, task3]),
                employee=emp,
                defaults={'allocated_hours': random.choice([15, 20, 25, 30])}
            )

        # 9. Pre-generate a TeamRun and variants for P1 so analytics and UI show data immediately
        self.stdout.write('Generating initial team variants for Project 1...')
        run = TeamRun.objects.create(
            project=p1,
            initiated_by=pm_user,
            status=TeamRun.RunStatus.SUCCEEDED,
            started_at=timezone.now() - timedelta(minutes=5),
            finished_at=timezone.now() - timedelta(minutes=4),
        )

        team_var1 = Team.objects.create(
            run=run,
            project=p1,
            variant_name='Сбалансированный состав (Рекомендуемый)',
            total_score=Decimal('92.50'),
            skill_score=Decimal('95.00'),
            availability_score=Decimal('90.00'),
            workload_score=Decimal('88.50'),
            time_score=Decimal('94.00'),
            compatibility_score=Decimal('95.00'),
            skill_coverage_pct=Decimal('100.00'),
            explanation={
                'strengths': [
                    '100% покрытие всех обязательных и желательных навыков',
                    'Отсутствие пересечений с отпусками на весь период проекта',
                    'Высокая синергия: совпадающие предпочтения по асинхронным коммуникациям',
                    'Средняя загрузка участников не превышает 72%',
                ],
                'risks': ['Один из участников находится в другом часовом поясе (+2 часа)'],
                'recommendations': ['Назначить еженедельный синхронный статус по средам в 14:00'],
            },
            approval_status=Team.ApprovalStatus.APPROVED,
            approved_by=pm_user,
            approved_at=timezone.now() - timedelta(days=1),
        )

        team_var2 = Team.objects.create(
            run=run,
            project=p1,
            variant_name='Максимальный сеньорити и экспертиза',
            total_score=Decimal('87.20'),
            skill_score=Decimal('99.00'),
            availability_score=Decimal('85.00'),
            workload_score=Decimal('74.00'),
            time_score=Decimal('88.00'),
            compatibility_score=Decimal('90.00'),
            skill_coverage_pct=Decimal('100.00'),
            explanation={
                'strengths': [
                    'Исключительно Senior и Lead специалисты на ключевых позициях',
                    'Богатый опыт в FinTech и highload проектах',
                ],
                'risks': [
                    'Повышенная базовая загрузка ключевого бэкендера (80%)',
                    'Высокая совокупная стоимость команды',
                ],
                'recommendations': ['Разгрузить бэкенд-разработчика от поддержки других сервисов'],
            },
            approval_status=Team.ApprovalStatus.DRAFT,
        )

        team_var3 = Team.objects.create(
            run=run,
            project=p1,
            variant_name='Оптимальная доступность и минимум рисков',
            total_score=Decimal('84.80'),
            skill_score=Decimal('88.00'),
            availability_score=Decimal('100.00'),
            workload_score=Decimal('96.00'),
            time_score=Decimal('90.00'),
            compatibility_score=Decimal('80.00'),
            skill_coverage_pct=Decimal('92.00'),
            explanation={
                'strengths': [
                    'Все кандидаты имеют 100% свободное окно без текущих проектов',
                    'Полная взаимозаменяемость по frontend-стеку',
                ],
                'risks': ['Уровень владения PostgreSQL у миддла — 2 (требовался 3)'],
                'recommendations': ['Предусмотреть код-ревью архитектора на этапе проектирования схем'],
            },
            approval_status=Team.ApprovalStatus.DRAFT,
        )

        # Team members for variant 1
        for member_emp in created_employees[:5]:
            TeamMember.objects.create(
                team=team_var1,
                employee=member_emp,
                role_in_team=member_emp.position.name if member_emp.position else 'Разработчик',
                contribution_score=Decimal(str(random.randint(85, 98))),
                reason=f'Полное соответствие требованиям позиции и свободный график',
            )

        self.stdout.write(self.style.SUCCESS(
            f'Database seeded successfully!\n'
            f'- Users: 3 core (admin, pm, dev) + 105 employees\n'
            f'- Departments: {Department.objects.count()}\n'
            f'- Positions: {Position.objects.count()}\n'
            f'- Skills: {Skill.objects.count()}\n'
            f'- Employees: {Employee.objects.count()}\n'
            f'- Projects: {Project.objects.count()}\n'
            f'- Vacations: {Vacation.objects.count()}\n'
            f'- Team Variants: {Team.objects.count()}'
        ))
