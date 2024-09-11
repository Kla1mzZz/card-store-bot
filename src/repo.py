from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import async_session, engine
from models import Card, User, Base, MarketCard, Category

class Repo:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
    
    async def add_user(self, user_id: int, username: str):
        async with async_session() as session:
            user = User(user_id=user_id, username=username, balance=0)
            
            session.add(user)
            await session.commit()
    
    async def get_user(self, user_id: int):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            return user
        
    async def get_users_id(self):
        async with async_session() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars().all()
            
            return [user.user_id for user in users]
    
    async def add_cart_to_user(self, user_id: int, card: str, category: str):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            new_card = Card(user_id=user_id, card=card, category=category)
            
            user.card.append(new_card)
            
            session.add(new_card)
            await session.commit()
    
    async def user_unbalance(self, user_id, balance: float):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            user.balance -= balance
            
            await session.commit()
    
    async def add_to_user_balance(self, user_id: int, balance: float):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            user.balance += balance
            
            await session.commit()
    
    async def create_card(self, card: str, price: float, category_name: str):
        async with async_session() as session:
            category = await session.execute(select(Category).where(Category.name == category_name))
            
            category_obj = category.scalars().first()
            new_card = MarketCard(card = card, price=price, category = category_obj)
            
            session.add(new_card)
            await session.commit()
    
    async def get_card(self, card: str):
        async with async_session() as session:
            query = select(MarketCard).options(selectinload(MarketCard.category)).filter(
                MarketCard.card.like(f"{card}%")
            )
            result = await session.execute(query)
            new_card = result.scalar_one_or_none()
            
            return new_card
    
    async def get_card_in_six_digt(self, card: str):
        async with async_session() as session:
            
            six_digit_prefix = card[:6]
        
            query = select(MarketCard).options(selectinload(MarketCard.category)).filter(MarketCard.card.like(f'{six_digit_prefix}%'))
            result = await session.execute(query)
            cards = result.scalars().all()
            
            return cards
            
    async def get_cards_from_category(self, category: str):
        async with async_session() as session:
            query = select(MarketCard).filter(MarketCard.category.has(name=category))
            result = await session.execute(query)
            cards = result.scalars().all()
            
            return cards
    
    async def delete_card(self, card: str):
        async with async_session() as session:
            query = select(MarketCard).filter_by(card = card)
            result = await session.execute(query)
            market_card = result.scalar_one_or_none()
            
            await session.delete(market_card)
            await session.commit()
    
    async def add_category(self, name: str):
        async with async_session() as session:
            category = Category(name=name)
            
            session.add(category)
            await session.commit()
    
    async def get_categories(self):
        async with async_session() as session:
            query = select(Category).options(selectinload(Category.market_cards))
            result = await session.execute(query)
            categories = result.scalars().all()
            
            return categories
    
    async def get_category(self, name):
        async with async_session() as session:
            query = select(Category).options(selectinload(Category.market_cards)).filter_by(name = name)
            result = await session.execute(query)
            category = result.scalar_one_or_none()
            
            return category  

    async def delete_category(self, name: str):
        async with async_session() as session:
            query = select(Category).options(selectinload(Category.market_cards)).filter_by(name = name)
            result = await session.execute(query)
            category = result.scalar_one_or_none()
            
            await session.delete(category)
            await session.commit()
    
    async def apply_user_discount(self, user_id: int, discount: float):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            
            user.discount = discount
            
            session.add(user)
            await session.commit()
    
    async def remove_user_discount(self, user_id: int):
        async with async_session() as session:
            query = select(User).options(selectinload(User.card)).filter_by(user_id = user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            
            user.discount = 0
            
            session.add(user)
            await session.commit()