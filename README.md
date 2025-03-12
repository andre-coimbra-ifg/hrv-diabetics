# vfc-diabeticos

Pré-processamento de dados de RRi para cálculo da HRV.

1. Para executar o código, inicie instalando as dependências necessárias:

    `pip install -r requirements.txt`

2. Em seguida, garanta que os dados estejam organizados na seguinte estrutura ou altere os caminhos no arquivo `src/config.py`:

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
