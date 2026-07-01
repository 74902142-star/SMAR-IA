# Estado del Arte - Artículo 5: Detecting and Mitigating Botnet Attacks in SDN Using Deep Learning

**Autor(es):** Muhammad Waqas Nadeem, Hock Guan Goh, Yichiet Aun, Vasaki Ponnusamy  
**Título:** Detecting and Mitigating Botnet Attacks in Software-Defined Networks Using Deep Learning Techniques  
**Journal:** IEEE Access  
**Año:** 2024  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de los ataques botnet en redes definidas por software (SDN). Explican que SDN es una arquitectura emergente que separa el plano de control del plano de datos, ofreciendo flexibilidad y facilidad de gestión, pero que esta centralización introduce nuevas vulnerabilidades, incluyendo el riesgo de un punto único de fallo. Los atacantes pueden lanzar ataques maliciosos como botnets y DDoS contra el controlador a través de los switches OpenFlow, aprovechando la arquitectura centralizada.

Los autores revisan exhaustivamente la literatura reciente sobre métodos de detección de intrusiones en SDN. Mencionan que investigadores han propuesto diversos enfoques basados en machine learning (ML) y deep learning (DL) para detectar ataques botnet y DDoS. Citan el trabajo de Nguyen et al. (2020), que propuso características basadas en subgrafos PSI para detectar botnets en IoT utilizando una combinación híbrida de ML y DL con un número mínimo de características para reducir el espacio y acelerar la detección. También mencionan a Al Shorman et al. (2020), que desarrolló un sistema de sensores IoT basado en aprendizaje no supervisado con SVM optimizado mediante el algoritmo Grey Wolf Optimization (GWO). Otro enfoque citado es N-BaIoT (Meidan et al., 2018), que utiliza autoencoders profundos para detectar tráfico de ataque mediante instantáneas del comportamiento de la red.

Los autores revisan el trabajo de Asadi et al. (2020), que propuso un método híbrido de PSO con mecanismo de votación para detectar botnets en IoT, utilizando DNN, Decision Tree C4.5 y SVM. También mencionan BoTIDS (Idrissi et al., 2021), un método basado en CNN que mostró buenos resultados en un dataset completo y un subconjunto predefinido de 10 características. Citan sistemas de detección de anomalías basados en CNN (Saba et al., 2022) probados en datasets BoT-IoT y NID.

En cuanto a la detección de DDoS en SDN, los autores mencionan el método de dos niveles basado en DL y entropía de información (Liu et al., 2022), que primero usa entropía para detectar componentes sospechosos y luego ejecuta CNN para clasificación fina. También citan DDoSNet (Elsayed et al., 2020), que combina autoencoder y RNN; un método LSTM (Yuan et al., 2017) que reduce la tasa de error del 7.517% al 2.103%; y LUCID (Doriguzzi-Corin et al., 2020), un sistema ligero basado en CNN.

Los autores identifican varias limitaciones en los trabajos existentes:

1. La mayoría utiliza datasets tradicionales (NSL-KDD, DARPA, CIC-DDoS 2019, N-BaIoT) que no son adecuados para SDN debido a su naturaleza basada en flujos y sufren problemas de desbalanceo.
2. Muchos trabajos utilizan un gran número de características (83 o más), lo que aumenta la complejidad y el tiempo de procesamiento.
3. La mayoría de los métodos solo se validan mediante simulaciones, con poca verificación en testbeds reales.
4. La mayoría se centra en ataques DDoS simples, pero no específicamente en ataques botnet, que representan una amenaza crítica debido a su capacidad de controlar múltiples dispositivos.

