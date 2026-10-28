CREATE DATABASE scv;
GO
USE scv;
GO
CREATE SCHEMA ventas;
GO
CREATE SCHEMA rrhh;
GO
CREATE TABLE dbo.clientes (
  id int IDENTITY PRIMARY KEY,
  nombre varchar(100) NOT NULL,
  email varchar(255) NOT NULL UNIQUE,
  NumeroDocumento varchar(20),
  FechaNacimiento date,
  saldo decimal(12,2) DEFAULT 0
);
CREATE TABLE ventas.pedidos (
  id bigint IDENTITY PRIMARY KEY,
  cliente_id int NOT NULL REFERENCES dbo.clientes(id),
  estado varchar(20) DEFAULT 'nuevo'
);
CREATE INDEX idx_ped_estado ON ventas.pedidos (cliente_id, estado);
CREATE TABLE ventas.items (
  pedido_id bigint NOT NULL, linea int NOT NULL, producto varchar(50),
  CONSTRAINT pk_items PRIMARY KEY (pedido_id, linea),
  FOREIGN KEY (pedido_id) REFERENCES ventas.pedidos(id)
);
CREATE TABLE ventas.items_hist (
  pedido_id bigint, linea int, nota nvarchar(max),
  FOREIGN KEY (pedido_id, linea) REFERENCES ventas.items(pedido_id, linea)
);
CREATE TABLE rrhh.clientes (codigo int PRIMARY KEY, salario decimal(12,2), Religion varchar(30));
CREATE TABLE rrhh.empleados (
  id int PRIMARY KEY, CorreoElectronico varchar(120),
  cliente_codigo int REFERENCES rrhh.clientes(codigo)
);
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Maestro de clientes',
  @level0type=N'SCHEMA', @level0name=N'dbo', @level1type=N'TABLE', @level1name=N'clientes';
GO
CREATE LOGIN lector WITH PASSWORD = 'Lect0r!;x=1', CHECK_POLICY = OFF;
CREATE USER lector FOR LOGIN lector;
ALTER ROLE db_datareader ADD MEMBER lector;
GO
