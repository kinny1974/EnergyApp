from abc import ABC, abstractmethod
from typing import Any, List
from datetime import datetime

# Interfaz Observador
class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Any):
        pass

# Observador 1: Logger de Auditoría
class AuditLoggerObserver(Observer):
    def update(self, event_type: str, data: Any):
        dev = data.get('device_id', 'unknown')
        status = data.get('analysis', {}).get('estado_general', 'N/A')
        print(f"[AUDIT] {datetime.now()} | Event: {event_type} | Device: {dev} | Status: {status}")

# Observador 2: Sistema de Alertas Críticas
class CriticalAlertObserver(Observer):
    def update(self, event_type: str, data: Any):
        analysis = data.get('analysis', {})
        if analysis.get('estado_general') == 'CRITICO':
            anomalias = len(analysis.get('anomalias', []))
            print(f"🚨 [ALERTA MAIL] Enviando aviso a administrador... {anomalias} anomalías en {data.get('device_id')}")

# Clase Sujeto (Observable)
class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, event_type: str, data: Any):
        for observer in self._observers:
            observer.update(event_type, data)