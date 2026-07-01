# Estado del Arte - Artículo 8: Entropy and Machine Learning Based Approach for DDoS Detection in SDN

**Autor(es):** Amany I. Hassan, Eman Abd El Reheem, Shawkat K. Guirguis  
**Título:** An entropy and machine learning based approach for DDoS attacks detection in software defined networks  
**Journal:** Scientific Reports (Nature)  
**Volumen (issue):** Volume 14  
**Año:** 2024  
**Artículo:** 18159  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de los ataques DDoS en redes definidas por software (SDN). Explican que SDN es un enfoque innovador para la gestión de redes que mejora la adaptabilidad, programabilidad y capacidad de respuesta a necesidades dinámicas de servicios y aplicaciones. Sin embargo, la centralización del plano de control crea un punto único de fallo que los atacantes pueden explotar para lanzar ataques DDoS, inundando el sistema con tráfico malicioso y degradando la disponibilidad y calidad del servicio.

Los autores revisan exhaustivamente la literatura sobre técnicas de detección y mitigación de DDoS en SDN, clasificándolas en cuatro categorías principales:

### 1. Enfoques estadísticos:
Estos métodos analizan y recopilan estadísticas relacionadas con los flujos para generar un modelo de tráfico normal e identificar flujos maliciosos. Los autores citan el trabajo de Koay et al., que introdujo un conjunto completo de nuevas características basadas en entropía con un sistema multi-clasificador para mejorar la precisión de detección de ataques DDoS de baja y alta intensidad. También mencionan a Tsobdjou et al., que propuso una técnica dinámica de umbral de entropía basada en la desigualdad de Chebyshev para mejorar la adaptabilidad en escenarios dinámicos. Sahoo et al. propusieron un método para detectar ataques de baja tasa utilizando entropía definida y distancia de información, aunque encontraron desafíos para identificar altas tasas de tráfico. Pérez-Díaz et al. introdujeron un enfoque versátil para identificar y mitigar tráfico DDoS de baja y alta tasa utilizando IDS/IPS con seis modelos de ML, pero con una limitación en el umbral fijo que lo hace ineficaz para ataques de baja tasa con múltiples víctimas.

### 2. Enfoques basados en Machine Learning (ML):
Estos métodos analizan grandes volúmenes de tráfico y aprenden a identificar patrones y anomalías asociadas con ataques DDoS. Los autores citan a Li et al., que desarrolló un modelo de detección DDoS basado en SVM utilizando mensajes packet_in y extrayendo características como la IP de origen, aunque con limitaciones para detectar ataques a nivel de aplicación. Ye et al. desarrollaron una estrategia de detección basada en SVM con extracción de características, logrando alta precisión y baja tasa de falsas alarmas, pero con la necesidad de extracción manual de características. Cui et al. introdujeron un enfoque basado en computación cognitiva y análisis de entropía utilizando SVM para generar modos de detección específicos. Hannache et al. desarrollaron un clasificador de flujos basado en redes neuronales (TFC-NN) para detección en tiempo real, logrando una precisión del 96.13%. Cui et al. utilizaron clustering K-means para identificar tráfico malicioso en flujos de red. Gu et al. introdujeron una técnica de detección semi-supervisada K-means con selección de características híbrida para mejorar la robustez y precisión.

### 3. Enfoques basados en Deep Learning (DL):
Estos métodos utilizan redes neuronales profundas para analizar conjuntos de datos grandes y complejos. Los autores citan a Makuvaza et al., que desarrollaron una técnica basada en DNN para detección en tiempo real con una precisión del 97.59%. Nugraha et al. crearon un marco de deep learning basado en CNN-LSTM para detectar ataques DDoS lentos, aunque con alta demanda computacional. Doriguzzi-Corin et al. introdujeron LUCID, un sistema de detección basado en CNN 1D con una reducción de 40x en tiempo de procesamiento. Liang et al. emplearon LSTM para capturar dependencias temporales en el tráfico de red. Cil et al. introdujeron un modelo de clasificación de tráfico basado en DNN con una precisión del 95% en el dataset CIC-DDoS2019. Khan et al. desarrollaron múltiples marcos basados en autoencoders y redes recurrentes para la detección de intrusiones en entornos IIoT, logrando precisiones de hasta el 97.95%.

