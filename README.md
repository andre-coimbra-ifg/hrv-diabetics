# vfc-diabetics

Pré-processamento de dados de RRi para cálculo da HRV.

Para executar o código, inicie instalando as dependências necessárias:

    pip install -r requirements.txt

Em seguida, garanta que os dados estejam organizados na seguinte estrutura ou altere os caminhos no arquivo `src/config.py`:

```plaintext
vfc-diabeticos/
├── data/
│   ├── control/
│   └── diabetic/
├── src/
│   ├── main.py
│   └── ...
├── README.md
└── requirements.txt
```

**A metodologia adotada pode ser resumida em 4 etapas:**

1. Descarte das 10 primeiras entradas de cada arquivo (paciente);

2. Avaliação da qualidade dos sinais de RRi e descarte dos arquivos que não atenderem
   ao limiar estabelecido. A análise da qualidade do sinal é realizada a partir da:
    - Detecção de Outliers;
    - Detecção de Batimentos Ectópicos;

3. Transformação dos sinais de RRi em NNi:
    - Substituindo os Outliers por meio da interpolação linear;
    - Substituindo os Batimentos Ectópicos por meio da interpolação linear;
    
4. Truncamento dos arquivos de NNi, mantendo a parte inicial do arquivo, em função do
   registro de menor duração em tempo (não em número de batimentos).

Ao final, os resultados serão salvos no diretório `data/output/`, considerando 2 subdiretórios:

- `denoised/`: com os NNi completos
- `truncated/`: com os NNi truncados
    
- Além disso, será salvo um relatório com informações estatísticas básicas sobre o
  diretório 'truncated/', conforme exemplo abaixo:
    
        +-----------------------+----------------------------------+
        | Info                  |          Control Group           |
        +=======================+==================================+
        | Directory             | ../data/output/truncated/control |
        +-----------------------+----------------------------------+
        | Number of Files       |                X                 |
        +-----------------------+----------------------------------+
        | Max Duration (min)    |                X                 |
        +-----------------------+----------------------------------+
        | File Max Duration     |         example_x_min.txt        |
        +-----------------------+----------------------------------+
        | Min Duration (min)    |                X                 |
        +-----------------------+----------------------------------+
        | File Min Duration     |         example_x_min.txt        |
        +-----------------------+----------------------------------+
        | Mean Duration (min)   |                X                 |
        +-----------------------+----------------------------------+
        | Quality Threshold (%) |               95.0               |
        +-----------------------+----------------------------------+
        | Mean Quality (%)      |                X                 |
        +-----------------------+----------------------------------+
        | Files Below Threshold |                0                 |
        +-----------------------+----------------------------------+
        | Files Above Threshold |                X                 |
        +-----------------------+----------------------------------+
