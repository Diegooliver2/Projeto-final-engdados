# Importar as bibliotecas
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('spark-pf').getOrCreate()

# Criar o dataframe do tipo stream, apontando para o servidor kafka e o tópico a ser consumido.
df = (spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "node-master:9092")
        .option("subscribe", "pf-topic.public.tabelapf")
        .option("startingOffsets", "earliest")
        .load()
)

schema = StructType([
    StructField("payload", StructType([
        StructField("after", StructType([
            StructField("id_proc", IntegerType(), True),
            StructField("vara", IntegerType(), True)
        ]))
    ]))
])

# Converter o valor dos dados do Kafka de formato binário para JSON usando a função from_json
dx = df.select(from_json(df.value.cast("string"), schema).alias("data")).select("data.payload.after.*")

# Realizar as transformações e operações desejadas no DataFrame 'df'
# Neste exemplo, apenas vamos imprimir os dados em tela
ds = (dx.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .start()
)