### 4. Enfoques basados en Blockchain:
Estos métodos utilizan blockchain para mejorar la seguridad, escalabilidad y rendimiento. Los autores citan a Bose et al., que incorporaron cifrado basado en blockchain en los canales de comunicación entre planos de datos y control para bloquear ataques DDoS a nivel de switch. Mathieu et al. introdujeron un sistema de evaluación de confianza basado en SDN y blockchain para reducir los ataques en redes domésticas. Chattaraj et al. presentaron BACC-SDN, un control de acceso basado en blockchain para proteger contra posibles amenazas.

Los autores identifican varias limitaciones en los trabajos existentes:
- Los enfoques estadísticos tienen dificultades para distinguir con precisión entre tráfico normal y malicioso y para adaptarse a amenazas emergentes.
- Los enfoques de ML sufren de desbalanceo de datos y la naturaleza dinámica de los ataques.
- Los enfoques de DL tienen alta complejidad computacional y tiempos de procesamiento elevados.
- Los enfoques de blockchain enfrentan desafíos como la latencia y la escalabilidad.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Limitaciones de los enfoques estadísticos**: Los enfoques estadísticos tradicionales, como los basados en entropía, no son lo suficientemente precisos o receptivos, especialmente en sistemas SDN grandes y dinámicos. Estos métodos enfrentan limitaciones para distinguir con precisión entre tráfico normal y malicioso, y para ajustarse a amenazas emergentes, lo que puede llevar a falsos positivos o falsos negativos.

- **Limitaciones de los enfoques ML**: Muchos dependen de un número reducido de características (como solo la IP de origen), lo que puede no capturar adecuadamente todos los comportamientos de ataque, especialmente cuando los atacantes incrustan código malicioso en los paquetes de payload. La extracción manual de características es costosa y propensa a errores. Además, los enfoques de ML sufren de problemas de desbalanceo de datos y la naturaleza dinámica de los ataques, lo que requiere un reentrenamiento continuo.

- **Limitaciones de los enfoques DL**: Aunque ofrecen una precisión superior, enfrentan desafíos con grandes dimensiones de entrada y volúmenes de datos debido a problemas como la dimensionalidad y la difusión de gradientes. El algoritmo de descenso de gradiente puede tener dificultades para converger eficientemente en espacios de alta dimensión, lo que lleva a tiempos de entrenamiento más largos y mayor complejidad computacional. El mayor tiempo de procesamiento y uso de recursos asociados con el análisis de datos de tráfico de red puede impedir la eficiencia de los sistemas de detección basados en DNN, particularmente en escenarios en tiempo real.

- **Limitaciones de los enfoques blockchain**: Aunque prometedores, enfrentan desafíos como la latencia potencial, la escalabilidad, y problemas de acceso no autorizado y fuga de datos.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen un enfoque híbrido que combina la detección basada en entropía (estadística) con técnicas de clustering de ML (K-means). Este enfoque ofrece varias ventajas:
- **Detección en tiempo real** mediante monitoreo continuo de la entropía del sistema.
- **Adaptabilidad** a técnicas de ataque cambiantes al modificar dinámicamente las habilidades de detección en respuesta al comportamiento de la red observado.
- **Escalabilidad** para manejar la complejidad y el volumen de tráfico en sistemas SDN.
- **Reducción de falsos positivos** al combinar el análisis de entropía con clustering.
- **Mejora de la eficiencia de detección** y la resiliencia de la red.

---

## Descripción del Aporte

El aporte principal de los autores es un enfoque híbrido que combina la detección basada en entropía con clustering K-means para detectar y mitigar ataques DDoS en entornos SDN. El problema que abordan es crítico: los ataques DDoS en SDN explotan la arquitectura centralizada para inundar el controlador y los switches con tráfico malicioso, degradando la disponibilidad y calidad del servicio, con graves consecuencias económicas y operativas para las organizaciones.

