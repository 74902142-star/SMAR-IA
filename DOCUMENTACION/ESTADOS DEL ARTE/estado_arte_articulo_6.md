# Estado del Arte - Artículo 6: Defending SDN against Packet Injection Attacks Using Deep Learning

**Autor(es):** Anh Tuan Phu, Bo Li, Faheem Ullah, Tanvir Ul Huque, Ranesh Naha, Ali Babara, Hung Nguyen  
**Título:** Defending SDN against packet injection attacks using deep learning  
**Journal:** (Preprint/Journal)  
**Año:** 2023  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de los ataques de inyección de paquetes en redes definidas por software (SDN). Explican que la arquitectura centralizada de SDN los convierte en un objetivo fácil para este tipo de ataques, donde el atacante inyecta paquetes maliciosos en la red SDN para afectar los servicios y el rendimiento del controlador y desbordar la capacidad de los switches SDN, pudiendo detener el funcionamiento de la red en tiempo real.

Los autores revisan exhaustivamente los trabajos existentes sobre detección y defensa contra ataques de inyección de paquetes en SDN. Mencionan el trabajo seminal de Deng et al. (2018), que propuso PacketChecker para detectar y mitigar ataques de inyección de paquetes en switches. Sin embargo, critican que esta técnica aumenta la carga computacional en la red (controlador y switches) hasta el punto de que el controlador puede fallar eventualmente, y también incrementa la sobrecarga de reglas en el switch durante el ataque.

También citan a Alshra'a y Seitz (2019), que propusieron INSPECTOR, un dispositivo hardware-software que mantiene el controlador separado de la gestión de mensajes Packet-In de flujos de datos maliciosos. Señalan que esta técnica reduce la carga computacional en el controlador y la sobrecarga de reglas en los switches, pero su principal inconveniente es que no se ajusta a la conformidad de la arquitectura SDN.

Los autores mencionan a Scott-Hayward y Arumugam (2018), que propusieron una técnica para mitigar ataques de inyección de paquetes sin la intervención del controlador, utilizando un enfoque de plano de datos con estado para detener los ataques a nivel de switch en un alcance limitado. Señalan que esta técnica reduce la carga computacional del controlador y la sobrecarga de reglas, pero no puede detectar el ataque cuando el atacante utiliza una dirección de host no registrada.

Los autores también citan a Khorsandroo y Tosun (2019), que discuten el efecto de los ataques de inyección de paquetes de baja tasa en redes SDN, mostrando que un atacante que genera tráfico ofensivo a una tasa de casi el 1% del rendimiento total puede agotar casi el 25% de la sobrecarga de reglas de los switches y disminuir el rendimiento en casi un 40%. Sin embargo, no ofrecen una solución para mitigar este tipo de ataque.

Los autores mencionan a Zhan et al. (2020), que proponen una técnica probabilística para detectar y mitigar ataques de inyección de paquetes utilizando machine learning, ofreciendo una precisión de detección de aproximadamente el 91%. También citan a Tanvir y Frank (2021), que presentaron un enfoque de descarga de carga de trabajo para proteger SDN de ataques de inyección de paquetes, donde el controlador de borde toma el control del controlador central cuando el tráfico malicioso supera un cierto umbral.

Los autores mencionan a Li et al. (2022), que añadieron un nuevo componente (PIEDefender) al controlador SDN para detectar ataques de inyección de paquetes mediante la verificación de mensajes Packet-In, logrando una precisión del 97.8%.

Además, los autores revisan trabajos sobre métodos de deep learning para proteger SDN. Mencionan a Niyaz et al. (2016), que propusieron una técnica basada en autoencoders apilados para detectar ataques de inyección de paquetes con una precisión del 99.82% para clasificación binaria y 95.65% para clasificación de múltiples ataques. También citan a Tang et al. (2016), que propusieron un modelo DNN con solo seis características para detectar ataques en SDN, logrando una precisión del 75.75%. Mencionan a Li et al. (2018), que integraron RNN, CNN y LSTM para detectar ataques en SDN basado en OpenFlow, logrando una precisión del 98%.

