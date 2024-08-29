# Importar as bibliotecas
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('spark-pf').getOrCreate()

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
            StructField("Temperature (K)", IntegerType(), True),
            StructField("Luminosity(L/Lo)", IntegerType(), True),
            StructField("Radius(R/Ro)", FloatType(), True),
            StructField("Absolute magnitude(Mv)", FloatType(), True),
            StructField("Star type", IntegerType(), True),
            StructField("Star color", StringType(), True),
            StructField("Spectral Class", StringType(), True)
        ]))
    ]))
])

dx = df.select(from_json(df.value.cast("string"), schema).alias("data")).select("data.payload.after.*")

dff = dx.filter((col("Radius(R/Ro)") >= 1) & (col("Star color") == 'Blue')) # Estrelas azuis maiores que o sol


def salva_postgresql(df, epoch_id):
    df.write.jdbc(
        url="jdbc:postgresql://172.30.0.254:5432/pfdb",
        table="tabelafilterpf",
        mode="append",
        properties={
            "user": "postgres",
            "password": "spark",
            "driver": "org.postgresql.Driver"
        }
    )


dfx = dff.writeStream \
    .foreachBatch(salva_postgresql) \
    .option("checkpointLocation", "/home/spark/apps/user/spark/checkpoint") \
    .start()