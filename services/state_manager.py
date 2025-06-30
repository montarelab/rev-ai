import json
from typing import Optional, Dict, Any
from loguru import logger as log
from agents.workflow import CodeReviewState


class StateManager:
    """Gets and saves review state and results to Redis"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.state_prefix = "code_review:state:"
        self.result_prefix = "code_review:result:"

    async def save_state(self, task_id: str, state: CodeReviewState):
        """Save review state to Redis"""
        try:
            state_key = f"{self.state_prefix}{task_id}"
            # Convert state to serializable format
            serializable_state = {
                k: v for k, v in state.items()
                if k != 'messages'  # Don't serialize messages
            }
            state_json = json.dumps(serializable_state, default=str)
            await self.redis.setex(state_key, 3600, state_json)  # 1 hour TTL
        except Exception as e:
            log.error(f"Failed to save state for task {task_id}: {e}")
            raise

    async def get_state(self, task_id: str) -> Optional[CodeReviewState]:
        """Get review state from Redis"""
        try:
            state_key = f"{self.state_prefix}{task_id}"
            state_json = await self.redis.get(state_key)
            if state_json:
                state_data = json.loads(state_json)
                # Add empty messages list
                state_data['messages'] = []
                return state_data
            return None
        except Exception as e:
            log.error(f"Failed to get state for task {task_id}: {e}")
            return None

    async def save_result(self, task_id: str, result: Dict[str, Any]):
        """Save final result to Redis"""
        try:
            result_key = f"{self.result_prefix}{task_id}"
            result_json = json.dumps(result, default=str)
            await self.redis.setex(result_key, 86400, result_json)  # 24 hours TTL
        except Exception as e:
            log.error(f"Failed to save result for task {task_id}: {e}")
            raise