Los autores identifican que la mayoría de los métodos basados en DL para proteger SDN se basan únicamente en características de red, sin tener en cuenta la arquitectura relacional de la red en sí. Sin embargo, las redes informáticas pueden representarse naturalmente con una estructura de grafo, donde los nodos son objetos de red (hosts, switches, servidores) y las aristas son las conexiones entre esos objetos.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Enfoque en ataques de alta tasa**: La mayoría de las técnicas de detección de ataques de inyección de paquetes se centran únicamente en ataques de alta tasa, donde los paquetes maliciosos llegan a una velocidad tan alta que saturan el controlador. Los ataques de baja tasa, donde el atacante envía paquetes maliciosos a una velocidad muy inferior al valor umbral, también pueden representar una amenaza real, como demuestra el trabajo de Khorsandroo et al. (2019).

- **Dependencia del controlador**: Las técnicas existentes (PacketChecker, INSPECTOR) requieren la participación del controlador para abordar los ataques de inyección de paquetes, lo que aumenta la carga computacional en el controlador y la sobrecarga de reglas en los switches. Aunque Scott-Hayward y Arumugam (2018) propusieron una técnica sin intervención del controlador, esta no puede detectar ataques cuando el atacante utiliza una dirección de host no registrada.

- **Limitaciones de los enfoques DL**: La mayoría de los enfoques basados en deep learning se basan únicamente en características de red, sin tener en cuenta la arquitectura relacional de la red en sí. Las redes informáticas pueden representarse naturalmente como grafos, donde la estructura del grafo proporciona información valiosa para la detección de ataques, especialmente cuando los atacantes ocultan efectivamente sus características y generan tráfico indistinguible del tráfico normal.

- **Modelos de amenaza limitados**: Los modelos de amenaza existentes para ataques de inyección de paquetes (Deng et al., 2018) no pueden detectar ataques cuando la tasa de llegada maliciosa al switch está por debajo del umbral o fluctúa con frecuencia. Los autores proponen dos nuevas variantes de ataques de inyección de paquetes: el ataque de inyección de baja tasa y el ataque de inyección discontinuo, que no son detectados por las técnicas existentes.

Los autores justifican su trabajo en la necesidad de superar estos vacíos. Su contribución principal es el desarrollo de modelos novedosos de Graph Convolutional Network (GCN) y algoritmos para agrupar nodos/usuarios de la red en clases de seguridad, aprendiendo de los datos de red. Su solución es la primera que puede detectar y distinguir en tiempo real entre diferentes tipos de ataques (lentos/rápidos/discontinuos) en SDN, y proporciona una solución de mitigación escalable que ayuda a defender redes contra varios tipos de ataques de inyección de paquetes sin interrumpir el tráfico normal.

---

## Descripción del Aporte

El aporte principal de los autores es un sistema de detección, identificación y mitigación de ataques de inyección de paquetes en SDN utilizando Graph Convolutional Networks (GCN) y una solución de mitigación basada en listas de observación y bloqueo. El problema que abordan es crítico: los ataques de inyección de paquetes pueden afectar los servicios y el rendimiento del controlador SDN y desbordar la capacidad de los switches, deteniendo el funcionamiento de la red en tiempo real. Las técnicas existentes no pueden detectar ataques de baja tasa o discontinuos y a menudo dependen del controlador para la mitigación, lo que aumenta la carga computacional.

### Nuevos modelos de ataque propuestos:

1. **Ataque de inyección de baja tasa (Low-rate packet injection attack)**: El atacante envía paquetes maliciosos a una velocidad muy inferior al valor umbral (por ejemplo, casi el 1% del rendimiento total). Al lanzar este ataque a múltiples switches simultáneamente, el atacante puede aumentar la carga computacional en el controlador al mismo nivel que los ataques de alta tasa.

2. **Ataque de inyección discontinuo (Discontinuous packet injection attack)**: La tasa de llegada de paquetes maliciosos fluctúa alrededor del valor umbral dentro de la ventana de tiempo de detección fija. Los atacantes pueden evadir fácilmente las técnicas de detección existentes siguiendo un patrón de envío irregular.

### Sistema de detección de dos capas con GCN:

