from dataclasses import dataclass

from stock_manager import Hutches


@dataclass
class ItemMaintenance:
    hutch: Hutches
    rail: str
    plc: str
    plc_terminals: list[str]
    extender: str
    extender_terminals: list[str]
    deploy_date: str
    build_version: float
    modification_count: int
    days_since_incident: int
    priority: int
    git_hash: str
    
    def formula(self):
        pass  # TODO: get formula from Amir