Finalmente, los autores justifican su estudio en la necesidad de desarrollar un método DL ligero con hiperparámetros básicos y características óptimas para detectar ataques botnet en SDN, utilizando un dataset generado en un entorno SDN puro y validado en un testbed real.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Datasets no representativos**: La mayoría de los estudios existentes utilizan datasets tradicionales que no son representativos de las redes SDN, ya que estos datasets fueron capturados en redes tradicionales y no reflejan las características de flujo específicas de SDN. Además, estos datasets presentan problemas de desbalanceo que afectan el rendimiento de los clasificadores.

- **Exceso de características**: Muchos trabajos utilizan un número excesivo de características (83 o más), lo que aumenta significativamente la complejidad computacional y el tiempo de procesamiento, sin aportar necesariamente una mejora en la precisión. Critican que no se realice un análisis adecuado de la importancia de las características para seleccionar las más relevantes.

- **Falta de validación en entornos reales**: La mayoría de los métodos propuestos solo se validan mediante simulaciones o conjuntos de datos experimentales, sin realizar pruebas en entornos reales (testbeds). Esto limita la aplicabilidad práctica de las soluciones propuestas, ya que no se verifica su rendimiento en condiciones reales de red.

- **Enfoque limitado en botnet**: La mayoría de los estudios se centran en la detección de DDoS en general, pero no abordan específicamente los ataques botnet, que son particularmente peligrosos en SDN debido a la capacidad de los atacantes de controlar múltiples dispositivos y lanzar ataques coordinados contra el controlador.

- **Falta de estrategias de mitigación**: Los métodos existentes no incluyen estrategias de mitigación efectivas que eliminen los flujos maliciosos de los switches sin afectar al tráfico legítimo.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen un método DL con características óptimas seleccionadas mediante ponderación y ajuste de umbrales, que se entrena con un dataset generado en un entorno SDN puro y se valida en un testbed real. Además, incorporan una estrategia de mitigación basada en teoría de grafos que bloquea los ataques en el origen sin afectar al tráfico legítimo.

---

## Descripción del Aporte

El aporte principal de los autores es el sistema **DepBot**, una solución basada en deep learning para detectar y mitigar ataques botnet en redes SDN. El problema que abordan es crítico: los ataques botnet en SDN explotan la arquitectura centralizada para controlar múltiples dispositivos (bots) y lanzar ataques DDoS coordinados contra el controlador o servidores específicos. Un atacante (botmaster) compromete un dispositivo, instala malware y establece una conexión con un centro de comando y control (C&C), desde donde puede instruir a los bots para lanzar ataques masivos. Esto puede provocar la saturación del controlador, la congestión de la red y la denegación de servicio a usuarios legítimos.

El sistema DepBot se compone de varios módulos que abordan todo el ciclo de detección y mitigación:

### 1. Generación de dataset en entorno SDN puro:
Los autores crean un conjunto de datos específico para SDN que incluye tráfico normal y ataques botnet. Este dataset es generado en un entorno controlado con Mininet y POX controller, lo que asegura que las características del tráfico sean representativas de redes SDN reales. A diferencia de otros estudios que utilizan datasets tradicionales (NSL-KDD, DARPA, CIC-DDoS 2019), este dataset está diseñado específicamente para SDN y refleja las características de flujo de esta arquitectura. El dataset contiene 89,632 registros de flujo con 83 características (48,390 normales y 41,242 de ataque).

### 2. Extracción y selección de características óptimas:
Los autores utilizan CIC Flow Meter V4 para convertir los datos de pcap a CSV y extraer 83 características de flujo. Luego, aplican un método de selección de características basado en dos principios:
- **Ponderación de características (feature weighting)**: Se utiliza SVM para asignar pesos a cada característica según su importancia para predecir el ataque.
- **Ajuste de umbrales (threshold tuning)**: Determina el valor óptimo del umbral para seleccionar características con pesos superiores.

Este proceso permite dividir las características en cinco subconjuntos (Subset-1 a Subset-5) con diferentes números de características (83, 43, 30, 23 y 15 respectivamente). Subset-3, con 30 características, demostró ser el más efectivo para la detección.

