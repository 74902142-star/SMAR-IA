# Estado del Arte - Artículo 4: sFlow and Adaptive Polling Sampling for Deep Learning Based DDoS Detection in SDN

**Autor(es):** Raja Majid Ali Ujjan, Zeeshan Pervez, Keshav Dahal, Ali Kashif Bashir, Rao Mumtaz, J. Gonzalez  
**Título:** Towards sFlow and adaptive polling sampling for deep learning based DDoS detection in SDN  
**Journal:** Future Generation Computer Systems  
**Año:** 2020  

---

## Estado del Arte

En la introducción de su artículo, los autores contextualizan el problema de los ataques DDoS en el contexto del Internet de las Cosas (IoT), señalando que el crecimiento exponencial de dispositivos IoT conectados ha creado un vasto superficie de ataque. Mencionan que muchos de estos dispositivos no utilizan protocolos de comunicación seguros ni medidas de seguridad apropiadas, lo que los convierte en blancos fáciles para atacantes que buscan difundir intrusiones o interrupciones del servicio, como los ataques DDoS. Los autores citan estudios que predicen que decenas de miles de millones de dispositivos vulnerables estarán conectados a IoT, y que los ataques DDoS pueden amenazar directamente la seguridad de la vida humana, como en el caso de dispositivos médicos conectados o infraestructuras críticas. También mencionan el ataque DDoS de 2016, el más grande registrado, que fue causado por acceso remoto no autorizado a dispositivos IoT y debilidades de seguridad, permitiendo a los atacantes instalar Botnets en varios nodos.

Los autores revisan la literatura existente sobre sistemas de detección de intrusiones (IDS) en redes tradicionales y en SDN. Señalan que en redes grandes, los IDS son ampliamente desplegados para proporcionar salvaguarda contra amenazas, pero que estos sistemas enfrentan desafíos debido al crecimiento exponencial del tráfico de red, lo que dificulta seleccionar un punto de despliegue apropiado y limita los recursos de hardware. Citan el estudio de Shah et al. (2018) que muestra que Snort como herramienta independiente alcanza una caída de paquetes del 9.5% en redes de 4 Gbps y del 20% en redes de 10 Gbps. Para optimizar estas pérdidas, mencionan trabajos previos que proponen enfoques basados en muestreo en SDN (Ho et al., 2016) y sistemas de detección DDoS basados en deep learning en SDN.

Los autores también revisan trabajos que utilizan técnicas de muestreo basadas en el tamaño del flujo (Giotis et al., 2014), estadísticas de desviación del tráfico y muestreo de anomalías. Destacan que los enfoques basados en muestreo pueden aumentar los falsos positivos y reducir la capacidad de detección de los IDS, como se demuestra en trabajos que aplican tres algoritmos diferentes de detección de intrusiones a tráfico muestreado y original. También mencionan enfoques de coincidencia de patrones para mejorar el rendimiento de Snort IDS, centrados en reducir alarmas falsas positivas. Sin embargo, critican que la mayoría de los trabajos propuestos utilizan conjuntos de datos irreales y redundantes, y se centran principalmente en la capa de control de SDN, lo que lleva a baja precisión de detección y mayor consumo de recursos.

Finalmente, los autores identifican la necesidad de abordar estos problemas proponiendo una solución novedosa que utiliza muestreo basado en sFlow y adaptive polling en el plano de datos para gestionar flujos de tráfico pesados, reducir la carga de la red y permitir que el IDS registre actividades maliciosas de manera efectiva, combinado con un modelo de deep learning (Stacked Autoencoders) en el plano de control para optimizar la precisión de detección.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Conjuntos de datos irreales**: Los enfoques de detección DDoS en SDN existentes utilizan conjuntos de datos irreales y redundantes, lo que no refleja las condiciones reales de la red y conduce a resultados poco fiables.
- **Enfoque exclusivo en la capa de control**: La mayoría de estos trabajos se centran únicamente en la capa de control de SDN, ignorando la importancia del plano de datos para la detección temprana.
- **Limitaciones de los IDS tradicionales**: Los sistemas IDS tradicionales no son una solución factible para la monitorización en tiempo real debido al crecimiento exponencial del tráfico de red, lo que dificulta seleccionar un punto de despliegue apropiado y limita los recursos de hardware. Citan que Snort como herramienta independiente tiene una caída de paquetes significativa (9.5% a 4 Gbps y 20% a 10 Gbps).
- **Limitaciones de los enfoques de muestreo existentes**: Los enfoques de muestreo actuales pueden aumentar los falsos positivos y reducir la capacidad de detección de los IDS. Resultan en baja precisión, mayor consumo de memoria, mayor sobrecarga en procesamiento y red, y baja detección de ataques.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen una solución que utiliza muestreo basado en sFlow y adaptive polling en el plano de datos para reducir la sobrecarga, combinado con Snort IDS y un modelo de deep learning (Stacked Autoencoders) en el plano de control para mejorar la precisión de detección. Su objetivo es lograr una mayor precisión de detección con menor sobrecarga de recursos, proporcionando una comparación entre ambos enfoques de muestreo.

