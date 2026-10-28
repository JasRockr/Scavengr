CREATE DATABASE scv;
\c scv
CREATE SCHEMA ventas; CREATE SCHEMA rrhh;
CREATE TABLE public.clientes (
  id serial PRIMARY KEY,
  nombre varchar(100) NOT NULL,
  apellido varchar(100),
  email varchar(255) UNIQUE NOT NULL,
  telefono varchar(20),
  numero_documento varchar(20),
  "FechaNacimiento" date,
  tarjeta_credito varchar(19),
  direccion text,
  created_at timestamp without time zone DEFAULT now(),
  saldo numeric(12,2) DEFAULT 0
);
COMMENT ON TABLE public.clientes IS 'Maestro de clientes';
COMMENT ON COLUMN public.clientes.email IS 'Correo de contacto';
CREATE TABLE ventas.pedidos (
  id bigserial PRIMARY KEY,
  cliente_id int NOT NULL REFERENCES public.clientes(id),
  total double precision,
  estado varchar(20) DEFAULT 'nuevo'
);
CREATE INDEX idx_ped_lower ON ventas.pedidos (lower(estado));
CREATE TABLE ventas.items (
  pedido_id bigint, linea int, producto varchar(50), cantidad int,
  PRIMARY KEY (pedido_id, linea),
  FOREIGN KEY (pedido_id) REFERENCES ventas.pedidos(id)
);
CREATE TABLE ventas.items_hist (
  pedido_id bigint, linea int, nota text,
  FOREIGN KEY (pedido_id, linea) REFERENCES ventas.items(pedido_id, linea)
);
-- same table name in two schemas
CREATE TABLE rrhh.clientes ( codigo int PRIMARY KEY, salario numeric(12,2), "Religion" varchar(30), eps varchar(40));
CREATE TABLE rrhh.empleados ( id int PRIMARY KEY, "numeroDocumento" varchar(20), "correoElectronico" varchar(120), cliente_codigo int REFERENCES rrhh.clientes(codigo));
CREATE TABLE public.eventos (id bigint, fecha date, payload jsonb) PARTITION BY RANGE (fecha);
CREATE TABLE public.eventos_2026 PARTITION OF public.eventos FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE VIEW ventas.v_resumen AS SELECT cliente_id, sum(total) t FROM ventas.pedidos GROUP BY 1;
CREATE ROLE lector LOGIN PASSWORD 'Lect0r!;x=1';
GRANT USAGE ON SCHEMA ventas, rrhh TO lector;
GRANT SELECT ON ALL TABLES IN SCHEMA public, ventas, rrhh TO lector;
