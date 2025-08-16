"""
Module containing application-wide enums.

Defines fixed enum classes and values used throughout
the SLAC-LCLS-Stock-Management.
"""

from dataclasses import dataclass
from enum import Enum, auto


class Pages(Enum):
    """
    Represents all the pages in the application, each with metadata.

    Each member is an instance of _PageDetails which contains:

    - PAGE_TITLE: The human-readable title of the page.
    - FILE_NAME: The base filename for the corresponding UI view.
    - PAGE_INDEX: An integer used to track the page's position/order.
    """

    @dataclass
    class _PageDetails:
        PAGE_TITLE: str
        FILE_NAME: str
        PAGE_INDEX: int

    VIEW = _PageDetails('View', 'view', 0)
    SCAN = _PageDetails('QR Scanner', 'scanner', 1)
    ADD = _PageDetails('Add', 'add', 2)
    EDIT = _PageDetails('Edit', 'edit', 3)
    REMOVE = _PageDetails('Remove', 'remove', 4)
    GENERATE = _PageDetails('QR Generate', 'qr_generate', 5)
    LOGIN = _PageDetails('Login', 'login', 6)
    EXPORT = _PageDetails('Export', 'export', 7)
    FINISHED = _PageDetails('Finished', 'finish', 8)


class ExportTypes(Enum):
    """
    Represents supported export file types.

    Members:

    - PDF: Portable Document Format
    - CSV: Comma-Separated Values
    - TSV: Tab-Separated Values
    - PSV: Pipe-Separated Values
    """

    PDF = 'pdf'
    CSV = 'csv'
    TSV = 'tsv'
    PSV = 'psv'


class StockStatus(Enum):
    """
    Represents inventory status for an item.

    Members:

    - IN_STOCK: The item is available in sufficient quantity.
    - LOW_STOCK: The item is running low and may
    need to be reordered/restocked.
    - OUT_OF_STOCK: The item is currently unavailable.
    """

    IN_STOCK = 'In Stock'
    LOW_STOCK = 'Low Stock'
    OUT_OF_STOCK = 'Out Of Stock'


class DatabaseUpdateType(Enum):
    """
    Represents the type of database modification being made.

    Members:

    - ADD: Adding a new entry.
    - EDIT: Modifying an existing entry.
    - REMOVE: Deleting an entry.
    """

    ADD = auto()
    EDIT = auto()
    REMOVE = auto()


class Hutches(Enum):
    """Represents hutches at SLAC."""

    CXI = 'CXI (Coherent X-ray Imaging)',
    MEC = 'MEC (Matter in Extreme Conditions)',
    MFX = 'MFX (Macromolecular Femto-Second Crystallography)',
    QRIXS = 'qRIXS (Quantum Resonant Inelastic X-ray Scattering)',
    CHEMRIXS = 'chemRIXS (Chemistry Resonant Inelastic X-ray Scattering)'
    TMO = 'TMO (Time-resolved AMO)',
    TXI = 'TXI (Tender X-ray Instrument)',
    XCS = 'XCS (X-ray Correlation Spectroscopy)',
    XPP = 'XPP (X-ray Pump Probe)',
    MEV_UED = 'MeV-UED (Megaelectronvolt Ultrafast Electron Diffraction)',
    LCLS_II_HE = 'LCLS-II-HE Instruments',
    DXS = 'DXS (Dynamic X-ray Scattering)',