### El sistema propuesto consta de dos fases principales que operan secuencialmente:

**Fase 1: Detección basada en entropía (Módulo de detección de entropía):**

El sistema divide el flujo de solicitudes en múltiples intervalos de tiempo de igual duración (T). Después de cada intervalo, se calcula la entropía del sistema utilizando la fórmula de Shannon:

H(X) = -∑ p(xi) × log(p(xi))

donde X representa el conjunto de usuarios activos en el intervalo y p(xi) es la probabilidad de que un usuario i haya realizado una solicitud. La entropía es una medida de desorden o aleatoriedad en el sistema. Los autores introducen un supuesto fundamental: durante un ataque DDoS, la aleatoriedad del sistema disminuye, lo que se traduce en una reducción de la entropía.

Cuando la entropía del sistema cae por debajo de un umbral inferior predefinido (β_lower), el sistema considera que la red está bajo ataque y activa la segunda fase.

**Fase 2: Clustering con K-means (Módulo de clustering de machine learning):**

Una vez detectado un ataque, el sistema aplica el algoritmo K-means para agrupar a los usuarios activos del intervalo anterior en tres grupos distintos:
- **Usuarios normales**: Aquellos con patrones de solicitud típicos.
- **Usuarios sospechosos**: Aquellos con patrones ligeramente anómalos.
- **Posibles atacantes**: Aquellos con patrones claramente anómalos.

El valor de "k" se establece en 3, alineándose con la necesidad de clasificar a los usuarios en estas tres categorías. Después del clustering, el sistema evalúa el impacto de cada usuario en los grupos sospechoso y de posibles atacantes sobre la entropía del grupo de usuarios normales, utilizando la siguiente fórmula:

ratio(h) = H(X) / H(X ∪ ui)

donde H(X ∪ ui) es la entropía del grupo normal después de añadir el usuario ui, y H(X) es la entropía del grupo normal antes de la adición. Se establecen umbrales distintos para el cambio en la relación de entropía: δ_susp (para el grupo sospechoso) y δ_attack (para el grupo de posibles atacantes). Si la relación de cambio (ratio(h)) es menor que el umbral correspondiente (δi), el usuario se identifica como un atacante potencial.

### Optimización del cálculo de entropía:

Los autores proponen una optimización para reducir la complejidad computacional del cálculo de entropía de O(n²) a O(n). La derivación matemática muestra que:

H(X) = -∑ x_i log x_i + log(N)

donde Cx = ∑ x_i log x_i y N = ∑ x_i. Para la inserción de un usuario uj:

H(X ∪ uj) = (N + uj) - (uj log uj) - Cx + log(N + uj)

Esta optimización permite calcular rápidamente el impacto de cada usuario sospechoso en la entropía del sistema.

### Parámetros del sistema:

El sistema incluye cuatro parámetros clave que influyen en su rendimiento:
1. **Tamaño del intervalo (Interval Size)**: La duración después de la cual el sistema considera completado un intervalo.
2. **Umbral inferior de entropía (β_lower)**: La entropía por debajo de la cual el sistema considera que está bajo ataque.
3. **Delta de entropía del cluster sospechoso (δ_susp)**: La relación de entropía por debajo de la cual el sistema considera al usuario sospechoso como atacante.
4. **Delta de entropía del cluster de atacantes (δ_attack)**: La relación de entropía por debajo de la cual el sistema considera al posible atacante como atacante cuando se prueba contra el grupo de usuarios normales.

### Ventajas del enfoque híbrido:

- **Detección en tiempo real**: Mediante el monitoreo continuo de la entropía y el clustering.
- **Adaptabilidad**: Modificación dinámica de las habilidades de detección.
- **Escalabilidad**: Manejo de la complejidad y el volumen de tráfico en sistemas SDN grandes.
- **Reducción de falsos positivos**: Combinación de entropía y clustering.

