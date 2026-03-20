# Credenciales

- Usuario: pro-auxes
- Password: arqui2

</br>

# Enviroment

</br>

existe el archivo [.env.example](.env.example) que es una copia de como deberia de verse el .env original para que funcione docker compose, basta con renombrar el .example como .env. Esto es necesario ya que se le deben de pasar variables de entorno a los contenedores para realizar el build y la ejecucion del codigo.

# Comandos Docker

- `docker compose build`
- `docker compose up`
- `docekr compose push`

</br>


# Etornos de Producción
En produccion se suelen dejar unicamente las imagenes a utilizar en la maquina virutal, por ejemplo en este caso el archivo [docker-compose.prod.yaml](./docker-compose.prod.yaml) unicamente tiene las imagenes importantes, se elimino el contenedor de mongo ya que la base de datos no estara en la misma instancia, incluso se mejoro el uso de variables de entorno, dejando un archivo [.env.prdo.example](.env.prod.example) en base a la actualizacion. para desplegar los contenedores en la maquina virtual basta con correr el comando `docker compose -f docker-compose.prod.yaml up` cabe resaltar que es necesiar tener las imagenes subidas a un registry en este caso docker hub, ya que este archivo .yaml no construye las imagenes, es por eso que esta pensando para produccion, por que unicamente ira a descargar las imagenes. 

el uso del .env es mas que necesario, ya que ayuda a pasar los parametros necesarios al codigo.


</br>

---

</br>

# Actualizacion 20-03-2026

Se hizo un cambio en la forma de manejar los websockets en el frontend, antes se usaba nginx como reverse proxy, pero esto limitaba el poder usar el frontend en otras instancias, por lo que se elimino el reverse proxy y ahora se le pasa la ruta del broker desde el .env por ejemplo `localhost:9001`