### 3. Entrenamiento y comparación de cinco métodos DL:
Los autores implementan y comparan cinco algoritmos de deep learning: RNN (Red Neuronal Recurrente), CNN (Red Neuronal Convolucional), MLP (Perceptrón Multicapa), LSTM (Memoria a Corto y Largo Plazo) y DNN (Red Neuronal Profunda). Cada método se entrena con los cinco subconjuntos de características utilizando la misma estructura de hiperparámetros (una capa oculta con 128 neuronas, función de activación ReLU, salida sigmoide, learning rate 0.1, optimizador Adam, 20 épocas y batch size 32). El objetivo es identificar el método que ofrece el mejor equilibrio entre precisión, tasa de detección y tiempo de procesamiento.

### 4. Mitigación basada en teoría de grafos:
Los autores proponen una estrategia de mitigación que combina teoría de grafos y eliminación dinámica de flujos para bloquear los ataques en el origen sin afectar al tráfico legítimo. Cuando se detecta un ataque, el controlador crea una lista gris (S_g) y redirige los flujos sospechosos al clasificador para su análisis. Se establece un contador que cuenta los flujos de ataque (con límite c ≥ 10) y se crean dos listas adicionales: lista de eliminación (S_d) para flujos que deben eliminarse de los switches, y lista de bloqueo (S_b) para hosts maliciosos. Utilizando teoría de grafos, el sistema identifica la ruta de ataque en la red, calcula una tasa de caída (drop rate) para cada switch (r_edge) basada en la diferencia de entropía y el número de paquetes, y elimina selectivamente los flujos maliciosos, minimizando el impacto en el tráfico legítimo. Si la tasa de caída alcanza el 100%, el host se bloquea completamente.

### 5. Validación en testbed real:
Para verificar el rendimiento en condiciones reales, los autores implementan los métodos entrenados en un testbed real con la misma topología de red (11 switches, 18 hosts). Durante el tráfico en tiempo real, cada método clasifica los flujos entrantes como normales (0) o ataques (1). Se evalúan 50 decisiones consecutivas bajo estados de red normales y de ataque. Los resultados muestran que CNN alcanza el 99% de detección para flujos normales y el 97% para flujos de ataque, con tiempos de detección razonables.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que abarca desde la generación del dataset hasta la implementación y validación del sistema. El proceso se desarrolla en las siguientes etapas:

1. **Generación del dataset en entorno SDN**: Crean un conjunto de datos específico para SDN utilizando Mininet 2.3.2 con el controlador POX. Configuran una topología de red en árbol con un controlador, 7 switches OpenFlow y 18 hosts. Para generar tráfico normal, utilizan D-ITG (Distributed Internet Traffic Generator) con más de 200 flujos de fondo que siguen distribuciones constante, uniforme, exponencial, Poisson y gamma, con protocolo TCP y tamaños de paquete variables. Para generar ataques botnet, desarrollan scripts en Python: uno de los hosts actúa como botmaster y otros como bots. El botmaster envía instrucciones a los bots, que luego lanzan ataques DDoS contra un servidor objetivo. El ataque tiene una duración de 14.26 minutos y utiliza el concepto de socket programming para establecer comunicación entre el botmaster y los bots.

2. **Extracción y etiquetado de características**: Utilizan CIC Flow Meter V4 (versión 4) para convertir los datos capturados en formato pcap a CSV, generando estadísticas de flujo bidireccionales con 83 características. Las características incluyen duración del flujo, número de paquetes, longitudes, intervalos inter-arrival, flags TCP, etc. Se eliminan características como Flow ID, IPs origen/destino, puertos, protocolo y timestamp para generalizar el modelo y evitar que los métodos DL asocien el ataque a direcciones o puertos específicos. Los flujos se etiquetan como normales (0) y ataques (1), manteniendo el desbalanceo original (48,390 normales y 41,242 ataques) para imitar escenarios reales.