---

## Descripción del Aporte

El aporte principal de los autores es un sistema de detección de ataques DDoS en redes IoT basado en SDN que combina técnicas de muestreo en el plano de datos con un modelo de deep learning en el plano de control. El problema que abordan es crítico: los ataques DDoS en IoT pueden paralizar servicios esenciales, afectando a sectores financieros, de medios sociales, de entretenimiento, médicos, de ingeniería y de infraestructura crítica, provocando pérdidas reputacionales y económicas significativas.

El sistema propuesto se compone de varios módulos:

### 1. Muestreo en el plano de datos:
Los autores implementan dos enfoques de muestreo en los switches del plano de datos para reducir la sobrecarga de procesamiento y red:
- **sFlow (muestreo basado en paquetes)**: Un estándar de monitorización de red que muestrea paquetes de forma aleatoria y envía las muestras a un colector para su análisis.
- **Adaptive polling (muestreo basado en tiempo)**: Un enfoque de sondeo adaptativo que ajusta la frecuencia de muestreo en función de las condiciones de la red.

### 2. Snort IDS en el plano de control:
Los autores despliegan Snort como sistema de detección de intrusiones en red (NIDS) dentro del controlador Ryu SDN. Snort analiza el tráfico muestreado y genera alertas basadas en firmas de ataques conocidos. Para gestionar los datos de manera eficiente, utilizan Barnyard2 para crear una base de datos que almacena los conjuntos de datos.

### 3. Stacked Autoencoders (SAE):
Los autores utilizan un modelo de deep learning basado en Autoencoders apilados (SAE) para clasificar el tráfico en benigno y malicioso. Los Autoencoders son redes neuronales no supervisadas que aprenden a reconstruir sus entradas, y al apilarlos, pueden aprender representaciones jerárquicas de los datos. El SAE se entrena con los datos recolectados por Snort para mejorar la precisión de detección.

### 4. Colectores de datos:
Utilizan sFlow-RT y Ntopng como colectores para sFlow y adaptive polling respectivamente, que recopilan las muestras de tráfico y las envían al controlador para su análisis.

El impacto en la empresa y la sociedad es significativo: el sistema permite detectar ataques DDoS en tiempo real en redes IoT, protegiendo servicios críticos y evitando interrupciones. La combinación de muestreo en el plano de datos reduce la sobrecarga de procesamiento, permitiendo que el IDS y el modelo de deep learning operen de manera eficiente incluso con grandes volúmenes de tráfico. El sistema es evaluado con tráfico de red en tiempo real, lo que proporciona resultados más realistas que los enfoques basados en conjuntos de datos sintéticos.

Los autores demuestran que el enfoque basado en sFlow (muestreo por paquetes) logra una mayor precisión de detección que el adaptive polling (muestreo por tiempo), con una tasa de verdaderos positivos del 95% y una tasa de falsos positivos inferior al 4%. Además, el sistema reduce significativamente la sobrecarga de CPU y red en comparación con los enfoques tradicionales, utilizando el 50% de CPU con una tasa de propagación de 340 KB/s hacia la unidad de detección del controlador.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que combina técnicas de muestreo, sistemas de detección de intrusiones y deep learning. El proceso se desarrolla en las siguientes etapas:

1. **Definición del problema y objetivos**: Identifican los desafíos de detectar ataques DDoS en redes IoT debido al gran volumen de tráfico, la limitación de recursos y la baja precisión de los enfoques existentes. Establecen como objetivos: (a) reducir la sobrecarga de procesamiento y red mediante muestreo en el plano de datos, (b) mejorar la precisión de detección mediante la combinación de Snort IDS y deep learning, y (c) comparar dos enfoques de muestreo (sFlow y adaptive polling).

2. **Selección de herramientas y tecnologías**: Eligen herramientas de código abierto para su implementación: Ryu como controlador SDN, Mininet para emular la topología de red, Snort como IDS, Barnyard2 para la gestión de bases de datos, sFlow-RT y Ntopng como colectores de muestreo, y TensorFlow 1.4 para implementar el modelo de deep learning.

3. **Implementación del muestreo en el plano de datos**: Despliegan dos enfoques de muestreo en los switches del plano de datos:
   - **sFlow**: Muestreo basado en paquetes que selecciona aleatoriamente un subconjunto de paquetes para su análisis.
   - **Adaptive polling**: Muestreo basado en tiempo que ajusta la frecuencia de sondeo en función de las condiciones de la red.