**Capa 1: Detección de ataques (Attack Detection)**: Los autores utilizan datos de tráfico basados en flujo para caracterizar tanto a usuarios benignos como a atacantes. Agrupan los paquetes en flujos básicos (mismo SrcIP:SrcPort y DstIP:DstPort) y luego en flujos de actividad (mismo SrcIP:SrcPort). Para cada nodo (IP:PORT), se extraen características basadas en el patrón de flujo. El problema se simplifica a una clasificación binaria (benigno vs. ataque). Se utiliza HyperGCN (una variante de GCN que opera en hipergrafos) para identificar hosts con patrones maliciosos de inyección de paquetes. HyperGCN es capaz de aprender información estructural y localizada entre muestras de datos representadas como estructuras no uniformes, como grafos, y es adecuado para ataques de inyección de paquetes con múltiples flujos entre switches.

**Capa 2: Identificación de ataques (Attack Identification)**: Una vez detectados los hosts maliciosos, el sistema clasifica el tipo de ataque (DDoS o PortScan). Se utiliza el mismo enfoque GCN, pero operando solo sobre las muestras maliciosas del dataset. Los nodos benignos se desactivan en esta etapa. HyperGCN aprende de los datos de entrenamiento etiquetados y propaga la información para identificar las clases de ataque de otros hosts en la red.

### Solución de mitigación:
El controlador ejecuta el Algoritmo 1 para mitigar los ataques de inyección de paquetes a nivel de switch. El algoritmo utiliza tres listas:
- **Network_List**: Almacena información de todos los hosts (benignos y sospechosos) conectados a la red como tuplas <IP, MAC, Switch ID:puerto>.
- **Observing_List**: Almacena información de hosts sospechosos.
- **Block_List**: Almacena información de atacantes bloqueados.

Cuando un switch encuentra un flujo de datos desconocido, envía un mensaje Packet_In al controlador. El controlador compara la dirección de origen del Packet_In con las entradas de Observing_List. Si hay coincidencia, instala una regla de bloqueo en el switch para descartar el flujo de datos inmediatamente. Si no hay coincidencia, compara la dirección de destino con Network_List. Si hay una coincidencia parcial (lo que indica un paquete malicioso), añade la dirección de origen a Observing_List. Si hay una coincidencia exacta, permite que el flujo de datos entre en la red.

### Evaluación en dataset generado:
Los autores generan un nuevo dataset de variantes DDoS en un entorno SDN emulado (Mininet con Ryu controller), con variantes como slowDDoS, fastDDoS, slowDiscontinuousDDoS, fastDiscontinuousDDoS. Este es el primer dataset de ataques de inyección de paquetes disponible públicamente.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que abarca desde la definición de nuevos modelos de ataque hasta la implementación y evaluación de los modelos GCN. El proceso se desarrolla en las siguientes etapas:

1. **Definición de modelos de amenaza extendidos**: Identifican las limitaciones del modelo de amenaza de Deng et al. (2018) y proponen dos nuevas variantes de ataques de inyección de paquetes: el ataque de baja tasa y el ataque discontinuo.

2. **Selección y preprocesamiento de datos**: Utilizan el dataset CICIDS2017 para la evaluación, que contiene tráfico benigno y 10 tipos de ataques (BruteForce, DoS, DDoS, Portscan, etc.). Se centran principalmente en ataques DDoS y PortScan, que representan el 52% de las muestras. También generan un nuevo dataset de variantes DDoS en un entorno SDN emulado con Mininet, OpenFlow switches y Ryu controller, utilizando nping para simular tráfico de ataque.

3. **Extracción de características y construcción del grafo**: Para el modelo GCN, extraen la estructura del grafo a partir de los datos de tráfico. Cada combinación IP:PORT que envía flujo a otra IP:PORT se considera un nodo, y existe una arista entre dos nodos si hay un flujo entre ellos. Las características de los nodos se obtienen agrupando paquetes en flujos básicos, tomando el promedio de atributos, agrupando en flujos de actividad, y utilizando agregación por media para obtener un vector de características para cada nodo.

4. **Entrenamiento del modelo HyperGCN**: Implementan HyperGCN utilizando PyTorch. Configuran los parámetros de la red neuronal: rate=0.15, layers=2, activations=128, decay=0.005, dropout=0.5. Utilizan la propagación por capas de GCN:

   H(l+1) = σ(D̃⁻¹/² Ã D̃⁻¹/² H(l) W(l))

   Z = f(X,A) = softmax(Â ReLU(Â X W(0)) W(1))

