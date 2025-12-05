from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from server.database import Base
import datetime

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String(50), primary_key=True)
    hostname = Column(String(100))
    username = Column(String(100))
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    
    commands = relationship('Command', backref='agent', lazy=True)

    def __repr__(self):
        return f'<Agent {self.id}>'

class Command(Base):
    __tablename__ = 'commands'
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=False)
    command = Column(Text, nullable=False)
    output = Column(Text)
    status = Column(String(20), default='pending') 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    executed_at = Column(DateTime)

    def __repr__(self):
        return f'<Command {self.id} for {self.agent_id}>'