3. **Preprocesamiento de datos**: Los datos se normalizan y se verifica la existencia de valores infinitos o faltantes. Las características no numéricas se codifican adecuadamente para su uso en los métodos DL.

4. **Selección de características óptimas**: Implementan un método de selección de características basado en ponderación por SVM y ajuste de umbrales. El SVM asigna pesos a cada una de las 83 características según su importancia en la predicción. Mediante el método de ajuste de umbrales, se determinan valores de umbral óptimos (α) que seleccionan características con pesos superiores. Este proceso se repite para generar cinco subconjuntos: Subset-1 (todas las 83 características), Subset-2 (α≥1.80, 43 características), Subset-3 (α≥2.70, 30 características), Subset-4 (α≥3.15, 23 características) y Subset-5 (α≥4.90, 15 características).

5. **Entrenamiento de los métodos DL**: Implementan cinco métodos DL (RNN, CNN, MLP, LSTM y DNN) utilizando el framework Keras en Python. Todos los métodos utilizan la misma estructura de hiperparámetros: una capa oculta con 128 neuronas, función de activación ReLU en las capas ocultas y sigmoide en la salida, learning rate de 0.1, optimizador Adam, 20 épocas y batch size de 32. Cada método se entrena con los cinco subconjuntos de características.

6. **Implementación de la estrategia de mitigación**: Desarrollan un módulo de mitigación basado en teoría de grafos y eliminación dinámica de flujos. Este módulo se integra en el controlador y se activa cuando se detecta un ataque. Utiliza conceptos de teoría de grafos para identificar la ruta de ataque y calcula tasas de caída para cada switch en la ruta, priorizando la eliminación de flujos maliciosos en los switches más cercanos a la fuente del ataque.

7. **Validación en testbed real**: Finalmente, los métodos entrenados se implementan en el controlador y se evalúan en un testbed real con la misma topología de red. Se mide la tasa de detección correcta durante 50 decisiones consecutivas en condiciones de tráfico normal y de ataque, y se comparan los tiempos de entrenamiento y detección de cada método.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de su sistema para resolver el problema de detección y mitigación de ataques botnet en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan Mininet 2.3.2 para emular una topología de red SDN con un controlador POX, 7 switches OpenFlow y 18 hosts. La topología sigue una estructura de árbol compleja. La configuración de hardware es Intel Core i7, 8GB RAM y Windows 10. Los métodos DL se implementan en Python con el framework Keras. Se designa H2 como botmaster, H3-H6 como bots, H13 como servidor objetivo, y el resto de hosts para generar tráfico legítimo.

2. **Generación de tráfico normal y de ataque**: El tráfico normal se genera utilizando D-ITG con más de 200 flujos de fondo que siguen distribuciones constante, uniforme, exponencial, Poisson y gamma, con TCP y tamaños de paquete variables. El tráfico de ataque se genera mediante scripts en Python: el botmaster (H2) instruye a los bots (H3-H6) para lanzar ataques DDoS contra H13. Los bots esperan en puertos designados las instrucciones del botmaster, y cuando la fecha y hora coinciden con las instrucciones, envían tráfico de ataque al servidor objetivo. La duración del ataque es de 14.26 minutos.

3. **Recolección de datos y extracción de características**: Los datos de tráfico se capturan en formato pcap y se convierten a CSV utilizando CIC Flow Meter V4, que extrae 83 características de flujo. Este proceso genera un dataset de 89,632 flujos (48,390 normales y 41,242 de ataque).

4. **Selección de características y entrenamiento**: Aplican el método de selección de características (ponderación por SVM y ajuste de umbrales) para generar cinco subconjuntos de características (desde 83 hasta 15 características). Cada método DL (RNN, CNN, MLP, LSTM, DNN) se entrena con cada subconjunto utilizando la misma estructura de hiperparámetros. Se registra la precisión (accuracy), la tasa de detección (detection rate), la precisión (precision), el F1-score, la tasa de falsos positivos (FPR) y el tiempo de entrenamiento para cada combinación.

