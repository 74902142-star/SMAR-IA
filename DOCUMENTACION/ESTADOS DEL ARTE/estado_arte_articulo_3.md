# Estado del Arte - Artículo 3: Detection of DDoS Attack in SDN and Its Protocol-wise Analysis using ML

**Autor(es):** Nisha Ahuja, Gaurav Singal, Debajyoti Mukhopadhyay  
**Título:** Detection of DDoS Attack in Software-Defined Networking Environment and Its Protocol-wise Analysis using Machine Learning  
**Journal:** (Artículo sin información de journal en el PDF proporcionado)  
**Año:** 2020-2022 (según referencias)  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de los ataques DDoS en redes definidas por software (SDN). Explican que los ataques DDoS representan una gran amenaza para organizaciones y sus stakeholders, ya que al ser exitosos, los usuarios legítimos quedan privados de los servicios de la red, causando pérdidas de tiempo y dinero. Señalan que no solo las redes tradicionales son víctimas de ataques DDoS, sino que incluso las redes modernas basadas en tecnología SDN son susceptibles a ellos debido a su arquitectura centralizada.

Los autores revisan exhaustivamente los trabajos existentes sobre detección de DDoS en SDN. Mencionan el estudio de Tan et al., que registró registros de tráfico en la red como imágenes y desplegó análisis de coherencia multivariante para detectar el tráfico con máxima precisión, utilizando el método de distancia Earthmovers basado en la distancia medida entre distribuciones de probabilidad. También citan a Garg et al., que desplegaron redes neuronales artificiales con un algoritmo de entrenamiento sobre un conjunto de datos, contrastando esta metodología con otras técnicas como back-propagation, SVMs, chi-cuadrado y Snort, logrando una precisión de detección de ataques del 98%.

Los autores mencionan el trabajo de Yan et al., que consideraron diferentes características para detectar la ocurrencia de un ataque, tomando la dirección IP de destino como uno de los parámetros principales detectados mediante entropía. También citan a Cui et al., que desplegaron un algoritmo de red neuronal para reducir la carga de trabajo de controladores y switches como medio de detectar el ataque de manera más rápida, utilizando algoritmos de clasificación basados en entropía para observar ataques DDoS de bajo y alto volumen.

Los autores revisan el trabajo de Fallahi et al., que implementaron su modelo utilizando dos algoritmos de minería de datos (Ripper y C5.0) en datasets UNB-ISCX, logrando una precisión del 99% en la detección de ataques. También mencionan a Wang et al., que utilizaron una técnica de selección de características en conjunto con un perceptrón multicapa dinámico para identificar el ataque, con un mecanismo de retroalimentación para reiniciar el sistema si la detección no era precisa.

Los autores citan a Liang y Znati, que utilizaron enfoques estadísticos para predecir ataques en contraste con técnicas de ML, utilizando distribuciones tradicionales para pronosticar comportamientos normales y anormales de la red, junto con clasificadores como K-means, SVMs y árboles de decisión. También mencionan a Criscuolo, que utilizó un método basado en entropía junto con un algoritmo de clasificación para distinguir entre ataques DDoS de bajo y alto volumen.

Los autores revisan el trabajo de Zhong y Yue, que propusieron un modelo de mitigación de ataques basado en un algoritmo de minería de datos, utilizando un algoritmo de clustering FCM y un algoritmo de asociación a priori para extraer el modelo de tráfico de red y el modelo de estado del protocolo de paquetes de red, seguido de la definición de un umbral del modelo de detección. También citan a Wu et al., que presentaron un enfoque de detección que involucra un árbol de decisión y análisis de relación grey, utilizando 15 atributos diferentes para monitorear el flujo de paquetes de datos y combinar las tasas de flags TCP SYN y ACK para reflejar el flujo de tráfico en el canal.

Finalmente, los autores mencionan a Chen et al., que presentaron un enfoque de clasificación basado en redes neuronales probabilísticas para clasificar tráfico y detectar ataques DDoS, combinando la regla de decisión de Bayes con una red neuronal de función de base radial. También citan a Li et al., que mejoraron la precisión de detección combinando SVMs con otras técnicas, utilizando SNORT y un firewall para desarrollar un módulo de sistema inteligente de prevención.

