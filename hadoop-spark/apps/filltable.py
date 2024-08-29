from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CSV para PostgreSQL") \
    .getOrCreate()

df = spark.read.csv("file:///home/spark/apps/dataset.csv", sep=",", header=True, inferSchema=True)

#dff = df.filter((col("Radius(R/Ro)") >= 1) & (col("Star color") == 'Blue'))

df.write.format("jdbc")\
    .option("url","jdbc:postgresql://172.30.0.254:5432/pfdb") \
    .option("dbtable","tabelapf") \
    .option("user","postgres") \
    .option("password","spark") \
    .option("driver","org.postgresql.Driver") \
    .mode("append") \
    .save()

spark.stop()