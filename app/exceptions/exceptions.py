class PaymentProcessingError(Exception):
    def __init__(self, message: str = "Payment processing failed"):
        self.message = message
        super().__init__(self.message)

class DuplicateTransactionError(PaymentProcessingError):
    def __init__(self):
        super().__init__("Transaction ID already exists")

class AccountNotFoundError(PaymentProcessingError):
    def __init__(self):
        super().__init__("Account not found or doesn't belong to user")