Los autores identifican que, aunque existen múltiples enfoques para la detección de DDoS en SDN, muchos se centran en la detección general sin un análisis específico por protocolo. Además, señalan que algunos enfoques utilizan un número reducido de características o dependen de técnicas computacionalmente costosas.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Falta de análisis por protocolo**: Muchos enfoques existentes se centran en la detección general de ataques sin realizar un análisis específico por protocolo. Esto limita la capacidad de los administradores de red para comprender qué tipos de ataques son más prevalentes y cómo se manifiestan en diferentes protocolos.
- **Limitaciones de los métodos basados en entropía**: Aunque son efectivos para detectar cambios en la aleatoriedad del tráfico, pueden no ser suficientes para distinguir entre diferentes tipos de ataques (TCP SYN, UDP flood, ICMP) que tienen diferentes patrones de comportamiento.
- **Dependencia de características reducidas**: Algunos métodos dependen de un número reducido de características (como solo la IP de origen), lo que puede no capturar adecuadamente todos los comportamientos de ataque.
- **Alta complejidad computacional**: Muchos enfoques utilizan técnicas computacionalmente costosas (como redes neuronales profundas) que pueden no ser adecuadas para entornos SDN con recursos limitados.
- **Falta de validación con AUC-ROC**: Algunos trabajos no validan adecuadamente sus modelos con métricas como AUC-ROC, lo que limita la capacidad de evaluar su rendimiento en diferentes umbrales de clasificación.
- **Falta de comparativa de algoritmos**: Existe una falta de estudios que comparen múltiples algoritmos de machine learning en un mismo dataset SDN para la detección de DDoS por protocolo.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen un estudio que utiliza cinco algoritmos de machine learning (KNN, Logistic Regression, MLP, ID3 y SGD) para detectar ataques DDoS en un dataset SDN específico, con un análisis detallado por protocolo (TCP SYN, UDP flood, ICMP). Además, validan los modelos con curvas ROC-AUC y seleccionan características mediante análisis de correlación y Random Forest para optimizar el rendimiento.

---

## Descripción del Aporte

El aporte principal de los autores es un estudio comparativo de algoritmos de machine learning para la detección de ataques DDoS en SDN con análisis específico por protocolo. El problema que abordan es crítico: los ataques DDoS pueden causar graves daños a organizaciones y sus stakeholders, privando a los usuarios legítimos de los servicios de red y causando pérdidas de tiempo y dinero. Las redes SDN, aunque ofrecen flexibilidad y programabilidad, son particularmente vulnerables a estos ataques debido a su arquitectura centralizada.

El sistema propuesto consta de una arquitectura con dos módulos principales:

### 1. Módulo de gestión de datos (Data Management Module):
Comprende la recolección de datos, el preprocesamiento de datos y la creación de subconjuntos del dataset original basados en el protocolo. La recolección de datos se logra a partir del dataset SDN obtenido de Mendeley Data (Ahuja et al., 2020). Durante el paso de preprocesamiento, se eliminan los valores nulos o faltantes del dataset. Luego, se crean tres subconjuntos del dataset preprocesado basados en los tres protocolos principales (TCP, UDP, ICMP). Así, para esta investigación, se consideran cuatro datasets preprocesados:
- El dataset SDN completo para la detección de ataques DDoS independientemente del protocolo involucrado.
- El dataset basado en el protocolo TCP para la detección de ataques TCP SYN.
- El dataset basado en el protocolo UDP para la detección de ataques UDP flood.
- El dataset basado en el protocolo ICMP para la detección de ataques ICMP.

### 2. Módulo de cálculo y detección (Calculation and Detection Module):
Calcula las características y realiza la detección requerida de los ataques DDoS. Las características (o atributos del dataset) que muestran mayores covarianzas entre sí se seleccionan para el entrenamiento y prueba de los modelos. El dataset bajo consideración se divide en conjuntos de entrenamiento y prueba en una proporción de 70:30, dejando el 30% de los datos para validación.