El impacto en la empresa y la sociedad es significativo: al detectar y mitigar ataques DDoS en tiempo real, el sistema protege la disponibilidad y calidad de los servicios de red, evita interrupciones del servicio, protege datos sensibles y reduce el riesgo de pérdidas económicas y daños reputacionales para las organizaciones que dependen de redes SDN.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que combina técnicas estadísticas y de machine learning. El proceso se desarrolla en las siguientes etapas:

1. **Preprocesamiento de datos**: Extraen características importantes de los datasets basándose en técnicas de extracción de características basadas en flujos. Las características clave incluyen: dirección IP de origen, dirección IP de destino, puerto de origen, puerto de destino, protocolo, timestamp y etiqueta. Los datos se limpian eliminando información faltante. Luego, los datos se agrupan en intervalos de tiempo de duración T, donde cada grupo contiene solicitudes del mismo identificador de usuario (definido como la combinación IP origen - IP destino) dentro del intervalo.

2. **Normalización**: Después de cada intervalo de tiempo, las frecuencias de solicitudes de los usuarios activos se normalizan utilizando la siguiente ecuación:

   x̂i = (xi - xmin) / (xmax - xmin)

   donde x̂i es la frecuencia normalizada del usuario i, xi es la frecuencia del usuario i en el conjunto X, xmin es la frecuencia mínima en el conjunto X, y xmax es la frecuencia máxima en el conjunto X. Esta normalización asegura que las frecuencias estén escaladas apropiadamente para un análisis robusto.

3. **Implementación del módulo de detección de entropía**: Implementan el algoritmo de detección basado en entropía. Para cada intervalo, el sistema:
   - Normaliza las frecuencias de los usuarios.
   - Calcula la entropía del sistema H(X).
   - Si H(X) < β_lower, el sistema llama a la función DetectAttackers(X) para identificar atacantes potenciales.

4. **Implementación del módulo de clustering K-means**: Cuando se detecta un ataque, el sistema aplica el algoritmo K-means para agrupar a los usuarios en tres clusters (normal, sospechoso y posible atacante). Para cada usuario en los clusters sospechoso y de posibles atacantes, el sistema calcula la relación de cambio de entropía utilizando la optimización propuesta:

   H(X ∪ uj) = (N + uj) - (uj log uj) - Cx + log(N + uj)

   Si la relación ratio(h) = H(X ∪ ui) / H(X) es menor que el umbral correspondiente (δ_susp o δ_attack), el usuario se marca como atacante.

5. **Entrenamiento de parámetros**: Entrenan el sistema determinando los valores óptimos para los cuatro parámetros clave (tamaño del intervalo, β_lower, δ_susp, δ_attack). Utilizan autoevaluación en el dataset CIC-IDS2017 para identificar los valores que maximizan la precisión y minimizan los falsos positivos. Observan que cada parámetro sigue una curva de distribución normal, donde la precisión aumenta con el parámetro hasta alcanzar un pico y luego disminuye.

6. **Selección de datasets para validación**: Seleccionan tres datasets modernos para la evaluación:
   - **CIC-IDS2017**: 50 GB de datos durante 5 días, incluyendo ataques DoS y DDoS.
   - **CSE-CIC-2018**: 500 GB de datos durante 2 días, incluyendo fuerza bruta, DoS, botnet y DDoS.
   - **CIC-DDoS2019**: 150 GB de datos durante 2 días, incluyendo ataques DDoS reflectivos modernos (DNS, NetBIOS, LDAP, MSSQL, UDP, SYN, NTP, SNMP, WebDDoS).

7. **Implementación de métricas de evaluación**: Implementan métricas estándar para evaluar el rendimiento: accuracy, FPR (False Positive Rate), TPR (True Positive Rate, recall), F1-score, G-means y MCC (Matthews Correlation Coefficient). El MCC proporciona una medida equilibrada de la calidad del clasificador, mientras que G-means evalúa el rendimiento considerando tanto la sensibilidad como la especificidad.

8. **Autoevaluación y comparación**: Realizan una autoevaluación detallada en el dataset CIC-IDS2017 para entender el comportamiento de los parámetros del sistema. Luego, comparan el rendimiento del sistema con técnicas del estado del arte (Lucid, MLP, 1D-CNN, LSTM, 1D-CNN+LSTM, Cil et al., Alghazzawi et al.) en los tres datasets.

