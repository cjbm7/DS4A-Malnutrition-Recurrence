# DS4A-Malnutricion-Recurrence
DS4A Team 12 - Cohorte 5.


Clonar el repositorio https://github.com/cjbm7/DS4A-Malnutricion-Recurrence.git
Crear entorno virtual de python dentro de la carpeta y activarlo
Instalar las dependencias 'requirements.txt'

Correr con 'flask run' 
Ir al navegador con la dirección local http://localhost:5000/ ó http://127.0.0.1:5000/

Para terminar, CTRL + C



** PENDIENTES **

PAGINA DE INICIO:
- ~~Landing page con información descriptiva del proyecto~~
- ~~Perfiles de participantes~~
- Enlaces a las vistas más importantes

DASH
- ~~scatterplot: mejorar los controles, hacer contenido responsive~~
- heat maps: cambiar nombre de variables 
- box plots: poner colores
- incluir las gráficas restantes 
- ~~actualizar origen de datos (acrchivos nuevos .parquet)~~
/dash/scatter
/dash/maps
/dash/boxplots

REGIONAL(nombre sujeto a cambio)
- ~~Hacer grafica dinámica, callbacks por URL,~~
- Definir las métricas a mostrar en la vista
- ~~Generar Json con datos de individuos para el datatable~~
- Generar la grafica de seguimiento nutricional en un modal

PREDICTOR
- Modificar la función del predictor (utils.py)
- ~~Iniciar con una tarjeta que contenga una explicacion de como subir el CSV, manejar el predictor, incluir plantilla para descargar y modelo de archivo. Esconder datatable cuando no se ha hecho una predicción.~~
- ~~Al obtener resultados del predictor, esconder la explicación y mostrar el datatable.~~

SEGUIMIENTO NUTRICIONAL
- ~~Ajustar las llaves del diccionario con los nombres de la columnas del nuevo dataset(join de tomas_500)~~
- ~~información de la predicción al pie del documento (no dispnible actualmente)~~(parcial)
- Generar la gráfica de seguimiento e integrar a la vista con iFrame
- ~~hora de generación del documento (debajo de NIUP)~~

MISC
- ~~Poner los datos(.db y .parquet) en una sola carpeta, puede ser data en la raíz del proyecto, hacer los respectivos cambios en el código~~

API (futuro)
- Crear funcion que reciba datos en formato JSON, convertirlo en DF, validarlos y procesarlos en la funcion utils.py
- Generar respuesta en JSON
- Generar una vista de tipo SWAGGER para la API
- Documentación de uso