### Selección de características:
- **Para la detección general de DDoS**: Se seleccionan 19 características "a priori" para el preprocesamiento: dt, switch, pkctcount, bytecount, dur, dur_nsec, tot_dur, flows, packets, pkterflow, byteperflow, pktrate, Pairflow, port_no, tx_bytes, rx_bytes, tx_kbps, rx_kbps, y tot_kbps. La etiqueta "label" es la variable objetivo. Tras calcular los valores de correlación (umbral > 0.70), se aceptan 12 características.
- **Para la detección de ataques TCP SYN**: Mediante un clasificador Random Forest, se aceptan 8 características.
- **Para la detección de ataques ICMP**: Se aceptan 6 características.
- **Para la detección de ataques UDP flood**: Se seleccionan características similares con altos valores de correlación.

### Algoritmos de machine learning implementados:
- **Logistic Regression (LR)**: Modelo lineal para clasificación binaria.
- **K-Nearest Neighbors (KNN)**: Algoritmo basado en instancias con tres vecinos más cercanos.
- **Multilayer Perceptron (MLP)**: Red neuronal feed-forward con valor alfa de 0.005.
- **Iterative Dichotomiser 3 (ID3)**: Algoritmo de árbol de decisión.
- **Stochastic Gradient Descent (SGD)**: Optimizador para modelos lineales.

### Análisis por protocolo:
Una contribución clave del estudio es el análisis específico por protocolo de los ataques DDoS, permitiendo a los administradores de red comprender qué tipos de ataques son más prevalentes y cómo se manifiestan en diferentes protocolos.

### Validación con AUC-ROC:
Los autores validan los modelos utilizando curvas ROC-AUC (Area Under the Curve of Receiver Operator Characteristic), que miden la capacidad del clasificador para distinguir entre clases positivas y negativas en diferentes umbrales.

El impacto en la empresa y la sociedad es significativo: el estudio proporciona una guía práctica para los profesionales de la seguridad sobre qué algoritmos de ML son más efectivos para detectar ataques DDoS en SDN, tanto a nivel general como por protocolo específico.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que combina la selección de características, la implementación de múltiples algoritmos de ML, y la validación mediante curvas ROC-AUC. El proceso se desarrolla en las siguientes etapas:

1. **Recolección de datos**: Utilizan un dataset SDN específico para ataques DDoS obtenido de Mendeley Data (Ahuja et al., 2020). El dataset contiene registros de tráfico de red en un entorno SDN con ataques DDoS.

2. **Preprocesamiento de datos**: Se eliminan los valores nulos o faltantes del dataset. Luego, se crean tres subconjuntos del dataset preprocesado basados en los tres protocolos principales (TCP, UDP, ICMP), resultando en cuatro datasets para el análisis:
   - Dataset completo (detección general de DDoS)
   - Dataset TCP (detección de ataques TCP SYN)
   - Dataset UDP (detección de ataques UDP flood)
   - Dataset ICMP (detección de ataques ICMP)

3. **Selección de características (Feature Selection)**: Para cada uno de los cuatro datasets, los autores realizan un proceso de selección de características:
   - **Cálculo de correlación**: Se calculan los valores de covarianza entre las características y la variable objetivo ("label"). Se seleccionan las características con un valor de correlación superior a 0.70 para la detección general de DDoS.
   - **Clasificador Random Forest**: Para la detección de ataques TCP SYN, ICMP y UDP flood, se utiliza un clasificador Random Forest para encontrar los valores de correlación de las características. Las características con mayor correlación se seleccionan para el entrenamiento.

4. **División de datos**: Cada dataset se divide en conjuntos de entrenamiento y prueba en una proporción de 70:30, dejando el 30% de los datos para validación.

5. **Implementación de algoritmos de machine learning**: Implementan cinco algoritmos utilizando bibliotecas estándar de Python:
   - Logistic Regression (LR)
   - K-Nearest Neighbors (KNN) con k=3
   - Multilayer Perceptron (MLP) con alfa=0.005
   - Iterative Dichotomiser 3 (ID3)
   - Stochastic Gradient Descent (SGD)

6. **Entrenamiento y prueba**: Cada algoritmo se entrena con el conjunto de entrenamiento (70%) y se prueba con el conjunto de validación (30%) para cada uno de los cuatro datasets. Se registran las predicciones y se generan matrices de confusión para cada modelo.

7. **Evaluación de métricas**: Calculan accuracy, precision, recall (TPR), F1-score, FPR, TNR (especificidad), y FNR.