9. **Análisis de resultados**: Analizan los resultados para identificar fortalezas y limitaciones del sistema, y discuten posibles direcciones para investigación futura.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de su enfoque híbrido para resolver el problema de detección de ataques DDoS en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan tres datasets modernos disponibles públicamente: CIC-IDS2017 (50 GB, 5 días), CSE-CIC-2018 (500 GB, 2 días) y CIC-DDoS2019 (150 GB, 2 días). Estos datasets incluyen tráfico de red con etiquetas que distinguen entre tráfico normal y varios tipos de ataques DDoS. Los autores utilizan el 90% de cada dataset para entrenamiento y el 10% para pruebas.

2. **Autoevaluación de parámetros**: Realizan una autoevaluación detallada en el dataset CIC-IDS2017 para analizar el impacto de los tres parámetros principales (β_lower, δ_attack, δ_susp) en el rendimiento del sistema. Para cada parámetro, varían su valor y miden el impacto en accuracy, FPR y F1-score.

3. **Medición de métricas de rendimiento**: Calculan las siguientes métricas para cada dataset: accuracy, FPR (False Positive Rate), TPR (True Positive Rate o recall), F1-score, G-means y MCC. Los resultados se presentan en tablas comparativas.

4. **Comparación con técnicas del estado del arte**: Comparan su sistema con varias técnicas establecidas:
   - En CIC-IDS2017: Comparan con Lucid (Doriguzzi-Corin et al., 2020), MLP, 1D-CNN, LSTM y 1D-CNN+LSTM (Roopak et al., 2019).
   - En CSE-CIC-2018: Comparan con Lucid.
   - En CIC-DDoS2019: Comparan con Cil et al. (2021) y Alghazzawi et al. (2021).

5. **Análisis de resultados por dataset**:
   - **CIC-IDS2017**: El sistema propuesto logra una precisión del 99.94%, FPR del 0.0000%, TPR del 99.93% y F1-score de 0.9997, superando a Lucid (99.67%), MLP (86.34%), 1D-CNN (95.14%), LSTM (96.24%) y 1D-CNN+LSTM (97.16%).
   - **CSE-CIC-2018**: El sistema logra una precisión del 99.92%, FPR del 0.0045%, TPR del 99.92% y F1-score de 0.9996, superando ligeramente a Lucid (99.87%).
   - **CIC-DDoS2019**: El sistema logra una precisión del 99.97%, FPR del 0.0023%, TPR del 99.90% y F1-score de 0.9992, superando significativamente a Cil et al. (94.57%) y Alghazzawi et al. (94.52%).

6. **Análisis de la complejidad computacional**: Demuestran que el sistema tiene complejidad temporal O(n) y complejidad espacial O(n), donde n es el número de usuarios activos en el intervalo. La optimización propuesta reduce la complejidad del cálculo de entropía de O(n²) a O(n).

7. **Análisis de la robustez**: Evalúan la capacidad del sistema para manejar diferentes tipos de ataques DDoS, incluyendo ataques de baja tasa y alta tasa, así como ataques reflectivos modernos (DNS, NetBIOS, LDAP, MSSQL, UDP, SYN, NTP, SNMP, WebDDoS).

8. **Validación de la reducción de falsos positivos**: Demuestran que la combinación de la detección basada en entropía con clustering K-means reduce significativamente los falsos positivos en comparación con los enfoques que solo utilizan entropía o solo utilizan ML.

---

## Métricas y Resultados

Los autores utilizan un conjunto completo de métricas de rendimiento para evaluar su sistema: accuracy (precisión), FPR (False Positive Rate), TPR (True Positive Rate o recall), F1-score, G-means y MCC (Matthews Correlation Coefficient). Estas métricas se calculan a partir de la matriz de confusión y proporcionan una evaluación equilibrada del rendimiento del clasificador.

### Resultados obtenidos en los tres datasets:

| Dataset | Accuracy | FPR (%) | TPR (%) (Recall) | F1-score | G-means | MCC |
|---|---|---|---|---|---|---|
| CIC-IDS2017 | 99.94% | 0.0000 | 99.93% | 0.9997 | 0.9997 | 0.7298 |
| CSE-CIC-2018 | 99.92% | 0.0045 | 99.92% | 0.9996 | 0.9973 | 0.7043 |
| CIC-DDoS2019 | 99.97% | 0.0023 | 99.90% | 0.9992 | 0.9984 | 0.8127 |

### Comparación con técnicas del estado del arte:

**En CIC-IDS2017, el sistema supera a:**
- Lucid (99.67% accuracy, 0.59% FPR)
- MLP (86.34% accuracy)
- 1D-CNN (95.14% accuracy)
- LSTM (96.24% accuracy)
- 1D-CNN+LSTM (97.16% accuracy)

**En CSE-CIC-2018, el sistema supera a:**
- Lucid (99.87% accuracy)

**En CIC-DDoS2019, el sistema supera a:**
- Cil et al. (94.57% accuracy)
- Alghazzawi et al. (94.52% accuracy)

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de detección de DDoS: precisión general, sensibilidad (capacidad de detectar ataques), especificidad (capacidad de evitar falsos positivos), y métricas equilibradas como F1-score, G-means y MCC que son particularmente útiles cuando hay desbalanceo en los datasets.

El enfoque híbrido que combina entropía con clustering K-means es particularmente acertado por varias razones:
1. La detección basada en entropía proporciona una alerta temprana y eficiente de posibles ataques, con una complejidad computacional baja O(n).
2. El clustering K-means permite un análisis más detallado de los patrones de comportamiento de los usuarios, identificando no solo a los atacantes obvios sino también a los sospechosos.
3. La optimización del cálculo de entropía (reduciendo de O(n²) a O(n)) hace que el sistema sea escalable y adecuado para entornos SDN grandes y dinámicos.
4. El sistema es adaptable a diferentes tipos de ataques DDoS, incluyendo ataques de baja tasa y ataques reflectivos modernos.

Sin embargo, hay aspectos que podrían mejorarse:
1. El sistema depende de la selección adecuada de los parámetros (β_lower, δ_susp, δ_attack), que requieren entrenamiento y pueden variar según las características de la red.
2. El sistema se evalúa en datasets públicos, pero no en un entorno SDN real con tráfico en vivo. La validación en un testbed real sería un valor añadido significativo.
3. Aunque el sistema detecta ataques DDoS, no aborda explícitamente la mitigación de los ataques detectados.
4. El sistema utiliza K-means con k=3, que puede no ser óptimo para todos los escenarios; un enfoque que determine dinámicamente el número óptimo de clusters podría mejorar aún más el rendimiento.

---

## Observaciones Críticas

El artículo presenta un enfoque híbrido innovador y bien fundamentado para la detección de ataques DDoS en SDN, combinando técnicas estadísticas (entropía) con machine learning (clustering K-means). A continuación, realizo algunas observaciones y críticas constructivas:

1. **Validación en entornos reales**: Aunque los autores utilizan tres datasets modernos y ampliamente reconocidos (CIC-IDS2017, CSE-CIC-2018, CIC-DDoS2019), la evaluación se limita a datos estáticos. Sería interesante validar el sistema en un entorno SDN real con tráfico en vivo y ataques en tiempo real para demostrar su eficacia en condiciones operativas reales, incluyendo la latencia de detección y la capacidad de respuesta en tiempo real.

2. **Mitigación de ataques**: El artículo se centra exclusivamente en la detección de ataques DDoS, pero no aborda la mitigación. Aunque los autores mencionan que la detección permite iniciar medidas de mitigación, no se proporciona una estrategia concreta de mitigación ni se evalúa su efectividad. Un sistema completo de defensa debería incluir tanto detección como mitigación.