5. **Evaluación de la eficiencia de detección**: Utilizan una matriz de confusión para calcular las métricas de rendimiento: accuracy, detection rate (recall), precision, F1-score y FPR. Comparan el rendimiento de los cinco métodos en los cinco subconjuntos de características para identificar el mejor método y el subconjunto óptimo. También analizan las curvas de precisión y pérdida (loss) durante el entrenamiento para evaluar la estabilidad de cada método.

6. **Evaluación de la estrategia de mitigación**: Cuando se detecta un ataque, el controlador implementa la estrategia de mitigación basada en teoría de grafos. Se crean listas grises (S_g), de eliminación (S_d) y de bloqueo (S_b). Utilizando la ecuación Ei,j=∑(si,ri)→(sj,rj) se identifica la ruta de ataque, y se calculan las tasas de caída para cada switch en la ruta usando la fórmula redge=k(ΔH,ΔN). El controlador envía mensajes "OFFPC_ADD" a los switches para insertar nuevas reglas de flujo que eliminan selectivamente los flujos maliciosos. Si la tasa de caída alcanza el 100%, el host se bloquea completamente.

7. **Validación en testbed real**: Implementan los métodos entrenados en el testbed real utilizando la misma topología de red. Durante el tráfico en tiempo real, cada método clasifica los flujos entrantes como normales (0) o ataques (1). Se evalúan 50 decisiones consecutivas bajo estados de red normales y de ataque. Se miden las tasas de detección correcta para flujos normales y de ataque, así como los tiempos de entrenamiento y detección (en microsegundos por flujo) para determinar cuál método ofrece el mejor rendimiento en tiempo real.

8. **Análisis de resultados**: Analizan los resultados y concluyen que: (a) el Subset-3 (30 características) ofrece el mejor equilibrio entre precisión y eficiencia; (b) CNN es el método más estable y preciso, con 99.37% de accuracy en simulación y 99%/97% de detección en tiempo real para tráfico normal/ataque; (c) el tiempo de detección de CNN es razonable, mientras que LSTM es significativamente más lento; (d) la estrategia de mitigación basada en teoría de grafos elimina eficazmente los flujos maliciosos sin afectar al tráfico legítimo.

---

## Métricas y Resultados

Los autores utilizan métricas estándar de rendimiento para sistemas de detección de intrusiones: precisión (accuracy), tasa de detección (detection rate o recall), precisión (precision), F1-score, tasa de falsos positivos (FPR), tiempo de entrenamiento y tiempo de detección por flujo. Estas métricas se calculan a partir de la matriz de confusión.

### Resultados obtenidos:

| Método | Accuracy (Subset-3) | Detection Rate (Subset-3) | Tiempo Entrenamiento (s) | Detección en testbed (Normal/Attack) |
|---|---|---|---|---|
| RNN | 99.25% | 99.21% | 263.17 | -/87% |
| CNN | 99.37% | 99.60% | 181.88 | 99%/97% |
| MLP | 99.33% | 99.41% | 142.37 | -/85% |
| LSTM | 99.16% | 99.13% | 211.73 | -/93% |
| DNN | 99.30% | 99.11% | 154.13 | -/85% |

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de detección de intrusiones: precisión, sensibilidad, y eficiencia. La inclusión del tiempo de entrenamiento y detección es especialmente relevante para evaluar la viabilidad del sistema en entornos con recursos limitados, como los controladores SDN. La validación en testbed real es un valor añadido significativo, ya que muchos estudios se limitan a simulaciones o conjuntos de datos estáticos, y esto demuestra la aplicabilidad práctica del sistema.

