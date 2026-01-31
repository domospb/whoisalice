# WhoIsAlice Domain Model

Domain layer for WhoIsAlice ML service - a voice assistant supporting TTS and STT operations.

## Structure

```
         User (base)
         ├── RegularUser
         └── AdminUser
              └── can moderate balances

    Transaction (abstract)
    ├── CreditTransaction  → adds credits
    └── DebitTransaction   → deducts credits
         └── linked to MLTask

         MLModel
         └── has cost_per_prediction

         MLTask
         ├── has User
         ├── has MLModel
         ├── has input_type (TEXT/AUDIO)
         ├── has output_type (TEXT/AUDIO)
         └── produces PredictionResult
              ├── valid_data
              └── invalid_data
```

## Entities

**Users** - `user.py`
- `User` (base class): manages identity and balance
- `RegularUser`: standard user
- `AdminUser`: can moderate other users' balances

**Transactions** - `transaction.py`
- `Transaction` (abstract): balance operations with polymorphic `apply()`
- `CreditTransaction`: adds credits
- `DebitTransaction`: deducts credits for ML tasks

**ML Models** - `ml_model.py`
- `MLModel`: available models with pricing

**ML Tasks** - `ml_task.py`
- `MLTask`: user prediction requests with status lifecycle
- `PredictionResult`: outcomes with valid/invalid data separation

**Enums** - `enums.py`
- `UserRole`, `TaskStatus`, `TransactionType`, `DataType`

## OOP Principles

✅ **Encapsulation** - private fields with `@property` getters
✅ **Inheritance** - User and Transaction hierarchies
✅ **Polymorphism** - `Transaction.apply()` behaves differently per subclass

## Quick Example

```python
from domain import RegularUser, CreditTransaction, MLModel, MLTask, DataType

# Create user and add balance
user = RegularUser(username="alice", email="alice@example.com", password_hash="...")
credit = CreditTransaction(amount=100.0, user=user)
credit.apply()

# Create model and task
model = MLModel(name="STT Model", description="Speech to text", cost_per_prediction=5.0)
task = MLTask(user=user, model=model, input_data=b"audio", 
              input_type=DataType.AUDIO, output_type=DataType.TEXT)

# Process task
task.start_processing()
# ... worker processes ...
task.mark_completed(result)
```

## Voice Assistant Support

Tasks support both TTS and STT via `input_type` and `output_type`:
- STT: `AUDIO` → `TEXT`
- TTS: `TEXT` → `AUDIO`