5. **Entrenamiento de modelos de comparación**: Comparan HyperGCN con otros algoritmos de machine learning: Random Forest (RF), Support Vector Machines (SVM) y Gradient Boost (GB). Los parámetros de RF: 100 árboles, profundidad máxima 3, random state 32, criterio 'entropy'. SVM: kernel 'rbf', C=1, gamma='auto', max_iter=8000. GB: n_estimators=100, learning_rate=1, max_depth=3.

6. **Implementación de la mitigación**: Implementan el Algoritmo 1 de mitigación en el controlador Ryu. El algoritmo utiliza tres listas (Network_List, Observing_List, Block_List) para gestionar hosts y bloquear atacantes a nivel de switch.

7. **Evaluación en escenarios de ataque**: Evalúan el sistema en tres aspectos: detección de ataques, identificación de ataques y mitigación. Para la detección, utilizan el dataset CICIDS2017 con una división de datos balanceada (20k benignos, 20k atacantes) para evitar sobreajuste. Para la identificación, clasifican entre DDoS y PortScan. Para la mitigación, miden la utilización de CPU y memoria del controlador en tres escenarios: idle, con ataque sin mitigación, y con ataque con mitigación.

8. **Análisis de resultados**: Analizan los resultados utilizando métricas de accuracy y F1-score, comparando los cuatro algoritmos en diferentes configuraciones de muestras de entrenamiento (50, 250, 500, 750, 1000 muestras).

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de su sistema para resolver el problema de detección, identificación y mitigación de ataques de inyección de paquetes en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan Ubuntu 20.04 LTS, Mininet V2.2.2, Open vSwitch V2.13.0, Python 3.8, y Ryu como controlador. La topología de red consiste en 2 hosts y 22 switches. Instalan CouchDB para almacenar datos de tráfico. Para la generación de ataques, utilizan nping con diferentes parámetros de tasa (5-20,000 paquetes/segundo) y sleep timeout (3-10 segundos).

2. **Generación de dataset de variantes DDoS**: Generan un nuevo dataset con cuatro variantes de DDoS: slowDDoS, fastDDoS, slowDiscontinuousDDoS, fastDiscontinuousDDoS. Capturan datos a nivel de paquete y utilizan CIC-Flowmeter para extraer características estadísticas del flujo de tráfico en tiempo real.

3. **Evaluación de detección de ataques (Capa 1)**: Utilizan el dataset CICIDS2017. Para evitar sobreajuste debido al desbalanceo de datos (mayoría de usuarios benignos), seleccionan aleatoriamente 20k muestras de la clase benigna y 20k de la clase atacante para el conjunto de entrenamiento, y utilizan el resto para pruebas. Comparan HyperGCN con RF, SVM y GB en términos de accuracy y F1-score.

4. **Evaluación de identificación de ataques (Capa 2)**: Clasifican entre DDoS y PortScan. Utilizan dos enfoques de división de datos: (1) muestreo fijo (20k muestras de cada clase), y (2) división 80-20 (80% entrenamiento, 20% prueba). Comparan los cuatro algoritmos en términos de accuracy y F1-score. También evalúan el rendimiento con diferentes números de muestras de entrenamiento (50, 250, 500, 750, 1000).

5. **Evaluación de mitigación**: Miden la utilización de CPU y memoria del controlador en tres escenarios:
   - **Idle mode (sin ataque)**: Miden la utilización en intervalos de 0.5 segundos y 5 segundos.
   - **Con ataque sin mitigación**: Miden la utilización durante un ataque DDoS continuo.
   - **Con ataque con mitigación**: Miden la utilización después de aplicar el Algoritmo 1.

6. **Resultados de detección**: HyperGCN logra una accuracy de 0.994 y F1-score de 0.979, comparable a RF (0.996) y GB (0.992), y superior a SVM (0.119).