8. **Validación con AUC-ROC**: Generan curvas ROC que comparan TPR vs FPR en diferentes umbrales de clasificación. Calculan el AUC para cada modelo.

9. **Análisis comparativo**: Comparan el rendimiento de los cinco algoritmos en los cuatro datasets, identificando cuáles son más efectivos para la detección general de DDoS y para la detección específica por protocolo.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de los cinco algoritmos de machine learning para resolver el problema de detección de ataques DDoS en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan el dataset SDN para ataques DDoS disponible en Mendeley Data (Ahuja et al., 2020). Los experimentos se realizan en un entorno de desarrollo estándar (Python con bibliotecas de ML).

2. **Creación de cuatro escenarios de prueba**:
   - Escenario 1: Detección general de DDoS (dataset completo)
   - Escenario 2: Detección de ataques TCP SYN (dataset TCP)
   - Escenario 3: Detección de ataques UDP flood (dataset UDP)
   - Escenario 4: Detección de ataques ICMP (dataset ICMP)

3. **Entrenamiento de modelos**: Para cada escenario, los cinco algoritmos se entrenan con el 70% de los datos. Los parámetros se mantienen en sus configuraciones por defecto con ajustes menores (k=3 para KNN, alfa=0.005 para MLP).

4. **Prueba de modelos**: Cada modelo entrenado se prueba con el 30% de los datos reservados para validación.

5. **Generación de matrices de confusión**: Para cada modelo y escenario, se genera una matriz de confusión con TP, TN, FP y FN.

6. **Cálculo de métricas de rendimiento**:
   - Accuracy: Proporción de predicciones correctas.
   - Precision: Proporción de verdaderos positivos entre todas las predicciones positivas.
   - Recall (TPR): Proporción de verdaderos positivos entre todos los casos positivos reales.
   - F1-Score: Media armónica de precision y recall.
   - FPR: Proporción de falsos positivos entre todos los casos negativos reales.
   - TNR (Specificity): Proporción de verdaderos negativos entre todos los casos negativos reales.
   - FNR: Proporción de falsos negativos entre todos los casos positivos reales.

7. **Generación de curvas ROC**: Generan curvas ROC para cada modelo en cada escenario, calculando el AUC.

8. **Análisis de resultados**: Comparan el rendimiento de los cinco algoritmos en los cuatro escenarios.

9. **Presentación de resultados**: Los resultados se presentan en tablas y gráficos, incluyendo figuras de accuracy, curvas ROC, y tablas de correlación y AUC.

10. **Conclusiones**: Concluyen que ID3 es el más efectivo para la detección general de DDoS, mientras que para la detección por protocolo, KNN e ID3 muestran un rendimiento sobresaliente. Todos los modelos logran una precisión superior al 98% para la detección de ataques ICMP.

---

## Métricas y Resultados

Los autores utilizan un conjunto completo de métricas de rendimiento para evaluar los algoritmos de machine learning: accuracy, precision, recall (TPR), F1-score, FPR, TNR (specificity), FNR y AUC-ROC.

### Resultados obtenidos:

**Detección general de DDoS:**
- **ID3**: Mayor accuracy (superior a los demás)
- **KNN y MLP**: Rendimiento comparable al ID3
- **LR y SGD**: Menor rendimiento, con SGD mostrando la accuracy más baja

**Detección de ataques TCP SYN:**
- **KNN e ID3**: Accuracy superior al 99%
- **MLP, LR y SGD**: Rendimiento decente pero inferior

**Detección de ataques UDP flood:**
- **Todos los modelos**: Accuracy superior al 90%

**Detección de ataques ICMP:**
- **LR, KNN, MLP e ID3**: Accuracy del 100%
- **SGD**: Accuracy ligeramente inferior

**AUC-ROC:**
- **ID3**: AUC más alto en la mayoría de los escenarios
- **SGD**: AUC de 0.5 en algunos casos (no mejor que clasificación aleatoria)

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de la evaluación de clasificadores: precisión general (accuracy), capacidad de detectar ataques (recall/TPR), capacidad de evitar falsos positivos (precision, FPR), y métricas equilibradas como F1-score y AUC-ROC. La inclusión del AUC-ROC es particularmente valiosa porque proporciona una medida de la capacidad de discriminación del modelo independiente del umbral de clasificación.

