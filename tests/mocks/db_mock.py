from typing import Any, Sequence


class MockDB:
    def __init__(self):
        self._insert_responses = {}
        self._select_responses = {}
        self._update_responses = {}
        self._delete_responses = {}
        self._call_history = []
        self._next_id = 1

    async def insert(self, query: str, query_params: dict) -> int:
        self._call_history.append({
            "method": "insert",
            "query": query,
            "params": query_params
        })

        if query in self._insert_responses:
            return self._insert_responses[query]

        # Автоинкремент ID
        result = self._next_id
        self._next_id += 1
        return result

    async def delete(self, query: str, query_params: dict) -> None:
        self._call_history.append({
            "method": "delete",
            "query": query,
            "params": query_params
        })

    async def update(self, query: str, query_params: dict) -> None:
        self._call_history.append({
            "method": "update",
            "query": query,
            "params": query_params
        })

    async def select(self, query: str, query_params: dict) -> Sequence[Any]:
        self._call_history.append({
            "method": "select",
            "query": query,
            "params": query_params
        })

        if query in self._select_responses:
            return self._select_responses[query]

        return []

    async def multi_query(self, queries: list[str]) -> None:
        self._call_history.append({
            "method": "multi_query",
            "queries": queries
        })

    def set_insert_response(self, query: str, response: int) -> None:
        self._insert_responses[query] = response

    def set_select_response(self, query: str, response: Sequence[Any]) -> None:
        self._select_responses[query] = response

    def get_call_history(self) -> list:
        return self._call_history

    def clear_call_history(self) -> None:
        self._call_history = []

    def reset_id_counter(self, start_id: int = 1) -> None:
        self._next_id = start_id
