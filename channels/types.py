from typing import Dict, Any, Union, List, NewType

ScopeType = Dict[str, Any]
MessageType = Dict[str, Any]

# JsonMappable = Union[float, int, None, str, Dict[str, 'JsonMappable'], List['JsonMappable']] is not supported yet
# Recursive types not fully supported yet, nested types replaced with "Any"
JsonMappable = Union[float, int, None, str, Dict[str, Any], List[Any]]