4. **Recolección de datos con Snort IDS**: Recolectan tráfico de red en tiempo real utilizando Snort en modo de coincidencia de firmas (Snort SM1-mode). Los datos se almacenan en una base de datos mediante Barnyard2, separando el tráfico benigno del malicioso.

5. **Entrenamiento del modelo Stacked Autoencoders**: Utilizan los datos recolectados para entrenar un modelo de deep learning basado en Autoencoders apilados (SAE). El SAE se entrena de manera no supervisada para aprender representaciones jerárquicas de los datos, lo que permite clasificar el tráfico en benigno y malicioso con alta precisión.

6. **Evaluación y comparación**: Evalúan el rendimiento de ambos enfoques de muestreo utilizando métricas como la tasa de verdaderos positivos (TPR), la tasa de falsos positivos (FPR), la sobrecarga de CPU y la tasa de propagación de paquetes. Comparan los resultados de sFlow y adaptive polling para determinar cuál ofrece mejores resultados.

7. **Análisis de resultados**: Analizan los resultados cuantitativamente, investigando el equilibrio entre la precisión de detección de ataques y la sobrecarga de recursos. Concluyen que el enfoque basado en sFlow supera al adaptive polling en precisión, con una TPR del 95% y una FPR inferior al 4%.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de su sistema propuesto para resolver el problema de detección de ataques DDoS en redes IoT basadas en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan Mininet para emular una topología de red IoT con múltiples nodos. Utilizan el controlador Ryu SDN y despliegan los switches OpenFlow. La configuración incluye la instalación de los colectores sFlow-RT y Ntopng para la recolección de muestras, y la implementación de Snort IDS con Barnyard2 para la creación de bases de datos.

2. **Adquisición de datos en tiempo real**: Recolectan datos de tráfico de red en tiempo real utilizando dos enfoques de muestreo de manera individual:
   - **Muestreo sFlow**: Basado en paquetes, donde se seleccionan aleatoriamente paquetes para su análisis.
   - **Muestreo adaptive polling**: Basado en tiempo, donde se ajusta la frecuencia de sondeo.
   Ambos enfoques se implementan en el plano de datos, y los datos recolectados se envían a Snort IDS para su análisis.

3. **Detección con Snort IDS**: Snort opera en modo de coincidencia de firmas (SM1-mode) para identificar patrones de ataques DDoS conocidos. Las alertas generadas por Snort se almacenan en una base de datos mediante Barnyard2, creando un conjunto de datos etiquetado que distingue entre tráfico benigno y malicioso.

4. **Clasificación con Stacked Autoencoders**: Utilizan el modelo SAE para clasificar el tráfico. El SAE se entrena con los datos recolectados y se evalúa su capacidad para distinguir correctamente entre tráfico benigno y malicioso. Utilizan una matriz de confusión para evaluar el rendimiento del modelo.

5. **Medición de métricas de rendimiento**: Durante los experimentos, registran múltiples métricas:
   - **Tasa de verdaderos positivos (TPR)**: Proporción de ataques detectados correctamente.
   - **Tasa de falsos positivos (FPR)**: Proporción de tráfico benigno clasificado erróneamente como ataque.
   - **Tasa de falsos negativos (FNR)**: Proporción de ataques no detectados (capture-failure rate).
   - **Sobrecarga de CPU**: Consumo de CPU del sistema durante la detección.
   - **Tasa de propagación de paquetes**: Velocidad de transmisión de paquetes hacia la unidad de detección del controlador.

6. **Comparación entre enfoques de muestreo**: Comparan el rendimiento de sFlow y adaptive polling para determinar cuál ofrece mejores resultados en términos de precisión y sobrecarga de recursos.

7. **Análisis de resultados**: Analizan los resultados de las métricas y concluyen que el enfoque basado en sFlow (muestreo por paquetes) supera al adaptive polling (muestreo por tiempo) en precisión de detección, logrando una TPR del 95% y una FPR inferior al 4%. También demuestran que sFlow utiliza el 50% de CPU con una tasa de propagación de 340 KB/s, lo que representa una mejora significativa en eficiencia.

8. **Evaluación de la captura-fallos**: Se centran en la tasa de captura-fallos (FNR) como una métrica crítica para los IDS, representando cuando el sistema no logra clasificar ataques que han ocurrido. Su modelo está diseñado para mejorar esta tasa y proporcionar una comparación entre los enfoques de muestreo.

---

## Métricas y Resultados

