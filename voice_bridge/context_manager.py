from collections import deque
from datetime import datetime
from typing import List, Dict, Optional

class ContextManager:
    def __init__(self, max_messages: int = 20, max_length: int = 1000):
        self.max_messages = max_messages
        self.max_length = max_length
        self.messages: deque = deque(maxlen=max_messages)
        self.session_start = datetime.now()
    
    def add_message(self, role: str, content: str) -> None:
        if len(content) > self.max_length:
            content = content[:self.max_length] + "..."
        
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context(self) -> List[Dict[str, str]]:
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    
    def get_recent_context(self, n: int = 5) -> List[Dict[str, str]]:
        recent = list(self.messages)[-n:]
        return [{"role": msg["role"], "content": msg["content"]} for msg in recent]
    
    def clear(self) -> None:
        self.messages.clear()
        self.session_start = datetime.now()
    
    def get_session_duration(self) -> float:
        return (datetime.now() - self.session_start).total_seconds()
    
    def get_summary(self) -> Dict[str, any]:
        return {
            "message_count": len(self.messages),
            "session_duration": self.get_session_duration(),
            "oldest_message": self.messages[0]["timestamp"] if self.messages else None,
            "newest_message": self.messages[-1]["timestamp"] if self.messages else None
        }