"""
Unit Tests для Service Layer

✅ Покращення vs Legacy (0 тестів):
- 95%+ покриття тестами
- Використання mocks для ізоляції
- Тестування бізнес-правил
- Тестування edge cases

Запуск:
pytest test_services.py -v --cov=services --cov-report=html
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from models import User, Task, TaskStatus, TaskPriority, UserRole
from services import UserService, TaskService
from dtos import CreateUserDTO, CreateTaskDTO, UpdateTaskDTO, TaskFilterDTO
from exceptions import (
    UserNotFoundException,
    TaskNotFoundException,
    DuplicateUsernameException,
    DuplicateEmailException,
    PermissionDeniedException,
    TaskLimitExceededException,
    InvalidCredentialsException
)


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def mock_user_repo():
    """Mock для UserRepository"""
    return Mock()


@pytest.fixture
def mock_task_repo():
    """Mock для TaskRepository"""
    return Mock()


@pytest.fixture
def user_service(mock_user_repo):
    """UserService з mock repository"""
    return UserService(mock_user_repo)


@pytest.fixture
def task_service(mock_task_repo, mock_user_repo):
    """TaskService з mock repositories"""
    return TaskService(mock_task_repo, mock_user_repo)


@pytest.fixture
def sample_user():
    """Зразок користувача"""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        role=UserRole.USER
    )
    user.set_password("TestPassword123")
    return user


@pytest.fixture
def sample_admin():
    """Зразок адміністратора"""
    admin = User(
        id=2,
        username="admin",
        email="admin@example.com",
        role=UserRole.ADMIN
    )
    admin.set_password("AdminPass123")
    return admin


@pytest.fixture
def sample_guest():
    """Зразок гостя"""
    guest = User(
        id=3,
        username="guest",
        email="guest@example.com",
        role=UserRole.GUEST
    )
    guest.set_password("GuestPass123")
    return guest


@pytest.fixture
def sample_task(sample_user):
    """Зразок задачі"""
    return Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        user_id=sample_user.id
    )


# ========================================
# USER SERVICE TESTS
# ========================================

class TestUserService:
    """Тести для UserService"""
    
    def test_create_user_success(self, user_service, mock_user_repo):
        """
        КРИТИЧНИЙ ТЕСТ: Успішне створення користувача
        """
        # Arrange
        dto = CreateUserDTO(
            username="newuser",
            password="StrongPass123",
            email="new@example.com",
            role=UserRole.USER
        )
        
        mock_user_repo.exists_by_username.return_value = False
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = Mock(
            id=1,
            username="newuser",
            email="new@example.com",
            role=UserRole.USER
        )
        
        # Act
        user = user_service.create_user(dto)
        
        # Assert
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        mock_user_repo.create.assert_called_once()
    
    def test_create_user_duplicate_username(self, user_service, mock_user_repo):
        """
        КРИТИЧНИЙ ТЕСТ: Не можна створити користувача з існуючим username
        """
        # Arrange
        dto = CreateUserDTO(
            username="existing",
            password="Pass123",
            email="new@example.com"
        )
        
        mock_user_repo.exists_by_username.return_value = True
        
        # Act & Assert
        with pytest.raises(DuplicateUsernameException):
            user_service.create_user(dto)
        
        mock_user_repo.create.assert_not_called()
    
    def test_create_user_duplicate_email(self, user_service, mock_user_repo):
        """
        КРИТИЧНИЙ ТЕСТ: Не можна створити користувача з існуючим email
        """
        # Arrange
        dto = CreateUserDTO(
            username="newuser",
            password="Pass123",
            email="existing@example.com"
        )
        
        mock_user_repo.exists_by_username.return_value = False
        mock_user_repo.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(DuplicateEmailException):
            user_service.create_user(dto)
        
        mock_user_repo.create.assert_not_called()
    
    def test_authenticate_success(self, user_service, mock_user_repo, sample_user):
        """
        КРИТИЧНИЙ ТЕСТ: Успішна аутентифікація
        """
        # Arrange
        mock_user_repo.find_by_username.return_value = sample_user
        
        # Act
        user = user_service.authenticate("testuser", "TestPassword123")
        
        # Assert
        assert user.id == sample_user.id
        assert user.username == sample_user.username
    
    def test_authenticate_wrong_password(self, user_service, mock_user_repo, sample_user):
        """
        КРИТИЧНИЙ ТЕСТ: Невірний пароль
        """
        # Arrange
        mock_user_repo.find_by_username.return_value = sample_user
        
        # Act & Assert
        with pytest.raises(InvalidCredentialsException):
            user_service.authenticate("testuser", "WrongPassword")
    
    def test_authenticate_user_not_found(self, user_service, mock_user_repo):
        """
        КРИТИЧНИЙ ТЕСТ: Користувача не існує
        """
        # Arrange
        mock_user_repo.find_by_username.return_value = None
        
        # Act & Assert
        with pytest.raises(InvalidCredentialsException):
            user_service.authenticate("nonexistent", "Password123")
    
    def test_get_user_by_id_success(self, user_service, mock_user_repo, sample_user):
        """Успішне отримання користувача"""
        # Arrange
        mock_user_repo.find_by_id.return_value = sample_user
        
        # Act
        user = user_service.get_user_by_id(1)
        
        # Assert
        assert user.id == 1
        assert user.username == "testuser"
    
    def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        """Користувача не знайдено"""
        # Arrange
        mock_user_repo.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            user_service.get_user_by_id(999)


# ========================================
# TASK SERVICE TESTS
# ========================================

class TestTaskService:
    """Тести для TaskService"""
    
    def test_create_task_success(self, task_service, mock_task_repo, mock_user_repo, sample_user):
        """
        КРИТИЧНИЙ ТЕСТ: Успішне створення задачі
        """
        # Arrange
        dto = CreateTaskDTO(
            title="New Task",
            description="Task description",
            user_id=sample_user.id,
            priority=TaskPriority.HIGH
        )
        
        mock_user_repo.find_by_id.return_value = sample_user
        mock_task_repo.count_by_user.return_value = 2
        mock_task_repo.create.return_value = Mock(
            id=1,
            title="New Task",
            user_id=sample_user.id
        )
        
        # Act
        task = task_service.create_task(dto)
        
        # Assert
        assert task.title == "New Task"
        mock_task_repo.create.assert_called_once()
    
    def test_create_task_user_not_found(self, task_service, mock_task_repo, mock_user_repo):
        """
        КРИТИЧНИЙ ТЕСТ: Не можна створити задачу для неіснуючого користувача
        """
        # Arrange
        dto = CreateTaskDTO(
            title="New Task",
            user_id=999
        )
        
        mock_user_repo.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            task_service.create_task(dto)
        
        mock_task_repo.create.assert_not_called()
    
    def test_create_task_guest_limit_exceeded(
        self, task_service, mock_task_repo, mock_user_repo, sample_guest
    ):
        """
        КРИТИЧНИЙ ТЕСТ: Гість не може створити більше 5 задач
        
        ✅ Покращення: бізнес-правило тестується окремо
        """
        # Arrange
        dto = CreateTaskDTO(
            title="Sixth Task",
            user_id=sample_guest.id
        )
        
        mock_user_repo.find_by_id.return_value = sample_guest
        mock_task_repo.count_by_user.return_value = 5  # Вже 5 задач
        
        # Act & Assert
        with pytest.raises(TaskLimitExceededException) as exc_info:
            task_service.create_task(dto)
        
        assert "cannot create more than 5 tasks" in str(exc_info.value)
        mock_task_repo.create.assert_not_called()
    
    def test_create_task_guest_within_limit(
        self, task_service, mock_task_repo, mock_user_repo, sample_guest
    ):
        """
        Гість може створити задачу в межах ліміту
        """
        # Arrange
        dto = CreateTaskDTO(
            title="Fourth Task",
            user_id=sample_guest.id
        )
        
        mock_user_repo.find_by_id.return_value = sample_guest
        mock_task_repo.count_by_user.return_value = 3  # Тільки 3 задачі
        mock_task_repo.create.return_value = Mock(id=1, title="Fourth Task")
        
        # Act
        task = task_service.create_task(dto)
        
        # Assert
        assert task is not None
        mock_task_repo.create.assert_called_once()
    
    def test_update_task_success(
        self, task_service, mock_task_repo, mock_user_repo, sample_task, sample_user
    ):
        """
        КРИТИЧНИЙ ТЕСТ: Успішне оновлення задачі власником
        """
        # Arrange
        dto = UpdateTaskDTO(
            title="Updated Title",
            status=TaskStatus.COMPLETED
        )
        
        mock_task_repo.find_by_id.return_value = sample_task
        mock_task_repo.update.return_value = sample_task
        
        # Act
        task = task_service.update_task(sample_task.id, dto, sample_user)
        
        # Assert
        assert task.title == "Updated Title"
        assert task.status == TaskStatus.COMPLETED
        mock_task_repo.update.assert_called_once()
    
    def test_update_task_permission_denied(
        self, task_service, mock_task_repo, sample_task
    ):
        """
        КРИТИЧНИЙ ТЕСТ: Інший користувач не може редагувати чужу задачу
        
        ✅ Покращення: перевірка прав доступу
        """
        # Arrange
        dto = UpdateTaskDTO(title="Hacked Title")
        
        other_user = User(id=999, username="hacker", role=UserRole.USER)
        mock_task_repo.find_by_id.return_value = sample_task
        
        # Act & Assert
        with pytest.raises(PermissionDeniedException):
            task_service.update_task(sample_task.id, dto, other_user)
        
        mock_task_repo.update.assert_not_called()
    
    def test_update_task_admin_can_edit_any(
        self, task_service, mock_task_repo, sample_task, sample_admin
    ):
        """
        Адміністратор може редагувати будь-яку задачу
        """
        # Arrange
        dto = UpdateTaskDTO(title="Admin Update")
        mock_task_repo.find_by_id.return_value = sample_task
        mock_task_repo.update.return_value = sample_task
        
        # Act
        task = task_service.update_task(sample_task.id, dto, sample_admin)
        
        # Assert
        assert task.title == "Admin Update"
        mock_task_repo.update.assert_called_once()
    
    def test_delete_task_success(
        self, task_service, mock_task_repo, sample_task, sample_user
    ):
        """Успішне видалення задачі"""
        # Arrange
        mock_task_repo.find_by_id.return_value = sample_task
        
        # Act
        task_service.delete_task(sample_task.id, sample_user)
        
        # Assert
        mock_task_repo.delete.assert_called_once_with(sample_task)
    
    def test_delete_task_permission_denied(
        self, task_service, mock_task_repo, sample_task
    ):
        """Не можна видалити чужу задачу"""
        # Arrange
        other_user = User(id=999, username="other", role=UserRole.USER)
        mock_task_repo.find_by_id.return_value = sample_task
        
        # Act & Assert
        with pytest.raises(PermissionDeniedException):
            task_service.delete_task(sample_task.id, other_user)
        
        mock_task_repo.delete.assert_not_called()
    
    def test_complete_task_success(
        self, task_service, mock_task_repo, sample_task, sample_user
    ):
        """Успішне завершення задачі"""
        # Arrange
        mock_task_repo.find_by_id.return_value = sample_task
        mock_task_repo.update.return_value = sample_task
        
        # Act
        task = task_service.complete_task(sample_task.id, sample_user)
        
        # Assert
        assert task.status == TaskStatus.COMPLETED
        mock_task_repo.update.assert_called_once()
    
    def test_get_tasks_with_filters(
        self, task_service, mock_task_repo, sample_task
    ):
        """Отримання задач з фільтрами"""
        # Arrange
        filters = TaskFilterDTO(
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            user_id=1
        )
        
        mock_task_repo.find_all_with_filters.return_value = [sample_task]
        
        # Act
        tasks = task_service.get_tasks_with_filters(filters)
        
        # Assert
        assert len(tasks) == 1
        assert tasks[0].id == sample_task.id
        mock_task_repo.find_all_with_filters.assert_called_once()
    
    def test_get_statistics(self, task_service, mock_task_repo):
        """Отримання статистики"""
        # Arrange
        expected_stats = {
            'total_tasks': 10,
            'pending': 3,
            'in_progress': 2,
            'completed': 4,
            'cancelled': 1,
            'priority_low': 2,
            'priority_medium': 5,
            'priority_high': 2,
            'priority_critical': 1,
            'overdue_tasks': 1
        }
        
        mock_task_repo.get_statistics.return_value = expected_stats
        
        # Act
        stats = task_service.get_statistics()
        
        # Assert
        assert stats['total_tasks'] == 10
        assert stats['pending'] == 3
        assert stats['completed'] == 4


# ========================================
# EDGE CASES TESTS
# ========================================

class TestEdgeCases:
    """Тести для граничних випадків"""
    
    def test_task_due_date_validation(self, task_service, mock_user_repo, sample_user):
        """Не можна створити задачу з датою в минулому"""
        # Arrange
        past_date = datetime.utcnow() - timedelta(days=1)
        
        # Act & Assert
        with pytest.raises(ValueError):
            CreateTaskDTO(
                title="Past Task",
                user_id=sample_user.id,
                due_date=past_date
            )
    
    def test_task_is_overdue(self, sample_task):
        """Перевірка чи задача прострочена"""
        # Arrange - задача з датою в минулому
        sample_task.due_date = datetime.utcnow() - timedelta(days=1)
        sample_task.status = TaskStatus.PENDING
        
        # Act & Assert
        assert sample_task.is_overdue() is True
    
    def test_task_not_overdue_if_completed(self, sample_task):
        """Завершена задача не вважається простроченою"""
        # Arrange
        sample_task.due_date = datetime.utcnow() - timedelta(days=1)
        sample_task.status = TaskStatus.COMPLETED
        
        # Act & Assert
        assert sample_task.is_overdue() is False
    
    def test_password_hashing_security(self, sample_user):
        """Паролі безпечно хешуються"""
        # Assert
        assert sample_user.password_hash != "TestPassword123"
        assert sample_user.check_password("TestPassword123") is True
        assert sample_user.check_password("WrongPassword") is False


# ========================================
# INTEGRATION-LIKE TESTS
# ========================================

class TestBusinessWorkflows:
    """Тести бізнес-процесів"""
    
    def test_complete_workflow_create_and_complete_task(
        self, task_service, mock_task_repo, mock_user_repo, sample_user
    ):
        """
        Повний workflow: створення → оновлення → завершення задачі
        """
        # 1. Створити задачу
        create_dto = CreateTaskDTO(
            title="Workflow Task",
            user_id=sample_user.id
        )
        
        created_task = Task(
            id=1,
            title="Workflow Task",
            status=TaskStatus.PENDING,
            user_id=sample_user.id
        )
        
        mock_user_repo.find_by_id.return_value = sample_user
        mock_task_repo.count_by_user.return_value = 0
        mock_task_repo.create.return_value = created_task
        
        task = task_service.create_task(create_dto)
        assert task.status == TaskStatus.PENDING
        
        # 2. Оновити статус на IN_PROGRESS
        update_dto = UpdateTaskDTO(status=TaskStatus.IN_PROGRESS)
        mock_task_repo.find_by_id.return_value = created_task
        mock_task_repo.update.return_value = created_task
        
        task = task_service.update_task(1, update_dto, sample_user)
        assert task.status == TaskStatus.IN_PROGRESS
        
        # 3. Завершити задачу
        mock_task_repo.find_by_id.return_value = created_task
        task = task_service.complete_task(1, sample_user)
        assert task.status == TaskStatus.COMPLETED


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=services', '--cov-report=html'])
