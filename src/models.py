from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class User(Base):
    __tablename__ = 'user'
    
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str]
    balance: Mapped[float]
    discount: Mapped[float] = mapped_column(default=0)
    
    card: Mapped[list['Card']] = relationship(back_populates='user')

class MarketCard(Base):
    __tablename__ = 'market_card'
    
    card: Mapped[str]
    price: Mapped[float]
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('category.id'))
    
    category: Mapped['Category'] = relationship(back_populates='market_cards')

class Card(Base):
    __tablename__ = 'card'
    
    card: Mapped[str]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'))
    category: Mapped[str]
    
    user: Mapped['User'] = relationship(back_populates='card')

class Category(Base):
    __tablename__ = 'category'
    
    name: Mapped[str] = mapped_column(unique=True)
    
    market_cards: Mapped[list['MarketCard']] = relationship(back_populates='category', cascade='all, delete-orphan')