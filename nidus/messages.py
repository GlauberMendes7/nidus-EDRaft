from dataclasses import dataclass
from typing import List, Union, Dict

from nidus.state import RaftState


@dataclass
class ClientRequest:
    sender: str
    command: str
    msg_type: str = "client_request"


@dataclass
class ClientResponse:
    result: str
    msg_type: str = "client_response"


@dataclass
class AppendEntriesRequest:
    sender: str
    term: int
    prev_index: int
    prev_term: int
    entries: List[List[Union[int, str]]]
    commit_index: int
    msg_type: str = "append_entries_request"

    @classmethod
    def from_raft_state(cls, sender, to, raft_state):
        next_index = raft_state.next_index[to]
        term = raft_state.current_term
        prev_index = next_index - 1

        if prev_index >= 0:
            prev_term = raft_state.log[prev_index].term
        else:
            prev_term = -1

        if len(raft_state.log) - 1 >= next_index:
            entries = raft_state.log[next_index:]
            entries = [[e.term, e.item] for e in entries]
        else:
            entries = []

        commit_index = raft_state.commit_index
        return cls(sender, term, prev_index, prev_term, entries, commit_index)


@dataclass
class AppendEntriesResponse:
    sender: str
    term: int
    success: bool
    match_index: int
    life_time : int
    msg_type: str = "append_entries_response"



@dataclass
class VoteRequest:
    term: int
    candidate: str
    last_log_index: int
    last_log_term: int
    life_time : int
    msg_type: str = "vote_request"
    



@dataclass
class VoteResponse:
    sender: str
    term: int
    vote_granted: bool
    life_time: int
    msg_type: str = "vote_response"
    cause: str = "Requirements problem"


@dataclass
class HeartbeatRequest:
    empty: bool = False
    msg_type: str = "heartbeat_request"
    heartbeat_decrease: bool = False

@dataclass
class HeartbeatUpdate:
    mode:bool = False
    msg_type: str = "heartbeat_update"
    

@dataclass
class ElectionRequest:
    msg_type: str = "election_request"
    

@dataclass
class ProxyRequest:
    candidate: str
    life_time: int
    msg_type: str = "proxy_request"

@dataclass
class ProxyResponse:
    sender: str
    candidate: str
    life_time: int
    msg_type: str = "proxy_response"

@dataclass
class ProxyElectionResponse:
    candidate: str
    msg_type: str = "proxy_election_response"
    
@dataclass
class ProxyElectionRequest:
    sender: str
    state: list
    msg_type: str = "proxy_election_request"


message_classes = [
    ClientRequest,
    ClientResponse,
    AppendEntriesRequest,
    AppendEntriesResponse,
    VoteRequest,
    VoteResponse,
    HeartbeatRequest,
    HeartbeatUpdate,
    ElectionRequest,
    ProxyRequest,
    ProxyResponse,
    
    ProxyElectionRequest,
    ProxyElectionResponse,
]


def snakecase_to_camelcase(snake_case):
    parts = snake_case.lower().split("_")
    return "".join(map(str.capitalize, parts))


def message_from_payload(payload):
    msg_type = snakecase_to_camelcase(payload["msg_type"])

    for msg_cls in message_classes:
        if msg_cls.__name__ == msg_type:
            return msg_cls(**payload)
