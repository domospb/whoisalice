"""
ML Task and Prediction Result domain models for the ML service.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from .enums import DataType, TaskStatus
from .ml_model import MLModel
from .user import User


class PredictionResult:
    """
    Prediction result containing validated and invalid data with predictions.

    Stores the outcome of ML task processing, including data validation results.
    """

    def __init__(
        self,
        prediction_data: Dict[str, Any],
        valid_data: List[Dict[str, Any]],
        invalid_data: List[Dict[str, Any]],
        result_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a PredictionResult instance.

        Args:
            prediction_data: The actual prediction results
            valid_data: List of valid input records that were processed
            invalid_data: List of invalid input records with error details
            result_id: Unique identifier (generated if not provided)
            created_at: Result creation timestamp (default: now)
        """
        self._id: UUID = result_id or uuid4()
        self._prediction_data: Dict[str, Any] = prediction_data
        self._valid_data: List[Dict[str, Any]] = valid_data
        self._invalid_data: List[Dict[str, Any]] = invalid_data
        self._created_at: datetime = created_at or datetime.utcnow()

    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get result ID."""
        return self._id

    @property
    def prediction_data(self) -> Dict[str, Any]:
        """Get prediction data."""
        return self._prediction_data

    @property
    def valid_data(self) -> List[Dict[str, Any]]:
        """Get valid input data."""
        return self._valid_data

    @property
    def invalid_data(self) -> List[Dict[str, Any]]:
        """Get invalid input data."""
        return self._invalid_data

    @property
    def created_at(self) -> datetime:
        """Get result creation timestamp."""
        return self._created_at

    @property
    def has_invalid_data(self) -> bool:
        """Check if there is any invalid data."""
        return len(self._invalid_data) > 0

    @property
    def valid_count(self) -> int:
        """Get count of valid records."""
        return len(self._valid_data)

    @property
    def invalid_count(self) -> int:
        """Get count of invalid records."""
        return len(self._invalid_data)

    def __repr__(self) -> str:
        """String representation of PredictionResult."""
        return (
            f"PredictionResult(id={self._id}, "
            f"valid={self.valid_count}, invalid={self.invalid_count})"
        )


class MLTask:
    """
    ML Task representing a user's prediction request.

    Manages the lifecycle of an ML prediction task from submission to completion.
    """

    def __init__(
        self,
        user: User,
        model: MLModel,
        input_data: Any,
        input_type: DataType,
        output_type: DataType,
        task_id: Optional[UUID] = None,
        status: TaskStatus = TaskStatus.PENDING,
        result: Optional[PredictionResult] = None,
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """
        Initialize an MLTask instance.

        Args:
            user: User who created the task
            model: ML model to use for prediction
            input_data: Input data for prediction (text or audio)
            input_type: Type of input data (TEXT or AUDIO)
            output_type: Type of output data (TEXT or AUDIO)
            task_id: Unique identifier (generated if not provided)
            status: Current task status (default: PENDING)
            result: Prediction result (set when completed)
            error_message: Error message if task failed
            created_at: Task creation timestamp (default: now)
            completed_at: Task completion timestamp

        Raises:
            ValueError: If model is not active or user cannot afford the cost
        """
        if not model.is_active:
            raise ValueError("Cannot create task with inactive model")

        if not user.can_afford(model.cost_per_prediction):
            raise ValueError("Insufficient balance for this prediction")

        self._id: UUID = task_id or uuid4()
        self._user: User = user
        self._model: MLModel = model
        self._input_data: Any = input_data
        self._input_type: DataType = input_type
        self._output_type: DataType = output_type
        self._status: TaskStatus = status
        self._result: Optional[PredictionResult] = result
        self._error_message: Optional[str] = error_message
        self._created_at: datetime = created_at or datetime.utcnow()
        self._completed_at: Optional[datetime] = completed_at

    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get task ID."""
        return self._id

    @property
    def user(self) -> User:
        """Get associated user."""
        return self._user

    @property
    def user_id(self) -> UUID:
        """Get associated user's ID."""
        return self._user.id

    @property
    def model(self) -> MLModel:
        """Get associated ML model."""
        return self._model

    @property
    def model_id(self) -> UUID:
        """Get associated model's ID."""
        return self._model.id

    @property
    def input_data(self) -> Any:
        """Get input data."""
        return self._input_data

    @property
    def input_type(self) -> DataType:
        """Get input data type."""
        return self._input_type

    @property
    def output_type(self) -> DataType:
        """Get output data type."""
        return self._output_type

    @property
    def status(self) -> TaskStatus:
        """Get current task status."""
        return self._status

    @property
    def result(self) -> Optional[PredictionResult]:
        """Get prediction result."""
        return self._result

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if task failed."""
        return self._error_message

    @property
    def created_at(self) -> datetime:
        """Get task creation timestamp."""
        return self._created_at

    @property
    def completed_at(self) -> Optional[datetime]:
        """Get task completion timestamp."""
        return self._completed_at

    @property
    def cost(self) -> float:
        """Get task cost."""
        return self._model.cost_per_prediction

    # Status management methods
    def start_processing(self) -> None:
        """
        Mark task as processing.

        Raises:
            ValueError: If task is not in PENDING status
        """
        if self._status != TaskStatus.PENDING:
            raise ValueError("Can only start processing pending tasks")
        self._status = TaskStatus.PROCESSING

    def mark_completed(self, result: PredictionResult) -> None:
        """
        Mark task as completed with result.

        Args:
            result: Prediction result

        Raises:
            ValueError: If task is not in PROCESSING status
        """
        if self._status != TaskStatus.PROCESSING:
            raise ValueError("Can only complete processing tasks")
        self._status = TaskStatus.COMPLETED
        self._result = result
        self._completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        """
        Mark task as failed with error message.

        Args:
            error_message: Description of the failure

        Raises:
            ValueError: If task is not in PENDING or PROCESSING status
        """
        if self._status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            raise ValueError("Can only fail pending or processing tasks")
        self._status = TaskStatus.FAILED
        self._error_message = error_message
        self._completed_at = datetime.utcnow()

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self._status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if task failed."""
        return self._status == TaskStatus.FAILED

    def __repr__(self) -> str:
        """String representation of MLTask."""
        return (
            f"MLTask(id={self._id}, user_id={self.user_id}, "
            f"model='{self._model.name}', status={self._status.value}, "
            f"input={self._input_type.value}, output={self._output_type.value})"
        )