Los autores utilizan métricas estándar de rendimiento para sistemas de detección de DDoS, incluyendo la tasa de verdaderos positivos (TPR), la tasa de falsos positivos (FPR), la tasa de falsos negativos (FNR) o tasa de captura-fallos, y métricas de sobrecarga de recursos como el consumo de CPU y la tasa de propagación de paquetes.

### Resultados obtenidos:

| Métrica | Valor (sFlow) |
|---|---|
| Tasa de verdaderos positivos (TPR) | 95% |
| Tasa de falsos positivos (FPR) | <4% |
| Consumo de CPU | 50% |
| Tasa de propagación de paquetes | 340 KB/s |

### Comparación entre enfoques:
- **sFlow**: Supera a adaptive polling en precisión de detección.
- **Adaptive polling**: Menor precisión que sFlow.

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de detección: precisión y eficiencia. La inclusión del consumo de CPU y la tasa de propagación de paquetes es especialmente relevante para evaluar la viabilidad del sistema en entornos con recursos limitados, como las redes IoT. La comparación entre sFlow y adaptive polling es un valor añadido, ya que proporciona información práctica para los administradores de red sobre qué enfoque de muestreo elegir.

Sin embargo, creo que sería interesante incluir métricas adicionales como el tiempo de detección (latencia) y la escalabilidad del sistema a medida que aumenta el número de nodos IoT. También sería valioso comparar el rendimiento del modelo SAE con otros clasificadores de deep learning (como redes neuronales convolucionales o LSTM) para justificar la elección de los Autoencoders. A pesar de estas consideraciones, los resultados son sólidos y demuestran una mejora significativa sobre los enfoques tradicionales, especialmente en términos de reducción de falsos positivos y sobrecarga de recursos.

---

## Observaciones Críticas

El artículo presenta una solución innovadora para la detección de DDoS en redes IoT utilizando SDN y deep learning con muestreo en el plano de datos. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Generalización de los resultados**: Los autores utilizan un entorno de emulación con Mininet, que si bien es ampliamente aceptado en la investigación, no refleja completamente las condiciones de una red IoT real con dispositivos heterogéneos y restricciones de recursos. Sería interesante validar el sistema en un entorno real con dispositivos IoT físicos para confirmar su eficacia.

2. **Comparación con otros clasificadores**: Los autores utilizan Stacked Autoencoders, pero no comparan su rendimiento con otros modelos de deep learning como redes neuronales convolucionales (CNN), LSTM o incluso algoritmos de machine learning tradicionales como Random Forest o SVM. Esta comparación ayudaría a justificar la elección de SAE.

3. **Ataques de baja tasa**: El sistema se evalúa con ataques DDoS de alto volumen, pero no se menciona su capacidad para detectar ataques de baja tasa (low-rate DDoS) que están diseñados para evadir la detección basada en umbrales y muestreo.

4. **Mitigación de ataques**: El artículo se centra exclusivamente en la detección de DDoS, pero no aborda la mitigación. Un sistema completo de defensa debería incluir mecanismos para bloquear o mitigar los ataques detectados. Los autores mencionan que el trabajo se enfoca en la detección y dejan la mitigación para trabajos futuros.

5. **Conjunto de datos**: Aunque los autores recolectan datos en tiempo real, no proporcionan detalles sobre la cantidad de datos, la duración de la recolección, o si el conjunto de datos está disponible públicamente para su replicación. La falta de un conjunto de datos estandarizado dificulta la comparación con otros trabajos.

6. **Sobrecarga del modelo SAE**: Los autores mencionan que el SAE reduce la sobrecarga de Snort, pero no proporcionan mediciones detalladas del tiempo de entrenamiento e inferencia del modelo SAE, que podría ser significativo en redes con recursos limitados.

7. **Escalabilidad**: No se evalúa el rendimiento del sistema con un número creciente de nodos IoT, lo que es crítico para determinar su viabilidad en redes IoT a gran escala.

---

## Relevancia para el Proyecto

Este artículo es relevante porque demuestra la eficacia de combinar **muestreo en el plano de datos (sFlow) con deep learning (Stacked Autoencoders)** para la detección de DDoS en redes IoT basadas en SDN. La reducción de sobrecarga de CPU (50%) y la alta tasa de detección (95% TPR) son resultados que pueden guiar el diseño de nuestro sistema, especialmente en la selección de técnicas de muestreo para reducir la carga del controlador. Aunque el artículo no cubre mitigación, proporciona una base sólida para la fase de detección en entornos con recursos limitados.

---

**Referencia:**  
Ujjan, R. M. A., Pervez, Z., Dahal, K., Bashir, A. K., Mumtaz, R., & Gonzalez, J. (2020). Towards sFlow and adaptive polling sampling for deep learning based DDoS detection in SDN. *Future Generation Computer Systems*.