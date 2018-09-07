# Matrix-Synapse-mysql-password-provider
MYSQL Password provider for matrix-synapse


### homeserver.yml:

```
password_providers:
  - module: "mysql_auth_provider.MysqlAuthProvider"
    config:
      enabled: True
      host: "10.1.0.143"
      user: "mysqluser"
      password: "ChangeMe"
      database: "mysqlserver"

```