3. **Dependencia de parámetros**: El rendimiento del sistema depende críticamente de la selección adecuada de los parámetros (β_lower, δ_susp, δ_attack). Aunque los autores demuestran un comportamiento consistente en CIC-IDS2017, la generalización a otros entornos de red podría requerir un ajuste fino adicional. Los autores no discuten cómo se podrían adaptar automáticamente estos parámetros en diferentes entornos.

4. **Ataques de baja tasa**: Aunque el sistema está diseñado para detectar tanto ataques de alta como de baja tasa, la evaluación no proporciona un análisis detallado de su rendimiento específicamente en ataques de baja tasa. Estos ataques están diseñados para evadir la detección basada en entropía y podrían representar un desafío para el sistema.

5. **Clustering K-means con k=3**: La elección de k=3 (normal, sospechoso, atacante) podría no ser óptima en todos los escenarios. En algunos casos, podría haber múltiples tipos de atacantes con diferentes patrones de comportamiento, o podría no haber suficientes usuarios para justificar tres clusters. Un enfoque que determine dinámicamente el número óptimo de clusters (por ejemplo, usando el método del codo o la silueta) podría mejorar la flexibilidad del sistema.

6. **Complejidad computacional del clustering**: Aunque la optimización del cálculo de entropía reduce la complejidad a O(n), el clustering K-means tiene una complejidad de O(k × n × I), donde I es el número de iteraciones. En redes con un gran número de usuarios activos, el clustering podría convertirse en un cuello de botella. Los autores no proporcionan mediciones detalladas del tiempo de procesamiento del clustering en escenarios de alta carga.

7. **Falsos negativos en el cluster sospechoso**: Los autores observan que ningún atacante verdadero cae en el cluster sospechoso en sus datasets. Esto sugiere que el cluster sospechoso puede ser redundante en la práctica. Aunque los autores argumentan que es "más seguro" mantenerlo, esto añade complejidad sin beneficios claros en los datasets evaluados.

8. **Integración con SDN**: El artículo no aborda cómo se integraría el sistema en un controlador SDN real, ni cómo se comunicaría con los switches OpenFlow para implementar medidas de mitigación. Esta brecha entre la detección y la acción práctica limita la aplicabilidad inmediata del sistema en entornos SDN reales.

9. **Generalización a otros tipos de ataques**: Aunque el sistema se evalúa en ataques DDoS, no está claro cómo se comportaría con otros tipos de ataques (como ataques de suplantación, ataques de capa de aplicación, o ataques zero-day). Los autores mencionan la adaptabilidad como una ventaja, pero no proporcionan evidencia empírica de la capacidad del sistema para detectar ataques no vistos durante el entrenamiento.

---

## Relevancia para el Proyecto

Este artículo es especialmente relevante porque presenta un enfoque híbrido que combina técnicas estadísticas (entropía) y machine learning (K-means) para la detección de DDoS en SDN. Los aspectos clave aplicables a nuestro proyecto son:

1. **Detección basada en entropía como mecanismo de alerta temprana**: La entropía proporciona una detección rápida de posibles ataques, activando el clustering solo cuando es necesario, lo que reduce la carga computacional.

2. **Clustering K-means para clasificación de usuarios**: La agrupación de usuarios en tres categorías (normal, sospechoso, atacante) permite una identificación más precisa de los atacantes.

3. **Optimización del cálculo de entropía**: La reducción de O(n²) a O(n) hace que el sistema sea escalable para redes grandes.

4. **Alta precisión**: Los resultados (>99.9% en todos los datasets) demuestran la efectividad del enfoque híbrido.

5. **Reducción de falsos positivos**: La combinación de entropía y clustering reduce significativamente los falsos positivos en comparación con enfoques que solo usan entropía o solo ML.

Aunque el artículo no cubre mitigación, su enfoque de detección proporciona una base sólida para la fase de detección de nuestro sistema SDN-ML, y los principios de clustering pueden adaptarse para incluir mecanismos de mitigación.

---

**Referencia:**  
Hassan, A. I., Abd El Reheem, E., & Guirguis, S. K. (2024). An entropy and machine learning based approach for DDoS attacks detection in software defined networks. *Scientific Reports (Nature)*, 14, 18159.