Sin embargo, hay aspectos que podrían mejorarse:
1. El estudio se centra únicamente en ataques botnet de inundación (flooding), pero no evalúa ataques de baja tasa (low-rate DDoS) o ataques más sofisticados que podrían evadir la detección.
2. Aunque se comparan cinco métodos DL, todos utilizan la misma estructura de hiperparámetros, lo que podría no ser óptimo para cada método individual.
3. El proceso de selección de características se basa en SVM, lo que introduce dependencia del clasificador.
4. Aunque la estrategia de mitigación es innovadora, no se proporcionan métricas cuantitativas de su efectividad (por ejemplo, porcentaje de tráfico malicioso bloqueado vs. tiempo de interrupción del servicio).

---

## Observaciones Críticas

El artículo presenta una solución completa y bien fundamentada para la detección y mitigación de ataques botnet en SDN, con un enfoque en la selección óptima de características y la validación en testbed real. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Enfoque limitado a ataques de inundación**: El sistema está diseñado específicamente para ataques botnet de inundación DDoS, pero no se evalúa su capacidad para detectar ataques de baja tasa (low-rate DDoS) o ataques no volumétricos. Los autores reconocen esta limitación.

2. **Generalización de hiperparámetros**: Utilizan la misma estructura de hiperparámetros para todos los métodos DL para hacer la comparación justa, pero esto podría no ser óptimo para cada método. Por ejemplo, LSTM podría beneficiarse de más capas o diferentes tasas de aprendizaje.

3. **Métricas de mitigación**: Aunque la estrategia de mitigación basada en teoría de grafos es innovadora, no proporcionan métricas cuantitativas de su efectividad (por ejemplo, tiempo de mitigación, porcentaje de flujos maliciosos bloqueados, impacto en el tráfico legítimo).

4. **Comparación con otros clasificadores**: Comparan los métodos DL entre sí, pero no incluyen una comparación con métodos de machine learning tradicionales (como Random Forest, SVM o árboles de decisión) que podrían ofrecer un mejor equilibrio entre precisión y eficiencia.

5. **Disponibilidad del dataset**: Aunque proporcionan un enlace al dataset y al código fuente (https://github.com/Waqas-Nadeem/Botnet-based-DDoS-attack-in-an-SDN-Environment), sería útil que el dataset estuviera disponible en un repositorio público estándar.

6. **Escalabilidad**: El sistema se evalúa en una topología de 7 switches y 18 hosts. Sería interesante probar su escalabilidad en redes más grandes.

7. **Ataques cifrados y evasión**: No se evalúa el rendimiento del sistema ante ataques que utilizan tráfico cifrado o técnicas de evasión (por ejemplo, modificación de patrones de tráfico para eludir la detección basada en características).

---

## Relevancia para el Proyecto

DepBot es un sistema completo que cubre todo el ciclo de detección y mitigación de ataques botnet en SDN. Es especialmente relevante por:

1. **Dataset SDN puro**: La generación de un dataset específico para SDN es una práctica que debemos replicar para asegurar que nuestros modelos sean representativos del entorno SDN.
2. **Selección óptima de características**: El método de ponderación por SVM y ajuste de umbrales reduce la dimensionalidad de 83 a 30 características, mejorando la eficiencia sin sacrificar precisión.
3. **CNN como mejor clasificador**: La CNN logra el mejor equilibrio entre precisión (99.37%) y eficiencia (181.88 segundos de entrenamiento), lo que sugiere que es una buena opción para nuestro sistema.
4. **Mitigación basada en teoría de grafos**: La estrategia de mitigación que bloquea en el origen y elimina selectivamente flujos maliciosos es aplicable a nuestro sistema.
5. **Validación en testbed real**: La validación en un entorno real proporciona confianza en la aplicabilidad práctica del sistema.

---

**Referencia:**  
Nadeem, M. W., Goh, H. G., Aun, Y., & Ponnusamy, V. (2024). Detecting and Mitigating Botnet Attacks in Software-Defined Networks Using Deep Learning Techniques. *IEEE Access*.