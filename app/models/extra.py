from sqlmodel import Field, SQLModel


class UserAccountLink(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.uid", primary_key=True)
    account_id: int = Field(foreign_key="account.id", primary_key=True)
