import json
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models.models import Account, AccountType

class RotationSystem:
    def __init__(self, db: Session):
        self.db = db

    def get_available_account(self, account_type: AccountType) -> Optional[Account]:
        account = self.db.query(Account).filter(
            Account.account_type == account_type,
            Account.is_active == True,
            Account.daily_usage_count < 5
        ).order_by(Account.last_used_at.asc()).first()
        return account

    def increment_usage(self, account_id: int):
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.daily_usage_count += 1
            account.last_used_at = datetime.utcnow()
            self.db.commit()

    def reset_daily_counts(self):
        self.db.query(Account).update({Account.daily_usage_count: 0})
        self.db.commit()
