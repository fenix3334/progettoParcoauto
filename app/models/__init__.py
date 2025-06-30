# Import dai file individuali (sistema originale)
from .veicoli import Veicolo
from .fornitori import Fornitore  
from .manutenzioni import Manutenzione
from .scadenze import Scadenza
from .users import User

__all__ = ['Veicolo', 'Fornitore', 'Manutenzione', 'Scadenza', 'User']
