from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base

class Medidor(Base):
    __tablename__ = "medidor"
    __table_args__ = {'schema': 'public'}

    # Definición de columnas según el DDL
    id_loc = Column(String(8), nullable=True)
    deviceid = Column(String(10), primary_key=True, nullable=False)
    devicetype = Column(String(50), nullable=True)
    description = Column(String(60), nullable=True)
    connectiontype = Column(String(50), nullable=True)
    customerid = Column(String(50), nullable=True)
    usergroup = Column(String(2), nullable=True)
    ipaddress = Column(String(50), nullable=True)
    port = Column(Integer, nullable=True)
    activado = Column(DateTime, nullable=True)
    desactivado = Column(DateTime, nullable=True)
    tc_rel = Column(String(30), nullable=True)
    tp_rel = Column(String(30), nullable=True)
    ke = Column(Float, nullable=True)
    id_cen = Column(String(15), nullable=True)

    # Relación con lecturas
    lecturas = relationship("MLectura", back_populates="medidor")

class MLectura(Base):
    __tablename__ = "m_lecturas"
    __table_args__ = {'schema': 'public'}  # Esquema público explícito

    # Definición de columnas según tu tabla PostgreSQL
    fecha = Column(DateTime, primary_key=True, nullable=False)
    deviceid = Column(String(10), ForeignKey('public.medidor.deviceid'), primary_key=True, nullable=False)
    kwhd = Column(Float, nullable=False)
    kvarhd = Column(Float, nullable=False)

    # Relación con medidor
    medidor = relationship("Medidor", back_populates="lecturas")