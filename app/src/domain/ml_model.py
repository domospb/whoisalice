"""
ML Model domain models for the ML service.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class MLModel:
    """
    ML Model class representing an available machine learning model.

    Encapsulates model metadata and pricing logic.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost_per_prediction: float,
        model_id: Optional[UUID] = None,
        version: str = "1.0.0",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize an MLModel instance.

        Args:
            name: Model name (e.g., "Voice Recognition Model")
            description: Model description and capabilities
            cost_per_prediction: Cost in credits for one prediction
            model_id: Unique identifier (generated if not provided)
            version: Model version (default: "1.0.0")
            is_active: Whether model is available for use (default: True)
            created_at: Model creation timestamp (default: now)

        Raises:
            ValueError: If cost_per_prediction is not positive
        """
        if cost_per_prediction <= 0:
            raise ValueError("Cost per prediction must be positive")

        self._id: UUID = model_id or uuid4()
        self._name: str = name
        self._description: str = description
        self._cost_per_prediction: float = cost_per_prediction
        self._version: str = version
        self._is_active: bool = is_active
        self._created_at: datetime = created_at or datetime.utcnow()

    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get model ID."""
        return self._id

    @property
    def name(self) -> str:
        """Get model name."""
        return self._name

    @property
    def description(self) -> str:
        """Get model description."""
        return self._description

    @property
    def cost_per_prediction(self) -> float:
        """Get cost per prediction."""
        return self._cost_per_prediction

    @property
    def version(self) -> str:
        """Get model version."""
        return self._version

    @property
    def is_active(self) -> bool:
        """Get model active status."""
        return self._is_active

    @property
    def created_at(self) -> datetime:
        """Get model creation timestamp."""
        return self._created_at

    # Business logic methods
    def calculate_cost(self, num_predictions: int) -> float:
        """
        Calculate total cost for multiple predictions.

        Args:
            num_predictions: Number of predictions to calculate cost for

        Returns:
            Total cost in credits

        Raises:
            ValueError: If num_predictions is not positive
        """
        if num_predictions <= 0:
            raise ValueError("Number of predictions must be positive")
        return self._cost_per_prediction * num_predictions

    def deactivate(self) -> None:
        """Deactivate the model, making it unavailable for new predictions."""
        self._is_active = False

    def activate(self) -> None:
        """Activate the model, making it available for predictions."""
        self._is_active = True

    def __repr__(self) -> str:
        """String representation of MLModel."""
        return (
            f"MLModel(id={self._id}, name='{self._name}', "
            f"version='{self._version}', cost={self._cost_per_prediction}, "
            f"active={self._is_active})"
        )
