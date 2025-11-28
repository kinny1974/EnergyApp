from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base

class Departamento(Base):
    __tablename__ = "departamentos"
    __table_args__ = {'schema': 'public'}

    id_dep = Column(String(2), primary_key=True, nullable=False)
    departamento = Column(String(50), nullable=True)

    # Relación con municipios
    municipios = relationship("Municipio", back_populates="departamento")

class Municipio(Base):
    __tablename__ = "municipios"
    __table_args__ = {'schema': 'public'}

    id_mun = Column(String(8), primary_key=True, nullable=False)
    id_dep = Column(String(2), ForeignKey('public.departamentos.id_dep'), nullable=False)
    municipio = Column(String(50), nullable=True)

    # Relaciones
    departamento = relationship("Departamento", back_populates="municipios")
    localidades = relationship("Localidad", back_populates="municipio")

class Localidad(Base):
    __tablename__ = "localidades"
    __table_args__ = {'schema': 'public'}

    id_loc = Column(String(12), primary_key=True, nullable=False)
    id_mun = Column(String(8), ForeignKey('public.municipios.id_mun'), nullable=False)
    localidad = Column(String(70), nullable=False)
    clas_politica = Column(String(2), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    id_empresa = Column(Integer, nullable=True)

    # Relaciones
    municipio = relationship("Municipio", back_populates="localidades")
    medidores = relationship("Medidor", back_populates="localidad")

class Medidor(Base):
    __tablename__ = "medidor"
    __table_args__ = {'schema': 'public'}

    # Definición de columnas según el DDL
    id_loc = Column(String(8), ForeignKey('public.localidades.id_loc'), nullable=True)
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

    # Relaciones
    lecturas = relationship("MLectura", back_populates="medidor")
    localidad = relationship("Localidad", back_populates="medidores")

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