El enfoque del estudio es útil por varias razones:
1. La comparación de múltiples algoritmos (5) en el mismo dataset proporciona una base sólida para recomendar el algoritmo más adecuado.
2. El análisis por protocolo (TCP, UDP, ICMP) ofrece información práctica sobre qué tipos de ataques son más difíciles de detectar y qué algoritmos funcionan mejor para cada tipo.
3. La selección de características mediante correlación y Random Forest ayuda a reducir la dimensionalidad y mejorar el rendimiento, evitando el sobreajuste.

Sin embargo, hay aspectos que podrían mejorarse:
1. El estudio no proporciona detalles sobre el tiempo de entrenamiento y prueba de los algoritmos.
2. Aunque se comparan cinco algoritmos, todos son relativamente simples. La inclusión de algoritmos más avanzados como XGBoost, Random Forest o redes neuronales profundas podría proporcionar información adicional.
3. El estudio se basa en un único dataset SDN.
4. El estudio se centra en la detección, pero no aborda la mitigación de los ataques detectados.

---

## Observaciones Críticas

El artículo presenta un estudio comparativo útil de algoritmos de machine learning para la detección de DDoS en SDN con análisis específico por protocolo. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Falta de información sobre la publicación**: El PDF proporcionado no incluye información completa sobre el journal, volumen, número y año de publicación. Esto dificulta la correcta citación del artículo.

2. **Dataset único**: El estudio se basa en un único dataset SDN (Ahuja et al., 2020, Mendeley Data). Aunque el dataset es específico para SDN, la generalización de los resultados a otros entornos SDN podría ser limitada.

3. **Falta de análisis de tiempo**: El estudio no proporciona métricas de tiempo de entrenamiento y prueba de los algoritmos. En un entorno SDN donde la detección en tiempo real es crucial, el tiempo de procesamiento es un factor clave.

4. **Algoritmos limitados**: Aunque se comparan cinco algoritmos, todos son relativamente simples. Algoritmos más modernos y potencialmente más eficientes como XGBoost, LightGBM, Random Forest o redes neuronales profundas (CNN, LSTM) no se incluyen en la comparación.

5. **Ausencia de mitigación**: El estudio se centra exclusivamente en la detección de ataques DDoS, pero no aborda la mitigación. Un sistema completo de defensa debería incluir tanto detección como mitigación.

6. **Selección de características inconsistente**: El proceso de selección de características varía entre los diferentes tipos de detección (general, TCP, UDP, ICMP). Aunque esto puede ser justificado por las diferencias en los patrones de ataque, la falta de un enfoque consistente dificulta la comparación directa entre los resultados.

7. **Formato y referencias**: El PDF tiene problemas de formato en la sección de referencias, con citas duplicadas y falta de numeración clara.

8. **SGD con AUC=0.5**: El hecho de que SGD tenga AUC=0.5 en algunos casos indica que el modelo no es mejor que una clasificación aleatoria. Sería interesante investigar por qué SGD tiene un rendimiento tan pobre.

9. **Falta de interpretabilidad**: El estudio no proporciona una interpretación detallada de por qué ciertos algoritmos funcionan mejor que otros en diferentes tipos de ataques.

10. **Métrica de G-mean y MCC**: El estudio no utiliza métricas como G-mean o MCC (Matthews Correlation Coefficient), que son particularmente útiles para conjuntos de datos desbalanceados.

---

## Relevancia para el Proyecto

Este artículo es relevante porque proporciona un análisis comparativo de algoritmos ML para detección de DDoS en SDN, con un enfoque específico en el análisis por protocolo (TCP, UDP, ICMP). Los resultados muestran que ID3 (árbol de decisión) y KNN son los más efectivos, especialmente para ataques TCP SYN. El enfoque de selección de características mediante correlación y Random Forest es aplicable a nuestro sistema. Sin embargo, el artículo se limita a la detección y no cubre mitigación, por lo que debe complementarse con otros trabajos que aborden la mitigación.

---

**Referencia:**  
Ahuja, N., Singal, G., & Mukhopadhyay, D. (2020-2022). Detection of DDoS Attack in Software-Defined Networking Environment and Its Protocol-wise Analysis using Machine Learning. *Mendeley Data* (Dataset).