7. **Resultados de identificación**: HyperGCN logra una accuracy de 0.9999 y F1-score de 0.9995 en muestreo fijo, y 0.9999/0.9997 en división 80-20. GCN, RF y GB muestran rendimiento similar, pero GCN tiene un F1-score ligeramente superior. El rendimiento de GCN mejora con el aumento de muestras de entrenamiento.

8. **Resultados de mitigación**:
   - En idle mode (intervalo 0.5s): CPU media 3.46%, desviación 3.72; memoria máxima 2.1%.
   - En idle mode (intervalo 5s): CPU media 5.96%, desviación 3.02; memoria máxima 0.6%.
   - Con mitigación (intervalo 0.5s): CPU máxima 33.1%, media 5.27, desviación 7.36; memoria máxima 0.7%.
   - Con mitigación (intervalo 5s): CPU máxima 44.4%, media 5.72, desviación 5.97; memoria máxima 0.7%.
   - La técnica de mitigación consume recursos razonables y reduce el impacto del ataque en el controlador.

9. **Comparación con otros enfoques**: Demuestran que su enfoque supera a SVM y es comparable a RF y GB en detección, pero con la ventaja de capturar información estructural del grafo que otros métodos no consideran.

---

## Métricas y Resultados

Los autores utilizan métricas estándar de rendimiento para sistemas de clasificación: accuracy y F1-score. La accuracy mide la proporción de predicciones correctas, mientras que el F1-score (media armónica de precisión y recall) es más adecuado para conjuntos de datos desbalanceados.

### Resultados obtenidos:

**Detección de ataques (Capa 1):**

| Algoritmo | Accuracy | F1-score |
|---|---|---|
| GCN (HyperGCN) | 0.994 | 0.979 |
| SVM | 0.119 | 0.119 |
| Random Forest | 0.996 | 0.987 |
| Gradient Boost | 0.992 | 0.971 |

**Identificación de ataques (Capa 2):**

| Algoritmo | Accuracy | F1-score (muestreo fijo) | F1-score (80-20) |
|---|---|---|---|
| GCN (HyperGCN) | 0.9999 | 0.9995 | 0.9997 |
| SVM | 0.1193/0.9214 | 0.1185/0.5219 | - |
| Random Forest | 0.9964/0.9999 | 0.9868/0.9997 | 0.9997 |
| Gradient Boost | 0.9916/0.9999 | 0.9710/0.9997 | 0.9997 |

**Mitigación:**
- CPU media en idle: 3.46-5.96%
- CPU máxima con mitigación: 33.1-44.4%
- Memoria máxima: ~0.7%

**Comparación de resultados:**
- GCN, RF y GB tienen rendimiento similar en detección e identificación.
- GCN tiene la ventaja de considerar la estructura del grafo de la red.
- La solución de mitigación consume recursos mínimos.

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas (accuracy y F1-score) y cubren los aspectos clave de la evaluación de sistemas de detección de intrusiones. El uso del F1-score es especialmente apropiado debido al desbalanceo de clases en los datasets de ciberseguridad.

El enfoque de utilizar GCN/HyperGCN es particularmente innovador y acertado por varias razones:
1. GCN captura la información estructural del grafo de la red (las relaciones entre nodos), lo que proporciona información adicional que los enfoques basados únicamente en características de flujo no consideran.
2. HyperGCN es capaz de manejar hipergrafos, lo que es adecuado para ataques de inyección de paquetes con múltiples flujos entre switches.
3. El sistema de dos capas (detección + identificación) proporciona información granular sobre el tipo de ataque, lo que permite una mitigación más específica.
4. La solución de mitigación es ligera y escalable, consumiendo recursos mínimos incluso durante ataques.

Sin embargo, hay aspectos que podrían mejorarse:
1. Aunque GCN logra una alta precisión, RF y GB logran resultados muy similares, lo que sugiere que la ventaja de GCN puede ser marginal en términos de precisión.
2. SVM muestra un rendimiento extremadamente pobre (F1-score de 0.119), lo que puede deberse a la elección de parámetros.
3. La evaluación de la mitigación se limita a la utilización de CPU y memoria del controlador, pero no se mide el impacto en el tráfico legítimo (falsos positivos) o en el tiempo de respuesta del controlador.
4. La generación del dataset de variantes DDoS es una contribución valiosa, pero la evaluación en este dataset no se presenta en detalle en el artículo.

