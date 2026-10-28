CREATE DATABASE scv;
USE scv;
CREATE TABLE clientes (
  id int PRIMARY KEY AUTO_INCREMENT,
  email varchar(255) NOT NULL UNIQUE,
  nombre varchar(100),
  FechaNacimiento date,
  saldo decimal(12,2) DEFAULT 0
) COMMENT='Maestro de clientes';
CREATE TABLE pedidos (
  id bigint PRIMARY KEY,
  cliente_id int NOT NULL,
  estado varchar(20) DEFAULT 'nuevo',
  KEY idx_cli_estado (cliente_id, estado),
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
CREATE TABLE items (
  pedido_id bigint, linea int, producto varchar(50),
  PRIMARY KEY (pedido_id, linea),
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
CREATE TABLE items_hist (
  pedido_id bigint, linea int, nota text,
  FOREIGN KEY (pedido_id, linea) REFERENCES items(pedido_id, linea)
);
CREATE USER 'scv'@'%' IDENTIFIED BY 'x';
GRANT SELECT ON scv.* TO 'scv'@'%';