---

## Observaciones Críticas

El artículo presenta una contribución innovadora al aplicar Graph Convolutional Networks para la detección de ataques de inyección de paquetes en SDN. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Ventaja marginal de GCN sobre RF/GB**: Aunque GCN logra una alta precisión, Random Forest y Gradient Boost logran resultados muy similares tanto en detección como en identificación de ataques. Esto sugiere que, en este conjunto de datos específico, la ventaja de GCN es marginal en términos de precisión. Sería valioso evaluar GCN en escenarios donde la estructura del grafo sea más relevante.

2. **Evaluación limitada de los nuevos modelos de ataque**: Proponen dos nuevas variantes de ataques de inyección de paquetes (baja tasa y discontinuos) y generan un dataset de variantes DDoS, pero no presentan resultados detallados de la evaluación de estos nuevos modelos de ataque.

3. **Rendimiento pobre de SVM**: SVM muestra un rendimiento extremadamente pobre (F1-score de 0.119). Podría deberse a la elección de parámetros (C=1, gamma='auto') que no son óptimos para este dataset. Una optimización de hiperparámetros para SVM podría haber mejorado significativamente su rendimiento.

4. **Falta de validación en testbed real**: La evaluación se realiza en un entorno emulado (Mininet) y con datasets estáticos (CICIDS2017). Sería valioso validar el enfoque en un testbed real con hardware SDN y tráfico en vivo.

5. **Complejidad computacional de GCN**: No proporcionan métricas de tiempo de entrenamiento o inferencia de los modelos GCN. Para aplicaciones en tiempo real en SDN, el tiempo de procesamiento es crítico.

6. **Mitigación en el switch**: El Algoritmo 1 de mitigación instala reglas de bloqueo en el switch para cada atacante. En escenarios con múltiples atacantes, esto puede consumir espacio en la tabla de flujo del switch. No se discute este aspecto.

7. **Dependencia de la lista Network_List**: El Algoritmo 1 asume que la Network_List contiene información de todos los hosts conectados a la red. En redes SDN dinámicas donde los hosts se unen y abandonan frecuentemente, mantener esta lista actualizada puede ser un desafío.

8. **Falsos positivos**: Aunque la precisión de detección es alta (99.4%), no se proporcionan métricas específicas de falsos positivos (FP) y falsos negativos (FN). Sería valioso proporcionar estas métricas para evaluar el equilibrio entre sensibilidad y especificidad.

9. **Evaluación del dataset generado**: El artículo menciona la generación de un dataset de variantes DDoS, pero no proporciona detalles sobre el tamaño del dataset, el número de muestras por clase, o las características extraídas.

10. **Clasificación de ataques en la Capa 2**: En la Capa 2 (identificación de ataques), los autores solo clasifican entre DDoS y PortScan. Sin embargo, el dataset CICIDS2017 contiene otros tipos de ataques (BruteForce, Heartbleed, etc.). La limitación a dos clases reduce la aplicabilidad del sistema.

---

## Relevancia para el Proyecto

Este artículo es especialmente relevante porque introduce el uso de **Graph Convolutional Networks (GCN)** para la detección de ataques de inyección de paquetes en SDN. La capacidad de capturar la estructura de grafo de la red es una ventaja significativa sobre los enfoques basados únicamente en características de flujo. Además:

1. La detección de ataques de baja tasa y discontinuos es un área que otros sistemas no cubren adecuadamente.
2. El sistema de dos capas (detección e identificación) proporciona información granular sobre el tipo de ataque.
3. La mitigación basada en listas de observación y bloqueo es ligera y consume recursos mínimos.
4. La generación de un dataset de variantes DDoS es una práctica que podemos replicar para nuestro sistema.

Aunque GCN no supera significativamente a RF/GB en precisión, su capacidad para considerar la estructura de la red lo hace valioso para ataques donde los patrones de tráfico individuales no son suficientes.

---

**Referencia:**  
Phu, A. T., Li, B., Ullah, F., Huque, T. U., Naha, R., Babara, A., & Nguyen, H. (2023). Defending SDN against packet injection attacks using deep learning. *Preprint/Journal*.